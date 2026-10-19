"""Whole existing station geometry at a newly allocated functional row.

Keeps purchased cases/occupied mouths,9mm lands, radii, full band/head.
Old back-return/low-rail branches are NOT automatically translated as an
approved load path. A joint carrier receipt remains mandatory for N01.
"""
import itertools
import numpy as np
from feline_flat_station_templates import build,compact


def zone_build(station,slot,departure,bend_mode='OUTWARD_CONCENTRIC'):
    wanted=np.array(slot['centre_mm'],float)
    if station['fixed_identity_pose']:
        assert slot['profile']=='fixed_P_SYS'
        model=build(station,'inner',1,-1)
        assert np.allclose(wanted,model['centre_mm'])
        return model
    assert slot['profile']==('large' if station['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard')
    side=-1 if wanted[1]<0 else 1
    family='outer' if abs(wanted[1])>45 else 'inner'
    source=dict(station,row_families=['inner','outer'])
    model=build(source,family,side,departure,wanted[0],None,bend_mode,'SIDE')
    delta=wanted-np.array(model['centre_mm'])
    for key in ('points','bounds'):model[key]=model[key]+delta
    for box in model['boxes']:box['bounds']=box['bounds']+delta
    for wire in model['wires']+model['reused_jacket_lands']:
        wire['points']=wire['points']+delta
        for key in ('point_mm','before_arc_grip_line_mm','after_arc_end_mm'):
            if key in wire:wire[key]=(np.array(wire[key])+delta).tolist()
    model.update(centre_mm=wanted.tolist(),expanded_zone=dict(slot),
        row_family_changed_from_obsolete_catalogue=True,
        legacy_translated_return_NOT_an_approved_carrier=True,
        frame_family='SHARED_NEW_ZONE_CARRIER_STILL_REQUIRED')
    case=next(b for b in model['boxes'] if b['kind']==0)
    assert np.allclose(case['bounds'],slot['bounds_mm'])
    return model


def restore_zone(station,recipe):
    return zone_build(station,recipe['expanded_zone'],recipe['departure_X'],recipe.get('bend_mode','OUTWARD_CONCENTRIC'))


def vertical_build(station,slot,departure_z,lever_sign,head_side):
    """A proper rigid rotation of the WHOLE source and its complete fan."""
    assert not station['fixed_identity_pose'] and departure_z in (-1,1) and lever_sign in (-1,1) and head_side in (-1,1)
    assert slot['pose_family']=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS'
    source=dict(station,row_families=['inner','outer'])
    model=build(source,'outer',head_side,departure_z*lever_sign,0.,None,'OUTWARD_CONCENTRIC','SIDE')
    old=np.array(model['centre_mm']);wanted=np.array(slot['centre_mm'])
    rotation=np.array([[0.,1.,0.],[0.,0.,lever_sign],[lever_sign,0.,0.]])
    assert abs(np.linalg.det(rotation)-1)<1e-8
    point=lambda p:(np.asarray(p)-old)@rotation.T+wanted
    for key in ('points',):model[key]=point(model[key])
    for box in model['boxes']:
        corners=point(list(itertools.product(*zip(*box['bounds']))))
        box['bounds']=np.array([corners.min(0),corners.max(0)])
    for wire in model['wires']+model['reused_jacket_lands']:
        wire['points']=point(wire['points'])
        for key in ('point_mm','before_arc_grip_line_mm','after_arc_end_mm'):
            if key in wire:wire[key]=point(wire[key]).tolist()
        for key in ('departure_axis','bend_unit'):
            if key in wire:wire[key]=(rotation@wire[key]).tolist()
    p=model['points'];rr=model['radii'];model['bounds']=np.array([(p-rr[:,None]).min(0),(p+rr[:,None]).max(0)])
    model.update(centre_mm=wanted.tolist(),expanded_zone=dict(slot),vertical_departure_Z=departure_z,
        vertical_lever_Y=lever_sign,vertical_head_side=head_side,source_case_rotation_rows=rotation.tolist(),
        pose_family=slot['pose_family'],source_lever_UP_preserved_from_actual_handedness=False,
        actual_source_handedness_preserved_by_proper_rotation=True,
        lever_access_lateral_requires_shared_assembly_proof=True,
        legacy_translated_return_NOT_an_approved_carrier=True,
        frame_family='SHARED_VERTICAL_SIDE_TIER_CARRIER_STILL_REQUIRED')
    case=next(b for b in model['boxes'] if b['kind']==0)
    assert np.allclose(case['bounds'],slot['bounds_mm'])
    return model
