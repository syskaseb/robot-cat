"""Prototype jacket post with an axial arm entry below the band.

One post replaces the earlier side columns and long bridge around the tie
head. The unchanged9mm jacket land and staggered band seats are retained.
The head stays outward and accessible; the arm joins below it. This is a
new shared construction, requiring actual complete-motion qualification.
"""
import FreeCAD as A
from loom_land_port import box,build as original


def build(land,arrival_normal,band_offset_mm=0):
    ref=original(land,arrival_normal,band_offset_mm)
    transform=ref['placement'];recipe=ref['recipe']
    bottom=-7.5+band_offset_mm
    pads=[dict(name='NineMmLand',bounds_mm=[4,-3,-4.5,8,3,4.5]),
          dict(name='AxialArmEntry',bounds_mm=[4,-3,bottom,8,3,-3.5])]
    body=box(pads[0]['bounds_mm']).fuse(box(pads[1]['bounds_mm'])).removeSplitter()
    for cut in recipe['cuts']:body=body.cut(box(cut)).removeSplitter()
    ring=recipe['ring_cut'];body=body.cut(box(ring['outer']).cut(box(ring['inner']))).removeSplitter()
    assert body.isValid() and len(body.Solids)==1 and not body.check(True)
    body.Placement=transform*body.Placement
    band=ref['band'];assert body.common(band).Volume<1e-6
    recipe=dict(recipe,pads=pads,construction='single_post_axial_entry_below_band')
    return dict(body=body,band=band,placement=transform,recipe=recipe,
        arrival_world_mm=list(transform.multVec(A.Vector(6,0,-5.5+band_offset_mm))))
