"""Split existing optical mask faces along the two eye boundaries without adding material."""
from pathlib import Path
import json
from OCP.BRep import BRep_Builder
from OCP.BRepTools import BRepTools
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepFeat import BRepFeat_SplitShape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS,TopoDS_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
P=Path(__file__).parent
def read(n):
    s=TopoDS_Shape();assert BRepTools.Read_s(s,str(P/n),BRep_Builder());return s
s=read("cheek-before-paint.brep");eyes=read("eye-boundaries.brep")
sec=BRepAlgoAPI_Section(s,eyes,False);sec.ComputePCurveOn1(True);sec.Approximation(True);sec.Build()
assert sec.IsDone()
cut=BRepFeat_SplitShape(s);it=TopExp_Explorer(sec.Shape(),TopAbs_EDGE);i=0
while it.More():
    e=TopoDS.Edge(it.Current());f=TopoDS_Shape()
    if sec.HasAncestorFaceOn1(e,f):cut.Add(e,TopoDS.Face(f));i+=1
    it.Next()
cut.Build();assert cut.IsDone()
coated=cut.Shape()
def count(x):
    exp=TopExp_Explorer(x,TopAbs_FACE);n=0
    while exp.More():n+=1;exp.Next()
    return n
def volume(x):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(x,p,1e-8);return p.Mass()
res=dict(edges_added=i,faces_before=count(s),faces_after=count(coated),before_mm3=volume(s),after_mm3=volume(coated),valid=BRepCheck_Analyzer(coated).IsValid())
(P/"paint-partition.json").write_bytes((json.dumps(res,indent=1)+"\n").encode("utf8"))
assert res["valid"] and res["faces_after"]>res["faces_before"] and abs(res["before_mm3"]-res["after_mm3"])<1,res
BRepTools.Write_s(coated,str(P/"cheek-painted-surface.brep"));print(res)
