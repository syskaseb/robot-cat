"""One local G2 feed allocation on its real existing UpperCarrier floor.

Three equal TKD4mm2 jackets share a binding. The smaller BUS G jacket has
its own binding. Actual floor union/whole-world/access/native/stock remain
mandatory; this geometry test alone does not qualify W5 or retention.
"""
import FreeCAD as A
from loom_land_port import box


def saddle(name, x, y, radius, half_span, wires):
    t, width = .381, 1.6764
    n0, n1 = radius + .5, radius + 4.5
    # Local normal DOWN, lateral NORTH, axial EAST. Existing floor top148.01.
    seat = [n0, -half_span, -1.5, n1, half_span, 1.5]
    foot = [n1-.5, -half_span, -1.5, 7.09, half_span, 1.5]
    inside = [-radius-.05, -half_span-.15, -width, n1, half_span+.15, width]
    outside = [-radius-.05-t, -half_span-.15-t, -width/2,
               n1+t, half_span+.15+t, width/2]
    band = box(outside).cut(box(inside))
    knot = [-radius-.05-t-3, -1, -width/2, -radius-.05, 1, width/2]
    band = band.fuse(box(knot)).removeSplitter()
    cut_outer = [outside[i] + (-.15 if i < 3 else .15) for i in range(6)]
    cut_inner = [inside[i] + (.15 if i < 3 else -.15) for i in range(6)]
    body = box(seat).fuse(box(foot)).cut(box(cut_outer).cut(box(cut_inner))).removeSplitter()
    m = A.Matrix()
    m.A11=0; m.A21=0; m.A31=-1
    m.A12=0; m.A22=1; m.A32=0
    m.A13=1; m.A23=0; m.A33=0
    m.A14=x; m.A24=y; m.A34=155
    for s in (body, band):
        assert s.isValid() and len(s.Solids)==1 and not s.check(True), name
        s.Placement=A.Placement(m)*s.Placement
    assert body.common(band).Volume < 1e-6
    return dict(body=body,band=band,recipe=dict(name=name,wires=wires,
        seat=seat,foot=foot,ring_cut=dict(outer=cut_outer,inner=cut_inner),knot=knot,
        local_to_world=list(m.A),parent='UpperCarrier001',floor_top_mm=148.01,
        lacing_blank_mm=150,land_mm=3,physical_retention_creep_gate_open=True))


def geometry():
    return {
        'Heavy3': saddle('Heavy3',107,39.25,2.1,6.75,['W061','W062','W063']),
        'BUS_G': saddle('BUS_G',104,48.75,1,2,['W003'])}
