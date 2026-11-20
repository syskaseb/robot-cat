"""Build, save, and export only the 20C inlet and MTA assembly changes in FreeCAD."""
from pathlib import Path
from runpy import run_path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
import MeshPart
from PySide import QtWidgets

folder=Path(__file__).resolve().parent
root=folder.parent
native=folder/"whole-cat20C.FCStd"
g=run_path(str(folder/"geometry.py"))
l=run_path(str(folder/"layout.py"))
box,fuse,bbox,overlap=[g[k] for k in ("box","fuse","bbox","overlap")]
V=App.Vector

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()

def write_json(name,data):
    out=folder/name
    tmp=out.with_suffix(".tmp")
    with tmp.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(data,stream,indent=2,ensure_ascii=False);stream.write("\n")
    os.replace(tmp,out)

def add(name,label,shape,color,visible=True):
    obj=doc.addObject("Part::Feature",name)
    obj.Label=label;obj.Shape=shape
    obj.ViewObject.ShapeColor=color
    obj.ViewObject.LineColor=(.16,.19,.21)
    obj.ViewObject.Visibility=visible
    return obj

def replace(name,shape,label=None):
    obj=doc.getObject(name)
    obj.Shape=shape
    if label:
        obj.Label=label
    assert max(abs(x-y) for x,y in zip(bbox(obj.Shape),bbox(shape)))<.001,(name,bbox(obj.Shape),bbox(shape))
    return obj

def geometry_check(name,shape):
    if shape.isNull() or not shape.isValid() or len(shape.Solids)!=1:
        raise RuntimeError(f"{name}: expected one valid solid")

doc=App.ActiveDocument
assert Path(doc.FileName).resolve()==native.resolve() and len(doc.Objects)==568
ghost=doc.C20_Pack_XT60_Stroke
wire_objects=[doc.getObject(n) for n in ("C20_BAT_Leads_Indicative","C20_Inlet_W075","C20_F0_Outlet_Ideal","C20_Protected_and_Return")]
view=Gui.activeDocument().activeView()
def camera(v):
    z=V(*v);z.normalize();x=V(0,0,1).cross(z);x.normalize()
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,"ZXY").Q)
    view.fitAll();view.redraw();Gui.updateGui()
def render(path,v):
    camera(v)
    view.saveImage(str(folder/path),1600,1080,"White")
render("20C-closed.png",(.60,.99,.50))
opened_names=("E19_ForeLid","E19_RearLid","F19_ForeCap","F19_RearCap",
              "E19_ReSpeakerSource","Speaker","E19_BUS_PCB","E19_BUS_population",
              "E19_BatteryDoor","C20_BatteryUpperBridge","C20_Bridge_M3x12_1",
              "C20_Bridge_M3x12_2","C20_Bridge_M3_Nut_1","C20_Bridge_M3_Nut_2")
before={name:doc.getObject(name).ViewObject.Visibility for name in opened_names}
for name in opened_names:doc.getObject(name).ViewObject.Visibility=False
for obj in wire_objects+[ghost]:obj.ViewObject.Visibility=True
try:
    render("20C-open-service.png",(.42,.84,1.22))
finally:
    for name,visible in before.items():doc.getObject(name).ViewObject.Visibility=visible
    for obj in wire_objects+[ghost]:obj.ViewObject.Visibility=False
    camera((.60,.99,.50))
doc.recompute()
doc.save()
mdi=Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
active=[q for q in mdi if q.isVisible() and doc.Label in q.windowTitle()]
modified=bool(active[0].isWindowModified()) if len(active)==1 else bool(doc.isTouched())
write_json("20C-native-readback.json",{
    "path":native.name,"sha256":digest(native),"document_name":doc.Name,
    "document_label":doc.Label,"object_count":len(doc.Objects),"modified":modified,
    "touched":doc.isTouched(),"gui_pid":os.getpid(),"saved_utc":datetime.now(timezone.utc).isoformat(),
    "pending_operation":None,"state":"IDLE"
})
print("20C NATIVE IDLE",doc.FileName,len(doc.Objects),modified,flush=True)
