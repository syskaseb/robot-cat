"""One body/chest skin with a communicating head socket and shared rear head opening."""
from pathlib import Path
import json, math
import FreeCAD as A
import Part
D=A.ActiveDocument
P=Path(__file__).parent
V=A.Vector
assert Path(D.FileName).resolve()==(P/"front-insert.FCStd").resolve()
assert not D.getObject("INSERT_FRONT_NEG")
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def feature(name,shape,color=(.14,.15,.17)):
    obj=D.addObject("PartDesign::Feature",name)
    obj.Shape=shape;obj.ViewObject.ShapeColor=color;obj.ViewObject.DisplayMode="Shaded"
    return obj
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=1)+"\n").encode())
# Longitudinal stations fitted to the front monitor, lower frame, side banks,
# both flat audio modules, and old short factory pair. All belong to the same
# exterior. The change of section reaches the lower floor rather than leaving
# the old rectangular box under a cosmetic neck piece.
stations=[(-184,17,61,100,.74),(-172,36,48,125,.72),(-150,55,37,150,.70),
          (-128,68,34,169,.62),(-100,84,34,182,.56),(-74,93,34,186,.54),
          (-40,95,34,183,.56),(-4,94,34,180,.48),(20,94,34,181,.46),
          (65,94,34,181,.46),(106,93,35,180,.46),(132,89,39,174,.58),
          (150,79,48,160,.64),(171,60,59,146,.73),(185,31,84,130,.85)]
def profile(row,d):
    x,ry,lo,hi,e=row
    ry-=d;lo+=d;hi-=d
    cz=(hi+lo)/2;rz=(hi-lo)/2
    pts=[]
    # Rounded superellipse in YZ. Analytic design stations are interpolated
    # periodically in section, and the loft is ruled between adjacent stations.
    for i in range(32):
        a=2*math.pi*i/32
        y=ry*math.copysign(abs(math.cos(a))**e,math.cos(a))
        z=cz+rz*math.copysign(abs(math.sin(a))**e,math.sin(a))
        pts.append(V(x,y,z))
    curve=Part.BSplineCurve();curve.interpolate(pts,PeriodicFlag=True)
    return Part.Wire([curve.toShape()])
outer=Part.makeLoft([profile(s,0) for s in stations],True,True)
inner=Part.makeLoft([profile(s,1.8) for s in stations],True,True)
# A rearmost and a foremost cap remain real material.
inner=inner.common(box(-182.2,-130,0,365.4,260,250))
wall=outer.cut(inner)
tool=json.loads((P.parent/"day18-latest-whole-front"/"shoulder-volume.json").read_bytes())
def closed_mesh(q):
    vs=[V(*p) for p in q["vertices"]]
    faces=[Part.Face(Part.makePolygon([vs[i] for i in ids]+[vs[ids[0]]])) for ids in q["faces"]]
    sh=Part.makeSolid(Part.makeShell(faces)).removeSplitter()
    if sh.Volume<0:sh.reverse()
    assert sh.isValid()
    return sh
a=closed_mesh(tool["small"]);b=closed_mesh(tool["large"])
# The same port connects the head and torso voids. It retracts inside the
# moving skull at the front, while the fixed shoulder wraps the outside.
# The cross section carries the upper FFC, positive ToF and negative JR.
def port_section(x,lo,hi,yl,yr):
    pts=[V(x,yl,lo+8),V(x,yl+8,lo),V(x,yr-8,lo),V(x,yr,lo+8),V(x,yr,hi-8),V(x,yr-8,hi),V(x,yl+8,hi),V(x,yl,hi-8)]
    return Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)
neck=Part.makeLoft([port_section(*s) for s in [(-170,80,184,-65,57),(-145,80,185,-70,61),(-116,82,185,-67,62),(-81,94,184,-55,61),(-58,100,184,-47,58)]],True,True)
# Limit internal socket material to the body interior; window only in socket.
skin=wall.cut(a)
dish=b.cut(a).common(outer).cut(neck)
# Keep the socket wall separately identifiable for this occupied-space check.
# Its structural seam is open for engineering acceptance.
assert not skin.isNull() and not dish.isNull()
# Complete monitor remains fixed and readable. Preserve access paths in the
# proposed physical material for S0, S1, tail pitch, battery and cooling.
cuts=[box(-190,-21.75,70.75,25,43.5,27.5),
      Part.makeCylinder(28,200,V(115.5,-100,92),V(0,1,0)),
      box(-9,72,40,102,52,36),
      box(-92,-110,78,18,48,26),box(133,-83,119,45,68,23)]
# One bay door has real acoustic perforations; both selected faces sit below
# the perforated zones. Port alignment and resonance need hardware samples.
for x in (12,24,36,48,60,72,84,96):
    cuts.append(box(x,36,160,4,32,50))
for x in (21,33,45,57,69,81,93):
    cuts.append(box(x,-56,159,3,24,50))
for x in (-71,-56,-41,-26):
    cuts.append(box(x,75,93,4,40,29))
for cut in cuts:
    skin=skin.cut(cut)
# Keep the 98 lower receiving members as an actual retained subset. Old
# upper coverings retire in this copy only. Child components are untouched.
records=[]
for key,old_name,x0,x1,y0 in [("FRONT_NEG","F3_BODY_FORE_NEG",-190,20,-120),("FRONT_POS","F3_BODY_FORE_POS",-190,20,0),
                             ("REAR_NEG","F3_BODY_REAR_NEG",20,191,-120),("REAR_POS","F3_BODY_REAR_POS",20,191,0)]:
    src=D.getObject(old_name)
    clip=box(x0,y0,22,x1-x0,120,210)
    half=skin.common(clip)
    socket=dish.common(clip)
    low=src.Shape.common(box(x0,y0,38,x1-x0,120,36))
    composite=Part.makeCompound([s for s in (half,socket,low) if not s.isNull() and s.Volume>1e-6])
    feature("INSERT_"+key,composite)
    src.ViewObject.Visibility=False
    records.append(dict(name=key,valid=composite.isValid(),solids=len(composite.Solids),bounds=str(composite.BoundBox),skin_volume=half.Volume,socket_volume=socket.Volume,retained_lower_volume=low.Volume,structural_seam="open"))
back=D.F3_HEAD_BACK.Shape.cut(neck).removeSplitter()
feature("INSERT_HEAD_BACK",back)
D.F3_HEAD_BACK.ViewObject.Visibility=False
wr("insert-exterior.json",dict(stations=stations,body=records,back_valid=back.isValid(),back_solids=len(back.Solids),
    passage="single open rear of pitch skull through internal shoulder socket; exterior nominal 1.8 mm. Old lower source joints retained; independent mate/coverage and actual motion gates open.",
    whole_closed_accepted=False,physical_PASS=False))
D.recompute();D.save()
print("FRONT INSERT EXTERIOR SAVED",records,len(back.Solids))
