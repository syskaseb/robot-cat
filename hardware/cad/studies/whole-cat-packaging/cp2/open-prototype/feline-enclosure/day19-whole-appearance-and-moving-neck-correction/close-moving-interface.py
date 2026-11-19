"""Two swept diaphragms and an under-jaw shield. Open torso-laid return and captured yaw tabs."""
from pathlib import Path
import json,math,runpy
import FreeCAD as A, FreeCADGui as G,Part
from zipfile import ZipFile
from xml.etree import ElementTree as ET
P=Path(__file__).parent
src=(P/"form-and-neck.py").read_text()
exec(src[:src.index("def whole():")])
records=json.loads((P/"form-members.json").read_bytes())
checks={}
def update(n,s):
    s=s.removeSplitter()
    if len(s.Solids)!=1 or not s.isValid():raise ValueError((n,len(s.Solids),s.isValid()))
    D.getObject(n).Shape=s;records[n].update(volume=s.Volume,solids=1,extents=[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength])
    write("form-members.json",records)
def join_valid(s,t):
    q=s.fuse(t).removeSplitter()
    return q if len(q.Solids)==1 and q.isValid() else s
def diag(side,x,rs,shape):
    slab=outer(rs).common(box(x,-120,30,2.45,240,220))
    for poly in json.loads((P/"seam-profiles.json").read_bytes())[side]:
        w=Part.makePolygon([V(x-.2,y,z) for y,z in poly]);slab=slab.cut(Part.Face(w).extrude(V(3.2,0,0)))
    before=shape.Volume;shape=join_valid(shape,slab);checks[side+"_front_web_mm3"]=shape.Volume-before
    return shape
def pad(x,y,z,axis=1):
    # Through slots flank the four jackets; no vertical rails intersect the
    # entry turn. Thread the tie before installing the detachable covers.
    return box(x-5,y-7.2,z-4.8,10,14.4,2.7).cut(box(x-1.7,y-5.9,z-5,3.4,2.2,4)).cut(box(x-1.7,y+3.7,z-5,3.4,2.2,4))
S=lay["head_receiver"];B=lay["fixed_receiver"]
fl=sh("B19_FrontFloor");car=sh("D18C_TRUE_PITCH_OPTICAL_RECEIVER").cut(box(-204,1.2,91,17.5,15,24))
# Bridge above the source camera frame to the negative cheek, with one root on
# the optical frame roof. The inclined pad-side fan clears the positive holder lip.
base=box(-182.9,-19.8,156.9,5.2,5.1,3.4);beam=box(-182.9,-43,156.6,33,4.4,2.9);leg=box(-182.9,-41,156.8,5.2,25,3.0)
carrier=fused([car,base,beam,leg,pad(*S)])
update("D19D_OpticsCarrier",carrier)
fore=fused([fl,box(-73.2,20,41,6.2,34.2,4.5),box(-73.2,51,42.5,5.6,4.2,92.7),box(-73.2,50.7,133.1,20.9,4.5,2.6),pad(*B)])
update("D19D_FrontFloor",fore)
yawrows=[(-138,82,72,220),(-126,79,70,220),(-111,74,68,218),(-97,67,67,211)]
bodyrows=[(-110,91,38,220),(-98,99,27,220),(-77,104,18,211),(-54,101,17,189),(-31,99,21,172),(-5,98,23,164),(20,102,23,167)]
hood=diag("yaw",-138,yawrows,sh("D19D_YawHood"))
body=diag("fixed",-110,bodyrows,sh("D19D_Shoulder"))
# Fixed bottom shield closes the front service opening after gimbal insertion.
# The outward face tapers back behind the jaw. Upper edge is below the pitch
# housing. Keep an opening around the existing fixed collar, including its screws.
lower_rs=[(-166.8,30,45,78),(-151,44,41,88),(-129,60,39,94),(-109,76,39,98),(-101,88,35,103)]
shield=split_skin(lower_rs,1.45,True)
# Preserve the fixed load path and overlap the front body shoulder below the joint.
shield=shield.cut(fore)
for x in [-116,-110]:
    for sign in [-1,1]:
        bridge=box(x,min(sign*50,sign*92),58,10,42,3.5).common(outer(bodyrows))
        body=join_valid(body,bridge)
res=body.fuse(shield).removeSplitter()
if len(res.Solids)==1 and res.isValid():body=res;checks["underjaw_owner"]="shoulder"
else:
    carrier_shield=join_valid(fore,shield);checks["underjaw_owner"]="floor" if carrier_shield.Volume>fore.Volume+.1 else "unconnected"
    update("D19D_FrontFloor",carrier_shield);fore=carrier_shield
# Lowest yaw skirt sweeps around the fixed motor housing. Use the actual coaxial
# clearance of the complete C floor/collar across yaw, maintaining the two sides.
spindle=Part.makeCylinder(46.7,57,V(-130,0,41))
hood=hood.cut(spindle)
# Two keyed rails, integral with the actual yaw saddle, take the detachable
# hood in the negative flank. End stops and a common tie slot retain it.
saddle=sh("BR_FINISHED_YAW_SADDLE")
ribs=[]
for x in [-136,-130]:
    rib=box(x,-72,128.6,4.2,25,3.6)
    ribs.append(rib)
rail=box(-136,-73,128.6,10.2,6,4.4).cut(box(-132.8,-71.8,128,2.8,3.2,6))
new_saddle=fused([saddle,rail]+ribs)
if len(new_saddle.Solids)==1 and new_saddle.isValid():
    install("D19D_YawSaddle",new_saddle,(.20,.34,.34),"source full saddle with two integral rails and a slotted stop")
    D.BR_FINISHED_YAW_SADDLE.ViewObject.Visibility=False
    # Hood lands above its rail, retained by a loop through both paired openings.
    tab=box(-136,-84,133.2,10.2,16.8,3.1).common(outer(yawrows)).cut(box(-132.8,-71.8,133,2.8,3.2,4))
    hood=join_valid(hood,tab);checks["yaw_mount"]="integral rail under shell tab"
else:checks["yaw_mount"]="integral saddle extension rejected"
update("D19D_YawHood",hood)
body=body.cut(fore);update("D19D_Shoulder",body)
rear=sh("D19D_RearShell").cut(sh("B19_TailMatedPair"));update("D19D_RearShell",rear)
# Avoid full rigid interference of the pitch MG loom on the negative side of
# the rear pitch housing. Open the underside, which sits inside the yaw shroud.
back=sh("D19D_PitchBack")
# Two independent optical halves seat against a continuous rim without volume overlap.
face=sh("D19D_Face").cut(back)
# Short paired muzzle lobes and the wall of both source optical apertures.
muzzles=[]
for sign in [-1,1]:
    a=ell((-217,sign*11.8,121.7),(8.8,13.3,8.7));b=ell((-216.5,sign*11.8,121.7),(7.55,11.8,7.25));muzzles.append(a.cut(b))
for s in muzzles:face=join_valid(face,s)
with ZipFile(P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd") as z:
    xml=ET.fromstring(z.read("Document.xml"))
    for n in ["D18C_CAM_MODEL_CLOCK_BOUND_FOV","D18C_TOF_MODEL_CLOCK_BOUND_FOV"]:
        ref=xml.find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%n).get("file");field=Part.Shape();field.importBrepFromString(z.read(ref).decode("ascii"))
        outside=field.copy();outside.translate(V(1.6,0,0))
        well=outside.cut(field).common(box(-221.5,-35,90,28.5,70,94))
        face=join_valid(face,well);face=face.cut(field)
face=face.cut(sh("D19D_Nose"))
update("D19D_Face",face)
q=next(m for m in lay["motion"] if m["yaw"]==m["pitch"]==0)
def paths(lines):return Part.makeCompound([Part.makePolygon([V(*p) for p in line]) for line in lines])
D.D19D_ToF.Shape=paths(lay["head"]+q["cores"]+[f["centreline"] for f in lay["fixed"]])
pitch=json.loads((P.parent/"day18-body-reception-and-closed-fit/yaw-laid-factory.json").read_bytes())["rows"]
D.D19D_HeadServoWires.Shape=paths([lay["yaw_factory"]["centreline"],next(m["centreline"] for m in pitch if m["yaw"]==0)]+[j["centreline"] for j in lay["jr"]]+[f["centreline"] for j in lay["jr"] for f in j["fans"]])
s=sh("BR_PAIR_HY").copy();s.translate(V(*lay["yaw_pair_translation"]));D.D19D_YawMatedPair.Shape=s
D.recompute();D.save();write("assembly-interfaces.json",checks)
runpy.run_path(str(P/"views.py"))

