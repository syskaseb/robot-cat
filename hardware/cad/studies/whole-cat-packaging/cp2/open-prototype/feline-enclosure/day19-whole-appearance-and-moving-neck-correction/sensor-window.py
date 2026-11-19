"""Inspect centre and four neighbouring rays from each actual board side through the native face."""
from pathlib import Path
import json,runpy,hashlib
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.gp import gp_Pnt,gp_Dir,gp_Lin
P=Path(__file__).parent;native=P/"whole-cat19D.FCStd";D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](native)
rows=[]
for board,area,x,z in [("Camera3_NoIR_Wide","camera",D.bounds("Camera3_NoIR_Wide")[0]-.05,145),("VL53L5CX","ToF",D.bounds("VL53L5CX")[0]-.05,103)]:
    for y,dz in [(0,0),(-1.5,0),(1.5,0),(0,-1.5),(0,1.5)]:
        hits=[]
        for n in ["D19D_Face","D19D_Nose","D19D_Iris_L","D19D_Iris_R","D19D_OpticsCarrier"]:
            inter=IntCurvesFace_ShapeIntersector();inter.Load(D.shape(n),1e-6);inter.Perform(gp_Lin(gp_Pnt(x,y,z+dz),gp_Dir(-1,0,0)),0,130)
            if inter.NbPnt():hits.append(dict(part=n,first_x=x-min(inter.WParameter(i+1) for i in range(inter.NbPnt()))))
        rows.append(dict(sensor=area,origin=[x,y,z+dz],hits=hits))
(P/"sensor-window.json").write_bytes((json.dumps(dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows),indent=1)+"\n").encode());print([r for r in rows if r["hits"]])

