"""Outer operating harness resource below upper modules, not through AUX.

The accepted XA02 middle and all selected modules stay. One removable wire
closure is planned for ATO service; temporary harness parking is a separate
assembly gate, NOT deletion of an operating collision or74WAGO disconnects.
Resource tracks are capacity, not finished individual routes or extra stock.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe


def construct(ends,profiles,parent):
    rows=[r for r in ends if r['group']=='NineWireCuffRR'];assert len(rows)==9
    targets={r['wire']:r for r in ends if r['wire'] in {r['wire'] for r in rows} and r['group']!='NineWireCuffRR'}
    assert len(targets)==9
    old=np.array([r['point_mm'] for r in rows]);off=old-old.mean(0)
    # Actual fuse rearX87.55/topZ78.55 and upper-case bottomZ93.5 govern
    # the bend lead and operating layer. Retain full9 before the bend.
    # Full old F_PWM strap top71.55 +0.2 gap +new-loop lower8.55 =80.3.
    # Allocate a separate complete closure tier, not two intersecting straps.
    points=np.array([121.,-76.,80.4])+off
    actors={};recipes={};resources={};updates={}
    for row,p in zip(rows,points):
        q=p+[-9,0,0]
        radius=profiles[row['portion_id']]['project_radius_mm']
        parts=[dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=9.)]
        n='RROuter:'+row['id'];actors[n]=pipe(parts,radius)
        rn='RROuterResource:'+row['id']
        # Transport the WHOLE9 section diagonally in one S. The actual ATO
        # tool ends atY-80.55. The previous purely vertical rise put the
        # outermost OD3.1 row atY-79.6 and obstructed that tool. Move the
        # entire section2mm INBOARD, above the actual fuse, not through it.
        # Final outer materialY-79.15 leaves1.4mm to the retained tool.
        lift=np.array([0.,2.,84.95-80.4]);height=float(np.linalg.norm(lift))
        d=np.array([-1.,0,0]);u=lift/height
        projected=off@u
        Rc=math.ceil((max(profiles[r['portion_id']]['minimum_project_R_mm'] for r in rows)
                      +max(abs(projected)))*10)/10
        theta=math.acos(1-height/(2*Rc))
        radial=float(np.dot(p-np.array([121.,-76.,80.4]),u));R1=Rc-radial;R2=Rc+radial
        at=lambda t:q+R1*(math.sin(t)*d+(1-math.cos(t))*u)
        corner=at(theta);d2=math.cos(theta)*d+math.sin(theta)*u;n2=math.sin(theta)*d-math.cos(theta)*u
        bt=lambda t:corner+R2*(math.sin(t)*d2+(1-math.cos(t))*n2)
        raised=bt(theta);last=raised.copy();last[0]=targets[row['wire']]['routing_exit_mm'][0]
        assert last[0]<raised[0]
        tracks=[dict(kind='arc',start=q.tolist(),mid=at(theta/2).tolist(),end=corner.tolist(),radius_mm=float(R1),length_mm=float(R1*theta)),
                dict(kind='arc',start=corner.tolist(),mid=bt(theta/2).tolist(),end=raised.tolist(),radius_mm=float(R2),length_mm=float(R2*theta)),
                dict(kind='line',start=raised.tolist(),end=last.tolist(),length_mm=float(raised[0]-last[0]))]
        assert min(R1,R2)>=profiles[row['portion_id']]['minimum_project_R_mm']-1e-7
        resources[rn]=pipe(tracks,radius)
        recipes[n]=dict(end_id=row['id'],wire=row['wire'],new_seam_mm=p.tolist(),new_axis=[-1,0,0],
            old_seam_mm=row['point_mm'],parts=parts,radius_mm=radius,exit_mm=q.tolist(),exit_axis=[-1,0,0],
            resource=rn,resource_parts=tracks,resource_end_mm=last.tolist(),resource_is_capacity_NOT_wire_cut=True,
            actual_target_end_id=targets[row['wire']]['id'],actual_target_exit_mm=targets[row['wire']]['routing_exit_mm'],
            common_section_translation_mm=lift.tolist(),common_bend_radius_mm=Rc,
            resource_stops_at_own_recipient_NOT_arbitrary_full_span=True,
            whole900_moving_wire_and_actual_forks_NOT_received=True)
        updates[row['id']]=dict(point_mm=p.tolist(),fixed_kinematic_seam_mm=p.tolist(),departure_axis=[-1,0,0],
            routing_exit_mm=q.tolist(),routing_exit_axis=[-1,0,0],prefix_geometry_owner=n,source_prefix_length_mm=9.,
            moving_side_interface_CHANGED=True,full_middle_route_accepted=False)
    def box(lo,hi):return Part.makeBox(*(v-u for u,v in zip(lo,hi)),A.Vector(*lo))
    floor=box([112,-83.35,73.05],[121,-68.65,75.05])
    walls=[box([112,a,73.05],[121,b,87.75]) for a,b in ((-83.35,-81.35),(-70.65,-68.65))]
    # This inboard2mm-high branch stays above the full F_PWM strap/head,
    # beside the typed OD2power row, not through nylon or the case cylinder.
    # Join on the source side AFTER the complete new strap slot. A bridge
    # through that slot would fill2.65mm3 of the full retained nylon budget.
    bridge=box([119,-71.25,71.75],[136,-68.25,74.55])
    guide=floor.multiFuse([*walls,bridge]).removeSplitter()
    parent_copy=Part.Shape();parent_copy.importBrepFromString(parent.exportBrepToString())
    joint=guide.common(parent_copy).Volume;whole=guide.fuse(parent_copy)
    assert joint>1e-5 and whole.isValid() and len(whole.Solids)==1,('Actual AUX print joint absent',joint)
    # Full2.5x1.2 loop about the actual U-guide; close UP, not outside the body.
    band=box([115.25,-84.55,71.85],[117.75,-67.45,88.95]).cut(
        box([115.,-83.35,73.05],[118.,-68.65,87.75]))
    head=box([114.,-78.65,88.95],[119.,-73.35,93.25])
    assert abs(head.Volume-5*4.3*5.3)<1e-6
    actors.update({'RROuterGuide':guide,'RROuterBand':band,'RROuterHead':head})
    assert all(s.isValid() and len(s.Solids)==1 for s in (*actors.values(),*resources.values()))
    return actors,resources,dict(recipes=recipes,updates=updates,parent='AuxGrip:CommonRoot',parent_joint_mm3=joint,
        first9_straight_full=True,all_accepted_AUX_XA02_and_POWER_and_cases_unchanged=True,
        independent_WAGO_end_grips_unchanged=True,
        service_sequence=['power disconnected inphase2','remove side panel','release shared loom closure and park flexible loom',
                          'withdraw ATO without disconnecting WAGO','replace closure and panel'],
        service_parking_constant_lengths_and_forks_still_OPEN=True,
        routing_resource_NOT169mm_cut_of_each_core=True,N01_complete=False,physical_pass=False,
        moving900_N02_N05_actualforks_N04_and_native_N03_OPEN=True)


def package(world,actors,resources,plan,parent,scene,ends,profiles,receipt,pins,retired):
    """Receive the source and shared resource, not the unfinished nine forks."""
    import time,hashlib,zipfile,json
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();all_shapes={**actors,**resources}
    assert len(all_shapes)==21 and not receipt['failures']
    checks=dict(receipt['checks'])
    for name,s in all_shapes.items():
        if name=='RROuterGuide':continue
        gap=s.distToShape(parent)[0]
        checks[name+'|'+plan['parent']]=dict(gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
    assert all(r['ok'] for r in checks.values())
    core=json.loads((OUT/'n01-shared-Pi-carrier-r3-core-received.json').read_text())
    outerfile=ROOT/core['recipe']['outer_file'];selected_outer=Part.Shape();selected_outer.read(str(outerfile))
    assert abs(selected_outer.Volume-world.outer.Volume)<1e-5,'Wrong historical torso envelope'
    outside={n:outer_margin(s,selected_outer) for n,s in all_shapes.items()}
    assert all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in all_shapes.values())-max(r['bounds'][1][2] for r in world.motion)
    assert zbound>1.25 and {r['pose'] for r in world.motion}==set(range(36))
    names=['RROuterGuide',plan['parent'],'PowerMount:F_PWM:PETG','PowerGripRoot:XP02','PowerFan:grip:XP02:pad']
    def clone(s):
        c=Part.Shape();c.importBrepFromString(s.exportBrepToString());return c
    printed={n:clone(all_shapes[n] if n in all_shapes else scene[n]) for n in names}
    joints=[]
    for a,b in zip(names,names[1:]):
        v=clone(printed[a]).common(clone(printed[b])).Volume
        assert v>1e-5;joints.append(dict(a=a,b=b,common_mm3=v))
    whole=clone(printed[names[0]]).multiFuse([clone(printed[n]) for n in names[1:]])
    assert whole.isValid() and len(whole.Solids)==1
    envelope=[whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength];assert max(envelope)<250
    path=OUT/'n01-RR9-service-spine-rooted-space.json';archive=path.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,s in {**all_shapes,**{'Input:'+n:s for n,s in printed.items() if n!='RROuterGuide'},'Input:outer':selected_outer}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    wires={r['wire'] for r in plan['recipes'].values()}
    rows=[r for r in ends if r['wire'] in wires];assert len(rows)==18
    specs={r['portion_id']:{k:profiles[r['portion_id']][k] for k in ('project_radius_mm','minimum_project_R_mm')} for r in rows}
    result=dict(status='RR9_SOURCE_AND_SHARED_RESOURCE_STATIC_SAMPLE36_RECEIVED_FORKS_MOVING900_OPEN',
        N01_complete=False,physical_pass=False,native_changed=False,whole123_NOT_received=True,
        plan=plan,constructor_rows=rows,constructor_profiles=specs,retired=retired,checks=checks,outer=outside,
        positive_shared_print_graph=joints,shared_print_solids=1,shared_print_envelope_mm=envelope,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,
        full_moving_wire_and_head_tail_motion_NOT_received=True,
        resources_are_capacity_not_finished_wire_cuts=True,all_retained_ATO_tools_in_static_receiver=True,
        final_target_forks_and_whole_assembly_service_NOT_received=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**pins,outerfile.relative_to(ROOT).as_posix():sha(outerfile),
                       Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(path,result);return result
