"""Actual moving rigid pairs; two independent axes. Reuse one check for invariant pairs."""
from pathlib import Path
import sys,json,runpy,math,ast,hashlib
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
P=Path(__file__).parent;native=P/"whole-cat19D.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](native)
for fn in ast.parse((P.parent/"day18-open-front-assembly/occupied-gate.py").read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(P),"exec"))
mode=sys.argv[1];rows=[];cache={}
def obj(n,pose,owner):
    y,p=pose
    if owner=="fixed":return D.shape(n)
    key=(n,y,p if owner=="pitch" else 0)
    if key not in cache:
        R,T=transforms(y,p)[owner];t=gp_Trsf();t.SetValues(*np.column_stack([R,T]).ravel().tolist());cache[key]=BRepBuilderAPI_Transform(D.shape(n),t,False).Shape()
    return cache[key]
def test(a,b,oa,ob,y,p):
    s,t=obj(a,(y,p),oa),obj(b,(y,p),ob)
    op=BRepAlgoAPI_Common(s,t);assert op.IsDone();g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
    rows.append(dict(a=a,b=b,yaw=y,pitch=p,common_mm3=g.Mass()));save()
def save():
    (P/("joint-"+mode+".json")).write_bytes((json.dumps(dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows),indent=1)+"\n").encode())
if mode=="moving":
    for p in (0,-10,10):
        test("D19D_PitchBack","D19D_YawHood","pitch","yaw",0,p)
        test("D19D_Face","D19D_YawHood","pitch","yaw",0,p)
    for y in (0,-20,20):
        test("D19D_YawHood","D19D_Shoulder","yaw","fixed",y,0);test("D19D_YawHood","D19D_FrontFloor","yaw","fixed",y,0)
    for y,p in ((0,0),(-20,-10),(20,10),(-20,10),(20,-10)):
        test("D19D_PitchBack","D19D_Shoulder","pitch","fixed",y,p)
        test("D19D_Face","D19D_Shoulder","pitch","fixed",y,p)
elif mode=="mounts":
    pairs={"D19D_FrontFloor":["D19D_Shoulder","B19_ToolEightAnchors","Pi4B_actual_PCB","Pi_components_and_cooling","PBAY_F_HY"],"D19D_RearShell":["B19_RearFloor","Speaker","Monitor_MOD05015","ReSpeakerLite_on_REMOVABLE_back","B19_TailMatedPair"],"D19D_YawMatedPair":["D19D_FrontFloor","D19D_Shoulder","Pi4B_actual_PCB","BUS25514_installed","BR_FLANK_THREE_LAPS","PBAY_F_HY"],"D19D_OpticsCarrier":["Camera3_NoIR_Wide","VL53L5CX","D19D_Face","D19D_PitchBack"],"D19D_Face":["D19D_PitchBack","D19D_Iris_L","D19D_Iris_R","D19D_Ear_L","D19D_Ear_R","D19D_Nose"],"D19D_YawHood":["D19D_YawSaddle","MG92B_Head_pitch","D19D_FrontFloor"]}
    for a,bs in pairs.items():
        for b in bs:rows.append(dict(a=a,b=b,**D.common(a,b)));save()
print([(r["a"],r["b"],round(r.get("common_mm3",0),3)) for r in rows if r.get("common_mm3",0)>.01])

