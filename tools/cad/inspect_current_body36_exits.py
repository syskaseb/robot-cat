"""Diagnose shared first bends using exact geometry, not more grid searches."""
import copy,json,time
from pathlib import Path
import FreeCAD as A
import Part
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C,AXES
from plan_axial_source_supports import arm_box
from plan_current_moving_looms import exact_quarter,add,mul
from plan_current_mta_interfaces import line
from csg_bore_clearance import prove


def run():
    tick=time.monotonic();targets,old,pins,grips=prepare()
    contract=json.loads((P.OUT/'body36-current-contract.json').read_text())
    rows={r['wire']:copy.deepcopy(r) for r in contract['rows']}
    analytic={}
    for name,g in grips['groups'].items():
        p,parts=material(g)
        for row in g['rows']:
            if row['wire'] in grips['changed_wire_ids']:rows[row['wire']]=row
        for kind,s in parts.items():
            key='Group_'+name+'/'+kind;targets[key]=s
            if g['kind']=='triple' and kind in ('body','cap'):analytic[key]=(p['recipe'],kind)
    rootfile=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rootfile.read_text())
    for row in roots['groups']:
        for path in row['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+row['name']+'/'+row['wire']+'/'+str(i)]=arm_box(a,b,row['arm_half_widths_world_mm'])
    for n in grips.get('replaced_wire_ids',[]):old.pop('body/'+n,None)
    bounds=C.ImmutableBounds();result={};pairs=0
    def hit(s,t,r):
        nonlocal pairs
        if not bounds.near(s,t,1.25+r+.0001):return None
        pairs+=1;gap,witness,_=s.distToShape(t)
        if gap<1.25+r-1e-6:
            return dict(gap_mm=gap,required_mm=1.25+r,
                        witness_mm=[list(v) for v in witness[0]] if witness else None)
    def save():
        files=[rootfile,P.OUT/'receiver-joint-selection.json',P.OUT/'body36-current-contract.json',Path(__file__)]
        receipt=dict(status='EXACT_FIRST_BEND_DIAGNOSIS_NOT_FULL_ROUTES',exits=result,pairs=pairs,
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files}},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
        p=P.OUT/'body36-exit-diagnosis.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');tmp.replace(p)
    for name in grips['changed_wire_ids']:
        row=rows[name];options=[]
        start=row['free_start'];u=row.get('source_free_axis',row['bodyward_bundle_tangent'])
        for v in AXES:
            if sum(a*b for a,b in zip(u,v))==-1:continue
            part=line(start,add(start,mul(u,10))) if list(v)==list(u) else exact_quarter(start,u,v,10)
            wire=P.wire([part]);contacts=[]
            for n,t in targets.items():
                if n in analytic and prove(*analytic[n],wire,1.25):continue
                contact=hit(wire,t,0)
                if contact:contacts.append(dict(target=n,**contact))
            for n,(t,r) in old.items():
                if n=='fan/'+row['loom']+'/'+row['core']:continue
                contact=hit(wire,t,r)
                if contact:contacts.append(dict(target=n,**contact))
            options.append(dict(end_axis=v,part=part,contacts=contacts))
        result[name]=options;save()
        print('Exact source exit',name,'clear',sum(not o['contacts'] for o in options),
              'blockers',sorted({c['target'] for o in options for c in o['contacts']}),flush=True)
    save()


if __name__=='__main__':run()
