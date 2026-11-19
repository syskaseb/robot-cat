"""Changed tail aperture/underbank occupancy, from the saved current-Y root only."""
from pathlib import Path
import runpy,json,math
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Ax1,gp_Pnt,gp_Dir,gp_Trsf
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19B.FCStd")
rows=[]
for angle in [-15,0,15]:
    tx=gp_Trsf();tx.SetRotation(gp_Ax1(gp_Pnt(140,0,130),gp_Dir(0,1,0)),math.radians(angle))
    s=BRepBuilderAPI_Transform(D.shape("TAIL_ROTATING_HOLLOW_REAL_ROOT"),tx,False).Shape()
    for n in ["D19_ROUNDED_REAR_COWL","B19_RearFloor","B19_TailJRUnderBank","B19_TailMatedPair"]:
        op=BRepAlgoAPI_Common(s,D.shape(n));assert op.IsDone()
        g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
        rows.append(dict(angle_Y_deg=angle,other=n,common_mm3=g.Mass()))
(P/"tail-swing.json").write_text(json.dumps({"tail_root_axis":[140,0,130],"checks":rows,"physical_PASS":False,"continuous_motion":None},indent=1)+"\n",encoding="utf8")
print([q for q in rows if q["common_mm3"]>.001])

