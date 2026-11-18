"""Save the allocation references and four views directly from the single working document."""
from pathlib import Path
import datetime,json,hashlib
import FreeCAD as A,FreeCADGui as G,Part
from PySide import QtCore
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("OPEN_NEUTRAL_RIBBON")
data=json.loads((P/"occupied-layout.json").read_bytes())
refs=[]
def geom(n,s,color):
    o=D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=color
    o.ViewObject.LineWidth=2;o.ViewObject.DisplayMode="Wireframe";o.ViewObject.Visibility=False;refs.append(o)
def tracks(n,lines,color):
    geom(n,Part.makeCompound([Part.makePolygon([V(*p) for p in line]) for line in lines]),color)
for k,n,col in [("FFC","OPEN_NEUTRAL_RIBBON",(.12,.62,.9)),("ToF_moving","OPEN_TOF_FIELDS",(.15,.72,.2))]:
    q=next(q for q in data[k] if q["yaw"]==q["pitch"]==0)
    lines=[[r[i] for r in q["corners"]] for i in range(4)]
    if k=="ToF_moving":lines += [q["centreline"] for q in data["ToF_header"]+data["ToF_fixed"]]
    tracks(n,lines,col)
ext=next(q for q in data["extension"] if q["yaw"]==0)
tracks("OPEN_THREE_JR_UNITS",[q["centreline"] for q in data["JR_factory"]]+[ext["centreline"]],(.95,.51,.12))
hardware=[]
for j in data["JR_factory"]:
    t=V(*j["key_axis"]);w=t.cross(V(0,0,1));w.normalize()
    s=Part.makeBox(30,14,10,V(-15,-7,-5));s.Placement=A.Placement(V(*j["key_tip"]),A.Rotation(t,w,t.cross(w),"XYZ"));hardware.append(s)
for x,y,z in ext["three_lap_centers"]:hardware.append(Part.makeBox(26,6,6,V(x-13,y-3,z-3)))
geom("OPEN_KEYS_AND_INSULATED_LANDS",Part.makeCompound(hardware),(.9,.62,.18))
usb=[[6,21,107],[10,21,107],[10,57,107],[10,57,135],[41,57,135],[41,74,135],[62,74,135],[62,74,171],[62,69,171]]
btl=[[96,-38,150],[104,-38,150],[104,-57,150],[117,-57,150],[117,-57,171]]
def regional(line):return sum(sum(abs(a-b) for a,b in zip(q,r)) for q,r in zip(line,line[1:]))
tracks("OPEN_AUDIO_CONNECTIONS",[usb,btl],(.53,.45,.89))
(P/"audio-connections.json").write_bytes((json.dumps(dict(USB_AUDIO=dict(free_region=usb,rectilinear_mm=regional(usb),ends="Pi USB-A + independent ReSpeaker USB-C full field, raw jacket, bend and installed slack unknown"),
    BTL=dict(free_region=btl,rectilinear_mm=regional(btl),ends="Dedicated OUT+ and OUT- amplifier pads to basket, terminal and strip lengths unknown"),
    DATA500=dict(full_stock=500,boot_each=26,free_stock=448,minimum_bend=30,capacity_OD=6.8,route="fixed-source rise to separate front upper layer, removable audio behind its fixed-port approaches"),physical_PASS=False),indent=1)+"\n").encode())
for n in ["F3_DATA500_HORIZONTAL_COMPLETE_UNIT","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD","OPEN_HANDLAY_OVER_FLOOR"]:refs.append(D.getObject(n))
skins=[D.getObject(n) for n in ["OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_BATTERY_DOOR","OPEN_SKULL_BACK","INSERT_OPTICAL_FACE"]]+[o for o in D.Objects if o.Name.startswith("F3_PAINT_")]
initial={o.Name:o.ViewObject.Visibility for o in skins+refs}
shots=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
receipt=[]
def camera(p):
    v=V(*p);v.normalize();x=V(0,0,1).cross(v);x.normalize()
    view=G.activeDocument().activeView();view.setCameraOrientation(A.Rotation(x,v.cross(x),v,"ZXY").Q);view.fitAll();view.redraw();return view
def step(i):
    if i==len(shots):
        for o in skins+refs:o.ViewObject.Visibility=initial[o.Name]
        camera(shots[2][1]);D.Label="Open front assembly - portal and separate data layer";G.runCommand("Std_Save")
        (P/"view-receipt.json").write_bytes((json.dumps(dict(views=receipt,objects=len(D.Objects),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_PASS=False),indent=1)+"\n").encode())
        return
    n,v,inside=shots[i]
    for o in skins:o.ViewObject.Visibility=not inside
    for o in refs:o.ViewObject.Visibility=inside
    view=camera(v)
    def take():
        f=P/("assembly-"+n+".png");view.saveImage(str(f),1500,1050,"White");receipt.append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
        QtCore.QTimer.singleShot(160,lambda:step(i+1))
    QtCore.QTimer.singleShot(400,take)
D.recompute();A._open_views=step;step(0)
