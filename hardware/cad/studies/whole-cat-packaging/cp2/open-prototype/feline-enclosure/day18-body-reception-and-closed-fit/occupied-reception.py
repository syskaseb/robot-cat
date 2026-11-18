"""Check full station solids and sample installed cable fields only where the anchor changed."""
from pathlib import Path
import json,runpy,ast
import numpy as np
P=Path(__file__).parent;prior=P.parent/"day18-open-front-assembly"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
assert "BR_BODY_ROOT" in D.members
import math
tree=ast.parse((prior/"occupied-gate.py").read_bytes())
for fn in tree.body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {"profile","transforms","unit"}:
        exec(compile(ast.Module([fn],type_ignores=[]),str(prior/"occupied-gate.py"),"exec"))
r=json.loads((P/"reception-layout.json").read_bytes());rows=[]
def write():
    (P/"occupied-reception.json").write_bytes((json.dumps(dict(rows=rows,scope="Positive witnesses are intersections. Finite profile sampling cannot certify clearance between samples or continuous motion.",physical_PASS=False),indent=1)+"\n").encode())
fixed=["Pi4B_actual_PCB","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","F2_COMMON_PI_BUS_PCA_RECEIVER","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX","OPEN_PORTAL_MATERIAL_SUBSET","BR_RECEIVER_HARD_MATERIAL","MG92B_Head_yaw"]+[n for n in D.members if n.startswith(("WAGO415_data","Motor_ATO4A_"))]
yaw=["HEAD_YAW_FORK_FIXED_PITCH_HOUSING","MG92B_Head_pitch"]+[n for n in D.members if n.startswith("YAW_SHAFT_FORK_POSITIVE_CROSSPIN")]
for a in ["BR_PAIR_HY","BR_PAIR_HP","BR_LAPS","BR_RECEIVER_HARD_MATERIAL"]:
    hits={}
    for b in fixed+yaw:
        if a==b:continue
        u=D.common(a,b)
        if u.get("common_mm3",0)>.005 or "error" in u:hits[b]=u
    rows.append(dict(name=a,exact_neutral=hits));write()
def test(label,line,w,h,y=0,p=0):
    pts=profile(line,w,h)
    pts=pts[np.unique(np.linspace(0,len(pts)-1,min(len(pts),37)).astype(int))].reshape(-1,3)
    hits={};m=transforms(y,p)
    for owner,names in [("fixed",fixed),("yaw",yaw),("pitch",["BR_PITCH_RECEIVER_AND_GRIP"])]:
        rot,t=m[owner]
        local=(pts-t)@rot
        for n in names:
            ix=D.inside(n,local)
            if ix is not None:hits[n]=pts[ix].tolist()
    rows.append(dict(name=label,yaw=y,pitch=p,witness=hits));write()
test("factory_yaw_static",r["yaw"]["centreline"],3.5,1.8)
test("existing_extension_static",r["extension"]["centreline"],3.5,1.8)
for q in r["extension"]["fans"]:test("extension_fan",q["centreline"],1.8,1.8)
for q in r["pitch"]:test("factory_pitch_to_body",q["centreline"],3.5,1.8,q["yaw"])
for q in r["ToF_move"]:
    if (q["yaw"],q["pitch"]) in [(0,0),(-20,-10),(20,10),(-20,10),(20,-10)]:
        test("ToF_shared",q["centreline"],4.9,4.9,q["yaw"],q["pitch"])
for q in r["ToF_fixed"]:test(q["wire"],q["centreline"],2.1,2.1)
