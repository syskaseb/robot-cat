"""Test both actual source optical fields against changed optical and shoulder members."""
from pathlib import Path
import hashlib,json,runpy,ast,math
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
P=Path(__file__).parent;source=P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd"
native=P/"whole-cat19C.FCStd";Saved=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"]
D=Saved(native);S=Saved(source)
for n in ["Camera3_NoIR_Wide","VL53L5CX"]:
    assert np.allclose(D.bounds(n),S.bounds(n),atol=1e-5)
    assert hashlib.sha256(D.zip.read(D.members[n])).digest()==hashlib.sha256(S.zip.read(S.members[n])).digest() or np.max(abs(D.bounds(n)-S.bounds(n)))<1e-6
for fn in ast.parse((P.parent/"day18-open-front-assembly/occupied-gate.py").read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(P),"exec"))
rows=[];fields=["D18C_CAM_MODEL_CLOCK_BOUND_FOV","D18C_TOF_MODEL_CLOCK_BOUND_FOV"]
def common(a,b):
    op=BRepAlgoAPI_Common(a,b);assert op.IsDone();g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g);return g.Mass()
for f in fields:
    shape=S.shape(f);S.shapes[f]=shape
    for n in ["C19_FaceAndEars","C19_MovingOpticsCarrier","C19_OpenRearHelmet","C19_Nose","C19_Ear_1","C19_Ear_2","C19_Iris_L","C19_Iris_R","C19_Pupil_L","C19_Pupil_R"]:
        a,b=S.bounds(f),D.bounds(n)
        sep=float(np.linalg.norm(np.maximum(0,np.maximum(a[:3]-b[3:],b[:3]-a[3:]))))
        rows.append(dict(field=f,member=n,scope="co-moving at all angles",bounds_gap_mm=sep,common_mm3=0 if sep>1e-5 else common(shape,D.shape(n))))
    for y in [-20,0,20]:
        for p in [-10,0,10]:
            R,T=transforms(y,p)["pitch"];tr=gp_Trsf();tr.SetValues(*(np.column_stack([R,T]).ravel().tolist()))
            s=BRepBuilderAPI_Transform(shape,tr,False).Shape()
            rows.append(dict(field=f,member="C19_FixedShoulderShell",yaw=y,pitch=p,common_mm3=common(s,D.shape("C19_FixedShoulderShell"))))
out=dict(source=str(source.relative_to(P.parent)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows,actual_optical_alignment=None)
(P/"optical-apertures.json").write_bytes((json.dumps(out,indent=1)+"\n").encode());print([r for r in rows if r["common_mm3"]>.001])

