"""One installed whole-stock closing direction, not another PCB offset."""
import FreeCAD as A
import Part
import math


def normal_projection_proposal(outer_gap,positive_rows,minimum=3.25,quantum=.1):
    """One coupled interval, not a sequence of PCB offsets.

    Foreign measured pairs remain safe by distance's1-Lipschitz bound.
    Newly close bbox pairs and exact outer containment MUST still be received;
    the lower interval bound alone does not certify a non-planar enclosure.
    """
    assert positive_rows and all(r['ok'] for r in positive_rows.values())
    low=max(0.,minimum-outer_gap)
    high=min(r['gap_mm']-r['minimum_mm'] for r in positive_rows.values())
    if low>high:raise ValueError('No coupled interval; change the whole layout, not one scalar')
    shift=round((low+high)/2/quantum)*quantum
    if not low-1e-7<=shift<=high+1e-7:raise ValueError('No quantized whole-unit proposal')
    return dict(translation_norm_mm=shift,interval_mm=[low,high],quantum_mm=quantum,
        status='COUPLED_NORMAL_PROJECTION_ONLY_OUTER_AND_NEW_PAIRS_OPEN')


def translated_static_candidates(actors,fixed,metadata,prior,translation_norm):
    """Reuse measured gaps only when their translation bound is sufficient.

    Bbox separation proves only positive separation. An unresolved pair is
    explicitly NOT reported as a collision or as accepted geometry.
    """
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_aux_vertical_unit import material_spacing
    targets=[(n,s.BoundBox,metadata.get(n,{}),metadata.get(n,{}).get('nominal_profile_radius_mm',0) if not s.Solids else 0)
             for n,s in fixed.items() if n not in actors]
    reused={};unresolved=[];separated=0
    for n,s in actors.items():
        b=s.BoundBox
        for k,t,md,reserve in targets:
            required=material_spacing(n,metadata[n],k,md)
            if bbox_lower_bound(b,t)>=required+(reserve or 0)+1e-6:
                separated+=1;continue
            old=prior.get(n+'|'+k)
            if old and old['ok'] and old.get('gap_mm',-1)-translation_norm>=required-1e-6:
                reused[n+'|'+k]=dict(ok=True,prior_measured_gap_mm=old['gap_mm'],
                    translation_norm_mm=translation_norm,
                    certified_new_lower_bound_mm=old['gap_mm']-translation_norm,
                    minimum_mm=required,new_measurement=False)
            else:unresolved.append([n,k])
    return dict(status='TRANSLATED_STATIC_CERTIFIED' if not unresolved else 'TRANSLATED_STATIC_NEW_PAIRS_OPEN',
        actor_count=len(actors),bbox_separated_pairs=separated,reused_measured_pairs=reused,
        unresolved_pairs=unresolved,N01_complete=False,physical_pass=False)


def clock_full_tie(tie,facts):
    assert facts['type']=='T18I-PA66-BK'
    assert (facts['band_width_mm'],facts['band_thickness_mm'])==(2.5,1.2)
    assert (facts['head_length_mm'],facts['head_width_mm'],facts['head_height_mm'])==(4.8,4.5,3.5)
    b=tie.BoundBox;head_z=b.ZMax-3.5
    slab=Part.makeBox(b.XLength+2,b.YLength+2,.1,A.Vector(b.XMin-1,b.YMin-1,(b.ZMin+head_z)/2))
    section=tie.common(slab);assert section.isValid() and len(section.Solids)==2
    s=section.BoundBox
    outer=Part.makeBox(s.XLength,2.5,head_z+1.2-b.ZMin,A.Vector(s.XMin,s.YMin,b.ZMin))
    inner=Part.makeBox(s.XLength-2.4,2.7,head_z-b.ZMin-1.2,A.Vector(s.XMin+1.2,s.YMin-.1,b.ZMin+1.2))
    band=outer.cut(inner)
    head=Part.makeBox(4.8,4.5,3.5,A.Vector(b.XMin,b.YMin,head_z))
    rebuilt=band.fuse(head)
    assert rebuilt.cut(tie).Volume<1e-5 and tie.cut(rebuilt).Volume<1e-5
    pivot=A.Vector(s.Center.x,s.Center.y,0);rotation=A.Rotation(A.Vector(0,0,1),180)
    tf=A.Placement(pivot-rotation.multVec(pivot),rotation)
    rotated_band=band.copy();rotated_band.Placement=tf*rotated_band.Placement
    assert band.cut(rotated_band).Volume<1e-5 and rotated_band.cut(band).Volume<1e-5
    changed=tie.copy();changed.Placement=tf*changed.Placement
    changed_head=head.copy();changed_head.Placement=tf*changed_head.Placement
    assert changed.isValid() and len(changed.Solids)==1
    assert abs(changed.Volume-tie.Volume)<1e-6
    return changed,changed_head,dict(
        status='FULL_T18I_CLOSURE_CLOCKED_180_NOT_WORLD_ACCEPTANCE',
        unchanged_whole_band=True,unchanged_full_head_mm=[4.8,4.5,3.5],
        unchanged_volume_mm3=tie.Volume,clock_axis_old_mm=[0,0,1],
        pivot_old_mm=list(pivot),degrees=180,selected_SKU_changed=False,
        PCB_and_all14_ports_unchanged=True,N01_complete=False,physical_pass=False)
