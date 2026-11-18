"""Test only the revised factory pitch field and the named yaw attachment."""
from pathlib import Path
import ast,json,math,runpy
import numpy as np
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
q=json.loads((P/"yaw-laid-factory.json").read_bytes())
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("unit","profile","transforms"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
banks=json.loads((P.parent/"day18-open-front-assembly"/"initial-assembly.json").read_bytes())["bank"]
parts=dict(fixed=[p["unit"] for p in banks]+json.loads((P/"pa-aux-effectivity.json").read_bytes())["selected_415"]+["BR_FLANK_SUPPORT_SUBSET","OPEN_PORTAL_MATERIAL_SUBSET","F2_COMMON_PI_BUS_PCA_RECEIVER","Pi4B_actual_PCB","BR_CLOSED_CHEST_LIP","PBAY_F_HP","PBAY_F_HY","BR_PAIR_HY","PBAY_P_REAR","PBAY_F_AUX"],
           yaw=["HEAD_YAW_FORK_FIXED_PITCH_HOUSING","MG92B_Head_pitch"]+[n for n in D.members if n.startswith("YAW_SHAFT_FORK_POSITIVE_CROSSPIN")],pitch=["BR_PARTED_SKULL_BACK","BR_COMMON_OPTICAL_MASK","BR_PITCH_RECEIVER_AND_GRIP"])
rows=[]
for row in q["rows"]:
    y=row["yaw"];ps=profile(row["centreline"],3.5,1.8)[::3].reshape(-1,3);hits=[]
    for p in (0,-10,10) if abs(y)==20 else (0,):
        tr=transforms(y,p)
        for owner,nn in parts.items():
            if p and owner!="pitch":continue
            R,T=tr[owner];la=(ps-T)@R
            for n in nn:
                h=D.inside(n,la)
                if h is not None:hits.append(dict(n=n,p=p,point=ps[h].tolist()))
    rows.append(dict(yaw=y,hits=hits));(P/"yaw-lay-gate.json").write_bytes((json.dumps(dict(rows=rows,sampled=True,physical_PASS=False),indent=1)+"\n").encode())
