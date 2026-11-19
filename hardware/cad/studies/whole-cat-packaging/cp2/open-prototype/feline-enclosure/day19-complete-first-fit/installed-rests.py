from common import *
from importlib.machinery import SourceFileLoader
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.BRepTools import BRepTools
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Ax1,gp_Dir,gp_Pnt,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
v=SourceFileLoader('sv',str(P/'station-survey.py')).load_module()
q=rd(P/'remote-pulldown-lay.json');a=np.radians(20);rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
c=np.linalg.solve(np.eye(2)-rot,np.array(q['stations']['20']['0'][:2])-rot@np.array(q['stations']['0']['0'][:2]))
r={}
for role,host in [('yaw','E19_ForeLid'),('pitch','E19_UpperYawCover'),('tail','E19_RearLid')]:
 s=TopoDS_Shape();assert BRepTools.Read_s(s,str(P/(role+'-tray.tmp.brep')),BRep_Builder())
 for angle in ([-20,0,20] if role=='pitch' else [0]):
    t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(*c,0),gp_Dir(0,0,1)),np.radians(angle));sh=BRepBuilderAPI_Transform(s,t,True).Shape()
    bb=Bnd_Box();BRepBndLib.AddOptimal_s(sh,bb,False,False);b=np.r_[bb.CornerMin().Coord(),bb.CornerMax().Coord()];skip=[host,'G19_RemoteR_'+role]
    if angle:skip+=['D19D_YawSaddle','BR_FLANK_HP_PAIR','MG92B_Head_pitch','D19D_PitchBack']
    r[role+str(angle)]=v.screen(b,skip,sh);wr('installed-rests.json',r)
print(r)
