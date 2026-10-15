"""Shared actual-world gate for G2's four ends and FL_G/W025.

Unchanged paths are inputs, not rerouted. No native selection or phase credit.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from current_mixed_receiver_material import prepare,material
from short_feed_lacing_saddle import build as feed_material
from current_g2_feed_restraints import geometry as g2_geometry
from current_fl_ground_feed import geometry as fl_geometry
from current_body36_candidates import resolve
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from current_work_guard import check


def run():
    check();tick=time.monotonic()
    targets,wires,pins,grips=prepare()
    for name,g in grips['groups'].items():
        profile,parts=material(g)
        targets.update({'Group_'+name+'/'+k:s for k,s in parts.items() if k!='seed'})
        if g['kind']=='triple':
            for feed in g['feeds']:
                q=feed_material(profile['recipe'],feed,support='cap' if name=='D_FL' and feed['wire']=='W002' else 'body')
                targets.update({'Feed_'+name+'/'+feed['wire']+'/'+k:q[k] for k in ('body','band')})
    rf=P.OUT/'body36-receiver-support-reservations.json'
    rooted=json.loads(rf.read_text())
    for n,h in rooted['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for row in rooted['groups']:
        for path in row['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+row['name']+'/'+row['wire']+'/'+str(i)]=arm_box(a,b,row['arm_half_widths_world_mm'])
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    current,ancestry=resolve(macro,P.ROOT)
    wires={n:v for n,v in wires.items() if not n.startswith('body/')}
    wires.update({'body/'+n:(P.wire(r['parts']),1) for n,r in current.items()})
    candidates=g2_geometry();candidates['FL_G']=fl_geometry()
    records=[];unions=[];errors=[];checks=0
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'remaining-fixed-feed-pairs.json',bounds.near)
    def same_print(owner,n):
        if n.split('/')[0]==owner or n.startswith(('Root/'+owner+'/', 'ReceiverRoot/'+owner+'/')):
            return True
        if n=='Source/'+owner+'/body/0':return True
        if n.startswith('Group_') and n.endswith('/body'):
            return grips['groups'][n.split('/')[0].removeprefix('Group_')]['owner']==owner
        return False
    for f in (Path(__file__),Path(__file__).with_name('current_g2_feed_restraints.py'),
              Path(__file__).with_name('current_fl_ground_feed.py'),mf,rf):
        pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    def save():
        complete=len(records)==6 and len(unions)==2 and not errors and all(not r['contacts'] for r in records)
        result=dict(status='FIVE_REMAINING_FIXED_FEEDS_COMPONENT_GATE_CLEAR' if complete else 'REMAINING_FIXED_FEEDS_COMPONENT_GATE_OPEN',
            components=records,parent_unions=unions,recipes={n:q['recipe'] for n,q in candidates.items()},
            checks=checks,errors=errors,source_sha256=pins,candidate_receipt_ancestry=ancestry,
            worker_seconds=round(time.monotonic()-tick,3),full36accepted=not macro['remaining_wire_ids'],
            selected=False,native_complete=False,W5_complete=False,physical_pass=False,
            lacing_candidate_blanks=3,lacing_candidate_mm=450,
            assembly_plan=['Install printed parents before attaching WAGO cases',
                'Lay three equal G2 heavy jackets onto common land; retain W003 separately',
                'Bind FL_G/W025 independently of three body receiver grips',
                'Support cases while opening levers; verify actual delivered retention/access/creep in phase2'])
        f=P.OUT/'remaining-fixed-feed-checks.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    save()
    for owner in sorted({q['recipe']['parent'] for q in candidates.values()}):
        check();key=owner+'/0/0';assert key in targets,('Missing actual parent',key)
        bodies=[q['body'] for q in candidates.values() if q['recipe']['parent']==owner]
        parent=targets[key]
        attachment=[]
        for body in bodies:
            contacts=[n for n,s in targets.items() if same_print(owner,n) and bounds.near(body,s)
                      and body.common(s).Volume>1e-6]
            attachment.append(contacts)
            if not contacts:errors.append('No rooted printed attachment for '+owner)
        # The FL attachment can be on an already rooted receiver seat, not
        # the obsolete bare Frame. Reuse its complete pinned root graph;
        # the final native Frame union is still required exactly once.
        if owner=='FrontLeftFixedCarrier':
            unions.append(dict(parent=owner,rooted_component_attachments=attachment,
                               prior_root_graph_verified=True,native_union_open=True))
        else:
            joined=parent.multiFuse(bodies).removeSplitter()
            valid=joined.isValid() and len(joined.Solids)==1 and not joined.check(True)
            if not valid:errors.append('Invalid parent/feed union '+owner)
            unions.append(dict(parent=owner,one_solid=valid,valid_BOP=valid,rooted_component_attachments=attachment))
        save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        checks+=1
        try:
            gap,volume=cache.check(a,b,0,r)
            return volume>1e-5 or (r and gap<r-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:
            errors.append(str(e));return True
    for name,q in candidates.items():
        owner=q['recipe']['parent'];own=q['recipe'].get('wires',[q['recipe'].get('wire')])
        for kind in ('body','band'):
            check();s=q[kind];contacts=[]
            for n,t in targets.items():
                if kind=='body' and same_print(owner,n):continue
                if hit(s,t):contacts.append('material/'+n)
            for n,(wire,r) in wires.items():
                if hit(s,wire,r if n in {'wire/'+w for w in own} else r+.25):contacts.append('curve/'+n)
            for other,v in candidates.items():
                for k in ('body','band'):
                    if other==name and k==kind:continue
                    if hit(s,v[k]):contacts.append('candidate/'+other+'/'+k)
            records.append(dict(component=name+'/'+kind,contacts=contacts));save()
            print('Remaining feed',name,kind,'contacts',contacts,'checks',checks,flush=True)
    save()


if __name__=='__main__':run()
