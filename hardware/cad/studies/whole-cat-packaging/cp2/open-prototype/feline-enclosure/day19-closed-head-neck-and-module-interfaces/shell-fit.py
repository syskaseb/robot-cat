"""Neutral attachment interfaces and kinematic shell seam on the saved assembly."""
from pathlib import Path
import json,runpy,ast,math,hashlib
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Trsf
P=Path(__file__).parent;native=P/"whole-cat19C.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
for fn in ast.parse((P.parent/"day18-open-front-assembly"/"occupied-gate.py").read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(P),"exec"))
fit=[]
for a,bs in {
    "C19_Iris_L":["C19_FaceAndEars","C19_Pupil_L"],"C19_Iris_R":["C19_FaceAndEars","C19_Pupil_R"],
    "C19_Ear_1":["C19_FaceAndEars","C19_OpenRearHelmet"],"C19_Ear_2":["C19_FaceAndEars","C19_OpenRearHelmet"],
    "C19_Nose":["C19_FaceAndEars"],"C19_OpenRearHelmet":["C19_FaceAndEars","C19_MovingOpticsCarrier"],
    "C19_MovingOpticsCarrier":["Camera3_NoIR_Wide","VL53L5CX","PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw"],
    "C19_ShoulderFloor":["Pi4B_actual_PCB","Pi_components_and_cooling","C19_FixedShoulderShell","B19_ToolEightAnchors","PBAY_F_TY","PBAY_F_HY"]}.items():
    for b in bs:fit.append(dict(a=a,b=b,**D.common(a,b)))
out={"native_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),"static":fit,"motion":[],"physical_PASS":False}
def save():(P/"shell-fit.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
save()
for y,p in [(0,0),(-20,10),(20,-10),(-20,-10),(20,10)]:
    R,T=transforms(y,p)["pitch"];tr=gp_Trsf();tr.SetValues(*(np.column_stack([R,T]).ravel().tolist()))
    for n in ["C19_OpenRearHelmet","C19_FaceAndEars"]:
        s=BRepBuilderAPI_Transform(D.shape(n),tr,False).Shape()
        op=BRepAlgoAPI_Common(s,D.shape("C19_FixedShoulderShell"));assert op.IsDone()
        g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
        out["motion"].append(dict(yaw=y,pitch=p,moving=n,stationary="C19_FixedShoulderShell",common_mm3=g.Mass()));save()
print([(q["yaw"],q["pitch"],q["moving"],round(q["common_mm3"],2)) for q in out["motion"] if q["common_mm3"]>.001])

