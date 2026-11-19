"""Export and reopen the two individual carrier parts for engineering fit checks."""
from pathlib import Path
import runpy,json,hashlib
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19B.FCStd")
exports=[]
for n in ["B19_FrontFloor","B19_RearFloor"]:
    s=D.shape(n);path=P/(n+".step");w=STEPControl_Writer()
    assert w.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone and w.Write(str(path))==IFSelect_RetDone
    r=STEPControl_Reader();assert r.ReadFile(str(path))==IFSelect_RetDone
    assert r.TransferRoots()>0
    opened=r.OneShape();p=GProp_GProps();q=GProp_GProps();BRepGProp.VolumeProperties_s(s,p,1e-8);BRepGProp.VolumeProperties_s(opened,q,1e-8)
    e=TopExp_Explorer(opened,TopAbs_SOLID);count=0
    while e.More():count+=1;e.Next()
    print(n, count, p.Mass(), q.Mass(), flush=True)
    assert count==1 and BRepCheck_Analyzer(opened).IsValid()
    assert abs(p.Mass()-q.Mass())/p.Mass()<0.00005
    exports.append(dict(part=n,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),native_volume_mm3=p.Mass(),volume_mm3=q.Mass(),reopened_solids=count))
(P/"floor-step-receipt.json").write_text(json.dumps(exports,indent=1)+"\n",encoding="utf8")

