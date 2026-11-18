"""Screen named full-profile fields against only the new material and confirm positive witnesses on the BRep."""
import ast,math,json,runpy,sys
from pathlib import Path
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray,vtkPolyData
from vtkmodules.vtkFiltersCore import vtkCleanPolyData
from vtkmodules.vtkFiltersModeling import vtkSelectEnclosedPoints
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("unit","profile","transforms"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
def mesh(n):
    s=D.shape(n);BRepMesh_IncrementalMesh(s,.15,False,.18,True)
    pts=vtkPoints();cells=vtkCellArray();e=TopExp_Explorer(s,TopAbs_FACE)
    while e.More():
        face=TopoDS.Face(e.Current());loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc)
        if tri:
            k=pts.GetNumberOfPoints();tr=loc.Transformation()
            for i in range(1,tri.NbNodes()+1):pts.InsertNextPoint(tri.Node(i).Transformed(tr).Coord())
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get()
                if face.Orientation()==TopAbs_REVERSED:b,c=c,b
                cells.InsertNextCell(3)
                for j in (a,b,c):cells.InsertCellPoint(k+j-1)
        e.Next()
    data=vtkPolyData();data.SetPoints(pts);data.SetPolys(cells);clean=vtkCleanPolyData();clean.SetInputData(data);clean.Update()
    surf=clean.GetOutput();tester=vtkSelectEnclosedPoints();tester.SetTolerance(1e-8);tester.Initialize(surf)
    return tester,surf
parts=dict(fixed=["BR_CHEST_WITH_COVERED_ENTRIES","BR_PI_CARRIER_AROUND_LANE","BR_CURRENT_RECEPTION_SUBSET"],yaw=["BR_YAW_FORK_WITH_SADDLE"],pitch=["BR_PITCH_RECEIVER_OPEN_ENTRY","BR_PARTED_SKULL_BACK"])
frozen="--frozen" in sys.argv
if frozen:
    updates={"BR_CHEST_WITH_COVERED_ENTRIES":"BR_CHEST_EXTENSION_ENTRY","BR_PI_CARRIER_AROUND_LANE":"BR_FORE_ROOT_PI_CARRIER","BR_YAW_FORK_WITH_SADDLE":"BR_FINISHED_YAW_SADDLE","BR_PARTED_SKULL_BACK":"BR_BACK_UPPER_RETURN"}
    for k in parts:parts[k]=[updates.get(n,n) if updates.get(n,n) in D.members else n for n in parts[k]]
cache={n:mesh(n) for ns in parts.values() for n in ns}
f=json.loads((lib.parent/"occupied-layout.json").read_bytes())["FFC"];r=json.loads((P/"flank-reception.json").read_bytes());jr=json.loads((P/"yaw-laid-factory.json").read_bytes())["rows"];fan=json.loads((P/"jp3-shared-fan.json").read_bytes())["rows"]
res=dict(rows=[],scope="0.15 mm mesh used only to select sampled witness points. Each reported material hit is checked at the same point against the saved BRep. Unsampled poses and spaces remain unverified.",physical_PASS=False)
def save():(P/("frozen-field-check.json" if frozen else "final-field-check.json")).write_bytes((json.dumps(res,indent=1)+"\n").encode())
def test(tag,y,p,field,owners=None):
    pts=np.asarray(field).reshape(-1,3);hits=[];m=transforms(y,p)
    for owner,ns in parts.items():
        if owners and owner not in owners:continue
        R,T=m[owner];q=(pts-T)@R
        for n in ns:
            b=D.bounds(n);keep=np.flatnonzero(np.all((q>=b[:3])&(q<=b[3:]),axis=1))
            idx=[i for i in keep if cache[n][0].IsInsideSurface(*q[i])]
            if idx:
                j=D.inside(n,q[idx])
                if j is not None:hits.append(dict(part=n,point=pts[idx[j]].tolist(),source_frame=q[idx[j]].tolist()))
    res["rows"].append(dict(field=tag,yaw=y,pitch=p,exact_witness=hits));save()
for y,p in [(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]:
    t=next(v for v in r["ToF_move"] if v["yaw"]==y and v["pitch"]==p)
    test("FFC200",y,p,next(v for v in f if v["yaw"]==y and v["pitch"]==p)["corners"])
    test("ToF 4x2.1",y,p,profile(t["centreline"],4.9,4.9))
    test("pitch 250",y,p,profile(next(v for v in jr if v["yaw"]==y)["centreline"],3.5,1.8))
test("yaw 250",0,0,profile(r["yaw"]["centreline"],3.5,1.8))
test("static300",0,0,profile(r["extension"]["centreline"],3.5,1.8))
for v in r["extension"]["fans"]:test("300 fan",0,0,profile(v["centreline"],1.8,1.8))
for v in fan:test(v["wire"],0,0,profile(v["centreline"],2.1,2.1))
