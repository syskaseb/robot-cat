from common import *
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
d=Saved(native);out={}
for a,b in [('E19_FrontShroud','E19_ForeBase'),('E19_FrontShroud','E19_ForeLid'),('E19_FrontShroud','F19_ForeCap'),('E19_ReSpeakerSource','E19_ForeLid')]:
 s=BRepAlgoAPI_Common(d.shape(a),d.shape(b)).Shape();ex=TopExp_Explorer(s,TopAbs_SOLID);rows=[]
 while ex.More():
    sh=ex.Current();g=GProp_GProps();BRepGProp.VolumeProperties_s(sh,g);bb=Bnd_Box();BRepBndLib.AddOptimal_s(sh,bb,False,False);rows.append([round(g.Mass(),4),[*np.round(bb.CornerMin().Coord(),2),*np.round(bb.CornerMax().Coord(),2)]]);ex.Next()
 out[a+' / '+b]=rows
for n in ['E19_ForeBase','E19_FrontShroud','E19_ForeLid','F19_ForeCap','MAX98357A_amp','Speaker','Pi_USB_DATA_Delock_mating','CF17_PI_PRIMARY_USB_A_front','CF17_PI_PRIMARY_USB_A_rear']:out[n]=d.bounds(n).tolist()
wr('source-interfaces.json',out);print(str(out)[:4000])
