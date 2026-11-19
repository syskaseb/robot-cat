"""Only the changed load interfaces, tool paths, full mate and occupied regions."""
from pathlib import Path
import json,runpy,hashlib,math
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt
P=Path(__file__).parent
native=P/"whole-cat19B.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
out={"native_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),"physical_PASS":False,"actual_fit_cut_slack":None,"pairs":[],"anchor_bearing":[]}
for f in ("B19_FrontFloor","B19_RearFloor"):
    ns=["B19_ToolEightAnchors","B19_ToolYawPin","D19_BROAD_SKULL_BACK","D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","Battery_GEA223S30X6GT","B19_TailJRUnderBank","B19_TailMatedPair","B19_TailLaps","D19_DATA_STORAGE_LAYER","BR_FLANK_HP_PAIR","Yaw608_120","Yaw608_134","MG92B_Head_yaw","MG92B_Tail","TAIL_REAL_REMOVABLE_SERVO_SADDLE","TAIL_FIXED_BEARING_CARTRIDGE","YAW_REAL_REMOVABLE_SERVO_SADDLE","MAX98357A_amp"]
    ns += [n for n in D.members if n.startswith(("H01_source","YAW_SHAFT_FORK_POSITIVE","TAIL_SADDLE_ROOT","TAIL_CARTRIDGE_CAP_ROOT","CB_PCA"))]
    for n in ns:out["pairs"].append(dict(a=f,b=n,**D.common(f,n)))
for n in ("B19_TailJRUnderBank","B19_TailMatedPair","B19_TailLaps"):
    for m in ("MG92B_Tail","MAX98357A_amp","OP_S1_PRIMARY_CASE_CONSERVATIVE","S0_body","D19_ROUNDED_REAR_COWL","D19_DATA_STORAGE_LAYER","Motor_ATO4A__1_2"):
        out["pairs"].append(dict(a=n,b=m,**D.common(n,m)))
for x in (-80,-70,112,122):
    f="B19_FrontFloor" if x<0 else "B19_RearFloor"
    for y in (-22.5,22.5):
        window=BRepPrimAPI_MakeBox(gp_Pnt(x-4.6,y-4.6,30),9.2,9.2,19).Shape()
        floor=BRepAlgoAPI_Common(D.shape(f),window).Shape()
        base=BRepAlgoAPI_Common(D.shape("WAVEGO_complete_126_source_solids"),window).Shape()
        dist=BRepExtrema_DistShapeShape(floor,base)
        row={"center":[x,y],"floor_base_distance":dist.Value() if dist.IsDone() else None}
        if dist.IsDone():row["witness"]=[dist.PointOnShape1(1).Coord(),dist.PointOnShape2(1).Coord()]
        out["anchor_bearing"].append(row)
(P/"changed-checks.json").write_text(json.dumps(out,indent=1)+"\n",encoding="utf8")
print("positive volumes",[(q["a"],q["b"],round(q["common_mm3"],3)) for q in out["pairs"] if q.get("common_mm3",0)>.001])
print("anchor gaps",[q["floor_base_distance"] for q in out["anchor_bearing"]])

