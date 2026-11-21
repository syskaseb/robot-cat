"""Load the localized correction into the one existing GUI and save native views."""
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
SOURCE=HERE.parent/"day21-functional-eye-face/whole-cat21-face.FCStd"
SHA="3026c641fb9aa1d569c62f3d9e11e9c9d8af4a3f9fec287e8f4ebd24217c3a15"
DEST=HERE/"whole-cat21-sculpted-head.FCStd"
KIT=Path(gettempdir())/"robot-cat21-sculpted-head-kit"
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

d=App.ActiveDocument
assert len(App.listDocuments())==1 and len(d.Objects)==610 and not d.isTouched()
assert digest(SOURCE)==SHA
current=Path(d.FileName).resolve()
assert current in (SOURCE.resolve(),DEST.resolve())
ready=json.loads((KIT/"shape-ready.json").read_text("utf-8"))
assert ready["baseline_sha256"]==SHA
if current==SOURCE.resolve():
    assert not DEST.exists()
    d.saveAs(str(DEST))
d.Label="whole-cat21-sculpted-head"

d.openTransaction("Wypukłe czoło, skronie i obie nasady uszu")
try:
    for n,detail in ready["members"].items():
        s=Part.Shape()
        s.importBrepFromString((KIT/(n+".brep")).read_text("ascii"))
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-detail["volume_mm3"])<.02,n
        obj=d.getObject(n)
        obj.Shape=s.cleaned()
        obj.ViewObject.DisplayMode="Shaded"
        obj.ViewObject.Deviation=.07
        obj.ViewObject.AngularDeflection=15.
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise

Gui.runCommand("Std_Save",0)
Gui.updateGui()

view=Gui.activeDocument().activeView()
V=App.Vector

def render(name,normal,centre,height,w,h):
    u=V(*normal)
    u.normalize()
    x=V(0,0,1).cross(u)
    x.normalize()
    view.setCameraOrientation(App.Rotation(x,u.cross(x),u,"ZXY").Q)
    view.fitAll()
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
    assert path.stat().st_size>10000

flags={o.Name:o.ViewObject.Visibility for o in d.Objects}
try:
    for o in d.Objects:
        if flags[o.Name] and not o.Name.startswith("D21_") and o.Name!="D19D_PitchBack":
            o.ViewObject.Visibility=False
    render("front.png",(-1,0,0),(-202,0,161),213,1420,1370)
    render("side.png",(0,1,0),(-196,0,161),213,1370,1370)
finally:
    for o in d.Objects:
        if o.ViewObject.Visibility!=flags[o.Name]:
            o.ViewObject.Visibility=flags[o.Name]

render("three-quarter.png",(-.83,.69,.29),(-188,0,158),216,1510,1320)
view.fitAll()
view.redraw()
Gui.runCommand("Std_Save",0)
Gui.updateGui()

def readback():
    windows=[w for w in Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
             if w.isVisible() and d.Label in w.windowTitle()]
    assert len(windows)==1 and len(App.listDocuments())==1
    assert not windows[0].isWindowModified() and not d.isTouched()
    assert len(d.Objects)==610 and digest(SOURCE)==SHA
    data=dict(document=d.Label,path=DEST.name,sha256=digest(DEST),source_sha256=SHA,
        objects=len(d.Objects),gui_pid=os.getpid(),modified=False,touched=False,
        pending_operation=None,state="IDLE",saved_utc=datetime.now(timezone.utc).isoformat())
    path=HERE/"native-readback.json"
    tmp=path.with_suffix(".tmp")
    with tmp.open("w",encoding="utf-8",newline="\n") as f:
        json.dump(data,f,indent=2)
        f.write("\n")
    os.replace(tmp,path)
    print("21 SCULPT SAVE",data,flush=True)
QtCore.QTimer.singleShot(400,readback)
