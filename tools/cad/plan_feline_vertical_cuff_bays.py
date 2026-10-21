"""Shared vertical cuff bays; project seams are not purchased connectors.

Move the complete3x3 seam/tangent and its9mm guide together. Actual motor
contacts, selected900mm conductors, R47 and electrical end grips do not move.
N02/N05 moving portions and the new printed load paths remain explicit gates.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe


def construct(ends,profiles,retained_RL,retained_RL_plan):
    actors=dict(retained_RL);recipes=dict(retained_RL_plan);updates={};guides={}
    assert len(actors)==len(recipes)==9
    # FL follows actual L1 front face-1.25clearance-7.35guide halfwidth.
    # RR lies in the shared space between the full F_PWM band and trunk comb.
    centres={'FL':[-54.5-1.25-7.35,40.,74.], 'FR':[-61.,-30.,74.],
             'RR':[117.5,(-64.34870023401956-48.3214)/2,74.]}
    for leg,centre in centres.items():
        rows=[r for r in ends if r['group']=='NineWireCuff'+leg];assert len(rows)==9
        old=np.array([r['point_mm'] for r in rows]);offset=old-old.mean(0)
        # Old plane YZ -> current XY. No bare pad or supplier contact transform.
        points=np.array(centre)+np.column_stack((offset[:,2],offset[:,1],np.zeros(9)))
        direction=np.array([0.,0,1]);normal=np.array([1.,0,0])*(1 if leg!='RR' else -1)
        Rc=max(profiles[r['portion_id']]['minimum_project_R_mm']+float(o@normal)
               for r,o in zip(rows,points-np.array(centre)))
        for row,p in zip(rows,points):
            spec=profiles[row['portion_id']];radius=spec['project_radius_mm']
            q=p+9*direction;R=Rc-float((p-np.array(centre))@normal)
            at=lambda t:q+R*(math.sin(t)*direction+(1-math.cos(t))*normal)
            turn=at(math.pi/2);tip=turn+10*normal
            parts=[dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=9.),
                   dict(kind='arc',start=q.tolist(),mid=at(math.pi/4).tolist(),end=turn.tolist(),
                        radius_mm=R,length_mm=R*math.pi/2),
                   dict(kind='line',start=turn.tolist(),end=tip.tolist(),length_mm=10.)]
            name='VerticalCuff:'+row['id'];actors[name]=pipe(parts,radius)
            recipes[name]=dict(end_id=row['id'],wire=row['wire'],leg=leg,parts=parts,radius_mm=radius,
                old_seam_mm=row['point_mm'],old_axis=row['departure_axis'],new_seam_mm=p.tolist(),
                new_axis=direction.tolist(),exit_mm=tip.tolist(),exit_axis=normal.tolist(),
                first9_straight_capacity_mm=9.,guide_owner='VerticalGuide:'+leg,
                actual_motor_contacts_and_electrical_grips_unchanged=True,
                whole900mm_moving_wire_NOT_qualified=True,new_root_NOT_received=True,
                N01_complete=False,physical_pass=False)
            updates[row['id']]=dict(point_mm=p.tolist(),departure_axis=direction.tolist(),
                fixed_kinematic_seam_mm=p.tolist(),routing_exit_mm=tip.tolist(),routing_exit_axis=normal.tolist(),
                prefix_geometry_owner=name,source_prefix_length_mm=9.+R*math.pi/2+10,
                previous_fixed_kinematic_seam_mm=row['point_mm'],moving_side_interface_CHANGED=True,
                pose_status='PROPOSED_VERTICAL_PROJECT_SEAM_NOT_RECEIVED',
                full_middle_route_accepted=False,full_flexible_kinematics_NOT_qualified=True)
        x,y,z=centre
        box=lambda lo,hi:Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
        floor=box([x-7.35,y-7.35,z],[x+7.35,y-5.35,z+9])
        walls=[box([x+a,y-5.35,z],[x+b,y+7.35,z+9]) for a,b in [(-7.35,-5.35),(5.35,7.35)]]
        guides['VerticalGuide:'+leg]=floor.multiFuse(walls)
        band=box([x-8.55,y-8.55,z+3.25],[x+8.55,y+8.55,z+5.75]).cut(
            box([x-7.35,y-7.35,z+3],[x+7.35,y+7.35,z+6]))
        head=box([x-12.85,y-2.65,z+2],[x-8.55,y+2.65,z+7])
        assert abs(head.Volume-5*4.3*5.3)<1e-6
        guides['VerticalBand:'+leg]=band;guides['VerticalHead:'+leg]=head
    assert len(actors)==36 and len(updates)==27 and len(guides)==9
    assert all(s.isValid() and len(s.Solids)==1 for s in (*actors.values(),*guides.values()))
    return actors,recipes,guides,updates


def root_front_right(guide,parent):
    """One full2mm bridge into the existing grounded printed connector.

    Inputs are isolated by BRep roundtrip: OCC must not mutate source packets.
    The original incidental0.35mm overlap alone is NOT a load-path witness.
    """
    def isolated(s):
        out=Part.Shape();out.importBrepFromString(s.exportBrepToString());return out
    guide=isolated(guide);parent=isolated(parent);g=guide.BoundBox;b=parent.BoundBox
    lo=[g.XMin,g.YMax-2,b.ZMin-.8];hi=[g.XMin+2,b.YMin+4,b.ZMin+2.2]
    bridge=Part.makeBox(*(v-u for u,v in zip(lo,hi)),A.Vector(*lo))
    joined=guide.fuse(bridge).removeSplitter()
    pg=isolated(bridge).common(isolated(guide));pp=isolated(bridge).common(isolated(parent))
    assert pg.Volume>=8-1e-5 and pp.Volume>=8-1e-5
    whole=isolated(joined).fuse(isolated(parent))
    assert joined.isValid() and len(joined.Solids)==1 and whole.isValid() and len(whole.Solids)==1
    return joined,dict(parent='StructureReserve:ForeNegativeBankConnection',
        guide_bridge_common_mm3=pg.Volume,parent_bridge_common_mm3=pp.Volume,
        bridge_bounds_mm=[lo,hi],same_shared_print_positive_joint=True,
        full2mm_cross_section_not_incidental_corner=True,physical_strength_NOT_verified=True,
        whole_new_moving900mm_and_N01_NOT_qualified=True)


def package_front_right(world,scene,wire9,recipes,guides,rooted,joint,raw,root_raw,retired,source_pins):
    """Receive the complete FR unit, not the rejected whole vertical proposal."""
    import hashlib,json,time,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from plan_feline_usb_service_bight import outer_margin
    from feline_solid_distance import bbox_lower_bound
    from feline_atomic_save import save_json
    tick=time.monotonic();parent=scene[joint['parent']]
    selected={**wire9,'VerticalGuide:FR':rooted,
              **{n:guides[n] for n in ('VerticalBand:FR','VerticalHead:FR')}}
    assert len(selected)==12
    # The band's INNER face intentionally bears on the printed guide; it
    # is a named zero-volume contact, not a foreign0.2mm clearance failure.
    band=guides['VerticalBand:FR'];a=Part.Shape();b=Part.Shape()
    a.importBrepFromString(rooted.exportBrepToString());b.importBrepFromString(band.exportBrepToString())
    face=dict(gap_mm=a.distToShape(b)[0],common_mm3=a.common(b).Volume,
              minimum_mm=0.,intended_print_strap_bearing_face=True)
    face['ok']=face['gap_mm']<=1e-6 and face['common_mm3']<1e-5;assert face['ok']
    checks={k:v for k,v in raw['checks'].items() if k.split('|')[0] in selected
            and 'VerticalGuide:FR' not in k.split('|')}
    checks.update(root_raw['checks']);checks['VerticalGuide:FR|VerticalBand:FR']=face
    assert all(r['ok'] for r in checks.values())
    # Restore ALL unchanged old FL/RL/RR cuff parts omitted by the rejected
    # whole-cuff proposal. Positive bbox distance is a valid separation bound.
    restored=[n for n in scene if n in raw['recipe']['retired'] and n not in retired]
    lower=min(bbox_lower_bound(s.BoundBox,scene[n].BoundBox) for s in selected.values() for n in restored)
    assert lower>=1.25
    outside={n:outer_margin(s,world.outer) for n,s in selected.items()}
    assert all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in selected.values())-max(r['bounds'][1][2] for r in world.motion)
    assert zbound>=1.25 and {r['pose'] for r in world.motion}==set(range(36))
    whole=Part.Shape();whole.importBrepFromString(rooted.exportBrepToString())
    p=Part.Shape();p.importBrepFromString(parent.exportBrepToString());whole=whole.fuse(p)
    assert whole.isValid() and len(whole.Solids)==1
    dest=OUT/'n01-FR-vertical9-rooted-space.json';archive=dest.with_suffix('.breps.zip');geometry=[]
    inputs={'Input:unrooted_guide':guides['VerticalGuide:FR'],'Input:parent':parent}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**selected,**inputs}.items():
            entry=str(len(geometry))+'.brep';data=s.exportBrepToString().encode();z.writestr(entry,data)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(data).hexdigest(),input=n in inputs))
    result=dict(status='FR_VERTICAL9_ROOTED_SPACE_STATIC_SAMPLE36_RECEIVED_MOVING900_OPEN',
        N01_complete=False,physical_pass=False,native_changed=False,whole123_NOT_received=True,
        actual_motor_contacts_and_selected900mm_unchanged=True,moving_boundary_CHANGED=True,
        retired=retired,
        source_recipes={n:recipes[n] for n in wire9},joint=joint,checks=checks,outer=outside,
        unchanged_other_cuffs_restored=len(restored),restored_bbox_separation_lower_bound_mm=lower,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,
        full_moving_wire_and_head_tail_motion_NOT_received=True,
        rooted_shared_print_solids=1,rooted_shared_print_envelope_mm=[whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength],
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**source_pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        raw_rejected_whole_static_provenance=dict(file='n01-vertical-cuff-bays-static.json',sha256=sha(OUT/'n01-vertical-cuff-bays-static.json'),
             failures_outside_selected_FR_NOT_promoted=True),
        unchanged_FR_wire_and_nylon_pairs_reused=True,new_guide_root_pairs_received=True,
        worker_seconds=round(time.monotonic()-tick,3))
    assert max(result['rooted_shared_print_envelope_mm'])<250
    save_json(dest,result);return selected,result
