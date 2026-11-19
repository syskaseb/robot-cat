"""Build the moving open helmet, fixed shoulder and actual receivers in the 19C native copy."""
from pathlib import Path
import json,math
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"whole-cat19C.FCStd").resolve()
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(p,r,h,n):return Part.makeCylinder(r,h,V(*p),V(*n))
def sh(n):return D.getObject(n).Shape
def put(n,s,color,kind):
    o=D.getObject(n) or D.addObject("Part::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.DisplayMode="Shaded"
    if "EvidenceKind" not in o.PropertiesList:o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=kind;return o
def fused(ss):return ss[0].multiFuse(ss[1:]).removeSplitter()
def write(n,o):(P/n).write_bytes((json.dumps(o,indent=1)+"\n").encode())
def ell(c,r):
    m=A.Matrix();m.A11,m.A22,m.A33=r;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(*c));return s
def ring(row,d=0,k=.72):
    x,w,lo,hi=row;z=(lo+hi)/2;h=(hi-lo)/2-d;w-=d;edges=[]
    for q in [[(0,h),(k*w,h),(w,k*h),(w,0)],[(w,0),(w,-k*h),(k*w,-h),(0,-h)],[(0,-h),(-k*w,-h),(-w,-k*h),(-w,0)],[(-w,0),(-w,k*h),(-k*w,h),(0,h)]]:
        c=Part.BezierCurve();c.setPoles([V(x,y,z+zz) for y,zz in q]);edges.append(c.toShape())
    return Part.Wire(edges)
def skin(rows,wall,k=.72):
    return Part.makeLoft([ring(r,0,k) for r in rows],True,True).cut(Part.makeLoft([ring(r,wall,k) for r in rows],True,True))
def cheek_seat(x,y,z):
    # Open top, separate tie slot and an approach flared beyond the 4.9 square pack.
    bed=box(x-6,y-4,z-5.5,12,8,3.0)
    cheeks=[box(x-6,y-4,z-3.1,2.6,8,5.5),box(x+3.4,y-4,z-3.1,2.6,8,5.5)]
    return fused([bed]+cheeks).cut(box(x-2.5,y-1.65,z-4.3,5,3.3,1.25))
# Both reception seats are structural. Body support bypasses low F_TY and Pi
# cooling at y=35..39, then reaches inward over the PCB before fixing the loom.
floor=sh("B19_FrontFloor")
base=box(-71.4,21.5,41,6,18.3,4.8)
pillar=box(-71.3,34.8,43.5,5.9,5.1,91.8)
arm=box(-71.3,15.6,132.3,19.8,24.2,3.0)
arm=arm.cut(box(-65.5,22,132,8.6,11,3.6))
fore=fused([floor,base,pillar,arm,cheek_seat(-56,17,138)])
put("C19_ShoulderFloor",fore,(.22,.39,.39),"fixed load floor with positive-side open bundle receiver")
D.B19_FrontFloor.ViewObject.Visibility=False
receiver=sh("D18C_TRUE_PITCH_OPTICAL_RECEIVER")
bridge=box(-180.1,16.3,145.5,25.7,3.8,3.3)
carrier=fused([receiver,bridge,cheek_seat(-158,22,151)])
put("C19_MovingOpticsCarrier",carrier,(.22,.39,.39),"moving camera/ToF frame, original holes, cheek exit")
D.D18C_TRUE_PITCH_OPTICAL_RECEIVER.ViewObject.Visibility=False
# Keep the source mating lip and its two metal-backed closure stations.
# Moving protection ends near the pitch axis; the fixed load-bearing joint
# and the high service loop occupy the open rear of this shell.
old=sh("BR_PARTED_SKULL_BACK")
lip=old.common(box(-174,-94,66,19,188,171))
skirt=skin([(-169,76.5,84,212.4),(-159,75.5,86,213),(-148,70.5,91,211)],1.45,.56)
back=lip.fuse(skirt).removeSplitter()
put("C19_OpenRearHelmet",back,(.134,.147,.162),"moving rear rim at both original M2 stations")
D.D19_BROAD_SKULL_BACK.ViewObject.Visibility=False
# Body tapers down behind the head and meets the unaltered 19B rear at x=20.
# The shoulder is a continuous body-rooted exterior, open end to end inside.
sections=[(-171,85,75,216),(-155,96,66,219),(-139,102,47,216),(-117,109,24,205),(-96,110,7,191),(-67,103,0,176),(-38,98,-2,158),(-15,98,-2,157),(8,102,-2,165),(20,103,-2,169.94)]
cow=skin(sections,1.45)
for y in (-120,38):cow=cow.cut(box(-109,y,-12,68,82,54))
for x in (-94,-82,-70,-58):
    cow=cow.cut(box(x,-55,140,3.3,19,80)).cut(box(x,32,140,3.3,17,80))
put("C19_FixedShoulderShell",cow,(.135,.147,.165),"continuous detachable front body and shoulder cowling")
D.D19_ROUNDED_FORE_COWL.ViewObject.Visibility=False
# Move from colour-only eyes to an actual stepped two-piece printed button.
# Each dome is seated against the face by its own axial post. Seating and pin
# interference are recorded separately from optical cone clearance.
mask=sh("BR_COMMON_OPTICAL_MASK")
for sign,side in [(1,"L"),(-1,"R")]:
    axis=V(-.843,.516*sign,.150);axis.normalize()
    c=V(-210.14,sign*43,160);orient=A.Rotation(V(0,0,1),axis)
    def local(s):
        s.Placement=A.Placement(c,orient).multiply(s.Placement);return s
    def dome(rx,ry,rz,base):
        return ell((0,0,base),(rx,ry,rz)).common(box(-rx-1,-ry-1,base,2*rx+2,2*ry+2,rz+.3))
    iris=fused([dome(11.3,12.5,3.5,0),cyl((0,0,-4.8),3.05,5.3,(0,0,1))])
    iris=iris.cut(cyl((0,0,-5.1),1.45,10,(0,0,1)))
    pupil=fused([dome(8.25,9.4,2.3,2.3),cyl((0,0,-4.7),1.40,8,(0,0,1))])
    # Mate the underside of the black cap to the matching dome surface.
    pupil=pupil.cut(iris)
    mask=mask.cut(local(cyl((0,0,-9),3.12,16,(0,0,1))))
    put("C19_Iris_"+side,local(iris),(.87,.50,.10),"amber printed insert, rear post").ViewObject.Visibility=True
    put("C19_Pupil_"+side,local(pupil),(.019,.020,.022),"black printed insert, through iris post")
# Low small nose is between the camera and ToF apertures.
nose=fused([ell((-207.8,0,123.8),(4.3,6.2,3.3)),cyl((-207.8,0,123.8),2,7.5,(1,0,0))])
mask=mask.cut(cyl((-213,0,123.8),2.08,17,(1,0,0)))
put("C19_Nose",nose,(.049,.047,.05),"small printed nose with engagement post")
# Tapered ears have a broad elliptical base and a narrower, rearward tip.
ears=[]
for s in [-1,1]:
    rings=[]
    for z,x,y,rx,ry in [(189,-179,s*48,14,16),(201,-179,s*50,13,15),(222,-178,s*55,7.5,9),(237,-175,s*58,1.7,2.1)]:
        el=Part.Ellipse(V(x,y,z),max(rx,ry),min(rx,ry));w=Part.Wire([el.toShape()]);w.rotate(V(x,y,z),V(0,0,1),90);rings.append(w)
    outer=Part.makeLoft(rings,True,True)
    inner=outer.copy();inner=inner.common(box(-200,-90,198,44,180,38))
    # A shallow front recess leaves an opaque ear back, edge and full root.
    bowl=ell((-191,s*52,212),(8,10,19))
    ears.append(outer.cut(bowl))
# Separate ears root in the helmet rim. Preserve the unaltered camera mask seating.
for i,ear in enumerate(ears):
    s=(-1,1)[i];y=s*48
    pad=box(-179,y-6,189.8,14,12,3.2)
    peg=cyl((-172,y,185),2.8,8,(0,0,1))
    ear=ear.fuse(peg).removeSplitter()
    back=back.fuse(pad).cut(cyl((-172,y,184.9),2.89,8.3,(0,0,1))).removeSplitter()
    put("C19_Ear_"+str(i+1),ear,(.145,.15,.16),"ear with locating post; heel on rear rim")
D.C19_OpenRearHelmet.Shape=back
face=mask;put("C19_FaceAndEars",face,(.145,.15,.16),"single optical mask and broad ear roots")
for n in ["BR_COMMON_OPTICAL_MASK","D19_SKULL_EARS"]:D.getObject(n).ViewObject.Visibility=False
# Register each new connected group as installation geometry, separately from prints.
layout=json.loads((P/"side-return.json").read_bytes())
ff=json.loads((P.parent/"day18-open-front-assembly/occupied-layout.json").read_bytes())["FFC"]
factory=json.loads((P.parent/"day18-body-reception-and-closed-fit"/"flank-reception.json").read_bytes())
pitch=json.loads((P.parent/"day18-body-reception-and-closed-fit"/"yaw-laid-factory.json").read_bytes())["rows"]
def poly(points):
    pts=[V(*points[0])]
    for p in points[1:]:
        v=V(*p)
        if (v-pts[-1]).Length>1e-5:pts.append(v)
    return Part.makePolygon(pts)
neutral=next(q for q in layout["motion"] if q["yaw"]==q["pitch"]==0)
fields={"C19_ToFLeadSet":(layout["head"]+[neutral["centreline"]]+[q["centreline"] for q in layout["fixed"]],(.91,.58,.10)),"C19_FFC190":([next(q["centreline"] for q in ff if q["yaw"]==q["pitch"]==0)],(.44,.33,.71)),"C19_HeadFactory250Pair":([factory["yaw"]["centreline"],next(q["centreline"] for q in pitch if q["yaw"]==0)],(.19,.61,.75))}
for n,(paths,col) in fields.items():
    o=put(n,Part.makeCompound([poly(q) for q in paths]),col,"installation references only; variable free spans");o.ViewObject.LineColor=col;o.ViewObject.LineWidth=3.5;o.ViewObject.Visibility=False
for n in ["BR_FLANK_TOF","BR_FLANK_PITCH","BR_YAW_STATIC","BR_FLANK_300","OPEN_NEUTRAL_RIBBON"]:D.getObject(n).ViewObject.Visibility=False
D.recompute();G.runCommand("Std_Save")
names=["C19_ShoulderFloor","C19_MovingOpticsCarrier","C19_OpenRearHelmet","C19_FixedShoulderShell","C19_FaceAndEars","C19_Iris_L","C19_Iris_R","C19_Pupil_L","C19_Pupil_R"]
write("build-receipt.json",{n:{"volume":sh(n).Volume,"solids":len(sh(n).Solids),"valid":sh(n).isValid()} for n in names})

