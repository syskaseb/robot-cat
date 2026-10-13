"""One oriented9mm jacket seat with a below-band structural arrival.

Reusable geometry from the received source-carrier fix, not another family
of micro-offsets. Inputs are actual unchanged land ends and a planned radial
arrival direction. Nominal purchased tie head remains a project envelope.
"""
import FreeCAD as A
import Part


def box(b):
    return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))


def build(land, arrival_normal, band_offset_mm=0):
    assert abs(band_offset_mm)<=1.5
    centre=A.Vector(*land['centre_world_mm']);axis=A.Vector(*land['axis'])
    reverse=land.get('id','').endswith('/Splice/1')
    if reverse:
        # Both splice-side bridge slabs face AWAY from the sleeve zone.
        # The same9mm jacket segment is retained; only the asymmetric seat
        # template's local axial direction is reversed at the far land.
        axis=-axis
    axis.normalize();normal=A.Vector(*arrival_normal)
    normal-=axis*normal.dot(axis);assert normal.Length>1e-6
    normal.normalize();other=axis.cross(normal)
    matrix=A.Matrix()
    matrix.A11,matrix.A21,matrix.A31=normal
    matrix.A12,matrix.A22,matrix.A32=other
    matrix.A13,matrix.A23,matrix.A33=axis
    matrix.A14,matrix.A24,matrix.A34=centre
    transform=A.Placement(matrix)
    pads=[dict(name='NineMmLand',bounds_mm=[4,-3,-4.5,8,3,4.5]),
          dict(name='BelowBandSlab',bounds_mm=[4,-6.2,-7.5,16,6.2,-3.5]),
          dict(name='ArrivalColumn',bounds_mm=[14.9,-3,-7.5,18.9,3,2]),
          dict(name='SideColumnPositive',bounds_mm=[4,4.9,-7.5,8,8.9,2]),
          dict(name='SideColumnNegative',bounds_mm=[4,-8.9,-7.5,8,-4.9,2])]
    cuts=[[7,-3.1,-1.4,8.3,3.1,1.4],[8,-3.2,-2.7,14.4,3.2,2.7]]
    ring=dict(outer=[-4.4,-4.4,-1.45,8.4,4.4,1.45],inner=[-2.8,-2.8,-1.6,6.8,2.8,1.6])
    if band_offset_mm:
        # The jacket seat stays exactly9mm. Slide only the purchased band's
        # 2.5mm axial footprint, its passage and structural bridge. Paired
        # fixed ends use +/-1.5mm, leaving1.75mm to both land edges and0.5mm
        # between their band loops, without moving either continuous cable.
        for row in pads[1:]:
            row['bounds_mm'][2]+=band_offset_mm
            row['bounds_mm'][5]+=band_offset_mm
        if band_offset_mm<0:
            pads.append(dict(name='SeatToLowerBridge',bounds_mm=[4,-3,-3.6+band_offset_mm,8,3,-3.5]))
        for bounds in cuts+list(ring.values()):
            bounds[2]+=band_offset_mm;bounds[5]+=band_offset_mm
    body=box(pads[0]['bounds_mm'])
    for row in pads[1:]:body=body.fuse(box(row['bounds_mm'])).removeSplitter()
    for bounds in cuts:body=body.cut(box(bounds)).removeSplitter()
    body=body.cut(box(ring['outer']).cut(box(ring['inner']))).removeSplitter()
    band=box([-4.2,-4.2,-1.25,8.2,4.2,1.25]).cut(box([-3,-3,-1.4,7,3,1.4]))
    band=band.fuse(box([8.2,-3,-2.5,14.2,3,2.5])).removeSplitter()
    if band_offset_mm:band.translate(A.Vector(0,0,band_offset_mm))
    assert body.isValid() and len(body.Solids)==1 and not body.check(True)
    assert band.isValid() and len(band.Solids)==1 and not band.check(True)
    assert body.common(band).Volume<1e-6
    body.Placement=transform*body.Placement;band.Placement=transform*band.Placement
    return dict(body=body,band=band,placement=transform,
                arrival_world_mm=list(transform.multVec(A.Vector(16.9,0,band_offset_mm))),
                recipe=dict(pads=pads,cuts=cuts,ring_cut=ring,
                            local_to_world=list(matrix.A),
                            reverse_axis_for_outer_splice_bridge=reverse,
                            band_axial_offset_mm=band_offset_mm,
                            jacket_land_mm=9,band2_5mm_head6x6x5_provisional=True))
