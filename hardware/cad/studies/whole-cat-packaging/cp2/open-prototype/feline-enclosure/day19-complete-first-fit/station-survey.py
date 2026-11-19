from common import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
D=Saved(native)
def box(b):return BRepPrimAPI_MakeBox(gp_Pnt(*b[:3]),gp_Pnt(*b[3:])).Shape()
def details(s):
 ex=TopExp_Explorer(s,TopAbs_SOLID);ans=[]
 while ex.More():
    a=ex.Current();p=GProp_GProps();BRepGProp.VolumeProperties_s(a,p);bb=Bnd_Box();BRepBndLib.AddOptimal_s(a,bb,False,False)
    if p.Mass()>.0001:ans.append(dict(volume=round(p.Mass(),4),bounds=np.round([*bb.CornerMin().Coord(),*bb.CornerMax().Coord()],3).tolist()))
    ex.Next()
 return ans
names=rd(H19/'space-map.json')['members'];names+=[n for n in D.members if n.startswith(('H01_source_','CB_PI','HB_PI','CB_AUX','CF17_BUS_CSK','YAW_SHAFT_','Tail608','Yaw608','BR_FINISHED','TAIL_')) and n!='TAIL_ROTATING_HOLLOW_REAL_ROOT']
names=list(dict.fromkeys(names))
def screen(b,skip,shape=None):
 shape=box(b) if shape is None else shape;out={}
 for n in names:
    if n in skip or n not in D.members:continue
    t=D.bounds(n)
    if np.any(t[:3]>=b[3:]) or np.any(b[:3]>=t[3:]):continue
    hits=details(BRepAlgoAPI_Common(shape,D.shape(n)).Shape())
    if hits:out[n]=hits
 return out
if __name__=='__main__':
 out={}
 for lab in ['F_AUX','F_HY','F_HP','F_TY','F_PI']:
    n='PBAY_'+lab;b=D.bounds(n);out[lab]=screen(b,[n],D.shape(n))
 for k,b in [('G1_body',[-56,-64,52,-19,-42,63]),('G1_all_mouths',[-54.5,-80,54,-20.5,-64,61])]:
    out[k]=screen(np.asarray(b),['WAGO615_power_0_0'])
 wr('source-stations.json',out)
 print({k:[(n,round(sum(a['volume'] for a in s),1)) for n,s in v.items()] for k,v in out.items()})
