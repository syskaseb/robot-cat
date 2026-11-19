from common import *
from importlib.machinery import SourceFileLoader
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
v=SourceFileLoader('sv',str(P/'station-survey.py')).load_module();d=v.D;old=Saved(H19/'whole-cat19H.FCStd')
def cm(a,b):return sum(q['volume'] for q in v.details(BRepAlgoAPI_Common(a,b).Shape()))
r={};c={}
for host,xs in [('H19_FrontFrame',[-80,-70]),('E19_RearBase',[112,122])]:
 s=d.shape(host);oldshape=old.shape(host)
 for x in xs:
    for y in [-22.5,22.5]:
        box=v.box(np.array([x-4.62,y-4.62,36,x+4.62,y+4.62,45.52]));q=cm(s,box);qq=cm(oldshape,box);r[str([x,y])]=dict(native_land_volume=q,H_land_volume=qq,tool_common=cm(s,d.shape('B19_ToolEightAnchors')) if y<0 and x==xs[0] else None)
for role,n in [('pitch','E19_UpperYawCover'),('yaw','E19_ForeLid'),('tail','E19_RearLid')]:
 rod='G19_RemoteR_'+role;c[rod]=cm(d.shape(n),d.shape(rod))
b=np.array([-53,-55.5,54.45,-16.01,-36.8,59.875]);ports=v.screen(b,[],v.box(b))
p='PBAY_P_AUX';pa=v.screen(d.bounds(p),[p],d.shape(p))
wr('load-and-seats.json',dict(anchors=r,installed_R_common=c,front_power_used_approach=ports,P_AUX_full=pa));print(r,c,ports,pa)
