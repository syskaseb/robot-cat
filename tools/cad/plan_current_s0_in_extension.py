"""Whole outward S0-IN lug departure, not a correction of the old inner tip.

Stud24mm pitch/seating remain provisional. The older IN lug pointed back
through its own nominal cylinder. Clock the entire replaceable lug WEST;
no invented manufacturer terminal bay and no M4/physical acceptance.
"""
import json,time,math
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,U,D,E,W,N,S,entry,straight,offset,SHA,line,curve,add,mul
from plan_current_main_pi_wiring import turn
from open_prototype_source_group import check_path
from screen_current_remaining_routes import route_rows
from open_prototype_path_preflight import screen
R=25.2

def plan():
    pf=OUT/'positive-source-plan.json'
    rows,pins=route_rows((OUT/'ground-tree-plan.json',OUT/'data-bridges-plan.json',pf))
    # Rotate/relocate the WHOLE protected post-F0 WAGO and BOTH approaches.
    # This removes the inherited UP exit that forced65.2mm into Foundation.
    # Keep the actual part count/circuit, intact F0 factory lead,9mm grips.
    factory=entry([3,-58.8,50],E,9);turn(factory,E,D,10);turn(factory,D,E,10)
    straight(factory,[50,-58.8,30]);check_path(factory,min_radius=10)
    # NW lug departure leaves the entire neck/head bay instead of returning
    # through its Y16 centre. North crossing atY59.69; lift outside x-178.
    axis=[-.5,math.sqrt(3)/2,0];arrival=mul(axis,-1)
    tip=add([-89,16,80],mul(axis,26.9));land=add(tip,mul(arrival,-9))
    a=math.pi/3;pre=add(land,[-R*math.sin(a),R*(1-math.cos(a)),0])
    corner=-190+R
    q=entry([50,-58.8,23.25],W)
    # Both ports point WEST; fan the whole OUT branch SOUTH20 before rise:
    # north passes through P0 side frame and F0 casing, not a wire-only gap.
    # it cannot cross the intact F0 factory return in the same plane.
    offset(q,W,S,30)
    #43mm south aisle is below all FR inputs/head supply and outside F0.
    offset(q,W,U,23.75)
    straight(q,[corner,-88.8,47]);turn(q,W,N,R)
    offset(q,N,U,33);straight(q,[corner-R,pre[1]-R,80]);turn(q,N,E,R)
    straight(q,pre)
    def at(t):return add(pre,[R*math.sin(t),-R*(1-math.cos(t)),0])
    q.append(curve(pre,at(a),at(a/2),R,a));straight(q,tip);check_path(q,min_radius=R)
    routes={'W076_EXTENSION':dict(parts=q,radius_mm=2.1,guide_mm=sum(v['length_mm'] for v in q),
      endpoints=['POST_F0.2','S0.IN.barrel_tip'],termination_allowance_mm=26,actual_cut_mm=None,
      material='HELU23802 red4mm2',static_R_mm=R),
      'W076_FACTORY':dict(parts=factory,radius_mm=2.25,guide_mm=sum(v['length_mm'] for v in factory),
        endpoints=['F0.out','POST_F0.1'],termination_allowance_mm=11,actual_cut_mm=None,
        shortest_factory_mm=84.5,material='Original FHAC0002ZXJ12AWG',static_R_mm=10)}
    assert routes['W076_FACTORY']['guide_mm']+11<=84.5
    rows.pop('W076_EXTENSION',None)
    rows.pop('W076_FACTORY',None)
    g=screen(dict(tails=list(rows.values()),s1_routes=[dict(wire=n,OD_mm=2*v['radius_mm'],segments=v['parts']) for n,v in routes.items()],holders=[]))
    bad=[v for v in g['near_pairs'] if v['b'] in routes and v['status']=='REJECT_PLANNING_PROXIMITY']
    pins.update((Path(__file__),ROOT/'tools/cad/whole_cat_interior.py'))
    return dict(status='REJECTED_OUTWARD_S0_IN_PLAN' if bad else 'OUTWARD_S0_IN_PLAN_ACTUAL_TERMINAL_GATE_OPEN',
      routes=routes,rejected=bad,screen_seconds=g['worker_seconds'],selected=False,W5_complete=False,physical_pass=False,
      post_F0=dict(casing_mm=[50,-63.3,21.5,69,-54.3,35.5],ports={'1':[50,-58.8,30],'2':[50,-58.8,23.25]},
        departure=W,part='SAME protected221-412, no extra connection',
        physical_rotation_basis={'localX':[0,0,-1],'localY':W,'localZ':N},
        native_retention='OPEN; whole case/lever approach rotated with both ends, never old support'),
      source_change=dict(replace='S0_ring_IN only',stud_centre_mm=[-89,16,80],new_barrel_axis=axis,
        new_barrel_tip_mm=tip,rotation_z_degrees=180,terminal='Existing TE130207 allocation, no additional ring',
        same_net=True,stud_nut_washer='UNCHANGED',manufacturer_stud_datums_verified=False),
      route_architecture='Whole post-F0 WAGO WEST with both approaches; SOUTH30 fan before rise,47mm aisle above sampled leg housing, lift outsideFoundation X-190, cross north of entire head atY59.69 and9mm SE approach to outward NW lug. No structural cuts/closed-shell claim.',
      delivery_gates=['Actual S0 terminal bay, stud pitch/seating, tool and insulation; no nominal cylinder metal inference',
        'Actual source/terminal support and independent insulation grips, current geometry and movement'],
      source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'s0-in-extension-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],guide_mm=p['routes']['W076_EXTENSION']['guide_mm'],rejected=p['rejected'],seconds=p['planning_seconds'])))
