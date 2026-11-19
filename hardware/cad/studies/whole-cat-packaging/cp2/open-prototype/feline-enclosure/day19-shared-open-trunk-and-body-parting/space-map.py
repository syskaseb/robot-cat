"""Rasterize the changed fixed wiring bay to choose shared passages; exact named tests follow."""
from common import *
import ast,vtk
from vtkmodules.util.numpy_support import vtk_to_numpy
from scipy.ndimage import distance_transform_edt
src=(O/'day19-closed-head-neck-and-module-interfaces/changed-seam.py').read_text()
exec(src[:src.index('lay=json.loads')].replace('whole-cat19C.FCStd','whole-cat19H.FCStd'))
origin=np.array([-120,-106,38]);step=2.;N=np.array([167,107,94])
mask=np.zeros(tuple(N),dtype=bool)
parts=['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_ReSpeakerSource','E19_KeyedTail','G19_PermaProto1608','G19_U1_adapter_region','TTP223_touch','E19_BUS_PCB','E19_BUS_population','BNO085','E19_UpperYawCover','D19D_PitchBack','D19D_YawSaddle','D19D_YawMatedPair','BR_FLANK_HP_PAIR','B19_TailMatedPair','MG92B_Tail','MG92B_Head_pitch','MG92B_Head_yaw','MAIN_Pololu4853','AUX_Pololu4092','MAX98357A_amp','Pi4B_actual_PCB','PCA9685_Adafruit815_PCB','Battery_GEA223S30X6GT','Speaker','S0_body','Monitor_MOD05015','F0_FHAC0002_30A','XT60H_mated_with_boots','H19_DATA_A_Boot','G19_PiAudioBoot','G19_MIC_C_PlugAllow']
parts += [n for n in D.members if n.startswith(('OP_S1','OP_MONITOR_','WAGO','PBAY_','E19_Wago','Motor_ATO','NIGHT_INLINE','CF17_PI_PRIMARY','CF17_POWER_','CB_AMP_','HB_MIC_','CB_MAIN_','CB_PCA_')) and n!='WAGO415_data_1_0']
parts=list(dict.fromkeys(n for n in parts if n in D.members))
def addshape(poly,b):
    start=np.maximum(0,np.floor((b[:3]-origin)/step-1).astype(int));stop=np.minimum(N,np.ceil((b[3:]-origin)/step+2).astype(int));size=stop-start
    if min(size)<=0:return
    # Four half-step samples per transverse plane and two along Z keep thin walls in the screening field.
    dims=2*size;st=vtk.vtkPolyDataToImageStencil();st.SetInputData(poly);st.SetOutputOrigin(*(origin+start*step-.5));st.SetOutputSpacing(1,1,1);st.SetOutputWholeExtent(0,dims[0]-1,0,dims[1]-1,0,dims[2]-1);st.Update()
    cv=vtk.vtkImageStencilToImage();cv.SetInputConnection(st.GetOutputPort());cv.SetInsideValue(1);cv.SetOutsideValue(0);cv.SetOutputScalarTypeToUnsignedChar();cv.Update()
    vals=vtk_to_numpy(cv.GetOutput().GetPointData().GetScalars()).reshape(tuple(dims[::-1])).T.reshape(size[0],2,size[1],2,size[2],2).any(axis=(1,3,5))
    mask[tuple(slice(a,b) for a,b in zip(start,stop))]|=vals
for n in parts:
    b=D.bounds(n);_,p=mesh(n);addshape(p,b)
    if n=='E19_KeyedTail':
        # Reserve an additional band at the return side of the pitch mechanism, through its complete range.
        lo=np.maximum(0,((np.array([123,-7,117])-origin)/step).astype(int));hi=np.minimum(N,((np.array([179,26,194])-origin)/step).astype(int)+1);mask[tuple(slice(a,b) for a,b in zip(lo,hi))]=1
x,y,z=np.ogrid[:N[0],:N[1],:N[2]];x=x*step+origin[0];y=y*step+origin[1];z=z*step+origin[2]
mask|=(x<-101)|(x>206)|(y<-100)|(y>99)|(z<42)|((z>197)&~((x>=188)&(x<=205)&(y>=37)&(y<=85)&(z<=219)))|((x<-64)&(z>151)&(y>18))|((x<-65)&(y<-98))
mask|=(x>=6)&(x<=34)&(y>=-41)&(y<=-19)&(z>=101)&(z<=173)
dist=distance_transform_edt(~mask,sampling=step).astype('f4');np.savez_compressed(P/'clearance-cache.npz',dist=dist,origin=origin,step=step)
wr('space-map.json',dict(source=sha(native),members=parts,step=step,subsample=1,scope='local interior only; routing aid, conservative tail keep-out, material witnesses verified against BRep',volume_cells=int(mask.size),open_cells=int((~mask).sum())))
