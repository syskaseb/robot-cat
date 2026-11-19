from common import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
d=Saved(native);m=rd(P/'space-map.json')['members']
def screen(b,ignore):
 a=np.array(b);s=BRepPrimAPI_MakeBox(gp_Pnt(*a[:3]),gp_Pnt(*a[3:])).Shape();out=[]
 for n in m:
    if n in ignore:continue
    z=d.bounds(n)
    if np.any(z[:3]>=a[3:]-.0001) or np.any(a[:3]>=z[3:]-.0001):continue
    sh=BRepAlgoAPI_Common(s,d.shape(n)).Shape();g=GProp_GProps();BRepGProp.VolumeProperties_s(sh,g)
    if g.Mass()>.00001:
        v=Bnd_Box();BRepBndLib.AddOptimal_s(sh,v,False,False);out.append(dict(n=n,mm3=round(g.Mass(),2),bounds=np.round([*v.CornerMin().Coord(),*v.CornerMax().Coord()],2).tolist()))
 return out
bay=[-15,-5,75,9,45,93];pull=[-15,20,75,9,59,93];hand=[-14,47,74,8,103,94]
rows={}
for n,b in [('connector',bay),('battery_half_pull14',pull),('fingers_before_cell_extraction',hand),('all_five_D_FL_faces',[124,-60,115.4,150,-44,122.2])]:
 rows[n]=dict(field=b,hits=screen(b,['XT60H_mated_with_boots','E19_BatteryDoor']));print(n,rows[n]['hits'],flush=True)
wr('service-first.json',rows)
