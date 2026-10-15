"""Provisional 2mm insulated-core saddle, independent of terminal levers.

All dimensions are project assumptions for a non-energized fit sample. The
tie loop/head is an envelope, not a manufacturer-qualified clamp. Nominal
9mm straight is retained; tightening and insulation retention require a sample.
"""
import FreeCAD as A
from loom_land_port import box,build as reference


def build(land,normal,offset=0):
    assert offset in (-1.5,0,1.5)
    frame=reference(land,normal)['placement']
    pads=[dict(name='CoreSaddle',bounds_mm=[1.5,-2,-4.25,5.5,2,4.25]),
          dict(name='AxialArmEntry',bounds_mm=[1.5,-2,-7+offset,5.5,2,-3.5])]
    outer=[-2.6,-2.6,-1.45+offset,6.9,2.6,1.45+offset]
    inner=[-1.2,-1.2,-1.6+offset,5.5,1.2,1.6+offset]
    slot=box(outer).cut(box(inner))
    body=box(pads[0]['bounds_mm']).fuse(box(pads[1]['bounds_mm'])).cut(slot).removeSplitter()
    band=box([-2.4,-2.4,-1.25+offset,6.7,2.4,1.25+offset]).cut(
        box([-1.2,-1.2,-1.4+offset,5.5,1.2,1.4+offset]))
    band=band.fuse(box([6.7,-3,-2.5+offset,12.7,3,2.5+offset])).removeSplitter()
    assert body.isValid() and len(body.Solids)==1 and not body.check(True)
    assert band.isValid() and len(band.Solids)==1 and not band.check(True)
    assert body.common(band).Volume<1e-6
    body.Placement=frame*body.Placement;band.Placement=frame*band.Placement
    return dict(body=body,band=band,arrival_world_mm=list(frame.multVec(A.Vector(3.5,0,-5+offset))),
        recipe=dict(pads=pads,ring_cut=dict(outer=outer,inner=inner),local_to_world=list(frame.toMatrix().A),
            construction='provisional_independent_core_saddle',project_core_OD_mm=2,
            land_mm=9,band_axial_offset_mm=offset,band_head_6x6x5_provisional=True,
            sample_retention_and_tightening_gate_open=True))
