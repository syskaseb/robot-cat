"""Route changed middles in the joint36 receiver/current source scene.

Received full curves stay immutable except explicitly replaced wire IDs.
Planning meshes propose only;
actual changed whole curves require exact distance checks before acceptance.
"""
import copy,gc,json,math,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
import core_receiver_port as T
import plan_body_fanout_layout as R
from current_core_corridor import corridor
from current_mixed_receiver_material import material,prepare
from csg_bore_clearance import prove as prove_bores
from current_core_planning_scene import build
from plan_body36_receiver_space import shared_context,P,C
from check_body_fanout_material import mate_names,terminal_trim
from plan_axial_source_supports import arm_box


def run():
    tick=time.monotonic();cf=P.OUT/'body36-current-contract.json';gf=P.OUT/'receiver-joint-selection.json'
    contract=json.loads(cf.read_text());targets,old,pins,grips=prepare()
    assert grips['status']=='BOLTED36_RECEIVER_LAYOUT_JOINT_CLEAR_MIDDLES_OPEN'
    assert len(grips['groups'])==22
    for n,h in grips['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    changed=grips['changed_wire_ids'];replaced=set(grips.get('replaced_wire_ids',[]))
    for name in replaced:old.pop('body/'+name)
    targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    rows={r['wire']:copy.deepcopy(r) for r in contract['rows']};profiles={};analytic={};group_for_wire={}
    for group_id,q in grips['groups'].items():
        for row in q['rows']:
            if row['wire'] in changed:rows[row['wire']]=row
        profile,components=material(q);profiles[group_id]=profile
        for name in q['wires']:group_for_wire[name]=group_id
        for kind,s in components.items():
            key='Group_'+group_id+'/'+kind;targets[key]=s
            if q['kind']=='triple' and kind in ('body','cap'):analytic[key]=(profile['recipe'],kind)
    breakoutfile=P.OUT/'rl1-straight-breakout.json'
    breakout=json.loads(breakoutfile.read_text())
    assert breakout['status']=='RL1_THREE_STRAIGHT_BREAKOUTS_EXACT_CLEAR_FULL_MIDDLES_OPEN'
    assert not breakout['contacts'] and not breakout['errors']
    for n,h in breakout['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for name,row in breakout['replacement_rows'].items():
        assert row['receiving_parts']==rows[name]['receiving_parts']
        rows[name]=row
        old['fan/'+row['loom']+'/'+row['core']]=(P.wire(row['source_parts']),1)
    exitfile=P.OUT/'body36-exit-diagnosis.json';exits=json.loads(exitfile.read_text())
    for n,h in exits['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    rootfile=P.OUT/'body36-receiver-support-reservations.json';rootplan=json.loads(rootfile.read_text())
    assert rootplan['status']=='ALL_GROUPED_RECEIVER_SUPPORT_RESERVATIONS_CLEAR_MIDDLES_OPEN'
    assert rootplan['support_first'] and len(rootplan['groups'])==22
    for n,h in rootplan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for row in rootplan['groups']:
        assert row['paths'],row['wire']
        for path in row['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+row['name']+'/'+row['wire']+'/'+str(i)]=arm_box(a,b,row['arm_half_widths_world_mm'])
    planning_wires=dict(old)
    for name,row in rows.items():
        key='fan/'+row['loom']+'/'+row['core']
        if key in planning_wires:planning_wires['new/'+name+'/source']=planning_wires.pop(key)
        if name in changed:
            planning_wires['new/'+name+'/receiver']=(P.wire(row['receiving_parts']),1)
    for name in list(planning_wires):
        if name.startswith('chosen/'):
            planning_wires['leg/'+name.removeprefix('chosen/')]=planning_wires.pop(name)
    scene=build(targets,planning_wires);inherited={n:r for n,r in contract['inherited_routes'].items() if n not in replaced}
    routes=copy.deepcopy(inherited)
    failures={};contacts=[];errors=[];completed=[];checks=0
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in
        (cf,gf,rootfile,breakoutfile,exitfile,Path(__file__),Path(__file__).with_name('current_core_corridor.py'),
         Path(__file__).with_name('current_core_planning_scene.py'),Path(__file__).with_name('current_mixed_receiver_material.py'),
         Path(__file__).with_name('plan_bolted_receiver_layout.py'),Path(__file__).with_name('bolted_rail_pressure_bridge.py'),
         Path(__file__).with_name('csg_bore_clearance.py'))})
    def save(status):
        receipt=dict(status=status,rows=list(rows.values()),routes=routes,route_failures=failures,
            inherited_routes=len(inherited),changed_wire_ids=changed,replaced_wire_ids=list(replaced),
            completed_changed_routes=completed,contacts=contacts,errors=errors,
            changed_pairs=checks,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False,
            scope='Current36wholecurves plus22ROOTEDrestraints/7caps/21bands/oneM2cap+screw/nut/tool/8sourcearms.16middles planned AFTER all receiverarms. Native/19otherguides/stock OPEN.')
        out=P.OUT/'body36-current-layout.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');tmp.replace(out)
    original_clear=scene.clear
    for name in changed:
        row=rows[name]
        known={tuple(np.round(p,7)) for part in row.get('source_parts',[row['source_land']])+row['receiving_parts'] for p in R.part_points(part)}
        # These exact qualified first bends may bypass a conservative mesh
        # proposal rejection, NEVER the final whole-curve BRep acceptance.
        for option in exits['exits'][name]:
            if not option['contacts'] and math.dist(option['part']['start'],row['free_start'])<1e-7:
                known.update(tuple(np.round(p,7)) for p in R.part_points(option['part']))
        def clear(points,r):
            remaining=np.asarray([p for p in points if tuple(np.round(p,7)) not in known])
            return True if not len(remaining) else original_clear(remaining,r)
        scene.clear=clear
        result,points=corridor(scene,row,backward=False)
        if points is None:result,points=corridor(scene,row,backward=True)
        if points is None:failures[name]=dict(result=result,blockers=scene.blockers)
        else:
            routes[name]=result;scene.add_points('new/'+name,points)
        save('PARTIAL_CURRENT_BODY36_MIDDLE_PLAN')
        print('current body middle',name,points is not None,result.get('guide_mm'),flush=True)
    del scene;gc.collect()
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-current-layout-pairs.json',bounds.near)
    allcurves={n:P.wire(q['parts']) for n,q in routes.items()};last=time.monotonic()
    def check(name,s,target,t,rs=1.25,rt=0):
        nonlocal checks,last
        if not bounds.near(s,t,rs+rt+.0001):return
        if not rt and target in analytic:
            recipe,kind=analytic[target]
            if prove_bores(recipe,kind,s,rs):return
        checks+=1
        try:
            gap,vol=cache.check(s,t,rs,rt)
            if vol>1e-5 or gap<rs+rt-1e-6:contacts.append(dict(wire=name,target=target,gap_mm=gap,required_mm=rs+rt,volume_mm3=vol))
        except (AssertionError,ValueError,RuntimeError) as e:errors.append(dict(wire=name,target=target,error=str(e)))
        if time.monotonic()-last>20:cache.save();save('PARTIAL_CURRENT_BODY36_EXACT_GATE');last=time.monotonic()
    checked=[]
    for name in changed:
        if name not in routes:continue
        row=rows[name];parts=routes[name]['parts'];whole=allcurves[name];mouth=P.wire(terminal_trim(parts))
        source=row.get('source_parts',[row['source_land']]);after=P.wire(row.get('source_after_jacket_first5_mm',source[1:])+parts[len(source):])
        for target,s in targets.items():
            if target.startswith('Group_'+group_for_wire[name]+'/band'):
                landpart=row['receiving_parts'][row['receiving_grip_part_index']]
                check(name,P.wire([landpart]),target+'/land',s,1)
                other=[p for p in parts if p!=landpart]
                check(name,Part.makeCompound([P.wire([p]) for p in other]),target+'/rest',s)
            else:check(name,mouth if target.split('/')[0] in mate_names(row) else whole,target,s)
        for target,(w,r) in old.items():
            if target=='fan/'+row['loom']+'/'+row['core']:continue # Same conductor prefix, self-screened as part of whole route.
            ownbundle=target.startswith('leg/'+row['loom']+'/') or target.startswith('chosen/'+row['loom']+'/')
            check(name,after if ownbundle else whole,target,w,rt=r)
        for other in [*inherited,*checked]:check(name,whole,'body/'+other,allcurves[other],rt=1)
        checked.append(name);completed.append(name);cache.save();save('PARTIAL_CURRENT_BODY36_EXACT_GATE')
        print('body36 exact',name,'pairs',checks,'contacts',len(contacts),'errors',len(errors),flush=True)
    status='REJECTED_CURRENT_BODY36_LAYOUT' if contacts or errors else ('CURRENT36_CURVES_AND_RECEIVER_GRIPS_EXACT_CLEAR_ROOT_ARMS_NATIVE_OPEN' if len(completed)==len(changed) else 'PARTIAL_CURRENT_BODY36_LAYOUT_CLEAR_REMAINING_OPEN')
    save(status);cache.save()


if __name__=='__main__':run()
