"""Bind all36 current body ends BEFORE any fan-out/native detail.

Current ground/DATA overlays supersede old register coordinates. A straight
distance is a LOWER length bound, never a buildable route or W5 acceptance.
"""
import json,math,time
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA

def plan():
    tick=time.monotonic();pins={Path(__file__)}
    def read(name):
        f=OUT/name;pins.add(f);return json.loads(f.read_text())
    looms=read('moving-looms-plan.json');register=read('harness-interfaces-plan.json')
    ground=read('ground-tree-plan.json');rows={r['id']:r for r in register['body_conductors']}
    wires=[]
    for loom in looms['looms']:
        for core,electrical in loom['cores'].items():
            wid=electrical['wire'];role=electrical['body_end']
            end=next(e for e in rows[wid]['current_ends'] if e['role']==role)
            point=end['point_mm'];departure=end['departure'];station,port=role.split('.')
            mapping=None
            if station in ground['rear_gallery']:
                mapping=ground['rear_ground_same_rail_mapping'] if station.endswith('_G') else None
                cavity=str(mapping[port]) if mapping else port
                point=ground['rear_gallery'][station]['ports'][cavity];departure=[0,0,1]
            elif station=='FR_G':
                mapping=ground['FR_ground_same_rail_mapping'];point=ground['front_ground_station']['ports'][str(mapping[port])]
                departure=[0,0,1]
            lower=math.dist(loom['body_dock_mm'],point)
            # Reserve30 already set aside in the loom allocation includes
            # land/trim/termination; don't add it a second time to this bound.
            margin=loom['body_fanout_budget_remaining_mm']-lower
            wires.append(dict(wire=wid,loom=loom['loom'],core=core,body_role=role,
                body_point_mm=point,body_departure_axis=departure,
                dock_mm=loom['body_dock_mm'],fanout_lower_bound_mm=lower,
                available_after_project_reserves_mm=loom['body_fanout_budget_remaining_mm'],
                optimistic_remaining_mm=margin,actual_cut_mm=None,
                current_same_rail_cavity_mapping=mapping,
                route_and_independent_relief='OPEN; no straight chord is accepted',
                stock='Part of this one900mm factory3core cable, NOT another wire purchase',
                delivered_Cu_OD_and_termination_compatibility='OPEN'))
    assert len(wires)==36 and len({r['wire'] for r in wires})==36
    bad=[r['wire'] for r in wires if r['optimistic_remaining_mm']<0]
    report=dict(status='REJECTED_FACTORY_LENGTH_LOWER_BOUND' if bad else 'CURRENT_36_TERMINATIONS_BOUND_ACTUAL_FANOUT_OPEN',
        wires=wires,rejected=bad,selected=False,W5_complete=False,physical_pass=False,
        factory_cables=12,factory_nominal_mm=900,six_packs=2,
        scope='All ends bound to current SAME-RAIL overlays; length capacity only. No inferred physical pin cavity order, manufacturer cable bend or accepted routing.',
        planning_seconds=time.monotonic()-tick,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins})
    (OUT/'leg-terminations-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],wires=len(wires),rejected=bad,
        minimum_optimistic_remaining_mm=min(r['optimistic_remaining_mm'] for r in wires),seconds=report['planning_seconds'])))
    return report

if __name__=='__main__':plan()
