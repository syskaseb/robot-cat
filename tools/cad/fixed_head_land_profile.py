"""Actual nominal flat material at the straight factory restraint lands.

The free bends retain a conservative circular reservation. A diagonal circle
cannot establish whether the flat land actually bears on its supporting bed.
Dimensions remain a labelled delivery assumption, not a manufacturer fact.
"""
import FreeCAD as A
import Part

def flat_land(edge,width=3.5,height=1.8):
    assert isinstance(edge.Curve,Part.Line) and edge.Length>1e-6
    a=edge.valueAt(edge.FirstParameter);b=edge.valueAt(edge.LastParameter)
    t=(b-a);t.normalize();assert abs(t.z)<1e-7
    across=A.Vector(t.y,-t.x,0);up=A.Vector(0,0,1)
    p=[a+across*sx*width/2+up*sz*height/2 for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
    material=Part.Face(Part.makePolygon(p+[p[0]])).extrude(b-a)
    assert material.isValid() and len(material.Solids)==1
    assert abs(material.Volume-edge.Length*width*height)<1e-6
    return material

# LOCAL_BEND_REFINEMENT
def flat_bend_prefix(edge,length=8,width=3.5,height=1.8):
    """Nominal no-added-twist material for only the first local arc land.

    The remaining arc keeps its conservative diagonal-circle reservation.
    This local profile is a delivery assumption, not measured factory data.
    """
    assert isinstance(edge.Curve,Part.Circle) and 0<length<edge.Length
    split=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*length/edge.Length
    short=edge.Curve.toShape(edge.FirstParameter,split)
    rest=edge.Curve.toShape(split,edge.LastParameter)
    a=short.valueAt(short.FirstParameter);t=short.tangentAt(short.FirstParameter)
    assert abs(t.z)<1e-7
    across=A.Vector(t.y,-t.x,0);up=A.Vector(0,0,1)
    p=[a+across*sx*width/2+up*sz*height/2 for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
    material=Part.Wire([short]).makePipeShell([Part.makePolygon(p+[p[0]])],True,True)
    assert material.isValid() and len(material.Solids)==1
    assert abs(material.Volume-length*width*height)<1e-4
    return material,rest
