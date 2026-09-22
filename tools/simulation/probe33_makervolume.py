"""Last-resort OCC topology recovery study; exports candidates, never installs."""
from pathlib import Path
import time,json,hashlib
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape,TopoDS
from OCP.TopAbs import TopAbs_FACE,TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BOPAlgo import BOPAlgo_MakerVolume
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
source=ROOT/'hardware/skorupa/v31/shape-cache/HeadFront.brep'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='cf864082464ced13665d4987df0a58e9bac1633f092d09b50cd883566e0e51ac'
s=TopoDS_Shape();BRepTools.Read_s(s,str(ROOT/'hardware/skorupa/v31/shape-cache/HeadFront.brep'),BRep_Builder())
builder=BOPAlgo_MakerVolume();builder.SetIntersect(True);builder.SetAvoidInternalShapes(True)
builder.SetNonDestructive(True);builder.SetFuzzyValue(1e-5);builder.SetRunParallel(True)
ex=TopExp_Explorer(s,TopAbs_FACE);count=0
while ex.More():builder.AddArgument(ex.Current());count+=1;ex.Next()
print('MakerVolume faces',count,flush=True);started=time.monotonic();builder.Perform()
print('completed',time.monotonic()-started,'errors',builder.HasErrors(),'warnings',builder.HasWarnings(),flush=True)
assert not builder.HasErrors()
result=builder.Shape();BRepTools.Write_s(result,str(OUT/'maker_volume_all.brep'))
ex=TopExp_Explorer(result,TopAbs_SOLID);rows=[]
while ex.More():
    s=TopoDS.Solid(ex.Current());p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p)
    index=len(rows);name='maker_volume_%d'%index;BRepTools.Write_s(s,str(OUT/(name+'.brep')))
    r=dict(name=name,valid=BRepCheck_Analyzer(s).IsValid(),volume_mm3=p.Mass());rows.append(r);print(r,flush=True);ex.Next()
(OUT/'maker-volume.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
