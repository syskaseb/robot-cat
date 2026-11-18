"""Capture installed exterior and open assembly, preserving actual equipment visibility."""
from pathlib import Path
import json,hashlib,datetime
import FreeCAD as A,FreeCADGui as G
from PySide import QtCore
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
skin=[D.getObject(n) for n in ("BR_RECESSED_CHEST","BR_ROUNDED_RUMP","BR_OVERLAP_SKULL_BACK","BR_COMMON_OPTICAL_MASK","OPEN_BATTERY_DOOR")]
refs=[D.getObject(n) for n in ("BR_PAIR_HY","BR_FLANK_HP_PAIR","BR_FLANK_THREE_LAPS","BR_YAW_STATIC","BR_FLANK_PITCH","BR_FLANK_300","BR_FLANK_TOF","OPEN_NEUTRAL_RIBBON","F3_DATA500_HORIZONTAL_COMPLETE_UNIT","OPEN_AUDIO_CONNECTIONS","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD")]
assert all(skin+refs) and all(o.ViewObject.Visibility for o in skin)
v0={o.Name:o.ViewObject.Visibility for o in skin+refs}
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
receipt=[]
def camera(p):
    z=V(*p);z.normalize();x=V(0,0,1).cross(z);x.normalize()
    v=G.activeDocument().activeView();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,"ZXY").Q);v.fitAll();v.redraw();return v
def step(i):
    if i==len(views):
        for o in skin+refs:o.ViewObject.Visibility=v0[o.Name]
        camera(views[2][1]);G.runCommand("Std_Save")
        (P/"body-view-receipt.json").write_bytes((json.dumps(dict(views=receipt,objects=len(D.Objects),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_PASS=False),indent=1)+"\n").encode());return
    name,p,inside=views[i]
    for o in skin:o.ViewObject.Visibility=not inside
    for o in refs:o.ViewObject.Visibility=inside
    v=camera(p)
    def take():
        f=P/(name+".png");v.saveImage(str(f),1500,1050,"White")
        receipt.append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
        QtCore.QTimer.singleShot(250,lambda:step(i+1))
    QtCore.QTimer.singleShot(500,take)
A._br_views=step;D.recompute();step(0)
