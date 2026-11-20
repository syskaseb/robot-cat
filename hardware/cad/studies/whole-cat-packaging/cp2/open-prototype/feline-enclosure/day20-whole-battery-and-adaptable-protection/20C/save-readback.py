"""Save via FreeCAD's GUI command, then read the settled live window state."""
from pathlib import Path
import hashlib
import datetime
import json
import os

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

folder=Path(__file__).resolve().parent
doc=App.ActiveDocument
path=Path(doc.FileName)
assert path.resolve()==(folder/"whole-cat20C.FCStd").resolve() and len(doc.Objects)==568

def receipt():
    subwindows=Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
    active=[w for w in subwindows if w.isVisible() and doc.Label in w.windowTitle()]
    assert len(active)==1
    modified=bool(active[0].isWindowModified())
    with path.open("rb") as stream:
        pin=hashlib.file_digest(stream,"sha256").hexdigest()
    data={"path":path.name,"sha256":pin,"document_name":doc.Name,"document_label":doc.Label,
          "object_count":len(doc.Objects),"modified":modified,"touched":bool(doc.isTouched()),
          "gui_pid":os.getpid(),"saved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "pending_operation":None,"state":"IDLE"}
    dest=folder/"20C-native-readback.json"; source=dest.read_bytes()
    tmp=dest.with_suffix(".tmp")
    with tmp.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2);stream.write("\n")
    assert dest.read_bytes()==source
    os.replace(tmp,dest)
    print("20C FINAL NATIVE",data,flush=True)

Gui.runCommand("Std_Save",0)
Gui.updateGui()
QtCore.QTimer.singleShot(650,receipt)