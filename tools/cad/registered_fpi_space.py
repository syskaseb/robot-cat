"""Restore an explicit project allocation omitted from the Day26 native scene.

F_PI is a casing-box reservation, never exact manufacturer material. Its source
size comes from the registered R5 case and its current unqualified home from
the central-spine plan. Keep it separate from purchased/printed materials.
"""
import hashlib
import json
from pathlib import Path
import FreeCAD as A
import Part


def construct(out):
    out=Path(out)
    paths=[out/'n01-module-plan-r5.json',out/'n01-central-spine-power-plan-r4.json']
    modules=json.loads(paths[0].read_text())
    source=next(g for g in modules['groups'] if g['role']=='F_PI')
    plan=json.loads(paths[1].read_text())['F_PI']
    assert plan['rotation_relative_current']==[[1,0,0],[0,1,0],[0,0,1]]
    lo,hi=source['candidate_bounds_mm']
    size=[b-a for a,b in zip(lo,hi)]
    centre=plan['centre_mm']
    origin=[c-d/2 for c,d in zip(centre,size)]
    shape=Part.makeBox(*size,A.Vector(*origin))
    shape.check(True)
    assert shape.isValid() and len(shape.Solids)==1
    return shape,dict(
        actor='F_PI:registered_casing_reservation',
        kind='project_casing_reservation_not_supplier_material',
        source_object=source['objects'][0],
        source_size_mm=size,current_unqualified_centre_mm=centre,
        bounds_mm=[origin,[a+b for a,b in zip(origin,size)]],
        original_source_box_preserved=True,
        exact_manufacturer_geometry=False,selected_pose=False,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        source_constructor='registered_fpi_space.construct',
    )
