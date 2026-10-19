"""Keep all accepted wires; move whole right grips to their existing AFTER9.

One before/after receiving architecture, not moved purchased cases or smaller
clamps. Both sides' complete material, not just wires, need a shared test.
"""
import copy
import math
import numpy as np
import FreeCAD as A
import Part
from feline_bank_exit_lanes import under_key_candidates,under_key_materialise
from feline_remaining_kits import materialise as original_material


def candidates(groups):
    result={}
    for group,recipes in under_key_candidates(groups).items():
        if group=='Bank:W058/single/end' or recipes[0]['base_recipe']['point_mm'][1]>=0:continue
        result[group]=[dict(copy.deepcopy(r),right_receiving_grip='AFTER_EXISTING30_ARC') for r in recipes]
    assert len(result)==11
    return result


def grip_line(recipe):
    r=recipe['base_recipe'];q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis'])
    b=np.array([1. if '_IN_' in r['terminal_name'] else -1.,0.,0.]);theta=math.radians(30)
    start=q+(9+r['R_mm']*math.sin(theta))*d+r['R_mm']*(1-math.cos(theta))*b
    axis=math.cos(theta)*d+math.sin(theta)*b
    return start,axis,start+9*axis


def materialise(group,recipe):
    assert recipe['right_receiving_grip']=='AFTER_EXISTING30_ARC'
    r=recipe['base_recipe'];assert r['point_mm'][1]<0 and group!='Bank:W058/single/end'
    parts,kinds=under_key_materialise(group,recipe);q=A.Vector(*r['point_mm']);d=A.Vector(*r['departure_axis'])
    start,axis,tip=grip_line(recipe);rotation=A.Rotation(d,A.Vector(*axis));pose=A.Placement(A.Vector(*start)-rotation.multVec(q),rotation)
    for n,s in list(parts.items()):
        if kinds[n]=='proposal_wire':continue
        p=s.copy();p.Placement=pose*p.Placement;parts[n]=p
        assert p.isValid() and p.Solids
    return parts,kinds


def both_after_candidates(groups):
    return {g:[dict(copy.deepcopy(r),both_receiving_grips='AFTER_ENTRY3_TURN60',entry3_project_assumption=True,
        source_first9_unchanged=False,current_entry_straight_mm=3,full_grip_after_arc_mm=9) for r in recipes]
            for g,recipes in under_key_candidates(groups).items()}


def both_after_line(group,recipe):
    r=recipe['base_recipe'];q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis'])
    if q[1]>0 or group=='Bank:W058/single/end':b=np.array([0.,0.,-1.])
    else:b=np.array([1. if '_IN_' in r['terminal_name'] else -1.,0.,0.])
    theta=math.radians(60);start=q+(3+r['R_mm']*math.sin(theta))*d+r['R_mm']*(1-math.cos(theta))*b
    axis=math.cos(theta)*d+math.sin(theta)*b
    return start,axis,start+9*axis,b


def both_after_materialise(group,recipe):
    assert recipe['both_receiving_grips']=='AFTER_ENTRY3_TURN60'
    r=recipe['base_recipe'];parts,kinds=original_material(group,r);q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis'])
    start,axis,tip,b=both_after_line(group,recipe);R=r['R_mm'];theta=math.radians(60);a=q+3*d
    point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
    path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*start)).toShape(),Part.makeLine(A.Vector(*start),A.Vector(*tip))])
    radius=r.get('radius_mm',r.get('radius'));wire=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert wire.isValid() and len(wire.Solids)==1
    rotation=A.Rotation(A.Vector(*d),A.Vector(*axis));pose=A.Placement(A.Vector(*start)-rotation.multVec(A.Vector(*q)),rotation)
    for n,s in list(parts.items()):
        if kinds[n]=='proposal_wire':parts[n]=wire
        else:
            p=s.copy();p.Placement=pose*p.Placement;parts[n]=p
            assert p.isValid() and p.Solids
    return parts,kinds
