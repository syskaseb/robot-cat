"""One FL9/HP3/FHY allocation: open curved common guide, not9 rigid bores.

Full first9 sits ON the source arc. The source is a new PROJECT boundary;
actual servo contacts and selected factory conductors do not move. N02/N05
must still qualify the moving900mm approach to this proposed fixed seam.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe
from receive_feline_global_case_candidates import placement


def construct(ends,profiles,parent):
    rows=[r for r in ends if r['group']=='NineWireCuffFL'];assert len(rows)==9
    centre=np.array([-68.,43.,86.]);old=np.array([r['point_mm'] for r in rows])
    # Preserve each identity and the3x3 section. Only this project boundary moves.
    offsets=old-old.mean(0);points=centre+offsets
    d=np.array([1.,0,0]);up=np.array([0.,0,1]);Rc=16.;theta=math.pi/3
    actors={};recipes={};updates={}
    for row,p,o in zip(rows,points,offsets):
        radius=profiles[row['portion_id']]['project_radius_mm'];R=Rc-o[2]
        at=lambda t:p+R*(math.sin(t)*d+(1-math.cos(t))*up)
        q=at(theta);d2=math.cos(theta)*d+math.sin(theta)*up
        n2=math.sin(theta)*d-math.cos(theta)*up;R2=Rc+o[2]
        bt=lambda t:q+R2*(math.sin(t)*d2+(1-math.cos(t))*n2)
        end=bt(theta);tip=end+10*d
        parts=[dict(kind='arc',start=p.tolist(),mid=at(theta/2).tolist(),end=q.tolist(),radius_mm=float(R),length_mm=float(R*theta)),
               dict(kind='arc',start=q.tolist(),mid=bt(theta/2).tolist(),end=end.tolist(),radius_mm=float(R2),length_mm=float(R2*theta)),
               dict(kind='line',start=end.tolist(),end=tip.tolist(),length_mm=10.)]
        assert min(R,R2)>=profiles[row['portion_id']]['minimum_project_R_mm']-1e-7
        assert R*theta>=9 and abs(end[2]-(p[2]+16))<1e-6
        name='FLArcCuff:'+row['id'];actors[name]=pipe(parts,radius)
        recipes[name]=dict(end_id=row['id'],wire=row['wire'],parts=parts,radius_mm=radius,
            new_seam_mm=p.tolist(),new_axis=d.tolist(),old_seam_mm=row['point_mm'],
            first9_arclength_mm=[0,9],not_straight_chord=True,exit_mm=tip.tolist(),exit_axis=d.tolist(),
            actual_motor_contacts_unchanged=True,moving900_N02_N05_NOT_received=True)
        updates[row['id']]=dict(point_mm=p.tolist(),fixed_kinematic_seam_mm=p.tolist(),departure_axis=d.tolist(),
            routing_exit_mm=tip.tolist(),routing_exit_axis=d.tolist(),prefix_geometry_owner=name,
            source_prefix_length_mm=(R+R2)*theta+10,full_grip_arclength_mm=[0,9],
            moving_side_interface_CHANGED=True,full_middle_route_accepted=False)
    x,y,z=centre;zc=z+Rc
    def point(r,t,Y):return A.Vector(x+r*math.sin(t),Y,zc-r*math.cos(t))
    def sector(r0,r1,angle,Y):
        edges=[Part.Arc(point(r1,0,Y),point(r1,angle/2,Y),point(r1,angle,Y)).toShape(),
               Part.makeLine(point(r1,angle,Y),point(r0,angle,Y)),
               Part.Arc(point(r0,angle,Y),point(r0,angle/2,Y),point(r0,0,Y)).toShape(),
               Part.makeLine(point(r0,0,Y),point(r1,0,Y))]
        return Part.Face(Part.Wire(edges))
    # The end follows at least10.5mm arclength at EVERY retained wire row.
    # Extending ALL rows to the inner row's angle needlessly occupied HP3.
    radii=[23.85,21.35,19.6,18.05,17.55,16.,14.45,13.95,12.4,10.65,8.15]
    angle=lambda r:10.5/min(19.6,max(12.4,r));Y=35.15
    edges=[Part.Arc(point(radii[0],0,Y),point(radii[0],angle(radii[0])/2,Y),point(radii[0],angle(radii[0]),Y)).toShape()]
    edges += [Part.makeLine(point(a,angle(a),Y),point(b,angle(b),Y)) for a,b in zip(radii,radii[1:])]
    edges += [Part.Arc(point(radii[-1],angle(radii[-1]),Y),point(radii[-1],angle(radii[-1])/2,Y),point(radii[-1],0,Y)).toShape(),
              Part.makeLine(point(radii[-1],0,Y),point(radii[0],0,Y))]
    floor=Part.Face(Part.Wire(edges)).extrude(A.Vector(0,2.5,0))
    walls=[sector(a,b,angle((a+b)/2),37.4).extrude(A.Vector(0,10.4,0))
           for a,b in ((8.15,10.65),(21.35,23.85))]
    guide=floor.multiFuse(walls)
    station=.24;t=np.array([math.cos(station),0,math.sin(station)]);u=np.array([-math.sin(station),0,math.cos(station)])
    origin=centre+Rc*(math.sin(station)*d+(1-math.cos(station))*up)
    tf=placement(np.column_stack((t,[0,1,0],u)),origin)
    def box(lo,hi,local=False):
        s=Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
        if local:s.Placement=tf*s.Placement
        return s
    band=box([-1.25,-9.05,-9.05],[1.25,6.,9.05],True).cut(
        box([-1.5,-7.85,-7.85],[1.5,4.8,7.85],True))
    head=box([-2.5,-13.35,-2.65],[2.5,-9.05,2.65],True)
    assert abs(head.Volume-5*4.3*5.3)<1e-6
    # One complete stock loop; shallow full-loop channel, not a clipped head.
    clearance=band.makeOffsetShape(.2,1e-5,join=2)
    bridge=box([-68,36.15,77.65],[-64,53.65,80.15])
    riser=box([-68,51.65,77.65],[-64,53.65,85.8])
    guide=guide.multiFuse([bridge,riser]).cut(clearance).removeSplitter()
    parent_copy=Part.Shape();parent_copy.importBrepFromString(parent.exportBrepToString())
    common=guide.common(parent_copy).Volume;whole=guide.fuse(parent_copy)
    assert common>1e-5 and whole.isValid() and len(whole.Solids)==1
    assert guide.isValid() and len(guide.Solids)==1 and guide.common(band).Volume<1e-5
    actors.update({'FLArcGuide':guide,'FLArcBand':band,'FLArcHead':head})
    assert all(s.isValid() and len(s.Solids)==1 for s in actors.values())
    return actors,dict(recipes=recipes,updates=updates,parent='ForeFHAC:common_body_saddle',
        parent_joint_mm3=common,full9_curved_support=True,step_end_arclength_mm=10.5,
        nominal_wall_mm=2.5,whole_loop_clearance_mm=.2,N01_complete=False,physical_pass=False,
        moving900_approaches_roots_native_N03_and_N02_N05_NOT_qualified=True)


def continue_inner_gallery(actors,plan):
    """Whole9 turn after the actual HP end, before the FR_P comb.

    The first proposal's arbitrary10mm+X extension ended1.2453mm from that
    comb. Do not shave a margin or offset one core. Allocate the full bundle
    a common inward turn, referenced to HP's actualX-35 end instead.
    """
    import copy
    actors=dict(actors);plan=copy.deepcopy(plan)
    rows=plan['recipes'];centre=np.mean([r['parts'][1]['end'] for r in rows.values()],axis=0)
    for name,row in rows.items():
        parts=row['parts'][:2];p=np.array(parts[-1]['end']);q=p.copy();q[0]=-35.+.2
        assert q[0]>p[0]
        R=16.+float(p[1]-centre[1]);d=np.array([1.,0,0]);n=np.array([0.,-1,0])
        at=lambda t:q+R*(math.sin(t)*d+(1-math.cos(t))*n)
        end=at(math.pi/2)
        parts += [dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=float(q[0]-p[0])),
                  dict(kind='arc',start=q.tolist(),mid=at(math.pi/4).tolist(),end=end.tolist(),
                       radius_mm=R,length_mm=float(R*math.pi/2))]
        actors[name]=pipe(parts,row['radius_mm']);row.update(parts=parts,exit_mm=end.tolist(),exit_axis=n.tolist(),
            whole9_common_inboard_turn_after_HP_end=True)
        u=plan['updates'][row['end_id']];u.update(routing_exit_mm=end.tolist(),routing_exit_axis=n.tolist(),
            source_prefix_length_mm=sum(e['length_mm'] for e in parts))
    plan.update(whole_bundle_inboard_gallery=True,arbitrary10mm_extension_removed_not_extra_grip=True)
    return actors,plan


def power_band_above_feeder(actors,plan):
    """Allocate ALL3 OD2power cores above the actual W037 feeder.

    The arbitrary3.6mm grid for these smaller cores obstructed the crossing.
    Keep original source curvatures/first9 support, then transport to a2.2mm
    pitch band. Six OD3.1 data/ground rows do not move. No margin reduction.
    """
    import copy
    actors=dict(actors);plan=copy.deepcopy(plan)
    power=sorted(((n,r) for n,r in plan['recipes'].items() if abs(r['radius_mm']-1)<1e-7),
                 key=lambda nr:nr[1]['new_seam_mm'][2])
    assert len(power)==3
    for index,(name,row) in enumerate(power):
        p=np.array(row['new_seam_mm']);R=row['parts'][0]['radius_mm'];R2=row['parts'][1]['radius_mm']
        target=100.1+.2+row['radius_mm']+index*(2*row['radius_mm']+.2)
        theta=math.acos(1-(target-p[2])/(R+R2));d=np.array([1.,0,0]);u=np.array([0.,0,1])
        at=lambda t:p+R*(math.sin(t)*d+(1-math.cos(t))*u)
        q=at(theta);d2=math.cos(theta)*d+math.sin(theta)*u;n2=math.sin(theta)*d-math.cos(theta)*u
        bt=lambda t:q+R2*(math.sin(t)*d2+(1-math.cos(t))*n2)
        end=bt(theta);assert abs(end[2]-target)<1e-6 and R*theta>=10.5
        parts=[dict(kind='arc',start=p.tolist(),mid=at(theta/2).tolist(),end=q.tolist(),radius_mm=R,length_mm=float(R*theta)),
               dict(kind='arc',start=q.tolist(),mid=bt(theta/2).tolist(),end=end.tolist(),radius_mm=R2,length_mm=float(R2*theta))]
        actors[name]=pipe(parts,row['radius_mm']);row.update(parts=parts,exit_mm=end.tolist(),exit_axis=d.tolist(),
             power3_pitch_mm=2.2,actual_W037_top_mm=100.1,whole_power3_band_not_one_core_offset=True)
    return actors,plan


def package(world,actors,plan,parent,ends,profiles,base_static,gallery_static,power_static,pins,retired):
    """Compose selected evidence; keep all changed moving-wire gates open."""
    import time,hashlib,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();wire_names=set(plan['recipes'])
    power={n for n,r in plan['recipes'].items() if r['radius_mm']==1.}
    six=wire_names-power;checks={}
    assert len(wire_names)==9 and len(power)==3 and not power_static['failures']
    for packet,chosen in ((base_static,set(actors)-wire_names),(gallery_static,six),(power_static,power)):
        for key,row in packet['checks'].items():
            a,b=key.split('|')
            if a not in chosen:continue
            # All changed wires are received by the final3power receiver,
            # not inherited from earlier variants of those same identities.
            if b in power and packet is not power_static:continue
            checks[key]=row
    assert checks and all(r['ok'] for r in checks.values())
    # The retained printed parent was excluded ONLY as a positive print joint.
    # Actual wire and full nylon clearance to it is still received explicitly.
    for n,s in actors.items():
        if n=='FLArcGuide':continue
        gap=s.distToShape(parent)[0];checks[n+'|'+plan['parent']]=dict(gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
    assert all(r['ok'] for r in checks.values())
    outside={n:outer_margin(s,world.outer) for n,s in actors.items()};assert all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in actors.values())-max(r['bounds'][1][2] for r in world.motion)
    assert zbound>1.25 and {r['pose'] for r in world.motion}==set(range(36))
    p=Part.Shape();p.importBrepFromString(parent.exportBrepToString());g=Part.Shape();g.importBrepFromString(actors['FLArcGuide'].exportBrepToString())
    joint=g.common(p).Volume;whole=g.fuse(p);assert joint>0 and whole.isValid() and len(whole.Solids)==1
    envelope=[whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength];assert max(envelope)<250
    path=OUT/'n01-FL9-common-arc-rooted-space.json';archive=path.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,shape in {**actors,'Input:parent':parent}.items():
            raw=shape.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    src=[{k:r[k] for k in ('id','wire','portion_id','group','point_mm')} for r in ends if r['group']=='NineWireCuffFL']
    specs={r['portion_id']:{k:profiles[r['portion_id']][k] for k in ('project_radius_mm','minimum_project_R_mm')} for r in src}
    result=dict(status='FL9_COMMON_ARC_ROOTED_SPACE_STATIC_SAMPLE36_RECEIVED_MOVING900_OPEN',
        N01_complete=False,physical_pass=False,native_changed=False,whole123_NOT_received=True,
        plan=plan,constructor_rows=src,constructor_profiles=specs,retired=retired,checks=checks,outer=outside,
        parent_joint_mm3=joint,shared_print_solids=1,shared_print_envelope_mm=envelope,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,
        full_moving_wire_and_head_tail_motion_NOT_received=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        changed_power3_band_uses_actual_OD2_pitch2p2_above_W037=True,
        first9_curvatures_and_print_parent_unchanged_by_power_band=True,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(path,result);return result
