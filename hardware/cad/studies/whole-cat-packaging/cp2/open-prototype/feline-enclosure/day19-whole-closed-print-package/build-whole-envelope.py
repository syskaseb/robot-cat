"""Whole shell and accessible common layers for the first occupied-layout gate."""
import json,math,datetime,traceback
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import FreeCAD as A,FreeCADGui as G,Part
from PySide import QtCore
P=Path(__file__).parent;D=A.getDocument("cat19");V=A.Vector
assert D and Path(D.FileName).resolve()==(P/"whole-cat19.FCStd").resolve()
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=1)+"\n").encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def add(n,s,color=(.17,.18,.20),kind="PROVISIONAL_WHOLE_INTERFACE"):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.DisplayMode="Shaded"
    if "EvidenceKind" not in o.PropertiesList:o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=kind
    return o
def source(n):
    with ZipFile(P/"whole19.FCStd") as z:
        xml=ET.fromstring(z.read("Document.xml"))
        e=xml.find('./ObjectData/Object[@name="'+n+'"]/Properties/Property[@name="Shape"]/Part')
        s=Part.Shape();s.importBrepFromString(z.read(e.get("file")).decode());return s
def profile(q,d):
    x,w,lo,hi=q;cy=(lo+hi)/2;ry=w-d;rz=(hi-lo)/2-d
    edges=[];k=.55228475
    for ps in [[(0,rz),(k*ry,rz),(ry,k*rz),(ry,0)],[(ry,0),(ry,-k*rz),(k*ry,-rz),(0,-rz)],[(0,-rz),(-k*ry,-rz),(-ry,-k*rz),(-ry,0)],[(-ry,0),(-ry,k*rz),(-k*ry,rz),(0,rz)]]:
        c=Part.BezierCurve();c.setPoles([V(x,y,cy+z) for y,z in ps]);edges.append(c.toShape())
    return Part.Wire(edges)
def loft(rows,d):return Part.makeLoft([profile(q,d) for q in rows],True,True)
# Existing open source portal carries yaw bearings around the case exit band.
add("D19_OPEN_GIMBAL_LOAD_PORTAL",source("OPEN_PORTAL_AND_FLOOR"),(.28,.39,.41),"SOURCE_OPEN_PORTAL_PENDING_CHANGED_NEIGHBORS")
# Low shared floor at the retained P01 bearing planes. It is split for printing.
floor=box(-108,-95,45.52,279,190,3)
floor=floor.cut(box(-102,-89,45.42,267,178,3.2))
for x in (-80,-38,26,120):floor=floor.fuse(box(x,-95,45.52,6,190,3))
for y in (-25.5,19.5):floor=floor.fuse(box(-86,y,45.52,214,6,3))
for side in (-1,1):
    y=-95 if side<0 else 44
    shelf=box(-108,y,74,225,51,3)
    for x in (-106,-33,41,113):shelf=shelf.fuse(box(x,y+2,48.52,4,47,25.48))
    floor=floor.fuse(shelf)
add("D19_LOW_FORE_CARRIER",floor.common(box(-150,-110,40,170,220,80)),(.28,.39,.41))
add("D19_LOW_REAR_CARRIER",floor.common(box(20,-110,40,165,220,80)),(.28,.39,.41))
# The optical front and mechanism stay source-bound during this first whole gate.
# Current rear material and ToF failure remain visible in the receipt.
rows=[(-139,39,72,135),(-117,86,49,151),(-87,104,46,163),(-20,104,46,169),(60,104,46,171),(119,96,49,170),(151,73,64,166),(174,15,95,141)]
outer=loft(rows,0);inner=loft(rows,1.6);skin=outer.cut(inner)
# Source neck opening accommodates the moving head envelope; its final overlap
# and cable-bearing cheek require the connected-section gate.
skin=skin.cut(box(-145,-43,93,42,86,125))
# Real operator access: current whole S0/S1 retained, apertures follow their current stems.
for n,margin in [("S0_neck",1),("OP_S1_PRIMARY_STEM",1)]:
    o=D.getObject(n)
    if o:
        b=o.Shape.BoundBox
        skin=skin.cut(box(b.XMin-margin,b.YMin-12,b.ZMin-margin,b.XLength+2*margin,b.YLength+24,b.ZLength+2*margin))
skin=skin.cut(box(128,-24,120,65,48,60))
add("D19_ROUNDED_FORE_COWL",skin.common(box(-150,-120,30,170,240,180)))
add("D19_ROUNDED_REAR_COWL",skin.common(box(20,-120,30,165,240,180)))
# Mic requires the full 10.93 mm delivered-revision allowance.
mic=D.ReSpeakerLite_on_REMOVABLE_back.Shape.BoundBox
m=add("D19_MIC_FULL_HEIGHT_RESERVE",box(mic.XMin,mic.YMin,mic.ZMin,mic.XLength,mic.YLength,max(10.93,mic.ZLength)),(.58,.38,.23),"SUPPLIER_ENVELOPE_REVISION_FIT_UNKNOWN")
m.ViewObject.Transparency=70;m.ViewObject.Visibility=False
# Preserve full AUX populated height, explicitly separate from the bare source PCB.
b=D.AUX_Pololu4092.Shape.BoundBox
m=add("D19_AUX_POPULATED_9P5_RESERVE",box(b.XMin,b.YMin,b.ZMin,b.XLength,b.YLength,9.5),(.58,.38,.23),"PROJECT_POPULATED_RESERVE")
m.ViewObject.Transparency=70;m.ViewObject.Visibility=False
# Connected head fields retain source free-span families because head and Pi did not move.
for n in ("OPEN_NEUTRAL_RIBBON","BR_FLANK_PITCH","BR_YAW_STATIC","BR_FLANK_300","BR_FLANK_TOF"):
    o=add(n,source(n),(.70,.49,.18),"SOURCE_FLEX_REFERENCE_AFFECTED_NEIGHBORS_PENDING")
    o.ViewObject.LineWidth=2
# New common storage layer for the complete DATA500, above Pi and before audio.
# Its explicit length allocation is checked in the occupied-section stage.
regions=[
("D19_DATA_STORAGE_LAYER",[-109,-41,129,110,82,8],"DATA500/OD6.8/R30; full500=26+448+26; shape and both approaches pending"),
("D19_BODY_CONTROL_TRUNK",[-19,-35,103,129,70,7],"PCA-E1/JP3/ToF4 plus independent PWM/power ends; counts and branch budgets pending"),
("D19_SIDE_BUNDLE_NEG",[-107,-91,114,224,21,12],"6 complete fuse units, 8 WAGO/body ends; separate insulated power and signal groups"),
("D19_SIDE_BUNDLE_POS",[-107,74,114,224,21,12],"6 complete fuse units, 7 WAGO/body ends plus independent leg E2 branches"),
("D19_AUDIO_USB_BTL_LAYER",[1,-43,132,110,86,7],"USB_AUDIO separate unknown stock; full A/C mates plus AMP-to-speaker BTL"),
]
for n,b,note in regions:
    o=add(n,box(*b),(.81,.50,.17),"OCCUPIED_ALLOCATION_PENDING_CAPACITY")
    o.addProperty("App::PropertyString","OccupancyNote");o.OccupancyNote=note;o.ViewObject.Transparency=70;o.ViewObject.Visibility=False
prints=[o for o in D.Objects if o.Name.startswith(("D19_LOW_","D19_ROUNDED_"))]
receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),body_profiles=rows,
             mass_baseline_g=[1853.4,2593.4],new_floor_and_shell_full_PETG_g=sum(o.Shape.Volume for o in prints)*.00127,
             density_g_cm3=1.27,print_mass_scope="These four new carriers/cowls only. Retained legs, head, portal and other supports still enter P.",
             source_bom="../day19-source-bom-budgets/source-budget.json",physical_PASS=False,whole_accepted=False)
wr("whole-envelope-receipt.json",receipt)
D.recompute();D.save()
skin_names=["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","BR_PARTED_SKULL_BACK","BR_COMMON_OPTICAL_MASK"]
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
receipts=[]
def camera(p):
    z=V(*p);z.normalize();x=V(0,0,1).cross(z);x.normalize()
    v=G.getDocument(D.Name).activeView();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,"ZXY").Q);v.fitAll();v.redraw();return v
def step(i):
    try:
        if i==len(views):
            for n in skin_names:D.getObject(n).ViewObject.Visibility=True
            camera(views[2][1]);D.recompute();D.save()
            wr("whole-view-receipt.json",dict(views=receipts,objects=len(D.Objects),saved=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_PASS=False))
            wr("whole19.state.json",dict(phase="idle",saved=True));return
        name,p,inside=views[i]
        for n in skin_names:D.getObject(n).ViewObject.Visibility=not inside
        v=camera(p);G.updateGui();v.saveImage(str(P/(name+".png")),1500,1050,"White")
        receipts.append(dict(file=name+".png",interior=inside))
        QtCore.QTimer.singleShot(650,lambda:step(i+1))
    except Exception:
        (P/"native-error.txt").write_bytes(traceback.format_exc().encode())
step(0)
