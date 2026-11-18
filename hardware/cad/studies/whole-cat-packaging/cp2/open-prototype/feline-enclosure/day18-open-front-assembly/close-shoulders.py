"""Shape the lower chest, shoulder overlap and dorsal bay around the installed equipment."""
from pathlib import Path
import json,math
import FreeCAD as A, FreeCADGui as G, Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("OPEN_FRONT_COWL")
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def obj(n,s,col):
    assert not s.isNull() and s.isValid(),n
    o=D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode="Shaded";return o
def wire(s,d=0):
    x,w,lo,hi,power=s;lo+=d;hi-=d;w-=d;pts=[]
    for i in range(28):
        t=2*math.pi*i/28
        def signed(v):return math.copysign(abs(v)**power,v)
        pts.append(V(x,w*signed(math.cos(t)),(lo+hi)/2+(hi-lo)/2*signed(math.sin(t))))
    spline=Part.BSplineCurve();spline.interpolate(pts,PeriodicFlag=True);return Part.Wire([spline.toShape()])
def loft(rows,d):return Part.makeLoft([wire(s,d) for s in rows],True,True)
def mesh(q):
    pos=[V(*x) for x in q["vertices"]]
    faces=[Part.Face(Part.makePolygon([pos[a],pos[b],pos[c],pos[a]])) for a,b,c in q["faces"]]
    s=Part.makeSolid(Part.makeShell(faces)).removeSplitter()
    if s.Volume<0:s.reverse()
    return s
# The lower abdomen reaches the WAVEGO chassis. The leg casings enter from
# below the belly through two transverse openings, kept as functional ports.
rows=[(-190,14,57,100,.78),(-180,34,42,123,.77),(-161,58,27,158,.74),(-136,72,17,181,.70),
      (-105,86,12,189,.61),(-76,94,9,185,.53),(-35,96,8,182,.49),(5,92,8,181,.53),
      (43,87,11,186,.56),(76,85,15,193,.58),(104,85,17,198,.55),(126,84,21,197,.54),
      (147,76,27,173,.62),(168,59,40,148,.69),(187,33,64,126,.78)]
outer=loft(rows,0);inside=loft(rows,2).common(box(-188,-130,-20,373,260,280))
body=outer.cut(inside)
head=mesh(json.loads((P.parent/"day18-latest-whole-front"/"shoulder-volume.json").read_bytes())["small"])
body=body.cut(head)
for x,l in [(-129,63),(125,63)]:
    for y in (-106,50):
        body=body.cut(box(x,y,-30,l,56,64))
# Independent access to both switches, battery and tail. Recess wall around
# S0 carries the opening down to its operating face without a through-body bore.
s0=Part.makeCylinder(28,57,V(115.5,-111,92),V(0,1,0))
tube=Part.makeCylinder(30,58,V(115.5,-112,92),V(0,1,0)).cut(s0).common(outer)
body=body.cut(s0)
# Battery door is the original curved material as a separate removable panel.
door_tool=box(-10,59,39,109,57,40)
door=body.common(door_tool)
body=body.cut(door_tool)
cuts=[box(-94,-110,76,22,54,24),box(131,-18,117,70,45,108)]
# Acoustic slots follow each relocated transducer. Two separate rows of
# cooling slots remain above and below the Pi side, clear of the data boots.
for x in (49,55,61,67,73):cuts.append(box(x,-35,173,2.5,70,43))
for x in (86,93,100,107,114,121):cuts.append(box(x,-41,180,3,82,39))
for x in (-87,-73,-59,-45,-31):cuts.append(box(x,69,90,4.5,40,31))
for b in cuts:body=body.cut(b)
# A stationary open-top U liner shields the gimbal from the open side of
# the motion socket. The upper edge underlaps the moving skull side walls.
neck=[(-182,32,69,149,.79),(-160,52,67,166,.73),(-136,58,63,172,.68),
      (-113,62,57,168,.60),(-87,73,47,163,.55)]
lo=loft(neck,0);li=loft(neck,2)
liner=lo.cut(li).common(box(-183,-95,46,98,190,105))
# Attach the liner to the chest with broad webs below the moving fork;
# neither web passes through the middle of the mech or the upper loom.
supports=[]
for side in (-1,1):
    y=42 if side==1 else -92
    supports.append(box(-121,y,58,6,50,4).common(outer))
# Hood parting is across the torso and gives the two people open access from
# above. Keep screened contributors identifiable even when a joint is open.
fore_clip=box(-200,-110,-10,220,220,260);aft_clip=box(20,-110,-10,180,220,260)
f=body.common(fore_clip);a=body.common(aft_clip)
front=f.multiFuse([liner]+supports).removeSplitter()
aft=a.fuse(tube.common(aft_clip)).removeSplitter()
features=[obj("OPEN_FRONT_COWL",front,(.15,.16,.18)),obj("OPEN_AFT_COWL",aft,(.15,.16,.18)),
          obj("OPEN_BATTERY_DOOR",door,(.19,.20,.22))]
for n in ("INSERT_FRONT_NEG","INSERT_FRONT_POS","INSERT_REAR_NEG","INSERT_REAR_POS"):D.getObject(n).ViewObject.Visibility=False
# Keep actual source side cheeks and more side material around the new rear
# opening. The two-stage notch leaves a continuous rim around the skull.
rear=D.F3_HEAD_BACK.Shape.cut(box(-139,-48,97,52,96,99)).removeSplitter()
features.append(obj("OPEN_SKULL_BACK",rear,(.16,.17,.19)));D.INSERT_HEAD_BACK.ViewObject.Visibility=False
# The voltage monitor stays in the chest; closed hood lifts to read it.
(P/"closed-outline.json").write_bytes((json.dumps(dict(stations=rows,features=[dict(name=o.Name,solids=len(o.Shape.Solids),volume=o.Shape.Volume) for o in features],
    monitor="With the front hood lifted; no electrical disconnection intended.", battery_door="Provisional shell panel; attachment open.",
    optical_face="Existing local source windows and open mask qualification preserved.",physical_PASS=False),indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
