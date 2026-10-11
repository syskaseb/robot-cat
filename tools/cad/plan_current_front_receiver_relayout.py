"""One coupled FL receiver relocation, not another isolated cable offset.

The old front DATA/ground rails forced a long factory-cable reversal through
the head bay. Move both unselected W5 rails together into the electronics bay.
All nine affected electrical paths are explicitly invalidated. A clear FL3
math family alone cannot qualify the new rails, those paths or whole W5.
"""
import copy,itertools,json,math,time
from pathlib import Path
from plan_current_leg_body_joins import (ROOT,OUT,SHA,SharedMotionSpace,
    ankle_rise_basis,arch_family)
from screen_current_remaining_routes import route_rows


def run():
    tick=time.monotonic();pins={Path(__file__)}
    def load(name):
        f=OUT/name;pins.add(f);p=json.loads(f.read_text())
        for n,h in p.get('source_sha256',{}).items():assert SHA(ROOT/n)==h,n
        return p
    source=load('joined-leg-looms-plan.json')
    before=load('leg-body-joins-plan.json')
    ends=load('leg-terminations-plan.json')
    original={r['wire']:r for r in ends['wires']}
    # One coherent pair of real nominal purchased cases, not added duplicates.
    # These are project reservations; manufacturer lever/mount fit stays open.
    rails={
        'D_FL':dict(centre_mm=[70,60,110],casing_mm=[55,55.5,100.5,85,64.5,119.5],
                    first_port_mm=[60.5,60,119.5],old_first_port_mm=[-104.5,84,112.5]),
        'FL_G':dict(centre_mm=[110,84,110],casing_mm=[95,79.5,100.5,125,88.5,119.5],
                    first_port_mm=[100.5,84,119.5],old_first_port_mm=[-139.5,84,112.5])}
    for r in rails.values():
        r.update(SKU='WAGO221-415',entry_axis=[0,0,1],native_mount='OPEN',
                 lever_and_tool_access='OPEN',physical_case_verified=False)
        r['ports']={str(i):[r['first_port_mm'][0]+4.75*(i-1),*r['first_port_mm'][1:]] for i in range(1,6)}
    new_ends=copy.deepcopy(original)
    for row in new_ends.values():
        name,port=row['body_role'].split('.')
        if name in rails:
            row['body_point_mm']=rails[name]['ports'][port]
            row['body_departure_axis']=[0,0,1]
    changed=['W002','W004','W005','W006','W007','W019','W021','W023','W025']
    fixed,more=route_rows(tuple(OUT/(s+'-plan.json') for s in
                        ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    pins.update(more)
    for name in changed:fixed.pop(name,None)
    heads=load('head-wire-screen-reference.json')
    chosen=[copy.deepcopy(q) for q in before['looms'] if q['loom']!='FL3']
    space=SharedMotionSpace(list(fixed.values())+heads['rows'],chosen)
    raw=next(q for q in source['looms'] if q['loom']=='FL3')
    receivers=[new_ends[r['wire']]['body_point_mm'] for r in raw['cores'].values()]
    rejected=[];capacities=[];trials=0;accepted=None
    # Previous25 whole-prefix receipts are not rerun: only prefixes that were
    # clear at the previous planning gate can survive an unchanged source.
    prefix_bad={tuple(r['corridor_land_mm']) for r in before['shared_motion_station_rejections']
                if r['loom']=='FL3' and r.get('scope')=='WHOLE_SOURCE_PREFIX'}
    for east,inner in itertools.product((60,80,100,120,140),(20,40,60,0,80)):
        if (east,inner) in prefix_bad:continue
        loom=ankle_rise_basis(raw,east,inner)
        for floor,dock in itertools.product((160,190,220),itertools.product((30,60,90),(40,60,80),(120,160))):
            trials+=1
            candidate=arch_family(loom,list(dock),lambda a,b:max(a[2],b[2],floor))
            if candidate is None:continue
            lower=14+loom['initial_land_mm']+candidate['fixed_bundle_guide_mm']+max(math.dist(dock,p) for p in receivers)+21
            if lower>850:
                capacities.append(dict(dock_mm=dock,floor_mm=floor,blank_lower_bound_mm=lower));continue
            proposal=dict(loom='FL3',motion_stage=raw['motion_stage'],initial_land_mm=raw['initial_land_mm'],
                          cores=raw['cores'],**candidate,minimum_complete_blank_lower_bound_mm=lower,
                          corridor_land_mm=[east,inner])
            clear,hit=space.clear(proposal)
            if clear:accepted=proposal;break
            rejected.append(dict(dock_mm=dock,floor_mm=floor,**hit))
        if accepted:break
    chosen+=[] if accepted is None else [accepted]
    result=dict(status='FL_RECEIVER_RELAYOUT_MATH_ONLY' if accepted else 'REJECTED_FL_RECEIVER_RELAYOUT',
        rails=rails,changed_wire_ids=changed,leg_body_ends=list(new_ends.values()),looms=chosen,
        candidate_FL3=accepted,screen_rejections=rejected,capacity_rejections=capacities,trials=trials,
        retained_factory_mm=900,usable_factory_mm=850,selected=False,W5_complete=False,physical_pass=False,
        actual_material_open=True,native_open=True,
        invalidated=['W002 BUS D route, source jaw unchanged but downstream route NOT retained',
          'W007 DATA bridge and W025 ground trunk',
          'six FL DATA/GND fanouts; all three FL receiving restraints/supports/access',
          'whole static/moving mutual cable screen for changed interfaces'],
        unchanged=['R47 bank/fuses and FL positive terminals','all other electrical port assignments',
                   'P0/E6/15 drives/MG92B/325x200x160 torso; no new external enclosure'],
        limitations='This tests only a complete FL3 loose-bundle family against retained wires. New rail cases, nine full routes, grips and service MUST be planned together before any CAD or selection.',
        source_sha256={**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins},
          **{q:SHA(ROOT/q) for q in ('tools/cad/plan_current_leg_body_joins.py','tools/cad/screen_current_remaining_routes.py','tools/cad/route_current_leg_fanouts.py','tools/cad/screen_current_moving_looms.py')}},
        worker_seconds=time.monotonic()-tick)
    (OUT/'front-receiver-relayout-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],trials=trials,fixed_bundle_mm=None if accepted is None else accepted['fixed_bundle_guide_mm'],worker_seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':run()
