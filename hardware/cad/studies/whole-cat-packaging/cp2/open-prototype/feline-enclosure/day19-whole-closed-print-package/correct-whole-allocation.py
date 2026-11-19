"""Coherent correction: operator bay, control edge, full port work area and one rounded base silhouette."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json,math,datetime,shutil,traceback,hashlib
import FreeCAD as A,FreeCADGui as G,Part
from PySide import QtCore
P=Path(__file__).parent;D=A.getDocument("cat19");V=A.Vector
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=1)+"\n").encode())
wr("correction.state.json",dict(phase="running",utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
if not (P/"first-low-whole.FCStd").exists():shutil.copyfile(P/"whole-cat19.FCStd",P/"first-low-whole.FCStd")
for n in ("front","side","three-quarter","interior"):
    if (P/(n+".png")).exists() and not (P/("first-"+n+".png")).exists():shutil.copyfile(P/(n+".png"),P/("first-"+n+".png"))
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def pref(*s):return [o.Name for o in D.Objects if o.Name.startswith(s)]
moves=[]
def move(names,target,rotation=None):
    os=[D.getObject(n) for n in names if D.getObject(n)]
    primary=os[0];before={}
    for o in os:
        b=o.Shape.BoundBox;before[o.Name]=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    if rotation:
        t=A.Placement(V(),rotation)
        for o in os:o.Placement=t.multiply(o.Placement)
    b=primary.Shape.BoundBox;delta=V(*target)-V(b.XMin,b.YMin,b.ZMin)
    for o in os:o.Placement.Base+=delta
    moves.append(dict(primary=primary.Name,all_members=[o.Name for o in os],before=before,target_primary_min=target))
def add(n,s,col=(.17,.18,.20),kind="PROVISIONAL_CHANGED_WHOLE_INTERFACE"):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode="Shaded";o.ViewObject.Visibility=True
    if "EvidenceKind" not in o.PropertiesList:o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=kind;return o
def source(n):
    with ZipFile(P/"whole19.FCStd") as z:
        e=ET.fromstring(z.read("Document.xml")).find('./ObjectData/Object[@name="'+n+'"]/Properties/Property[@name="Shape"]/Part')
        s=Part.Shape();s.importBrepFromString(z.read(e.get("file")).decode());return s
# Rear operator bay keeps whole cases, keys, nuts and washers together.
move(["S0_body"]+[n for n in pref("S0_") if n!="S0_body"],[167,-28,57],A.Rotation(V(0,0,1),-90))
move(["OP_S1_PRIMARY_CASE_CONSERVATIVE"]+[n for n in pref("OP_S1_") if n!="OP_S1_PRIMARY_CASE_CONSERVATIVE"],[156,-75,77])
move(["Monitor_MOD05015"]+pref("OP_MONITOR_"),[156,34,79])
# The complete low bank remains one tier; the negative branch leaves the whole JR receiving station open.
for i in range(6):
    move(["Motor_ATO4A__1_"+str(i)],[-74+74*(i%3),-95+27*(i//3),77])
# Relocate the whole soldered pair onto a positive rear edge.
board=["PCA9685_Adafruit815_PCB","E1_populated_prototype_board"]+pref("CB_PCA_","F3_E1_CAP_")
move(board,[75,40,118],A.Rotation(V(1,0,0),-90))
move(["MAIN_Pololu4853"]+pref("CB_MAIN_","F3_MAIN_"),[86,-36,92])
move(["AUX_Pololu4092"]+pref("CB_AUX_","F3_AUX_"),[50,-42,95])
move(["BNO085"]+pref("CB_BNO_"),[39,13,106])
# This reversal points the complete BUS mating field into the dedicated outer port bay.
move(["BUS25514_installed","D18C_DATA_BUS_FULL26_PROJECT_BOOT"]+pref("CB_BUS_","CF17_BUS_CSK"),[4,22,123],A.Rotation(V(0,0,1),180))
move(["ReSpeakerLite_on_REMOVABLE_back"]+pref("HB_MIC_"),[-4,-18,125])
move(["MAX98357A_amp"]+pref("CB_AMP_"),[79,-47,119])
# Full WAGO housings have a normalized 30x19x9 orientation. Source poses had three different rotations.
bank=sorted(pref("WAGO415_"))
stations=[(x,-76,111) for x in (-103,-71,-39,57,89)]+[(125,-76,122),(157,-76,122),(125,-55,122)]
stations += [(x,54,111) for x in (-103,-71,57,89)]+[(125,65,122),(157,65,122),(125,44,122)]
assert len(stations)==len(bank)==15
for n,p in zip(bank,stations):
    b=D.getObject(n).Shape.BoundBox;rot=A.Rotation(V(0,1,0),90) if b.ZLength>b.XLength else None
    move([n],list(p),rot)
# Two power junctions occupy a shallow front lower well.
rot=A.Rotation(V(0,0,1),90).multiply(A.Rotation(V(1,0,0),90))
move(["WAGO615_power_0_0"],[-40,-58,52],rot)
move(["WAGO615_power_0_1"],[-16,-58,52],rot)
move(["PBAY_F_TY"],[-65,25,50])
# Both short factory-tail pairs are unchanged in their complete relative poses.
# The full JR300 insulated junction station is now below the new curved shoulder.
move(["BR_FLANK_THREE_LAPS"],[-52,39.220664,127.5])
# Broader moving skull accommodates the full upper ToF return instead of cutting off a cheek.
def ell(c,r):
    m=A.Matrix();m.A11,m.A22,m.A33=r
    s=Part.makeSphere(1).transformGeometry(m);s.translate(V(*c));return s
outer_head=ell((-166,0,145),(75,90,72));inner_head=ell((-166,0,145),(73.6,88.6,70.6))
back=outer_head.cut(inner_head).common(box(-171,-100,65,92,200,175))
bosses=[]
for y in (-73,73):
    b=Part.makeCylinder(4.1,12,V(-165,y,145),V(1,0,0)).cut(Part.makeCylinder(1.1,12,V(-165,y,145),V(1,0,0)))
    b=b.fuse(box(-165,min(y,y/abs(y)*89)-2,141,6,20,8))
    bosses.append(b)
back=back.multiFuse(bosses).removeSplitter()
o=add("D19_BROAD_SKULL_BACK",back);D.BR_PARTED_SKULL_BACK.ViewObject.Visibility=False
# Restore the real eye-face colors lost during FreeCAD's view-provider copy.
mask=D.BR_COMMON_OPTICAL_MASK;colors=[]
for f in mask.Shape.Faces:
    color=(.16,.17,.19,1.);b=f.BoundBox
    if b.XMax<-174 and b.ZMin>139 and b.ZMax<181:
        vs,tri=f.tessellate(.12)
        if tri:
            a,k,c=max(tri,key=lambda t:(vs[t[1]]-vs[t[0]]).cross(vs[t[2]]-vs[t[0]]).Length)
            p=(vs[a]+vs[k]+vs[c])/3;side=1 if p.y>0 else -1
            rho=lambda w,h:((p.y-side*43)/w)**2+((p.z-160)/h)**2
            if rho(16,19)<1:color=(.008,.009,.012,1.) if rho(13.4,16.4)<1 else (.72,.50,.16,1.)
    colors.append(color)
mask.ViewObject.DiffuseColor=colors
# Triangular ears form actual shell material on the wider skull.
ears=[]
for side in (-1,1):
    y=side*52
    sections=[]
    for x in (-184,-176):
        pts=[V(x,y-side*19,193),V(x,y+side*20,193),V(x,y+side*10,247)]
        sections.append(Part.makePolygon(pts+[pts[0]]))
    ears.append(Part.makeLoft(sections,True,True))
add("D19_SKULL_EARS",Part.makeCompound(ears))
# Rounded belly now includes the existing chassis, rather than showing a separate platform.
def profile(q,d):
    x,w,lo,hi=q;cy=(lo+hi)/2;ry=w-d;rz=(hi-lo)/2-d;k=.55228475;edges=[]
    for ps in [[(0,rz),(k*ry,rz),(ry,k*rz),(ry,0)],[(ry,0),(ry,-k*rz),(k*ry,-rz),(0,-rz)],[(0,-rz),(-k*ry,-rz),(-ry,-k*rz),(-ry,0)],[(-ry,0),(-ry,k*rz),(-k*ry,rz),(0,rz)]]:
        c=Part.BezierCurve();c.setPoles([V(x,y,cy+z) for y,z in ps]);edges.append(c.toShape())
    return Part.Wire(edges)
rows=[(-145,35,62,126),(-118,86,12,149),(-87,104,-3,163),(-20,104,-3,169),(60,104,-3,171),(125,99,0,170),(174,96,14,166),(207,59,30,155),(222,12,65,124)]
body=Part.makeLoft([profile(q,0) for q in rows],True,True);inner=Part.makeLoft([profile(q,1.5) for q in rows],True,True)
skin=body.cut(inner)
# A coarse whole-head motion socket is reserved together with the skull.
socket=ell((-163,0,145),(80,105,77))
skin=skin.cut(socket)
for x in (-75,125):
    for side in (-1,1):
        skin=skin.cut(box(x-34,38 if side>0 else -120,-12,68,82,54))
# Functional operator apertures and whole tail-Y socket.
for n in ("S0_neck","OP_S1_PRIMARY_STEM"):
    b=D.getObject(n).Shape.BoundBox
    skin=skin.cut(box(b.XMin-1,b.YMin-12,b.ZMin-1,b.XLength+2,b.YLength+24,b.ZLength+2))
skin=skin.cut(box(128,-24,120,48,48,55))
for n,b in [("D19_ROUNDED_FORE_COWL",box(-160,-120,-10,180,240,210)),("D19_ROUNDED_REAR_COWL",box(20,-120,-10,210,240,210))]:
    D.getObject(n).Shape=skin.common(b)
# Trim our new flat frame to the same body envelope, preserving all bought base parts.
for n in ("D19_LOW_FORE_CARRIER","D19_LOW_REAR_CARRIER"):D.getObject(n).Shape=D.getObject(n).Shape.common(body)
# A light inner neck wall is rooted to the fixed source portal, inside the moving head.
neck=ell((-130,0,101),(33,39,48)).cut(ell((-130,0,101),(31.5,37.5,46.5))).common(box(-145,-44,56,62,88,89))
add("D19_FIXED_INNER_NECK",neck)
# Body storage allocations include complete stock and both separate USB ends.
data=D.D19_DATA_STORAGE_LAYER;data.Shape=box(-20,-12,112,100,96,10);data.OccupancyNote="Whole DATA500=26+85 Pi approach+285 laid spiral reserve+78 BUS approach+26. OD6.8/R30. Full approach and actual port/cooling qualification pending."
data.ViewObject.Visibility=False
for n in ("D19_MIC_FULL_HEIGHT_RESERVE","D19_AUX_POPULATED_9P5_RESERVE"):
    o=D.getObject(n);o.ViewObject.Visibility=False
mic=D.ReSpeakerLite_on_REMOVABLE_back.Shape.BoundBox;D.D19_MIC_FULL_HEIGHT_RESERVE.Shape=box(mic.XMin,mic.YMin,mic.ZMin,mic.XLength,mic.YLength,10.93)
aux=D.AUX_Pololu4092.Shape.BoundBox;D.D19_AUX_POPULATED_9P5_RESERVE.Shape=box(aux.XMin,aux.YMin,aux.ZMin,aux.XLength,aux.YLength,9.5)
# Affected old flexible drawings are labelled explicitly; new body endpoints require new length plans.
for n in ("BR_FLANK_300","BR_FLANK_TOF"):
    D.getObject(n).EvidenceKind="ILLUSTRATIVE_OLD_BODY_ROUTE_CHANGED_ENDPOINT_UNQUALIFIED"
records=[]
for o in D.Objects:
    if hasattr(o,"Shape") and not o.Shape.isNull():
        b=o.Shape.BoundBox;records.append(dict(name=o.Name,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume=o.Shape.Volume,kind=getattr(o,"EvidenceKind","source")))
wr("corrected-low-actors.json",records)
wr("whole-correction.json",dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cause="Full old operator cases and complete port fields occupy the low control layer. Separate operator bay, rear control edge and connected front port area.",moves=moves,body_profiles=rows,head_axes=[75,90,72],head_wall=1.4,
    head_retention=dict(source_roots="two front pitch M2x12 retained",back="two full source M2x16 positions; radial ribs from original Y+/-73 bosses to wider back; parting/material connection still requires exact gate",back_solids=len(back.Solids)),
    full_DATA_budget=[26,85,285,78,26],source_ReSpeaker_height=10.93,physical_PASS=False,whole_accepted=False))
D.recompute();D.save()
# Capture the same physical occupancy and actual material in every exterior view.
skins=["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","D19_BROAD_SKULL_BACK","BR_COMMON_OPTICAL_MASK","D19_SKULL_EARS","D19_FIXED_INNER_NECK"]
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
captures=[]
def cam(p):
    z=V(*p);z.normalize();x=V(0,0,1).cross(z);x.normalize();v=G.getDocument(D.Name).activeView()
    v.setCameraOrientation(A.Rotation(x,z.cross(x),z,"ZXY").Q);v.fitAll();v.redraw();return v
def step(i):
    try:
        if i==len(views):
            for n in skins:D.getObject(n).ViewObject.Visibility=True
            cam(views[2][1]);D.recompute();D.save()
            wr("whole-view-receipt.json",dict(views=captures,objects=len(D.Objects),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),saved=True,physical_PASS=False))
            wr("correction.state.json",dict(phase="idle",saved=True));return
        name,p,inside=views[i]
        for n in skins:D.getObject(n).ViewObject.Visibility=not inside
        v=cam(p);G.updateGui();v.saveImage(str(P/(name+".png")),1500,1050,"White");captures.append(dict(file=name+".png",interior=inside))
        QtCore.QTimer.singleShot(650,lambda:step(i+1))
    except Exception:(P/"correction-error.txt").write_bytes(traceback.format_exc().encode())
step(0)
