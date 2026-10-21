"""Two finite U1 frame branches, cloned complete P0 edge-clamp family.

Planning solids only: no holes in P0, unchanged selected fastener geometry,
and source-grip roots stay at their already-received positions. Receive new
material and tools jointly; these are not finished N03 manufacture parts.
"""
import FreeCAD as A
import Part


def construct(scene, construction_cells=None):
    actors={};groups={};meta={};prints={};joints={};tools={}
    prefix='Station:Anchor:Rear:'
    # Clamps and carrying beams need not have the same X: the front beam
    # passes between complete P_SYS and FL_G, while its whole hardware stays
    # beyond P_SYS and before the battery strap. The old low-beam family is
    # rejected; this is a common upper slot46.51..46.75, not scalar retries.
    for side,x,beam_x,pillar_x,root in (
            ('Fore',32.5,26.,42.,'U1Relief:ForeRoot'),
            ('Rear',100.,133.,100.,'U1Relief:RearRoot')):
        delta=A.Vector(x-72,0,0)
        copies={}
        for part in ('TopClampPad4','LowerClampJaw4','RailClamp4Screw',
                     'RailClamp4TopWasher','RailClamp4BottomWasher','RailClamp4Nut'):
            shape=scene[prefix+part].copy();shape.translate(delta);copies[part]=shape
        seat=scene['CurrentFoundation:ClampSeat:4'].copy();seat.translate(delta)
        if side=='Fore':
            # Only the NEW3mm printed seat is relieved. Entire original
            # TopPad and selected screw/washer stack remain unchanged.
            seat=seat.common(Part.makeBox(20,20,10,A.Vector(28.,11.4,35)))
            neck0=Part.makeBox(11.5,1.9,2,A.Vector(24.,29.5,38.52))
            neck1=Part.makeBox(4,11,2,A.Vector(24.,29.5,38.52))
            neck=neck0.fuse(neck1)
            rise_y,beam_z=37.,46.6
        else:
            # Go underneath the received pair BEFORE moving east; the rise
            # is north of the entire rear motor, and the beam below G_TAIL.
            seat=seat.common(Part.makeBox(20,20,10,A.Vector(96.,10.5,35)))
            neck0=Part.makeBox(6,17.5,2,A.Vector(97.,31,38.52))
            neck1=Part.makeBox(38,6,2,A.Vector(97.,42.5,38.52))
            neck=neck0.fuse(neck1)
            rise_y,beam_z=42.5,42.
        rise_depth=3.5 if side=='Fore' else 6.
        rise=Part.makeBox(4,rise_depth,beam_z+4-40.02,A.Vector(beam_x-2,rise_y,40.02))
        beam_y=rise_y+rise_depth/2
        beam=Part.makeBox(4,95.2-beam_y,4,A.Vector(beam_x-2,beam_y,beam_z))
        cross_lo=min(beam_x,pillar_x)-2;cross_hi=max(beam_x,pillar_x)+2
        cross=Part.makeBox(cross_hi-cross_lo,4,4,A.Vector(cross_lo,91.2,beam_z))
        if side=='Fore':
            pillar=Part.makeBox(4,4,beam_z+4+14.84,A.Vector(pillar_x-2,91.2,-14.84))
            extra=[Part.makeBox(4,5.2,2,A.Vector(40,90,-14.84))]
        else:
            pillar=Part.makeBox(4,4,beam_z+4-23.74,A.Vector(pillar_x-2,91.2,23.74))
            extra=[Part.makeBox(12.25,5.5,4,A.Vector(89.75,89.7,23.74))]
        base=seat.multiFuse([neck,rise,beam,cross,pillar,*extra,copies['TopClampPad4']])
        # Exact construction union, not a bounding-box replacement. Keeping
        # these valid cells permits a conservative union-distance certificate
        # when OCC returns a false zero on the concave fused solid.
        if construction_cells is not None:
            construction_cells[side]=[seat,neck0,neck1,rise,beam,cross,pillar,
                                      *extra,copies['TopClampPad4']]
        joint=base.common(scene[root]).Volume
        whole=base.fuse(scene[root])
        assert base.isValid() and len(base.Solids)==1
        assert joint>0,(side,joint)
        assert whole.isValid() and len(whole.Solids)==1
        b=whole.BoundBox
        assert max(b.XLength,b.YLength,b.ZLength)<250
        name='U1Carrier:'+side+':Base'
        actors[name]=base;groups[name]=side;meta[name]=dict(kind='PETG')
        for part,shape in copies.items():
            if part=='TopClampPad4':continue
            name='U1Carrier:'+side+':'+part
            actors[name]=shape;groups[name]=side
            meta[name]=dict(kind='PETG' if part.startswith('Lower') else 'hardware')
        prints[root]=whole
        joints[side]=dict(named_integral_root=root,common_mm3=joint,
                          source_complete_clamp_index=4,source_X_mm=72.,X_mm=x,
                          beam_X_mm=beam_x,pillar_X_mm=pillar_x,
                          common_beam_lower_Z_slot_mm=[46.51,46.75],
                          selected_beam_lower_Z_mm=beam_z,
                          whole_GTAIL_underside_controls_rear_beam=True,
                          rear_beam_X_interval_mm=[129.85,136.225],
                          rear_beam_lower_Z_interval_mm=[41.77,42.325],
                          north_attachment_Y_mm=[91.2,95.2],
                          CAD_overlap_volume_NOT_a_strength_rating=True,
                          envelope_mm=[b.XLength,b.YLength,b.ZLength],
                          new_holes_in_P0=False,no_selected_SKU_changed=True,
                          strength_and_delivery_fit_phase2_not_physical_PASS=True)
        tools['U1Carrier:'+side+':Driver']=Part.makeCylinder(4.25,35,A.Vector(x,24.5,46.22))
    return actors,groups,meta,prints,joints,tools


def motion_certificate(world,actors,cells):
    """Exact union cells avoid an inconsistent OCC concave-distance zero.

    AABB separation proves clearance; overlap triggers an actual solid query.
    This does not replace motion by a box or qualify unsampled trajectories.
    """
    import time
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_global_case_candidates import placement
    start=time.monotonic();query=SolidQueries();rows=[];bounds=[];count=0
    assert {a['pose'] for a in world.motion}==set(range(36))
    for name,actor in actors.items():
        parts=cells[name.split(':')[1]] if name.endswith(':Base') else [actor]
        if name.endswith(':Base'):
            union=parts[0].multiFuse(parts[1:])
            assert union.isValid() and len(union.Solids)==1
            assert union.cut(actor).Volume<1e-6 and actor.cut(union).Volume<1e-6
        for index,part in enumerate(parts):
            assert part.isValid() and part.Solids
            minimum=float('inf')
            for moving in world.motion:
                count+=1
                lower=bbox_lower_bound(part.BoundBox,A.BoundBox(*moving['bounds'][0],*moving['bounds'][1]))
                minimum=min(minimum,lower)
                if lower>=1.25:continue
                local=part.copy();local.Placement=placement(moving['r'],moving['t']).inverse()*local.Placement
                gap=query.distance(local,world.rest[moving['name']])
                rows.append(dict(actor=name,cell=index,moving=moving['name'],pose=moving['pose'],
                                 gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6))
            bounds.append(dict(actor=name,cell=index,minimum_box_bound_mm=minimum))
    return dict(status='UNION_SAMPLE36_RECEIVED' if all(r['ok'] for r in rows) else 'UNION_SAMPLE36_HOLD',
                construction_union_equal=True,checked_cell_pose_pairs=count,exact_checks=rows,
                cell_bounds=bounds,actor_count=len(actors),sampled36_NOT_continuous_or_head_tail_motion=True,
                worker_seconds=round(time.monotonic()-start,3),N01_complete=False,physical_pass=False)
