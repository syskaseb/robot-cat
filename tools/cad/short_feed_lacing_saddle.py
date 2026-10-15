"""Independent3mm feed grip ABOVE the5mm shared cap, not in its feed hole.

The existing nine-mm straight leaves four mm above the pressure bridge.
A thin lacing band occupies that short fixed land; its foot joins only the
printed parent, never the WAGO or a PCB. Delivered retention/creep are gates.
"""
import FreeCAD as A
from loom_land_port import box
from build_front_fixed_port_clearance import placement


def build(common_recipe,feed,support='body'):
    frame=placement(common_recipe['local_to_world']);p=frame.inverse().multVec(A.Vector(*feed['point_world_mm']))
    assert abs(p.x)<1e-6 and abs(abs(p.y)-9.5)<1e-6 and abs(p.z-2.5)<1e-6
    r=feed['radius_mm'];y=p.y;t=.381;w=1.6764;z=-4.5
    assert support in ('body','cap')
    foot_max=min(r+4.5,common_recipe['base_bounds_mm'][3] if support=='body' else -common_recipe['cap_bounds_mm'][0])
    pads=[dict(name='ShortFixedFeedSeat',bounds_mm=[r+.5,y-2,-6,r+4.5,y+2,-3]),
          dict(name='ParentTopFoot',bounds_mm=[r+.5,y-2,-4.5,foot_max,y+2,-2.5])]
    outer=[-r-.2-t-.15,y-r-.2-t-.15,z-w/2-.15,r+4.5+t+.15,y+r+.2+t+.15,z+w/2+.15]
    inner=[-r-.2+.15,y-r-.2+.15,z-w,r+4.5-.15,y+r+.2-.15,z+w]
    band_outer=[-r-.2-t,y-r-.2-t,z-w/2,r+4.5+t,y+r+.2+t,z+w/2]
    band_inner=[-r-.2,y-r-.2,z-w,r+4.5,y+r+.2,z+w]
    knot=[r+4.5+t,y-1,-6,r+7.5+t,y+1,-4]
    if support=='cap':
        def mirror(b):return [-b[3],b[1],b[2],-b[0],b[4],b[5]]
        for pad in pads:pad['bounds_mm']=mirror(pad['bounds_mm'])
        outer,inner,band_outer,band_inner,knot=map(mirror,(outer,inner,band_outer,band_inner,knot))
    body=box(pads[0]['bounds_mm']).fuse(box(pads[1]['bounds_mm'])).cut(box(outer).cut(box(inner))).removeSplitter()
    band=box(band_outer).cut(box(band_inner))
    band=band.fuse(box(knot)).removeSplitter()
    for s in (body,band):assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    assert body.common(band).Volume<1e-6
    body.Placement=frame*body.Placement;band.Placement=frame*band.Placement
    return dict(body=body,band=band,
        recipe=dict(pads=pads,ring_cut=dict(outer=outer,inner=inner),local_to_world=common_recipe['local_to_world'],
            project_wire_radius_mm=r,parent_component=support,short_fixed_land_mm=3,contact_world_centre_mm=list(frame.multVec(A.Vector(0,y,z))),
            project_lacing_section_mm=[t,w],project_knot_bounds_local_mm=knot,lacing_blank_mm=150,
            does_not_claim_nine_mm_pressure_land=True,physical_retention_tightening_creep_gate_open=True))
