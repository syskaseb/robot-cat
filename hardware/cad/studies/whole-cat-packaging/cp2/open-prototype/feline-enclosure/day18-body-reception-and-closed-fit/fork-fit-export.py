"""Export only the connected printed fork for a cold MG lead and crosspin fit check."""
import json,runpy,hashlib
from pathlib import Path
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf,gp_Vec
import numpy as np,trimesh
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
name="BR_FINISHED_YAW_SADDLE";s=D.shape(name);g=D.bounds(name)
i=TopExp_Explorer(s,TopAbs_SOLID);count=0
while i.More():count+=1;i.Next()
assert count==1 and BRepCheck_Analyzer(s).IsValid()
report=json.loads((P/"frozen-unit-receipt.json").read_bytes())
checks=[q for q in report["local"] if q["a"]==name];assert len(checks)>=5
assert all("error" not in q and q.get("common_mm3",0)<.001 for q in checks)
t=gp_Trsf();t.SetTranslation(gp_Vec(128-(g[0]+g[3])/2,128-(g[1]+g[4])/2,-g[2]));s=s.Moved(TopLoc_Location(t))
BRepMesh_IncrementalMesh(s,.06,False,.12,True)
f=P/"conditional-yaw-fork-MG-crosspin.stl";w=StlAPI_Writer();w.ASCIIMode=False
assert w.Write(s,str(f))
m=trimesh.load_mesh(f,process=True)
dims=m.extents;envelope=dims+np.array([16,16,4])
data=dict(object=name,source_native_SHA=hashlib.sha256((P/"body-reception.FCStd").read_bytes()).hexdigest(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
          BRep_solids=count,triangle_count=len(m.faces),watertight=bool(m.is_watertight),consistent_winding=bool(m.is_winding_consistent),body_count=int(m.body_count),
          volume_mm3=float(m.volume),bed_orientation="Native Z up; translated to XY center 128,128 and Zmin=0",print_box_with_allowance=envelope.tolist(),
          allowed_scope="Conditional unpowered fit of the printed yaw fork, actual MG exit, intact 250 mm factory lead, open saddle, selected tie and complete crosspin stack.",
          unknown="Delivered cable outlet and jacket, tie strength, screw fits, actual supports, dynamic slack and full head-to-body closure.",physical_PASS=False)
(P/"fork-fit-export.json").write_bytes((json.dumps(data,indent=1)+"\n").encode())
assert m.is_watertight and m.is_winding_consistent and m.body_count==1 and m.volume>0 and np.all(envelope<256),data
