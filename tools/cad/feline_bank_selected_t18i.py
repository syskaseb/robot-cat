"""Full selected T18I maximum drawing envelope in the ACTUAL strap frame.

No change to source mouths, jackets, radii, PETG caps or nominal full bands.
Anchor the head at the old strap's outer face; never shrink it about a
floating centre. Every new head is proved a subset of the old6cube budget.
"""
import copy
from functools import lru_cache
import numpy as np
import FreeCAD as A
import Part
from feline_bank_receiving_grips import both_after_candidates,both_after_line
from feline_bank_zoned_layout import candidates as zoned_candidates,materialise as zoned_materialise,profile
from feline_t18i_selected_head import source


@lru_cache(maxsize=1)
def dimensions():
    doc=source();d=doc['all_linked_drawings_conservative_upper_mm']
    return d['D_radial'],d['H_tangent'],d['E_along_wire']


def candidates(groups):
    rows=both_after_candidates(groups);rows.update(zoned_candidates(groups))
    return {g:[dict(copy.deepcopy(r),selected_T18I_max_head=True) for r in rr] for g,rr in rows.items()}


def materialise(group,recipe):
    assert recipe['selected_T18I_max_head'] is True
    parts,kinds=zoned_materialise(group,recipe)
    if recipe.get('receiving_zone'):
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
