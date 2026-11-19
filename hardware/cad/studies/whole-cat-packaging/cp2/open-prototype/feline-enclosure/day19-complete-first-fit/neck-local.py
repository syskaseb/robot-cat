from common import *
from vtkmodules.util.numpy_support import vtk_to_numpy
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
boxes=np.array([[-177,-114,100.2,-143,-112.45,198.7],[-169.3,-114,100.25,-143.4,-100.2,101.85],[-165.8,-114,197.1,-152.55,-101.5,198.65]])
parts={'yaw':['E19_UpperYawCover','D19D_YawSaddle','BR_FLANK_HP_PAIR','MG92B_Head_pitch','PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw'],'pitch':['D19D_PitchBack','D19D_OpticsCarrier','D19D_Face','Camera3_NoIR_Wide','VL53L5CX']+[n for n in D.members if n.startswith(('D19D_Ear','D19D_Iris','D19D_Pupil','D19D_Nose'))]}
ans={}
def gap(lo,hi,b):return np.max(np.maximum(lo-b[3:],b[:3]-hi),axis=-1)
for owner,names in parts.items():
 for n in names:
    surf=mesh(n)[1];pts=vtk_to_numpy(surf.GetPoints().GetData());tri=vtk_to_numpy(surf.GetPolys().GetConnectivityArray()).reshape(-1,3)
    rad=max(np.linalg.norm(pts-[-130,0,127],axis=1))+max(np.linalg.norm(pts-[-159,0,121],axis=1))
    pad=.16+rad*math.radians(.5);worst=1e4;critical=[]
    for y in range(-20,21):
        for p in (range(-10,11) if owner=='pitch' else [0]):
            r,t=transforms(y,p)[owner];a=pts@r.T+t
            for b in boxes:
                margin=gap(a.min(axis=0),a.max(axis=0),b)
                if margin<pad+1:
                    vs=a[tri];margin=min(gap(vs.min(axis=1),vs.max(axis=1),b))
                worst=min(worst,float(margin)-pad)
                if margin<pad:critical.append([y,p,round(float(margin),3)])
    ans[n]=dict(lower_separation_mm=worst,step_cover_mm=pad,unseparated=critical)
wr('neck-local-fit.json',dict(boxes=boxes.tolist(),moving=ans,scope='added fixed guard only, enclosing component boxes or individual source-mesh triangles; 1 degree increments plus half-step displacement and mesh allowance'));print([(n,round(q['lower_separation_mm'],3)) for n,q in ans.items()])
