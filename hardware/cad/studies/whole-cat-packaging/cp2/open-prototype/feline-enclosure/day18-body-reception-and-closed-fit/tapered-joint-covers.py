"""A recessed chest with an overlapping inner throat; keep the two access covers."""
from pathlib import Path
import json,math,ast
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
prior=P.parent/"day18-open-front-assembly";lib=prior/"seat-both-data-runs.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("box","loft","mesh","ell"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
def add(n,s,c):
    assert not s.isNull() and s.isValid(),n
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.DisplayMode="Shaded";o.ViewObject.Visibility=True;return o
def slab(a,b):return box(a,-120,-20,b-a,240,280)
def wall(rows):
    o=loft(rows,0);inside=loft(rows,2);return o.cut(inside),o
def leg(s,x,l):
    for y in (-106,50):s=s.cut(box(x,y,-30,l,56,64))
    return s
rows=json.loads((prior/"closed-outline.json").read_bytes())["stations"]
front=[(-177,8,65,89,.92),(-171,23,49,106,.88),(-158,43,33,138,.81),(-137,62,21,167,.78)]+rows[4:9]
skin,out=wall(front);keep=mesh(json.loads((P.parent/"day18-latest-whole-front"/"shoulder-volume.json").read_bytes())["small"])
# The cheek is free to swing above the chest. The outer chest rim is recessed
# aft and inboard of the skull. A second surface underlaps the rear opening.
door=box(-10,59,39,109,57,40)
outer=leg(skin.fuse(out.common(slab(-177,-175))).cut(keep).common(slab(-178,20)), -129,63).cut(door)
outer=outer.cut(box(-94,-110,76,22,54,24))
for x in (-87,-73,-59,-45,-31):outer=outer.cut(box(x,69,90,4.5,40,31))
neck=[(-165,41,85,170,.84),(-153,48,80,174,.82),(-133,57,72,175,.77),(-111,65,59,176,.74),
      (-96,77,43,178,.72),(-84,90.1,13,185,.57),rows[5]]
inner,_=wall(neck)
# Open the lower bearing and factory exit into the common floor at the front.
# The central opening for moving groups stays behind the opaque lateral lips.
inner=inner.cut(box(-166,-27,42,67,54,61))
# Keep the original switch recess clear through both nested walls.
inner=inner.cut(box(-94,-110,76,22,54,24))
body=outer.fuse(inner).removeSplitter()
# A rounded return beyond the speaker and the original tail opening replaces
# the steep straight back wall. Keep the present battery door and both switches.
rr=rows[7:12]+[(137,82,21,191,.59),(147,78,23,183,.66),(158,72,25,171,.73),
    (169,65,29,158,.80),(179,56,35,146,.86),(188,40,42,134,.91),(194,17,57,117,.96)]
tail,o=wall(rr)
# Add the end shell thickness without a flat open rim.
tail=tail.fuse(o.common(slab(192.2,194))).cut(box(131,-18,117,70,45,108))
tail=leg(tail,125,63)
# S0 has a complete through-mouth and bonded recess tube on the source cowl.
s0=Part.makeCylinder(28,57,V(115.5,-111,92),V(0,1,0));tail=tail.cut(s0)
tube=Part.makeCylinder(30,58,V(115.5,-112,92),V(0,1,0)).cut(s0).common(o)
tail=tail.fuse(tube).common(slab(20,195)).cut(door)
for x in (49,55,61,67,73):tail=tail.cut(box(x,-35,173,2.5,70,43))
for x in (86,93,100,107,114,121):tail=tail.cut(box(x,-41,180,3,82,39))
aft_front=D.FIT_AFT_COWL.Shape.common(slab(20,126))
aft=aft_front.fuse(tail.common(slab(126,195)),.001)
# Keep the source screw bosses and tool entries on the real moving back.
# A rounded rear entry retains an opaque rim above and below the flex field.
rear_entrance=ell((-110,0,149),(39,51,48)).fuse(box(-108,-46,104,26,92,88))
back=D.F3_HEAD_BACK.Shape.cut(rear_entrance).removeSplitter()
facts={}
for name,s,prev in [("BR_RECESSED_CHEST",body,"FIT_FRONT_COWL"),("BR_ROUNDED_RUMP",aft,"FIT_AFT_COWL"),("BR_OVERLAP_SKULL_BACK",back,"OPEN_SKULL_BACK")]:
    obj=add(name,s,(.15,.16,.18));D.getObject(prev).ViewObject.Visibility=False
    facts[name]=dict(solids=len(s.Solids),valid=s.isValid(),volume=s.Volume)
facts["inner_outer_join"]=outer.common(inner).Volume
facts["rear_hardware"]="Existing two keyed M2x16 headback joints, full nuts and washers retained on the pitch group. Rear and chest access remain separable at X20."
facts["physical_PASS"]=False
(P/"tapered-joint-covers.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
