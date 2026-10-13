"""A local-axis arm entry for the two oblique compact splice seats."""
import FreeCAD as A
from loom_land_port import box,build as standard
from compact_loom_land_port import build as compact

def build(land,port,extension=None):
    recipe=port['recipe'];base=compact if recipe.get('construction') else standard
    result=base(land,port['arrival_normal'],recipe['band_axial_offset_mm'])
    length=recipe.get('axial_entry_extension_mm',0) if extension is None else extension
    if not length:return result
    assert recipe.get('construction')=='single_post_axial_entry_below_band'
    offset=recipe['band_axial_offset_mm']
    bounds=[4,-3,-7.5+offset-length,8,3,-3.5+offset]
    stub=box(bounds);stub.Placement=result['placement']*stub.Placement
    body=result['body'].fuse(stub).removeSplitter()
    assert body.isValid() and len(body.Solids)==1 and not body.check(True)
    assert body.common(result['band']).Volume<1e-6
    result['body']=body
    result['arrival_world_mm']=list(result['placement'].multVec(A.Vector(6,0,-5.5+offset-length)))
    result['recipe']=dict(result['recipe'],axial_entry_extension_mm=length,
        pads=result['recipe']['pads']+[dict(name='AxialApproach',bounds_mm=bounds)])
    return result
