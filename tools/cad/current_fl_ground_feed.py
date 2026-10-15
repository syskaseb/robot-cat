"""Missing FL_G/W025 end: independent short insulation land, not W019's.

One short branch from the existing FrontLeftFixedCarrier measured root.
All material and routing acceptance stays open until the shared gate.
"""
import FreeCAD as A
from loom_land_port import box
from plan_axial_source_supports import arm_box


def geometry():
    r,t,w=2.1,.381,1.6764
    seat=[r+.5,-2,-1.5,r+4.5,2,1.5]
    # Local axial UP. Root joins below the lacing plane, not through it.
    foot=[r+.5,-2,-5.5,r+4.5,2,-1.4]
    outer=[-r-.2-t-.15,-r-.2-t-.15,-w/2-.15,r+4.5+t+.15,r+.2+t+.15,w/2+.15]
    inner=[-r-.2+.15,-r-.2+.15,-w,r+4.5-.15,r+.2-.15,w]
    band=box([-r-.2-t,-r-.2-t,-w/2,r+4.5+t,r+.2+t,w/2]).cut(
        box([-r-.2,-r-.2,-w,r+4.5,r+.2,w]))
    knot=[r+4.5+t,-1,-1.5,r+7.5+t,1,.5]
    band=band.fuse(box(knot)).removeSplitter()
    body=box(seat).fuse(box(foot)).cut(box(outer).cut(box(inner))).removeSplitter()
    m=A.Matrix();m.A11=-1;m.A22=-1;m.A33=1
    m.A14=-139.5;m.A24=84;m.A34=119.5
    for s in (body,band):s.Placement=A.Placement(m)*s.Placement
    # Root on the existing W019 support beam, not under W021's lacing.
    # The whole top/outer elbow bypasses that occupied receiver seat.
    path=[[-126.25,95.5,123.5],[-144,95.5,123.5],[-144,84,123.5],[-144,84,116.5]]
    body=body.multiFuse([arm_box(a,b,[2,2,2]) for a,b in zip(path,path[1:])]).removeSplitter()
    for s in (body,band):assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    assert body.common(band).Volume<1e-6
    return dict(body=body,band=band,recipe=dict(wire='W025',end='FL_G',parent='FrontLeftFixedCarrier',
        centre_mm=[-139.5,84,119.5],seat=seat,foot=foot,ring_cut=dict(outer=outer,inner=inner),knot=knot,
        local_to_world=list(m.A),root_path_mm=path,arm_half_width_mm=2,
        source_mouth_mm=[-139.5,84,112.5],land_mm=3,lacing_blank_mm=150,
        independent_from_three_body_receiver_grips=True,physical_retention_creep_gate_open=True))
