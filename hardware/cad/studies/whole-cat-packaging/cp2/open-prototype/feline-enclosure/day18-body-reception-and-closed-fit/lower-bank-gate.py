"""Check one sectional allocation of the full fore negative bank on a lower side-opening carrier."""
from pathlib import Path
import json,runpy,math,ast
import numpy as np
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax1,gp_Trsf,gp_Vec
from OCP.TopLoc import TopLoc_Location
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
bank=["Motor_ATO4A_1_3","Motor_ATO4A__1_3","Motor_ATO4A_1_4","FRONT18_FORE_NEG_PANEL"]
# Use the source panel's installation plane. Rotate each complete 4-solid
# assembly and the one panel together. The mating direction is lateral.
c=(0,-68.8062,127.915);t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(*c),gp_Dir(1,0,0)),np.pi/2)
v=gp_Trsf();v.SetTranslation(gp_Vec(0,-65.5-c[1],68.5-c[2]));v.Multiply(t)
targets=["BR_PAIR_HY","BR_FLANK_HP_PAIR","PBAY_F_HP","PBAY_F_HY","PBAY_P_REAR","PBAY_P_AUX","PBAY_F_AUX","Pi4B_actual_PCB","F2_COMMON_PI_BUS_PCA_RECEIVER","OPEN_PORTAL_MATERIAL_SUBSET","D18C_P02_THREE_ROOT_THROUGH_VERSION","WAVEGO_complete_126_source_solids","Battery_GEA223S30X6GT","OPEN_BATTERY_DOOR","BR_RECESSED_CHEST","BR_ROUNDED_RUMP"]
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("profile","unit"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
r=json.loads((P/"flank-reception.json").read_bytes());rows=[]
for n in bank:
    moved="trial_"+n;D.shapes[moved]=D.shape(n).Moved(TopLoc_Location(v));hits={}
    for a in targets:
        m=D.common(moved,a)
        if m.get("common_mm3",0)>.01 or "error" in m:hits[a]=m
    ph=[]
    for q in r["pitch"]:
        w=profile(q["centreline"],3.5,1.8).reshape(-1,3);i=D.inside(moved,w)
        if i is not None:ph.append(dict(yaw=q["yaw"],point=w[i].tolist()))
    rows.append(dict(unit=n,bounds=D.bounds(moved).tolist(),neutral_material_hits=hits,factory_pitch_field_hits=ph))
    (P/"lower-bank-gate.json").write_bytes((json.dumps(dict(rows=rows,source_plane=c,new_plane=[0,-65.5,68.5],rotation_x=90,disposition="Candidate tested before changing any active bank or stock pose.",physical_PASS=False),indent=1)+"\n").encode())
