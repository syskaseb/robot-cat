"""Open the head first-fit copy in the existing resident FreeCAD window."""
from pathlib import Path
from tempfile import gettempdir
from hashlib import sha256
from datetime import datetime,timezone
import json
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore,QtWidgets

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"day21-sculpted-head-ear-roots/whole-cat21-sculpted-head.FCStd"
DEST=HERE/"whole-cat22-head-first-fit.FCStd"
EXPECTED="18c690a253ac8c0270ca4f9e4a49a492b85cccd51176696f4292b3ae9c53dd98"
KIT=Path(gettempdir())/"robot-cat22-head-kit"
V=App.Vector
def digest(p):
    return sha256(p.read_bytes()).hexdigest()

d=App.ActiveDocument
assert len(App.listDocuments())==1 and not d.isTouched()
assert digest(SOURCE)==EXPECTED
current=Path(d.FileName).resolve()
assert current in (SOURCE.resolve(),DEST.resolve())
if current==SOURCE.resolve():
    assert len(d.Objects)==610 and not DEST.exists()
    d.saveAs(str(DEST))
d.Label="whole-cat22-head-first-fit"
mech=json.loads((KIT/"mechanical-ready.json").read_bytes())
guide=json.loads((KIT/"keeper-ready.json").read_bytes())
assert mech["sha"]==EXPECTED
labels={
 "D21_Face":"22 | maska i zachowane policzki, wewnętrzne mocowania M2",
 "D19D_PitchBack":"22 | tył czaszki, dwa podparte zamki M2",
 "D21_Carrier":"22 | nośnik kamery i ToF, dwa gniazda mocowania maski",
 "D22_CSI_ParkingClip":"22 | stała prowadnica ślizgowa na końcu szyny POST",
 "D22_FFC_Moving":"CSI 300 | obszar zajęty ruchomej taśmy, pozycja neutralna",
 "D22_FFC_Parked":"CSI 300 | nieruchoma kieszeń zapasu na korpusie",
}
stock=[*mech["actors"],*mech["references"],guide["name"],"D22_FFC_Moving","D22_FFC_Parked",
       "D22_FFC_Moving_Trace","D22_FFC_Parked_Trace"]
scope={}
d.openTransaction("22 | zamknięte mocowania, taśma CSI i prowadnica")
try:
    for ob in d.Objects:
        if ob.Name.startswith(("F3_HEAD_BACK_","F3_HEAD_ROOT_","D21_Mask_M2_reference_")) or ob.Name=="D21_FFC_Screen_Unqualified":
            ob.ViewObject.Visibility=False
    for name in stock:
        s=Part.Shape()
        s.importBrepFromString((KIT/(name+".brep")).read_text("ascii"))
        assert s.isValid(),name
        o=d.getObject(name)
        fresh=o is None
        if fresh:o=d.addObject("Part::Feature",name)
        o.Shape=s.cleaned()
        o.Label=labels.get(name,name)
        o.ViewObject.Deviation=.06
        o.ViewObject.AngularDeflection=12.
        if fresh:
            is_path=name.startswith("D22_FFC_")
            is_driver=name.endswith("Driver")
            o.ViewObject.DisplayMode="Flat Lines" if name.endswith("Trace") else "Shaded"
            colour=(.48,.29,.78) if is_path else ((.21,.22,.24) if name==guide["name"] else (.73,.75,.76))
            o.ViewObject.ShapeColor=colour
            o.ViewObject.LineColor=colour
            o.ViewObject.LineWidth=2.8
            o.ViewObject.Visibility=not (is_path or is_driver)
        scope[name]={"solids":len(s.Solids),"volume_mm3":s.Volume}
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise
if current==SOURCE.resolve():
    Gui.runCommand("Std_Save",0)
    Gui.updateGui()

view=Gui.activeDocument().activeView()
def turn(normal):
    u=V(*normal)
    u.normalize()
    x=V(0,0,1).cross(u)
    x.normalize()
    view.setCameraOrientation(App.Rotation(x,u.cross(x),u,"ZXY").Q)
    return u

def image(name,normal,centre,height,w,h):
    u=turn(normal)
    view.fitAll()
    if centre is not None:
        camera=view.getCameraNode()
        camera.position.setValue(*(V(*centre)+u*540))
        camera.focalDistance.setValue(540)
        camera.height.setValue(height)
        camera.nearDistance.setValue(1)
        camera.farDistance.setValue(1400)
    view.redraw()
    Gui.updateGui()
    path=HERE/name
    view.saveImage(str(path),w,h,"White")
    assert path.stat().st_size>10000,name

flags={o.Name:o.ViewObject.Visibility for o in d.Objects}
def restore():
    for o in d.Objects:
        if o.ViewObject.Visibility!=flags[o.Name]:o.ViewObject.Visibility=flags[o.Name]

try:
    for o in d.Objects:
        if flags[o.Name] and not (o.Name.startswith(("D21_","D22_Root_","D22_Back_")) or o.Name=="D19D_PitchBack"):
            o.ViewObject.Visibility=False
    image("22-front.png",(-1,0,0),(-202,0,161),213,1420,1370)
    restore()
    image("22-three-quarter.png",(-.83,.69,.29),(-188,0,158),216,1510,1320)
    image("22-whole.png",(-.9,.86,.41),None,0,1680,1240)
    for name in ("D21_Face","D19D_PitchBack","D21_Ear_L","D21_Ear_R","D21_Ear_Inset_L","D21_Ear_Inset_R",
                 "D21_Rim_Cam","D21_Rim_ToF","D21_Insert_Cam","D21_Insert_ToF","D21_Nose",
                 "F19_ForeCap","E19_UpperYawCover","E19_ForeLid"):
        d.getObject(name).ViewObject.Visibility=False
    for o in d.Objects:
        if o.Name.startswith("D22_Back_"):o.ViewObject.Visibility=False
    for name in ("D22_FFC_Moving","D22_FFC_Parked","CF17_PI_PRIMARY_CSI"):
        d.getObject(name).ViewObject.Visibility=True
    image("22-head-open-csi.png",(-.48,-.44,.90),(-150,-4,147),231,1670,1200)
finally:
    restore()
turn((-.9,.86,.41))
view.fitAll()
view.redraw()
Gui.runCommand("Std_Save",0)
Gui.updateGui()

def readback():
    wins=[w for w in Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
          if w.isVisible() and d.Label in w.windowTitle()]
    assert len(wins)==1 and not wins[0].isWindowModified() and not d.isTouched()
    assert len(App.listDocuments())==1 and digest(SOURCE)==EXPECTED
    result={"state":"IDLE","pending_operation":None,"gui_pid":os.getpid(),
        "objects":len(d.Objects),"path":DEST.name,"sha256":digest(DEST),"source_sha256":EXPECTED,
        "document":d.Label,"modified":False,"touched":False,
        "saved_utc":datetime.now(timezone.utc).isoformat(),"installed":scope}
    f=HERE/"native-readback.json"
    temp=f.with_suffix(".tmp")
    temp.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    os.replace(temp,f)
    print("22 NATIVE SAVED",len(d.Objects),result["sha256"],flush=True)
QtCore.QTimer.singleShot(400,readback)
