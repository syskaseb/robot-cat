"""One coupled MAIN/Pi east departure and four independent grip stations.

Retains all electrical endpoints, the sealed USB plug, source splice, P0 and
all eight Knee sections. Replaces three OPEN north-going MAIN routes together,
not a scalar Hip-loop retry. Existing MAIN return is unchanged.
"""
import json, math, time
from pathlib import Path
from plan_current_main_sources import ROOT, OUT, SHA, E, N, S, U, D, W, line, reverse
from plan_current_main_pi_wiring import turn, straight, R
from open_prototype_source_group import check_path
from route_current_leg_fanouts import sampling_parts
from screen_current_remaining_routes import route_rows
from screen_current_moving_looms import only_new_pairs
from check_current_hip_axial_looms import parts as hip_parts


def build():
    tick=time.monotonic(); source=OUT/'main-pi-plan.json'
    previous=json.loads(source.read_text()); routes={}; grips={}
    # Both first arcs share a centre: outer red R14.6 and inner black R11.1.
    # A higher inner arc would cut across the adjacent red departure.
    for wid,x,endx,rise in [('W079',-48.68,-9.1,14.6),('W080',-45.18,-12.6,11.1)]:
        top=57.3+rise
        q=[line([x,21.289,51.0948],[x,21.289,57.3])]
        turn(q,U,E,rise); a=q[-1]['end']; straight(q,[a[0]+9,a[1],a[2]])
        grips[wid]=dict(start_mm=a,end_mm=q[-1]['end'],insulation_land_mm=9)
        bend=endx-q[-1]['end'][0]; assert bend>=R
        turn(q,E,S,bend)
        tail=[line([endx,-53,45.2],[endx,-62,45.2])]
        turn(tail,S,U);straight(tail,[endx,-73.1,top-R]);turn(tail,U,N)
        straight(q,tail[-1]['end']);q+=reverse(tail)
        routes[wid]=dict(previous['routes'][wid],parts=q,guide_mm=sum(p['length_mm'] for p in q))
    # Full VIN route from its unchanged splice to an EAST pad approach.
    x=-38.18;top=65.1948
    tail=[line([x,21.289,51.0948],[x,21.289,top-R])]
    turn(tail,U,E);a=tail[-1]['end'];straight(tail,[a[0]+9,a[1],a[2]])
    grips['W078']=dict(start_mm=a,end_mm=tail[-1]['end'],insulation_land_mm=9)
    # The inherited factory straight measured6.911mm, not the stated8mm
    # lap. Make the whole joint straight8mm before any new grip/selection.
    factory=list(previous['routes']['W077']['parts'])
    factory[-1]=line(factory[-1]['start'],[19,71.5,88.9])
    assert abs(factory[-1]['length_mm']-8)<1e-6
    q=[line([19,79.5,88.9],[19,32.389,88.9])]
    turn(q,S,D);straight(q,[19,21.289,top+R]);turn(q,D,W)
    straight(q,tail[-1]['end']);q+=reverse(tail)
    routes['W078']=dict(previous['routes']['W078'],parts=q,guide_mm=sum(p['length_mm'] for p in q))
    routes['W077']=dict(previous['routes']['W077'],parts=factory,guide_mm=sum(p['length_mm'] for p in factory))
    grips['W060']=dict(start_mm=[-41.68,10.189,65.1948],end_mm=[-41.68,1.189,65.1948],insulation_land_mm=9)
    for n,r in routes.items():
        expected_start=[19,79.5,88.9] if n=='W078' else previous['routes'][n]['parts'][0]['start']
        expected_end=[19,71.5,88.9] if n=='W077' else previous['routes'][n]['parts'][-1]['end']
        check_path(r['parts'],start=expected_start,end=expected_end,min_radius=6 if n=='W077' else R)
        assert r['guide_mm']+(8 if n=='W077' else 3) <= (100 if n=='W077' else 150 if n=='W078' else 250),n
    tags=('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')
    retained,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in tags))
    fixed=[dict(r,segments=sampling_parts(r['segments'])) for n,r in retained.items() if n not in routes]
    # The existing protected opposed8mm solder lap is intentional. Screen
    # its insulated factory prefix separately; do NOT exempt other pairs.
    head=OUT/'head-wire-screen-reference.json';hp=json.loads(head.read_text())
    fixed += [dict(r,segments=sampling_parts(r['segments'])) for r in hp['rows']]
    hip=OUT/'hip-axial-loom-plan.json';hips=json.loads(hip.read_text())
    for r in hips['loops']:
        fixed.append(dict(wire=r['section'],OD_mm=6,segments=sampling_parts(hip_parts(r,0))))
    new=[dict(wire=n,OD_mm=2*r['radius_mm'],segments=sampling_parts(r['parts'])) for n,r in routes.items()]
    near=only_new_pairs(fixed,new)
    # Remaining touching insulation edges at the two lap entrances are
    # checked as part of the existing sleeve joint, not as free-wire space.
    def own_lap(q):
        return {q['a'],q['b']}=={'W077','W078'} and all(
            16.6<=p[0]<=21.4 and 66.589<=p[1]<=86.589 and 86.5<=p[2]<=91.3
            for p in (q['sample_a_mm'],q['sample_b_mm']))
    bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY' and not own_lap(q)]
    p=dict(status='REJECTED_MAIN_EAST_COMB_SCREEN' if bad else 'MAIN_EAST_COMB_SCREEN_ONLY_MATERIAL_AND_NATIVE_OPEN',
        routes=routes,grips=grips,rejected=bad,near_pairs=near,selected=False,physical_pass=False,W5_complete=False,
        retained_MAIN_return=True,retained_source_splice=False,retained_USB_plug=True,
        corrected_source_splice=dict(factory_tip_mm=[19,71.5,88.9],custom_tip_mm=[19,79.5,88.9],
            opposed_straight_lap_mm=8,sleeve_bounds_mm=[16.6,66.589,86.5,21.4,86.589,91.3],
            reason='Inherited factory straight6.911mm was shorter than stated8mm lap; no source holder or net change'),
        intended_joint='Only W077/W078 opposed8mm lap inside existing RNF sleeve; no free-space exemption',
        shared_hip_reference='hip-axial-loom-plan.json remains REJECTED; only new MAIN clearance is tested, no Hip selection',
        assumptions=['Independent9mm insulation grip per core; bare3mm pad rise and delivered solder/fit gate unchanged',
            'Concentric/split-height whole east output fan replaces north crossings; actual support foot and service open'],
        worker_seconds=time.monotonic()-tick,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins|{source,head,hip,Path(__file__)}})
    (OUT/'main-east-comb-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],guides_mm={n:r['guide_mm'] for n,r in routes.items()},rejected=bad,seconds=p['worker_seconds'])),flush=True)
    return p


if __name__=='__main__':build()
