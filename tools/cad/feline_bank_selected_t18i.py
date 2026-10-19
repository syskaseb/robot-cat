"""Full selected T18I maximum drawing envelope in the ACTUAL strap frame.

No change to source mouths, jackets, radii, PETG caps or nominal full bands.
Anchor the head at the old strap's outer face; never shrink it about a
floating centre. Every new head is proved a subset of the old6cube budget.
"""
import copy
import math
from functools import lru_cache
import numpy as np
import FreeCAD as A
import Part
from feline_bank_receiving_grips import both_after_candidates,both_after_line
from feline_bank_zoned_layout import candidates as zoned_candidates,materialise as zoned_materialise,profile
from feline_t18i_selected_head import source
from feline_remaining_kits import materialise as original_material


@lru_cache(maxsize=1)
def dimensions():
    doc=source();d=doc['all_linked_drawings_conservative_upper_mm']
    return d['D_radial'],d['H_tangent'],d['E_along_wire']


def candidates(groups):
    rows=both_after_candidates(groups);rows.update(zoned_candidates(groups))
    result={g:[dict(copy.deepcopy(r),selected_T18I_max_head=True) for r in rr] for g,rr in rows.items()}
    for group,rr in both_after_candidates(groups).items():
        selected=[dict(copy.deepcopy(r),selected_T18I_max_head=True,joint_current_bank_plane=True) for r in rr]
        result[group]=selected+result[group]
    return result


def current_profile(group,recipe):
    r=recipe['base_recipe'];q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis'])
    fore={'Bank:W027/single/end','Bank:W028/single/end','Bank:W020/body/end'}
    returning=q[1]<0 or group in fore
    b=np.array([0.,0.,-1. if returning else 1.]);entry=0. if returning else 3.;degrees=180. if returning else 45.
    theta=math.radians(degrees);start=q+(entry+r['R_mm']*math.sin(theta))*d+r['R_mm']*(1-math.cos(theta))*b
    axis=math.cos(theta)*d+math.sin(theta)*b
    return dict(start=start,axis=axis,tip=start+9*axis,bend=b,entry=entry,degrees=degrees,
        role='OUTBOARD_RETURN_BELOW_BANK' if returning else 'UPPER_LEFT_ABOVE_PSYS_DFL')


def current_receiving(group,recipe):
    p=current_profile(group,recipe);r=recipe['base_recipe'];parts,kinds=original_material(group,r)
    q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis']);a=q+p['entry']*d;R=r['R_mm'];theta=math.radians(p['degrees'])
    at=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*p['bend']
    edges=([Part.makeLine(A.Vector(*q),A.Vector(*a))] if p['entry']>1e-8 else [])
    path=Part.Wire(edges+[Part.Arc(A.Vector(*a),A.Vector(*at(theta/2)),A.Vector(*p['start'])).toShape(),Part.makeLine(A.Vector(*p['start']),A.Vector(*p['tip']))])
    radius=r.get('radius_mm',r.get('radius'));wire=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert wire.isValid() and len(wire.Solids)==1
    rotation=A.Rotation(A.Vector(*d),A.Vector(*p['axis']));pose=A.Placement(A.Vector(*p['start'])-rotation.multVec(A.Vector(*q)),rotation)
    for n,s in list(parts.items()):
        if kinds[n]=='proposal_wire':parts[n]=wire
        else:
            v=s.copy();v.Placement=pose*v.Placement;assert v.isValid() and v.Solids;parts[n]=v
    return parts,kinds


def materialise(group,recipe):
    assert recipe['selected_T18I_max_head'] is True
    parts,kinds=current_receiving(group,recipe) if recipe.get('joint_current_bank_plane') else zoned_materialise(group,recipe)
    if recipe.get('joint_current_bank_plane'):
        p=current_profile(group,recipe);start,axis=p['start'],p['axis']
    elif recipe.get('receiving_zone'):
        p=profile(group,recipe);start,axis=p['start'],p['axis']
    else:start,axis,_,_=both_after_line(group,recipe)
    axis=A.Vector(*axis);land=A.Vector(*start)+axis*4.5
    D,H,E=dimensions()
    for n,s in list(parts.items()):
        if not n.endswith('head_budget'):continue
        radial=s.CenterOfMass-land;radial=radial-axis*radial.dot(axis)
        oldcentre_radius=radial.Length;radial.normalize();tangent=axis.cross(radial)
        centre=land+radial*(oldcentre_radius-3+D/2)
        matrix=A.Matrix()
        for i in range(3):
            for j,col in enumerate((radial,tangent,axis)):setattr(matrix,f'A{i+1}{j+1}',col[i])
        new=Part.makeBox(D,H,E,A.Vector(-D/2,-H/2,-E/2))
        new.Placement=A.Placement(centre,A.Rotation(matrix))
        outside=new.copy().cut(s.copy());assert outside.isNull() or outside.isValid()
        assert new.isValid() and len(new.Solids)==1 and outside.Volume<1e-7,(group,n,outside.Volume)
        assert abs(new.Volume-D*H*E)<1e-6
        parts[n]=new
    return parts,kinds
