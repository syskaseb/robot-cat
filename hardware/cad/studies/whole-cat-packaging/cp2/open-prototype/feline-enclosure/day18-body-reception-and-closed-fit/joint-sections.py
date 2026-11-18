"""Measure the chest / moving-back overlap at three actual cross sections."""
from pathlib import Path
import runpy,json,math
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Ax1,gp_Dir,gp_Trsf,gp_Pln
from OCP.TopLoc import TopLoc_Location
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
fixed=D.shape("BR_RECESSED_CHEST");back=D.shape("BR_OVERLAP_SKULL_BACK")
rows=[];cuts=[]
for x in (-151,-133,-111):
    plane=BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(x,0,140),gp_Dir(1,0,0)),-120,120,-130,130).Face()
    cuts.append((x,plane,BRepAlgoAPI_Common(fixed,plane).Shape()))
def rot(center,axis,deg):
    t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(*center),gp_Dir(*axis)),math.radians(deg));return t
for yaw,pitch in [(0,0),(-20,-10),(20,10),(-20,10),(20,-10)]:
    tr=rot((-130,0,127),(0,0,1),yaw);tr.Multiply(rot((-159,0,121),(0,1,0),pitch))
    s=back.Moved(TopLoc_Location(tr))
    for x,plane,f in cuts:
        b=BRepAlgoAPI_Common(s,plane).Shape()
        dst=BRepExtrema_DistShapeShape(b,f)
        if not dst.IsDone():rows.append(dict(yaw=yaw,pitch=pitch,x=x,status="no common section pair"));continue
        gap=dst.Value();area=0.
        if gap<.001:
            p=GProp_GProps();BRepGProp.SurfaceProperties_s(BRepAlgoAPI_Common(f,b).Shape(),p);area=p.Mass()
        rows.append(dict(yaw=yaw,pitch=pitch,x=x,section_gap_mm=gap,section_overlap_mm2=area))
    (P/"joint-sections.json").write_bytes((json.dumps(dict(rows=rows,scope="Named planar sections and five poses only; continuous motion and full shell clearance remain open.",physical_PASS=False),indent=1)+"\n").encode())
