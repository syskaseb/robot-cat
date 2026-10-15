"""Same provisional9mm saddle for measured project wire radii, not PCB pads.

It is an independent insulation restraint. Tie dimensions/tension and PETG
retention remain unpowered prototype-fit gates, not a pull-load rating.
"""
import FreeCAD as A
from loom_land_port import box,build as frame_for


def build(land,normal,radius):
    assert .5<=radius<=3 and land['length_mm']>=9
    r=radius;frame=frame_for(land,normal)['placement']
    pads=[dict(name='InsulationSaddle',bounds_mm=[r+.5,-2,-4.25,r+4.5,2,4.25]),
          dict(name='AxialArmEntry',bounds_mm=[r+.5,-2,-7,r+4.5,2,-3.5])]
    outer=[-r-1.6,-r-1.6,-1.45,r+5.9,r+1.6,1.45]
    inner=[-r-.2,-r-.2,-1.6,r+4.5,r+.2,1.6]
    body=box(pads[0]['bounds_mm']).fuse(box(pads[1]['bounds_mm'])).cut(box(outer).cut(box(inner))).removeSplitter()
    band=box([-r-1.4,-r-1.4,-1.25,r+5.7,r+1.4,1.25]).cut(
        box([-r-.2,-r-.2,-1.4,r+4.5,r+.2,1.4]))
    band=band.fuse(box([r+5.7,-3,-2.5,r+11.7,3,2.5])).removeSplitter()
    for s in (body,band):assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    assert body.common(band).Volume<1e-6
    body.Placement=frame*body.Placement;band.Placement=frame*band.Placement
    return dict(body=body,band=band,arrival_world_mm=list(frame.multVec(A.Vector(r+2.5,0,-5))),
        recipe=dict(pads=pads,ring_cut=dict(outer=outer,inner=inner),local_to_world=list(frame.toMatrix().A),
            project_insulation_radius_mm=r,land_mm=9,band_head_6x6x5_provisional=True,
            construction='independent_insulation_saddle_not_adhesive_WAGO_retention',
            sample_retention_tightening_creep_gate_open=True))
