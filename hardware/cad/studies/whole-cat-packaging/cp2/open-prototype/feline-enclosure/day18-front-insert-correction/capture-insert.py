"""Keep the new insert, true probes and separate connector allocations in the same native document."""
import FreeCAD as A,FreeCADGui as G,Part,json,hashlib,datetime
from PySide import QtCore
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"front-insert-current.FCStd").resolve()
assert not D.getObject("I2_FFC_NEUTRAL")
r=json.loads((P/"insert-regions.json").read_bytes())
e=json.loads((P/"connected-JR300.json").read_bytes())["poses"]
a=json.loads((P/"audio-space-check.json").read_bytes())
refs=[]
def add(n,shape,color):
    o=D.addObject("PartDesign::Feature",n);o.Shape=shape;o.ViewObject.LineColor=color;o.ViewObject.ShapeColor=color
    o.ViewObject.LineWidth=2;o.ViewObject.DisplayMode="Wireframe";o.ViewObject.Visibility=False;refs.append(o)
def line(ps):return Part.makePolygon([V(*p) for p in ps])
def group(n,arr,col):add(n,Part.makeCompound([line(ps) for ps in arr]),col)
f=next(q for q in r["FFC"] if q["yaw"]==q["pitch"]==0)
t=next(q for q in r["ToF_moving"] if q["yaw"]==q["pitch"]==0)
group("I2_FFC_NEUTRAL",[[v[i] for v in f["corners"]] for i in range(4)],(.1,.65,.88))
group("I2_TOF_ALL_FOUR",[[v[i] for v in t["corners"]] for i in range(4)]+[q["centreline"] for q in r["ToF_header"]+r["ToF_fixed"]],(.24,.7,.26))
group("I2_JR_THREE_UNITS",[q["centreline"] for q in r["JR_factory"]]+[next(q for q in e if q["yaw"]==0)["centreline"]],(.9,.44,.14))
j=r["JR_factory"][1];v=V(*j["key_axis"]);w=v.cross(V(0,0,1));w.normalize();u=w.cross(v);u.normalize()
key=Part.makeBox(30,14,10,V(-15,-7,-5))
key.Placement=A.Placement(V(*j["key_tip"]),A.Rotation(v,w,v.cross(w),"XYZ"))
add("I2_MATED_PITCH_KEY",key,(.88,.62,.17))
group("I2_AUDIO_SEPARATE_CONNECTIONS",[a["USB_AUDIO"]["port_to_port_region"],a["BTL"]["region"]],(.25,.47,.8))
for n in ("F3_DATA500_HORIZONTAL_COMPLETE_UNIT","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD"):refs.append(D.getObject(n))
skins=[D.getObject(n) for n in ("INSERT_FRONT_NEG","INSERT_FRONT_POS","INSERT_REAR_NEG","INSERT_REAR_POS","INSERT_HEAD_BACK","INSERT_OPTICAL_FACE")]+[o for o in D.Objects if o.Name.startswith("F3_PAINT_")]
original={o.Name:o.ViewObject.Visibility for o in skins+refs}
shots=[("front",(-1,0,.035),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
pins=[]
def camera(direction):
    view=G.activeDocument().activeView();v=V(*direction);v.normalize();right=V(0,0,1).cross(v);right.normalize()
    view.setCameraOrientation(A.Rotation(right,v.cross(right),v,"ZXY").Q);view.fitAll();view.redraw()
    return view
def step(i):
    if i==4:
        for o in skins+refs:o.ViewObject.Visibility=original[o.Name]
        camera(shots[2][1]);D.Label="FRONT INSERT - CLOSED OUTLINE TRIAL - ROUTE HOLD";G.runCommand("Std_Save")
        (P/"insert-view-receipt.json").write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),views=pins,objects=len(D.Objects),provisional=True,physical_PASS=False),indent=1)+"\n").encode())
        return
    n,di,inside=shots[i]
    for o in skins:o.ViewObject.Visibility=not inside
    for o in refs:o.ViewObject.Visibility=inside
    view=camera(di)
    def take():
        file=P/("insert-"+n+".png");view.saveImage(str(file),1500,1050,"White")
        pins.append(dict(file=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),inside=inside))
        QtCore.QTimer.singleShot(250,lambda:step(i+1))
    QtCore.QTimer.singleShot(500,take)
A._insert_views=step;D.recompute();step(0)
print("Full insert views scheduled")
