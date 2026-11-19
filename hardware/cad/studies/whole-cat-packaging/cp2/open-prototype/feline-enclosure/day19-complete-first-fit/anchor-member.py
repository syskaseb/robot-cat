from common import *
from importlib.machinery import SourceFileLoader
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse,BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepTools import BRepTools
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
v=SourceFileLoader('sv',str(P/'station-survey.py')).load_module();d=v.D
def op(method,a,b):
 op=method(a,b);sh=op.Shape()
 if sh.IsNull(): raise ValueError(('null Boolean',method.__name__))
 return sh
def details(sh):return v.details(sh)
def volume(sh):return sum(q['volume'] for q in details(sh))
def cm(a,b):return volume(op(BRepAlgoAPI_Common,a,b))
driver=d.shape('B19_ToolEightAnchors');result={}
for host in ['H19_FrontFrame','E19_RearBase']:
 s=TopExp_Explorer(d.shape(host),TopAbs_SOLID).Current();orig=s
 if host=='H19_FrontFrame':
    # Full transverse bearing returns onto the second existing HY pedestal at x=-56.78.
    # Make a tie between the two upper bearers under the admitted nominal case.
    web=v.box(np.array([-69,15.8,73.35,-52.95,18.75,75.96]));web2=v.box(np.array([-68.8,16.6,73.4,-64,30.5,75.97]))
    keep=op(BRepAlgoAPI_Fuse,web,web2)
    for lo,hi in [([-74.43,16.1,73.38],[-68.1,18.61,75.96]),([-74.43,16.42,73.53],[-72.87,22.9,75.96])]:
        keep=op(BRepAlgoAPI_Fuse,keep,v.box(np.r_[lo,hi]))
    common=cm(s,keep);s=op(BRepAlgoAPI_Fuse,s,TopExp_Explorer(keep,TopAbs_SOLID).Current());print('joined',details(s),flush=True)
 else:common=None
 cs=[]
 for x in ([-70] if host=='H19_FrontFrame' else [112,122]):
    for y in ([-22.5,22.5] if host=='H19_FrontFrame' else [22.5]):
        z=70 if host=='H19_FrontFrame' else 48.52
        c=v.box(np.array([x-2.81,y-2.81,z,x+2.81,y+2.81,88.02]));s=op(BRepAlgoAPI_Cut,s,c);print('access',x,y,details(s),flush=True)
 result[host]=dict(bearer_common=common,solids=details(s),valid=BRepCheck_Analyzer(s).IsValid(),driver_before=cm(orig,driver),driver_after=cm(s,driver));wr('anchor-member.json',result)
 print(host,result[host],flush=True)
 if len(details(s))!=1 or not result[host]['valid'] or result[host]['driver_after']>.001:raise ValueError(host)
 BRepTools.Write_s(s,str(P/(host+'.anchor.tmp.brep')))
