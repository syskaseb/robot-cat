from pathlib import Path
import json,math,numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.XCAFDoc import XCAFDoc_DocumentTool,XCAFDoc_ShapeTool
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
P=Path(__file__).parent;H=next(p for p in P.parents if (p/'electronics').is_dir())
d=TDocStd_Document(TCollection_ExtendedString('Mic'));r=STEPCAFControl_Reader();r.SetNameMode(True)
r.ReadFile(str(H/'reference/head-electronics-2026-09-22/ReSpeakerLitev1.1.step'));assert r.Transfer(d)
st=XCAFDoc_DocumentTool.ShapeTool_s(d.Main());seq=TDF_LabelSequence();st.GetFreeShapes(seq)
def name(l):
 a=TDataStd_Name()
 return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else ''
found=[]
def walk(l,loc):
 subs=TDF_LabelSequence();st.GetComponents_s(l,subs,False)
 for i in range(1,subs.Length()+1):
    c=subs.Value(i);ref=TDF_Label();st.GetReferredShape_s(c,ref);pos=loc.Multiplied(st.GetLocation_s(c))
    if name(c)=='USB1' or 'USB_C_Receptacle' in name(ref):
        shape=st.GetShape_s(ref).Moved(pos);b=Bnd_Box();BRepBndLib.AddOptimal_s(shape,b,False,False);found.append([name(c),name(ref),list(b.CornerMin().Coord()),list(b.CornerMax().Coord())])
    elif st.IsAssembly_s(ref):walk(ref,pos)
walk(seq.Value(1),TopLoc_Location());assert len(found)==1,found
# The registration used for all 484 bodies mapped the two source hole axes to the actual fasteners.
# Source holes span a long edge diagonally: original 83.6 direction is X, installed long direction +Y.
a=np.array([42.73,-76.375]);b=np.array([100.44,-105.295]);d0=np.array([-50.84,11.8])
from xml.etree import ElementTree as X
import runpy
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](P.parent/'day19-connected-servo-usb-and-closure/whole-cat19F.FCStd')
dst=[(S.bounds('HB_MIC_'+str(i)+'_nutwasher')[:3]+S.bounds('HB_MIC_'+str(i)+'_nutwasher')[3:])/2 for i in range(2)]
v=dst[1][:2]-dst[0][:2];u=b-a;t=math.atan2(v[1],v[0])-math.atan2(u[1],u[0]);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
lo=np.array(found[0][2]);hi=np.array(found[0][3]);ctr=(lo+hi)/2
# Receptacle projects off its nearest board edge. Determine which of the four side faces is outermost.
p=dst[0][:2]+R@(ctr[:2]-a);m=S.bounds('E19_ReSpeakerSource');wh=np.abs(R)@((hi-lo)[:2]);mb=np.r_[p-wh/2,p+wh/2]
options=[(abs(mb[0]-m[0]),0,-1),(abs(mb[1]-m[1]),1,-1),(abs(mb[2]-m[3]),0,1),(abs(mb[3]-m[4]),1,1)]
gap,j,sg=min(options);axis=[0,0,0];axis[j]=sg;p[j]+=sg*wh[j]/2
z0=S.bounds('HB_MIC_0_nutwasher')[2]-1.51
res=dict(instance=found[0][0],supplier=found[0][1],source_bounds=[*lo,*hi],installed_xy_bounds=mb.tolist(),nearest_outer_edge_gap_mm=gap,mouth=[*p,ctr[2]+z0],outward_axis=axis,registration='supplier USB1 assembly via both current hole centres; case-face midpoint, project approach axis at nearest board outer edge')
pivot=(dst[0][:2]+dst[1][:2])/2
res['source_19F_mouth']=res['mouth'][:];res['source_19F_axis']=axis
res['pivot_xy']=pivot.tolist();res['mouth']=[*(2*pivot-np.array(res['mouth'][:2])),res['mouth'][2]]
res['outward_axis']=[-axis[0],-axis[1],0]
(P/'mic-port.json').write_bytes((json.dumps(res,indent=1)+'\n').encode());print(res)
