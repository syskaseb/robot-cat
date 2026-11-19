"""Intersect the actual coplanar bearing faces at the eight base anchors."""
from pathlib import Path
import runpy,json
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.gp import gp_Pnt
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19B.FCStd")
def faces(s):
    e=TopExp_Explorer(s,TopAbs_FACE);rows=[]
    while e.More():
        f=e.Current();bb=Bnd_Box();BRepBndLib.Add_s(f,bb,False);lo=bb.CornerMin().Coord();hi=bb.CornerMax().Coord()
        if abs(lo[2]-38.52)<.002 and abs(hi[2]-38.52)<.002:rows.append((f,lo,hi))
        e.Next()
    return rows
def area(s):
    p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);return p.Mass()
def near(rows,x,y):
    return [f for f,lo,hi in rows if lo[0]<x+4.6 and hi[0]>x-4.6 and lo[1]<y+4.6 and hi[1]>y-4.6]
base=faces(D.shape("WAVEGO_complete_126_source_solids"));floors={n:faces(D.shape(n)) for n in ["B19_FrontFloor","B19_RearFloor"]}
rows=[]
for x in [-80,-70,112,122]:
    f="B19_FrontFloor" if x<0 else "B19_RearFloor"
    for y in [-22.5,22.5]:
        w=BRepPrimAPI_MakeBox(gp_Pnt(x-4.6,y-4.6,38),9.2,9.2,1).Shape()
        floor=[BRepAlgoAPI_Common(face,w).Shape() for face in near(floors[f],x,y)]
        total=sum(area(BRepAlgoAPI_Common(top,bottom).Shape()) for top in near(base,x,y) for bottom in floor)
        rows.append(dict(x=x,y=y,contact_patch_mm2=total,window_side_mm=9.2))
steel={n:D.common("B19_FrontFloor",n) for n in D.members if n.startswith(("YAW_SOURCE_EAR","YAW_FIXED_CAP_"))}
(P/"anchor-seats.json").write_text(json.dumps(dict(pads=rows,yaw_full_steel=steel,physical_PASS=False),indent=1)+"\n",encoding="utf8")
print([r["contact_patch_mm2"] for r in rows])

