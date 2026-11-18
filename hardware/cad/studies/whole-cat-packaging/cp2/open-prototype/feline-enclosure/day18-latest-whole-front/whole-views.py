"""Four same-state views; only the detachable skins come off for interior inspection."""
from pathlib import Path
from PySide import QtCore
import json, datetime, hashlib, math
import FreeCAD as A
import FreeCADGui as G
import Part
P=Path(__file__).parent
D=A.ActiveDocument
V=A.Vector
assert Path(D.FileName).resolve()==(P/"whole-front.FCStd").resolve()
assert D.getObject("FRONT18_REAR_POS_PANEL")
assert not D.getObject("FRONT18_FFC_NEUTRAL")
flex=json.loads((P/"front-flex.json").read_bytes())
refs=[]
def ref(n,s,c):
    o=D.addObject("PartDesign::Feature",n)
    o.Shape=s
    o.ViewObject.LineColor=c
    o.ViewObject.ShapeColor=c
    o.ViewObject.LineWidth=2
    o.ViewObject.DisplayMode="Wireframe"
    o.ViewObject.Visibility=False
    refs.append(o)
def wire(ps):
    return Part.makePolygon([V(*p) for p in ps])
f=next(q for q in flex["FFC"] if q["yaw"]==q["pitch"]==0)
ref("FRONT18_FFC_NEUTRAL",Part.makeCompound([wire([c[i] for c in f["corners"]]) for i in range(4)]),(.15,.67,.8))
t=next(q for q in flex["ToF"] if q["yaw"]==q["pitch"]==0)
s=V(*t["centreline"][0]);b=V(*t["centreline"][-1]);h=V(b.x-s.x,b.y-s.y,0);h.normalize()
normal=V(-h.y,h.x,0)
p=[V(*q) for q in t["centreline"]]
sides=[Part.makePolygon([v+normal*(a*5.2)+V(0,0,c*1.45) for v in p]) for a,c in [(-1,-1),(1,-1),(1,1),(-1,1)]]
ref("FRONT18_TOF4_NEUTRAL",Part.makeCompound(sides),(.2,.7,.28))
# JR is reserved as three separate units. The loops below give minimum-bend
# storage space; keyed housings and the joined ends remain installed as units.
jr=[dict(name="fixed_yaw_250",motion="body",center=[-84,-33,91],normal=[0,1,0],source=[-119.5,0,53.2],end=[-72,-33,118],raw=250),
    dict(name="yawing_pitch_250",motion="yaw",center=[-141,-41,151],normal=[0,0,1],source=[-159,-43.8,131.5],end=[-120,-51,151],raw=250),
    dict(name="existing_extension_300",motion="fixed_reserve_moving_entry",center=[-60,-38,148],normal=[0,1,0],source=[-120,-51,151],end=[-42,-40,108],raw=300)]
for i,q in enumerate(jr):
    c=V(*q["center"]);axis=V(*q["normal"])
    ring=Part.makeTorus(23.5,1.75,c,axis)
    # This cover is conservative for each radial or axial boundary of one flat
    # loop, but its circular section is illustrative; check rectangular corners.
    path=wire([q["source"],(c+V(-23.5,0,0)),q["end"]])
    ref("FRONT18_JR_"+q["name"],Part.makeCompound([ring,path]),(.88,.48,.16))
(P/"JR-space-plan.json").write_bytes((json.dumps(dict(units=jr,project_profile=[3.5,1.8],inner_R=22,loop_center_R=23.5,loop_perimeter=2*math.pi*23.5,
    role="Trial locations of occupied storage; one Turn does not account for full routed unit. Straight reference lines are not proved bend trajectories.",
    keyed_pair_project=[30,14,10],factory_ends_preserved=True,cut=None,physical_PASS=False),indent=1)+"\n").encode())
skins=[o for o in D.Objects if o.Name in ("F3_HEAD_FRONT","F3_HEAD_BACK","F3_BODY_FORE_POS","F3_BODY_FORE_NEG","F3_BODY_REAR_POS","F3_BODY_REAR_NEG") or o.Name.startswith("F3_PAINT_")]
shots=[("front",(-1,0,.035),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
old={o.Name:o.ViewObject.Visibility for o in skins+refs}
pins=[]
def step(i):
    if i==len(shots):
        for o in skins+refs:o.ViewObject.Visibility=old[o.Name]
        v=V(*shots[2][1]);v.normalize();right=V(0,0,1).cross(v);right.normalize()
        G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,"ZXY").Q)
        D.Label="DAY18 LOWER FRAME AND UPRIGHT BANKS - WHOLE TRIAL"
        G.runCommand("Std_Save")
        (P/"whole-view-receipt.json").write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),basis="98e25411",initial_trial="fc4b9337",views=pins,objects=len(D.Objects),only_inside_skin_removal=[o.Name for o in skins],whole_closed_accepted=False,physical_PASS=False),indent=1)+"\n").encode())
        return
    name,direction,inside=shots[i]
    for o in skins:o.ViewObject.Visibility=not inside
    for o in refs:o.ViewObject.Visibility=inside
    view=G.activeDocument().activeView()
    v=V(*direction);v.normalize();right=V(0,0,1).cross(v);right.normalize()
    view.setCameraOrientation(A.Rotation(right,v.cross(right),v,"ZXY").Q)
    view.fitAll();view.redraw()
    def capture():
        path=P/("whole-"+name+".png")
        view.saveImage(str(path),1500,1050,"White")
        pins.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),quaternion=list(view.getCameraOrientation().Q),inside=inside))
        QtCore.QTimer.singleShot(250,lambda:step(i+1))
    QtCore.QTimer.singleShot(550,capture)
A._front18_capture=step
step(0)
print("Four views scheduled")
