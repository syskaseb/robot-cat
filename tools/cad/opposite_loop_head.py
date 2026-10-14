"""Same provisional tie loop/seat, head closed on its opposite exposed side.

This changes a flexible purchased tie's installation, not the printed seat or
cable land. Nominal6x6x5head remains a project envelope requiring delivery fit.
"""
import FreeCAD as A
from loom_land_port import box


def band(profile):
    loop=box([-4.2,-4.2,-1.25,8.2,4.2,1.25]).cut(box([-3,-3,-1.4,7,3,1.4]))
    result=loop.fuse(box([-10.2,-3,-2.5,-4.2,3,2.5])).removeSplitter()
    offset=profile['recipe']['band_axial_offset_mm']
    if offset:result.translate(A.Vector(0,0,offset))
    result.Placement=profile['placement']*result.Placement
    assert result.isValid() and len(result.Solids)==1 and not result.check(True)
    assert abs(result.Volume-profile['band'].Volume)<1e-6
    assert result.common(profile['body']).Volume<1e-6
    return result
