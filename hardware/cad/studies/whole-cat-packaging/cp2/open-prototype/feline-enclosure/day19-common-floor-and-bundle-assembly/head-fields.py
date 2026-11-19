"""Rebind the four fixed ToF paths to the moved soldered board, and check the changed skins."""
from pathlib import Path
import json,ast,runpy,math,hashlib
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
P=Path(__file__).parent;old=P.parent/"day18-body-reception-and-closed-fit"
native=P/"whole-cat19B.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for file,selected in [(lib,("unit","profile","transforms")),(old/"final-field-check.py",("mesh",)),(old/"jp3-body-lane.py",("line","arc","join"))]:
    for fn in ast.parse(file.read_bytes()).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in selected:exec(compile(ast.Module([fn],type_ignores=[]),str(file),"exec"))
r=json.loads((old/"flank-reception.json").read_bytes())
typed={q["wire"]:q.copy() for q in json.loads((old/"typed-jp3.json").read_bytes())["rows"]}
before=np.array([-18,20.95,132.6]);after=D.bounds("PCA9685_Adafruit815_PCB")[:3]
for q in typed.values():q["world_center"]=(np.array(q["world_center"])+after-before).tolist()
rows=[];X,Y,Z=np.eye(3);B=np.array(r["shared_grips"]["body"])
source=(old/"jp3-body-lane.py").read_text(encoding="utf8")
exec(source[source.index("for i in (0,2,3,1):"):source.index('(P/"jp3-body-lane.json")')])
# Only changed floor/skull/cowl. Header and movement anchors are retained;
# a witness stops acceptance of this proposed routing/pose.
parts={"fixed":["B19_FrontFloor","D19_ROUNDED_FORE_COWL"],"pitch":["D19_BROAD_SKULL_BACK"]}
cache={n:mesh(n) for ns in parts.values() for n in ns}
records=[]
def screen(tag,y,p,field):
    pts=np.asarray(field).reshape(-1,3);hits=[];m=transforms(y,p)
    for owner,ns in parts.items():
        R,T=m[owner];q=(pts-T)@R
        for n in ns:
            b=D.bounds(n);keep=np.flatnonzero(np.all((q>=b[:3])&(q<=b[3:]),axis=1))
            idx=[i for i in keep if cache[n][0].IsInsideSurface(*q[i])]
            if idx:
                j=D.inside(n,q[idx])
                if j is not None:hits.append(dict(part=n,point=pts[idx[j]].tolist()))
    records.append(dict(field=tag,yaw=y,pitch=p,witness=hits))
ffc=json.loads((lib.parent/"occupied-layout.json").read_bytes())["FFC"]
for y,p in [(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]:
    R,T=transforms(y,p)["pitch"]
    for i,line_data in enumerate(r["ToF_head"]):
        field=profile(line_data["centreline"],2.1,2.1).reshape(-1,3)@R.T+T
        screen("head lead "+str(i+1),y,p,field)
    moving=next(q for q in r["ToF_move"] if (q["yaw"],q["pitch"])==(y,p))
    screen("ToF moving bundle",y,p,profile(moving["centreline"],4.9,4.9))
    screen("FFC200",y,p,next(q["corners"] for q in ffc if (q["yaw"],q["pitch"])==(y,p)))
    for row in rows:
        screen(row["wire"],y,p,profile(row["centreline"],2.1,2.1))
for row in rows:row.pop("centreline")
out={"native_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),"fixed_fans":rows,"checks":records,"cut_mm_actual":None,"solder_land_actual":None,"physical_PASS":False,"scope":"Sampled full head, moving bundle, four fixed fan paths and FFC against changed front material. Exact BRep witnesses confirm hits. Angles between sampled poses remain unchecked."}
(P/"head-field-result.json").write_text(json.dumps(out,indent=1)+"\n",encoding="utf8")
print(len(records),sum(bool(q["witness"]) for q in records))

