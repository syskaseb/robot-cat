"""Capture the revised common shell, current floor and all allocated equipment."""
from pathlib import Path
import json,hashlib,datetime
import FreeCAD as A,FreeCADGui as G
from PySide import QtCore
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert D.FIT_FRONT_COWL.ViewObject.Visibility and D.FIT_AFT_COWL.ViewObject.Visibility
skins=[D.getObject(n) for n in ("FIT_FRONT_COWL","FIT_AFT_COWL","OPEN_BATTERY_DOOR","OPEN_SKULL_BACK","INSERT_OPTICAL_FACE")]+[o for o in D.Objects if o.Name.startswith("F3_PAINT_")]
refs=[D.getObject(n) for n in ("OPEN_NEUTRAL_RIBBON","OPEN_TOF_FIELDS","OPEN_THREE_JR_UNITS","OPEN_KEYS_AND_INSULATED_LANDS","OPEN_AUDIO_CONNECTIONS","OPEN_HANDLAY_OVER_FLOOR","F3_DATA500_HORIZONTAL_COMPLETE_UNIT","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD")]
start={o.Name:o.ViewObject.Visibility for o in skins+refs}
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
receipt=[]
prefix="current" if (P/"audio-port-binding.json").exists() else "fit"
def camera(p):
    v=V(*p);v.normalize();x=V(0,0,1).cross(v);x.normalize()
    vw=G.activeDocument().activeView();vw.setCameraOrientation(A.Rotation(x,v.cross(x),v,"ZXY").Q);vw.fitAll();vw.redraw();return vw
def step(i):
    if i==len(views):
        for o in skins+refs:o.ViewObject.Visibility=start[o.Name]
        camera(views[2][1]);D.Label="Open front first fit - complete portal and separated DATA seats";G.runCommand("Std_Save")
        (P/(prefix+"-view-receipt.json")).write_bytes((json.dumps(dict(views=receipt,native_objects=len(D.Objects),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_PASS=False),indent=1)+"\n").encode())
        return
    label,p,inside=views[i]
    for o in skins:o.ViewObject.Visibility=not inside
    for o in refs:o.ViewObject.Visibility=inside
    vw=camera(p)
    def take():
        f=P/(prefix+"-"+label+".png");vw.saveImage(str(f),1500,1050,"White")
        receipt.append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
        QtCore.QTimer.singleShot(200,lambda:step(i+1))
    QtCore.QTimer.singleShot(450,take)
A._fit_views=step;D.recompute();step(0)
