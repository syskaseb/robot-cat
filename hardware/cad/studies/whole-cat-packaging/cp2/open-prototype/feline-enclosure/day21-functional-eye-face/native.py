"""Install the current kit in the single open FreeCAD copy and capture actual views."""
from pathlib import Path
from tempfile import gettempdir
import hashlib
import json
import os
from datetime import datetime,timezone

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore,QtWidgets

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"day20-whole-battery-and-adaptable-protection/20H/whole-cat20H.FCStd"
EXPECTED="40f9ee0753ebc8819f03559ac037af08d82c868e6ecab7a06ed68da312a84c41"
DEST=HERE/"whole-cat21-face.FCStd"
KIT=Path(gettempdir())/"robot-cat21-camera-oem/native-kit"
V=App.Vector
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

d=App.ActiveDocument
assert len(App.listDocuments())==1 and not d.isTouched()
assert sha(SOURCE)==EXPECTED
assert Path(d.FileName).resolve() in (SOURCE.resolve(),DEST.resolve())
if Path(d.FileName).resolve()==SOURCE.resolve():
    assert len(d.Objects)==577 and not DEST.exists()
    d.saveAs(str(DEST))
d.Label="whole-cat21-face"
props=json.loads((KIT/"objects.json").read_bytes())

labels={"D21_Face":"21 | pełna grafitowa maska, policzki i uszy",
        "D21_Nose":"21 | mały miękki nos",
        "D21_Carrier":"21 | nośnik dwóch modułów na zachowanej osi pitch",
        "D21_Camera_OEM":"Raspberry Pi Camera Module 3 Wide NoIR | STEP producenta",
        "D21_ToF":"Pololu 3417 VL53L5CX | przestawiony model źródłowy"}
retired={"D19D_Face","D19D_OpticsCarrier","Camera3_NoIR_Wide","VL53L5CX",
         "C19_FFC190","D19D_ToF","C19_ToFLeadSet","BR_FLANK_TOF",
         "CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT"}
for o in d.Objects:
    if o.Name in retired or o.Name.startswith(("D19D_Ear_","D19D_Iris_","D19D_Pupil_","CAM_primary","CAM_standoff","TOF_primary","TOF_standoff")) or o.Name=="D19D_Nose":
        o.ViewObject.Visibility=False

d.openTransaction("21 twarz z rzeczywistymi czujnikami")
try:
    for name,entry in props.items():
        s=Part.Shape()
        s.importBrepFromString((KIT/(name+".brep")).read_text("ascii"))
        assert s.isValid() and len(s.Solids)==entry["solids"],name
        assert abs(s.Volume-entry["volume"])<.02,name
        o=d.getObject(name) or d.addObject("Part::Feature",name)
        o.Shape=s.cleaned()
        o.Label=labels.get(name,name)
        o.ViewObject.DisplayMode="Shaded" if s.Volume>1 else "Flat Lines"
        colour=tuple(entry["color"])
        o.ViewObject.ShapeColor=colour
        o.ViewObject.LineColor=colour
        o.ViewObject.LineWidth=2.5
        o.ViewObject.Transparency=0
        o.ViewObject.Deviation=.045
        o.ViewObject.AngularDeflection=9.5
        if name in {"D21_Face","D21_Nose","D21_Ear_Inset_L","D21_Ear_Inset_R",
                    "D21_Insert_Cam","D21_Insert_ToF","D21_Rim_Cam","D21_Rim_ToF","D21_Ear_L","D21_Ear_R"}:
            material=o.ViewObject.ShapeMaterial
            material.DiffuseColor=colour
            material.SpecularColor=(0.,0.,0.,0.)
            material.Shininess=0.
            o.ViewObject.ShapeMaterial=material
        if name=="D21_ToF":
            o.ViewObject.DiffuseColor=[(.16,.17,.18) if f.CenterOfMass.x<-218.15 else colour for f in s.Faces]
        if name=="D21_Camera_OEM":
            o.ViewObject.DiffuseColor=[(.105,.123,.151) if f.CenterOfMass.x<-218.5 else colour for f in s.Faces]
        o.ViewObject.Visibility=not name.startswith(("D21_FFC","D21_ToF_Lead","D21_Field"))
    # Display intent only. The inherited tail part and its placement stay intact.
    d.E19_KeyedTail.ViewObject.ShapeColor=(.155,.161,.169)
    d.E19_KeyedTail.ViewObject.DiffuseColor=[(.155,.161,.169)]
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise

v=Gui.activeDocument().activeView()
def rotate_view(direction):
    z=V(*direction);z.normalize()
    x=V(0,0,1).cross(z);x.normalize()
    v.setCameraOrientation(App.Rotation(x,z.cross(x),z,"ZXY").Q)
    return z
def screenshot(name,width,height):
    v.redraw()
    Gui.updateGui()
    path=HERE/name
    v.saveImage(str(path),width,height,"White")
    assert path.stat().st_size>10000

def close_up(name,direction):
    direction=rotate_view(direction)
    v.fitAll()
    node=v.getCameraNode()
    center=V(-202,0,161)
    node.position.setValue(*(center+direction*510))
    node.focalDistance.setValue(510)
    node.height.setValue(218)
    node.nearDistance.setValue(1)
    node.farDistance.setValue(1500)
    screenshot(name,1490,1400)

# The front study is the assembled moving head, with the complete silhouette.
# The close oblique and whole image include the body and fixed joint.
visibility={o.Name:o.ViewObject.Visibility for o in d.Objects}
try:
    for o in d.Objects:
        if visibility[o.Name] and not o.Name.startswith("D21_") and o.Name!="D19D_PitchBack":
            o.ViewObject.Visibility=False
    close_up("21-front.png",(-1,0,0))
finally:
    for o in d.Objects:
        if o.ViewObject.Visibility!=visibility[o.Name]:
            o.ViewObject.Visibility=visibility[o.Name]
close_up("21-close-3q.png",(-1,.47,.15))
rotate_view((-.98,.90,.44))
v.fitAll()
screenshot("21-whole.png",1760,1260)
Gui.runCommand("Std_Save",0)
Gui.updateGui()

def done():
    mdi=[w for w in Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
         if w.isVisible() and d.Label in w.windowTitle()]
    assert len(App.listDocuments())==1 and len(mdi)==1
    assert not mdi[0].isWindowModified() and not d.isTouched()
    assert sha(SOURCE)==EXPECTED
    entry={"saved_utc":datetime.now(timezone.utc).isoformat(),"gui_pid":os.getpid(),
           "document":d.Label,"objects":len(d.Objects),"path":DEST.name,"sha256":sha(DEST),
           "source_sha256":EXPECTED,"modified":False,"touched":False,"pending_operation":None,"state":"IDLE"}
    path=HERE/"native-readback.json";temp=path.with_suffix(".tmp")
    with temp.open("w",encoding="utf-8",newline="\n") as stream:
        json.dump(entry,stream,indent=2);stream.write("\n")
    os.replace(temp,path)
    print("21 READY",entry,flush=True)
QtCore.QTimer.singleShot(400,done)
