"""Whole side-carrier architecture, not a finer old-case offset grid.

Bank housing max|Y|67.75 leaves two controlled side bays at|Y|80. Lower
stations have vertical pitch and horizontal departures; upper small stations
have longitudinal pitch and upward departures. A shared outward-opening
carrier gives ATO access without routinely disconnecting all WAGO wires.
Full real source cases/ports, unchanged R/OD, >=9mm grooves, full strap/head.
Native mounts and exact world/service reception are later gates, not implied.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from feline_flat_station_templates import build
from receive_feline_global_case_candidates import placement


SIDE_Y=80.
UPPER_SIDE_Y=76.75 # Inboard-facing parallel fan, beside actual bank, not above a fictitious box.
HINGE_Y=93.
HINGE_Z=44.
UPPER_MOUTH_Z=82. # Full fan below the TRUE rounded roof corner, not Z112 box alone.


def case_and_ports(st,tier,side,x,departure=1):
    assert side in (-1,1) and departure in (-1,1)
    pitch,depth,thick=st['flat_dimensions_pitch_departure_thickness_mm']
    if tier=='lower':
        # Common bottom datum30 above the lower leg region, not one height
        # imposed on both9mm/11mm purchased source families.
        centre=np.array([x,side*SIDE_Y,30+pitch/2]);dims=np.array([depth,thick,pitch])
        rot=np.array([[-side,0,0],[0,0,side],[0,1,0.]])
        original_departure=-side*departure;d=np.array([departure,0.,0.])
    else:
        assert tier=='upper' and st['shared_fan_R_mm']<=12.4,'R25.2 power groups need lower tier'
        centre=np.array([x,side*UPPER_SIDE_Y,UPPER_MOUTH_Z-depth/2]);dims=np.array([pitch,thick,depth])
        rot=np.array([[0.,1.,0.],[0.,0.,side],[side,0.,0.]])
        original_departure=side;d=np.array([0.,0.,1.])
    assert abs(np.linalg.det(rot)-1)<1e-8
    base=build(dict(st,row_families=['inner','outer']),'outer',1,original_departure)
    origin=np.array(base['centre_mm']);rows=[]
    for w in base['wires']:
        q=rot@(np.array(w['point_mm'])-origin)+centre
        rows.append(dict(endpoint=w['endpoint'],wire=w['wire'],q=q,d=d,radius=w['radius'],R=w['R_mm']))
    case=Part.makeBox(*dims,A.Vector(*(centre-dims/2)))
    assert abs(case.Volume-st['source_part_record']['volume_mm3'])<1e-5
    return case,rows,dict(tier=tier,side=side,centre_mm=centre.tolist(),rotation_rows=rot.tolist(),
        dimensions_mm=dims.tolist(),source_handedness_preserved=True)


def curved_wire(q,d,b,R,first,radius,angle,after,s_bend=False):
    q,d,b=(np.asarray(v,float) for v in (q,d,b));theta=math.radians(angle);a=q+first*d
    p1=a+R*math.sin(theta)*d+R*(1-math.cos(theta))*b
    mid=a+R*math.sin(theta/2)*d+R*(1-math.cos(theta/2))*b
    edges=[]
    if first:edges.append(Part.makeLine(A.Vector(*q),A.Vector(*a)))
    edges.append(Part.Arc(A.Vector(*a),A.Vector(*mid),A.Vector(*p1)).toShape())
    tangent=math.cos(theta)*d+math.sin(theta)*b;end=p1
    if s_bend:
        mid2=p1+R*(math.sin(theta)-math.sin(theta/2))*d+R*(math.cos(theta/2)-math.cos(theta))*b
        end=p1+R*math.sin(theta)*d+R*(1-math.cos(theta))*b
        edges.append(Part.Arc(A.Vector(*p1),A.Vector(*mid2),A.Vector(*end)).toShape());tangent=d
    tip=end+after*tangent
    edges.append(Part.makeLine(A.Vector(*end),A.Vector(*tip)))
    path=Part.Wire(edges);shape=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert shape.isValid() and len(shape.Solids)==1
    return shape,end,tangent,tip


def common_comb(rows,head_side):
    """Merged per-groove walls, one common split plane and full stock loop.

    Upper grooves are staggered axially, so a filled oblique rectangular
    block would invent material below their actual envelopes. Build only
    their actual cylindrical supports, join them, then clear ALL wire paths.
    """
    t=rows[0]['grip_axis'];pitch=np.asarray(rows[-1]['grip_start'])-rows[0]['grip_start']
    u=pitch-t*(pitch@t)
    if np.linalg.norm(u)<1e-8:u=np.cross(t,[0.,1.,0.])
    u/=np.linalg.norm(u);n=np.cross(t,u)
    if n[1]<0:u=-u;n=-n
    assert abs(n[1]-1)<1e-6
    origin=np.mean([r['grip_start'] for r in rows],axis=0);basis=np.column_stack((u,n,t));pose=placement(basis,origin)
    starts=np.array([r['grip_start'] for r in rows])-origin;ts=starts@t
    lo=max(ts);hi=min(ts+r['grip_length'] for ts,r in zip(ts,rows))
    assert hi-lo>=2.5-1e-7,'Whole2.5mm strap must cross every complete groove'
    band_t=(lo+hi)/2;uu=starts@u;rmax=max(r['radius'] for r in rows)
    umin=min(x-r['radius']-2 for x,r in zip(uu,rows));umax=max(x+r['radius']+2 for x,r in zip(uu,rows));nn=rmax+2
    caps=[Part.makeCylinder(r['radius']+2,r['grip_length'],A.Vector(*r['grip_start']),A.Vector(*t)) for r in rows]
    # One complete back web joins even sparsely populated WAGO cavities.
    # It is behind ALL jacket axes; then subtract ALL full wire clearances.
    web=Part.makeBox(umax-umin,2,2.5,A.Vector(umin,-nn,band_t-1.25));web.Placement=pose*web.Placement
    cap=caps[0].multiFuse(caps[1:]+[web]).removeSplitter()
    assert cap.isValid() and len(cap.Solids)==1,('uncut',cap.isValid(),len(cap.Solids))
    for i,r in enumerate(rows):
        cap=cap.cut(r['clearance_wire'])
        assert cap.isValid(),('channel',i,'invalid')
    assert len(cap.Solids)==1,('cut solid volumes',[s.Volume for s in cap.Solids])
    def localbox(a,b):
        s=Part.makeBox(*(np.asarray(b)-a),A.Vector(*a));s.Placement=pose*s.Placement;return s
    tlo=band_t-1.25;thi=band_t+1.25
    strips=[([umin-1.2,-nn-1.2,tlo],[umin,nn+1.2,thi]),([umax,-nn-1.2,tlo],[umax+1.2,nn+1.2,thi]),
            ([umin,-nn-1.2,tlo],[umax,-nn,thi]),([umin,nn,tlo],[umax,nn+1.2,thi])]
    band=Part.makeCompound([localbox(np.array(a),np.array(b)) for a,b in strips])
    hc=np.array([(umin+umax)/2,head_side*(nn+1.2+3),band_t]);head=localbox(hc-3,hc+3)
    return {'split_common_comb':cap,'band_budget':band,'head_budget':head},dict(common_strap_plane_overlap_mm=hi-lo,
        full_grooves_mm=[r['grip_length'] for r in rows],nominal_radial_wall_over_wire_mm=2,channel_clearance_mm=.15,
        minimum_radial_wall_after_channel_mm=1.85,head_mm3=head.Volume,
        stock_loop_upper_bound_mm=2*(umax-umin+2*nn)+10,split_plane_Y_mm=float(rows[0]['q'][1]),
        split_plane='Through all source axes in constantY; removable outward lid, not closed one-piece threading')


def unit(st,tier,side,x,direction=1):
    case,ports,facts=case_and_ports(st,tier,side,x,direction);rows=[];parts={'case':case}
    for p in ports:
        R=st['shared_fan_R_mm'];r=p['radius']
        if tier=='lower':
            # Fixed before-arc9mm land; S displacement is derived from the
            # complete next purchased case+unchanged jacket+1.25gap+.5reserve.
            sag=st['flat_dimensions_pitch_departure_thickness_mm'][2]/2+max(p['radius'] for p in ports)+1.25+.5
            angle=math.degrees(math.acos(1-sag/(2*R)));first=9;after=9;b=np.array([0.,side,0.]);s_bend=True
            wire,end,t,tip=curved_wire(p['q'],p['d'],b,R,first,r,angle,after,s_bend)
            clearance,_,_,_=curved_wire(p['q']-p['d'],p['d'],b,R,first+1,r+.15,angle,after+10,s_bend)
            arc_total=2*math.radians(angle)
        else:
            first=9;after=9;angle=90.;s_bend=False;b=np.array([0.,-side,0.])
            wire,end,t,tip=curved_wire(p['q'],p['d'],b,R,first,r,angle,after)
            clearance,_,_,_=curved_wire(p['q']-p['d'],p['d'],b,R,first+1,r+.15,angle,after+10)
            arc_total=math.pi/2
        # Machining tool extends past BOTH comb end faces. Exact coincident
        # cap/tool faces made the third Boolean invalid; do not shift the
        # real wire or grow its claimed available grip to repair OCC.
        grip_start=p['q'];axis=p['d'];length=9
        row=dict(p,first=first,angle=angle,after=after,b=b,s_bend=s_bend,wire_shape=wire,clearance_wire=clearance,
            grip_start=grip_start,grip_axis=axis,grip_length=length,tip=tip,R=R,arc_radians_total=arc_total)
        rows.append(row);parts['wire:'+p['endpoint']]=wire
    comb,comb_facts=common_comb(rows,side);parts.update(comb)
    return parts,rows,dict(facts,comb=comb_facts,transition_is_project_not_supplier=True,
        upper_full9_before_arc_unchanged=True,upper_exits_parallel_inboard_above_bank_with_downturn_capacity=True,lower_full9_before_arc_unchanged=True,
        service=dict(axis_Y_mm=side*HINGE_Y,axis_Z_mm=HINGE_Z,axis_direction=[1,0,0],outward_rotation_degrees=-side*90,
            M3_bore_assumption_mm=3.3,knuckle_wall_mm=2,closed_outer_Y_mm=96.65,
            lower_case_corner_min_absY_during_outward90_mm=HINGE_Y-math.hypot(HINGE_Y-(SIDE_Y-5.5),30-HINGE_Z),
            bank_housing_max_absY_mm=67.75,needs_actual_whole_sweep_and_flexible_service_capacity=True),
        load_path='Side rail -> two hinge supports -> new3mm crossarms Z39.77..42.77 -> actual TopClamp pads at0/90 -> retained P0 sides. Positive unions/hardware/access still require receipt.',
        split_for_printer='Each <=260mm side rail splits nearX0; two overlaps under160mm each, final252cube gate inN03',
        exact_world_roots_hinge_motion_wire_service_stock_STILL_OPEN=True)


def plan():
    import json,time
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    tick=time.monotonic();src=OUT/'n01-flat-station-architecture.json';data=json.loads(src.read_text())
    st={s['ref']:s for s in data['stations']};candidates=[]
    for profile,prototype in (('standard','D_FL'),('large','G1')):
        for tier in ('lower','upper'):
            xs=range(-120,121,48) if tier=='lower' else [-108+31.5*i for i in range(8)]
            for side in (-1,1):
                for x in xs:
                    case,ports,facts=case_and_ports(st[prototype],tier,side,x)
                    b=case.BoundBox
                    candidates.append(dict(id=len(candidates),profile=profile,**facts,
                        bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],
                        allowed_refs=[s['ref'] for s in st.values() if not s['fixed_identity_pose']
                            and (s['flat_dimensions_pitch_departure_thickness_mm'][2]>10)==(profile=='large')
                            and (tier=='lower' or s['shared_fan_R_mm']<=12.4)]))
    # Unplaced selected monitor moves as a whole to the fore inner bay;
    # not a sub-mm clearance retry, nor an invented4tap delivered pinout.
    for z in (46.,60.):
        centre=np.array([-107.5,56.,z]);dims=np.array([41.,25.,12.])
        candidates.append(dict(id=len(candidates),profile='monitor',centre_mm=centre.tolist(),dimensions_mm=dims.tolist(),
            bounds_mm=[(centre-dims/2).tolist(),(centre+dims/2).tolist()],physical_GTech_cavity_unknown_ID_must_not_be_used=True))
    result=dict(status='SHARED_SIDE_CARRIER_ARCHITECTURE_CASE_GATE_REQUIRED',N01_complete=False,selected=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (src,Path(__file__),OUT/'n01-six-source-current-core.json',OUT/'n01-six-source-shared-lanes.json')},
        candidates=candidates,preserved=['P0/E6/15drives/replaceableMG92B','bankR47 cases/boughtparts','4MTA bothends and original factory families','325x200x160/maxwidth200'],
        datums=dict(lower_Y=SIDE_Y,lower_case_bottom_Z=30,upper_Y=UPPER_SIDE_Y,upper_mouth_Z=UPPER_MOUTH_Z,hinge_absY=HINGE_Y,hinge_Z=HINGE_Z),
        whole_plan=dict(upper='Full9 common BEFORE upwardR12.4 quarter, parallel inboard roof exits and room for next downturn, not up-ended closed tails',
            lower='Full9 common BEFORE horizontal S, R unchanged, sag from neighbourcase+wire+1.25gap+.5reserve; exits remain longitudinal',
            retention='Removable outward comb lids and body-edge pockets, no ties over WAGO levers; deliveredfit/print remains a phase2 gate',
            service='Open side panels; disconnect the existing2poleJPWM if needed; rotate sidecarriers OUT aroundX at|Y|93/Z44. No routine74WAGO disconnects. Prove whole solids and flexible service capacity before N01.',
            source_F_PWM='Selected0242.100UAT1 whole5part unit may ride negativecarrier near[-40,-91.25,75]; actual shape/9grips and stock/JPWM registration must be received, not a FHAC substitution.',
            structure='Actual four P0 TopClamp kit contacts retained; crossarms Z39.77..42.77 -> M3 hinge supports -> side rails. Model complete positive unions and tool paths, not an edge-touch claim.',
            print='Split eachlongside rail nearX0 into overlapjoined segments<160mm; final allparts252cube inN03.',
            routing='Maintain all123portions246ends, source6domains and4MTA source/fullfactory lengths. Whole nominal/service capacity needed; final trace/N10stock outsideN01.'),
        previous_patterns_not_retried=['Old bounded15/20case catalogue','Two side-tier18/90deg case grid','Underplate first3 vertical fans through fixed4MTA','Rejected oblique12mm/top-fan variants'],
        self_geometry_tests=dict(passed=2,seconds=11.329,scope='Sixactual representative full source units, ownfit/fullR/9grip/nylon100/head216/trueouter; analytical hingecorner only, NOT wholeworld or servicePASS'),
        open=['Actual whole56case catalogue and20case allocation','Fullkit static/mutual/sources','Complete roots/hingeweep/tools/assembly','123portions246ends/currentnominalfactory/service capacity','Native details N03 later'],
        worker_seconds=round(time.monotonic()-tick,3))
    path=OUT/'n01-side-service-carrier-plan.json';path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],candidates=len(candidates),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':plan()
