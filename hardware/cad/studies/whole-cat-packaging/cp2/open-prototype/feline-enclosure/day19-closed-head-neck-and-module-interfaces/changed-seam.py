"""Check the changed opening and branch receivers against full-profile source fields."""
from pathlib import Path
import json,math,ast,runpy,hashlib
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
P=Path(__file__).parent;old=P.parent/"day18-body-reception-and-closed-fit";native=P/"whole-cat19C.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
source=P.parent/"day18-open-front-assembly"
for file,selected in [(source/"occupied-gate.py",("unit","profile","transforms")),(old/"final-field-check.py",("mesh",))]:
    for fn in ast.parse(file.read_bytes()).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in selected:exec(compile(ast.Module([fn],type_ignores=[]),str(file),"exec"))
lay=json.loads((P/"side-return.json").read_bytes())
ffc=json.loads((source/"occupied-layout.json").read_bytes())["FFC"]
factory=json.loads((old/"flank-reception.json").read_bytes());p250=json.loads((old/"yaw-laid-factory.json").read_bytes())["rows"]
parts={"fixed":["C19_ShoulderFloor","C19_FixedShoulderShell","Pi4B_actual_PCB","BUS25514_installed","Speaker","ReSpeakerLite_on_REMOVABLE_back","BR_FLANK_THREE_LAPS","PBAY_F_HY","MG92B_Head_yaw"],"yaw":["BR_FINISHED_YAW_SADDLE","MG92B_Head_pitch","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw"],"pitch":["C19_MovingOpticsCarrier","C19_FaceAndEars","C19_OpenRearHelmet"]}
# Check full rectangles on ribbon; the 4.9 square bundle includes the four
# jackets and their spacing, and the particular moving seam warrants testing.
meshcache={n:mesh(n) for ns in parts.values() for n in ns}
rows=[]
def screen(tag,y,p,points):
    pts=np.asarray(points).reshape(-1,3);hits=[]
    for owner,ns in parts.items():
        R,T=transforms(y,p)[owner];q=(pts-T)@R
        for n in ns:
            b=D.bounds(n);keep=np.flatnonzero(np.all((q>=b[:3])&(q<=b[3:]),axis=1))
            idx=[i for i in keep if meshcache[n][0].IsInsideSurface(*q[i])]
            if idx:
                j=D.inside(n,q[idx])
                if j is not None:hits.append(dict(part=n,point=np.round(pts[idx[j]],3).tolist(),field_hits=len(idx)))
    rows.append(dict(field=tag,yaw=y,pitch=p,hits=hits))
for y in (-20,0,20):
    for p in (-10,0,10):
        R,T=transforms(y,p)["pitch"]
        for i,h in enumerate(lay["head"]):screen("header"+str(i+1),y,p,profile(h,2.1,2.1).reshape(-1,3)@R.T+T)
        q=next(q for q in lay["motion"] if q["yaw"]==y and q["pitch"]==p)
        screen("moving ToF",y,p,profile(q["centreline"],4.9,4.9))
        screen("FFC190",y,p,next(q["corners"] for q in ffc if q["yaw"]==y and q["pitch"]==p))
        screen("pitch MG250",y,p,profile(next(q["centreline"] for q in p250 if q["yaw"]==y),3.5,1.8))
        for f in lay["fixed"]:screen(f["wire"],y,p,profile(f["centreline"][:-2],2.1,2.1))
screen("yaw MG250",0,0,profile(factory["yaw"]["centreline"],3.5,1.8))
for jr in json.loads((P/"two-head-jr-units.json").read_bytes()):
    screen(jr["role"]+" JR300",0,0,profile(jr["centreline"],3.5,1.8))
    for i,b in enumerate(jr["fans"]):screen(jr["role"]+" JR fan "+str(i),0,0,profile(b["centreline"],1.8,1.8))
# Conservative swept X bound from the eight corners of each actual moving
# member's world box. A 1-degree grid plus a rigid angular displacement bound
# encloses every unsampled position between grid points.
import itertools
centres=np.array([[-130,0,127],[-159,0,121]]);max_x=-1e6
for n in ["C19_FaceAndEars","C19_OpenRearHelmet","C19_MovingOpticsCarrier","BR_FINISHED_YAW_SADDLE","C19_Ear_1","C19_Ear_2","C19_Nose","C19_Iris_L","C19_Iris_R","C19_Pupil_L","C19_Pupil_R","Camera3_NoIR_Wide","VL53L5CX"]:
    b=D.bounds(n);corners=np.array(list(itertools.product(*zip(b[:3],b[3:]))))
    owner="yaw" if n.startswith("BR_") else "pitch";rmax=max(np.linalg.norm(corners-centres[1],axis=1))+30
    guard=2*rmax*2*math.sin(math.radians(.5)/2)
    for y in range(-20,21):
        for p in range(-10,11):
            R,T=transforms(y,p)[owner];max_x=max(max_x,np.max((corners@R.T+T)[:,0])+guard)
out=dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),fixed_receiver_min_x=lay["fixed_receiver"][0]-6,moving_head_conservative_high_x=max_x,clearance_lower_bound_x=(lay["fixed_receiver"][0]-6-max_x),rows=rows,physical_PASS=False)
(P/"changed-seam.json").write_text(json.dumps(out,indent=1)+"\n",encoding="utf8")
from collections import Counter
print(out["clearance_lower_bound_x"],Counter((r["field"],h["part"]) for r in rows for h in r["hits"]).most_common(24))

