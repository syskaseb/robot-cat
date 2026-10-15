"""One shared RL1 straight breakout before bends; no Frame/case movement."""
import copy,json,time
from pathlib import Path
import FreeCAD as A
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from plan_current_mta_interfaces import line
from csg_bore_clearance import prove


def run():
    tick=time.monotonic();targets,old,pins,grips=prepare()
    contractfile=P.OUT/'body36-current-contract.json';contract=json.loads(contractfile.read_text())
    rows={r['wire']:copy.deepcopy(r) for r in contract['rows']};analytic={}
    for name,g in grips['groups'].items():
        p,parts=material(g)
        for r in g['rows']:
            if r['wire'] in grips['changed_wire_ids']:rows[r['wire']]=copy.deepcopy(r)
        for kind,s in parts.items():
            key='Group_'+name+'/'+kind;targets[key]=s
            if g['kind']=='triple' and kind in ('body','cap'):analytic[key]=(p['recipe'],kind)
    rootfile=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rootfile.read_text())
    for r in roots['groups']:
        for path in r['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+r['name']+'/'+r['wire']+'/'+str(i)]=arm_box(a,b,r['arm_half_widths_world_mm'])
    for n in grips.get('replaced_wire_ids',[]):old.pop('body/'+n,None)
    for n in list(old):
        if n.startswith('fan/RL1/'):old.pop(n)
    # Keep the same three copper centres at the actual jacket mouth and the
    # same source clamp. A parallel-X departure avoids the arm's Y43 wall.
    changed={};curves={};trimmed={}
    for name,row in rows.items():
        if row['loom']!='RL1':continue
        start=row['source_parts'][0]['start'];end=[start[0]-22.75,start[1],start[2]]
        parts=[line(start,end)];after5=[line([start[0]-5,start[1],start[2]],end)]
        changed[name]=dict(row,source_parts=parts,source_land=parts[0],free_start=end,
            source_free_axis=[-1,0,0],source_after_jacket_first5_mm=after5,
            source_prefix_revision='RL1 shared straight22.75mm before body bends')
        curves[name]=P.wire(parts);trimmed[name]=P.wire(after5)
    assert set(changed)=={'W013','W047','W069'}
    bounds=C.ImmutableBounds();contacts=[];errors=[];pairs=0
    def check(name,s,target,t,rs=1.25,rt=0):
        nonlocal pairs
        if not bounds.near(s,t,rs+rt+.0001):return
        if target in analytic and prove(*analytic[target],s,rs):return
        pairs+=1
        try:
            gap,witness,_=s.distToShape(t)
            if gap<rs+rt-1e-6:contacts.append(dict(wire=name,target=target,gap_mm=gap,
                required_mm=rs+rt,witness_mm=[list(v) for v in witness[0]] if witness else None))
        except (RuntimeError,AssertionError,ValueError) as e:errors.append(dict(wire=name,target=target,error=str(e)))
    for name,s in curves.items():
        for n,t in targets.items():check(name,s,n,t)
        for n,(t,r) in old.items():check(name,trimmed[name] if n.startswith('chosen/RL1/') or n.startswith('leg/RL1/') else s,n,t,rt=r)
        for other,t in curves.items():
            if other<name:check(name,s,'new/'+other,t,rt=1)
        print('RL straight source',name,'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    files=[contractfile,rootfile,P.OUT/'receiver-joint-selection.json',P.OUT/'body36-exit-diagnosis.json',Path(__file__)]
    receipt=dict(status='RL1_THREE_STRAIGHT_BREAKOUTS_EXACT_CLEAR_FULL_MIDDLES_OPEN' if not contacts and not errors else 'REJECTED_RL1_STRAIGHT_BREAKOUT',
        replacement_rows=changed,contacts=contacts,errors=errors,pairs=pairs,
        unchanged='Original source clamp/bundle/flex,8source arms,22receiver roots,all other source fans/20wholebody routes; no Frame cut or case movement.',
        source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files}},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'rl1-straight-breakout.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
