"""Join all12 moving bundles and36 static fan-outs BEFORE more material CAD.

No outboard printed wings or fictional body clamps at curve joins. Remove the
unnecessary external UP/DOWN return previously imposed before fan-out. One
UP-arriving virtual join per cable; complete CORE length stays constant,
not the arbitrary bundle subsection. Actual body relief is
the9mm insulated receiving land. Project OD/radii remain delivery gates.
"""
import json,math,time,itertools
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA,add,mul,sub,norm,curve_length,best_span,exact_quarter,vertical_s
from plan_current_mta_interfaces import line
UP=[0,0,1];DOWN=[0,0,-1];R=10

def reverse_parts(parts):
    return [dict(q,start=q['end'],end=q['start']) for q in reversed(parts)]

def leave_port(point,axis,direction,land=9,spread=4):
    """Preserve the receiving grip BEFORE leaving its occupied vertical column.

    Both UP and DOWN mouths become UP-arriving free ends, using two R10
    quarters. In particular V leaves the W066 crossing laterally, not through
    its fixed source conductor. This is a candidate, not a clearance waiver.
    """
    tail=add(point,mul(axis,land));parts=[line(point,tail)]
    parts.append(exact_quarter(tail,axis,direction,R))
    p=parts[-1]['end'];parts.append(line(p,add(p,mul(direction,spread))))
    parts.append(exact_quarter(parts[-1]['end'],direction,UP,R))
    return parts

def whole_fanout(join,point,departure,core,loom,extra_length=0):
    angle={'D':0,'G':120,'V':240}[core]*math.pi/180
    radial=[math.cos(angle),math.sin(angle),0]
    start=add(join,mul(radial,1.2))
    # Three radial departures separate the cores instead of bending three
    # touching parallel columns in the same plane (which makes them cross).
    breakout=leave_port(start,UP,radial,land=5)
    side=1 if point[1]>0 else -1
    receiving=leave_port(point,departure,[0,side,0])
    root=breakout[-1]['end'];target=receiving[-1]['end']
    lane=({'D':0,'G':2,'V':4}[core]+int(loom[-1])-1)
    middle=bridge(root,target,DOWN,lane=lane,extra_length=extra_length)
    if middle is None:return None
    return breakout+middle+reverse_parts(receiving)

def bridge(start,end,arrival,lane=0,extra_length=0):
    """Exact circles/lands, no impossible one-cubic180return requirement."""
    delta=sub(end,start);delta[2]=0;distance=norm(delta)
    if distance<1e-6:return None
    direction=mul(delta,1/distance);parts=[]
    def straight(p):
        a=parts[-1]['end'] if parts else start
        if math.dist(a,p)>1e-8:parts.append(line(a,p))
    def quarter(u,v):
        a=parts[-1]['end'] if parts else start
        parts.append(exact_quarter(a,u,v,R))
    if arrival==DOWN:
        if distance<2*R:return None
        peak=max(start[2],end[2])+R+lane*4+extra_length/2
        straight([*start[:2],peak]);quarter(UP,direction)
        straight(add(parts[-1]['end'],mul(direction,distance-2*R)))
        quarter(direction,DOWN);straight(end)
    else:
        away=mul(direction,-1);quarter(UP,away);quarter(away,DOWN)
        bottom=min(start[2],end[2])-R-lane*4-extra_length/2
        straight([*parts[-1]['end'][:2],bottom]);quarter(DOWN,direction)
        straight(add(parts[-1]['end'],mul(direction,distance)))
        quarter(direction,UP);straight(end)
    assert math.dist(parts[-1]['end'],end)<1e-6
    for a,b in zip(parts,parts[1:]):assert math.dist(a['end'],b['start'])<1e-6
    return parts

def plan():
    tick=time.monotonic();lf=OUT/'moving-looms-plan.json';ef=OUT/'leg-terminations-plan.json'
    basis=json.loads(lf.read_text());ends=json.loads(ef.read_text());result=[];bad=[]
    assert basis['allocation_revision']==10 and basis['status']=='PROJECT_FLEX_ALLOCATION_ONLY'
    for n,h in ends['source_sha256'].items():assert SHA(ROOT/n)==h,n
    for old in basis['looms']:
        front_knee=old['loom'] in ('FL2','FR2');poses=[]
        if front_knee:
            poses=old['poses'];join=old['body_dock_mm'];flex=old['constant_flex_budget_mm']
        else:
            join=old['poses'][0]['spans_mm'][0][-1]
            for v in old['poses']:
                prefix=v['departure_parts_mm']
                length=sum(curve_length(q) for q in v['spans_mm'])+sum(q['length_mm'] for q in prefix)
                poses.append(dict(v,transition_parts_mm=[],return_parts_mm=[],flex_length_mm=length,
                    body_arrival_axis_mm=UP))
            flex=max(v['flex_length_mm'] for v in poses)
        fanouts={}
        for core,electrical in old['cores'].items():
            end=next(r for r in ends['wires'] if r['wire']==electrical['wire'])
            point=end['body_point_mm'];departure=end['body_departure_axis']
            parts=whole_fanout(join,point,departure,core,old['loom'])
            if parts is None:bad.append(dict(wire=end['wire'],cause='NO_R10_EXACT_FAN'));continue
            base_free=sum(q['length_mm'] for q in parts);free=base_free+10
            for v in poses:
                # The virtual bundle/core split is NOT a physical clamp.
                # Store the change of bundle length in this core's broad
                # arch/return. Whole core length, not the arbitrary bundle
                # subsection, must remain constant at every sampled pose.
                extra=flex-v['flex_length_mm']+10
                active=whole_fanout(join,point,departure,core,old['loom'],extra_length=extra)
                assert abs(sum(q['length_mm'] for q in active)-base_free-extra)<1e-6
                v.setdefault('fanouts',{})[end['wire']]=dict(parts=active,radius_mm=1,
                    combined_core_guide_mm=old['initial_land_mm']+v['flex_length_mm']+sum(q['length_mm'] for q in active))
            nominal=next(v for v in poses if not any(v['angles']))
            parts=nominal['fanouts'][end['wire']]['parts']
            # Whole fanout already includes9mm receiving grip.21mm remains
            # for terminal prep/trim; count the body land once, not twice.
            capacity=850-14-old['initial_land_mm']-flex-21
            if free>capacity:bad.append(dict(wire=end['wire'],cause='FACTORY_CAPACITY',shortfall_mm=free-capacity))
            fanouts[end['wire']]=dict(core=core,body_role=end['body_role'],parts=parts,radius_mm=1,
                free_fanout_mm=free-9,total_fanout_mm=free,remaining_after_project_reserves_mm=capacity-free,
                project_profile_OD_mm=2,project_free_core_R_mm=10,manufacturer_dynamic_bend_verified=False,actual_cut_mm=None,
                assumed_triangular_core_order_is_not_supplier_pinout=True)
        row=dict(old,poses=poses,body_dock_mm=join,body_join_is_not_hardware_anchor=True,
            constant_flex_budget_mm=None,maximum_bundle_section_mm=flex,body_fanout_budget_remaining_mm=850-14-old['initial_land_mm']-flex-30,
            fanouts=fanouts,body_fanout_routes_and_native_grips='RADIUS_LENGTH_ONLY; mutual/material/native/connected motion OPEN')
        result.append(row);print('Joined whole cable',old['loom'],'flex',round(flex,2),'fanouts',len(fanouts),flush=True)
    report=dict(status='REJECTED_JOINED_LEG_CAPACITY' if bad else 'JOINED_12_LOOMS_36_FANOUTS_LENGTH_ONLY',
        allocation_revision=2,topology='Whole radial breakouts and early lateral receiving departures, joined by radius-controlled arches; no V return below its incoming bundle.',
        looms=result,rejected=bad,selected=False,W5_complete=False,physical_pass=False,
        count=12,body_core_count=36,project_factory_usable_mm=850,factory_nominal_mm=900,
        complete_current_geometry_or_native_acceptance=False,
        scope='All factory cable sections planned together. Virtual outboard joins are NOT body anchors. No printed side wings. Actual12plugs/Cu/OD/900usable/R30/R10/support/service/installed travel are delivery and geometry gates.',
        planning_seconds=time.monotonic()-tick,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (lf,ef,Path(__file__),ROOT/'tools/cad/plan_current_moving_looms.py')})
    (OUT/'joined-leg-looms-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],rejected=bad,seconds=report['planning_seconds'])),flush=True)
    return report

if __name__=='__main__':plan()
