"""Bound the added material against the retained leg poses; screen opened fuse covers and actual service stations."""
from pathlib import Path
import itertools,math,json,runpy,numpy as np
from scipy.spatial.transform import Rotation
P=Path(__file__).parent;R=next(x for x in P.parents if (x/'.git').exists());H=R/'hardware'
def rd(p):return json.loads(p.read_bytes())
def wr(n,v):(P/n).write_bytes((json.dumps(v,indent=1)+'\n').encode())
layout=rd(P.parent/'motion-layout.json');axes=rd(H/'simulation/p0/e6-leg-compatibility.json')['axes'];inv={q['object']:q['bounds_mm'] for q in layout['inventory']};J={(q['code'],q['stage']):q for q in axes};leg=[]
for i,q in enumerate(layout['poses']):
 for code,x in q['legs'].items():
    T=np.eye(4);z=-1e9
    for stage,deg in zip(['Hip','Knee','Ankle'],x['angles_delta_degrees']):
        a=J[code,stage];pv=np.array(a['pivot_mm']);r=Rotation.from_rotvec(np.array(a['axis'])*math.radians(deg)).as_matrix();m=np.eye(4);m[:3,:3]=r;m[:3,3]=pv-r@pv;T=T@m
        for n in layout['membership'][code][stage]:
            pts=np.array(list(itertools.product(*zip(*inv[n]))))@T[:3,:3].T+T[:3,3];z=max(z,float(max(pts[:,2])))
    leg.append(dict(pose=i,code=code,leg=x['physical_leg'],zmax=z))
s=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](P/'whole-cat19G.FCStd')
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
fuse=[]
for k in ['F_HY','F_HP','F_TY','F_PI','F_AUX']:
 name='PBAY_'+k;b=s.bounds(name);lo=b[:3].copy();lo[2]=b[5];hi=b[3:].copy();hi[2]+=21.45
 flap=BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape();hits=[]
 for n in ['E19_ForeBase','E19_RearBase','Pi4B_actual_PCB','MAIN_Pololu4853','AUX_Pololu4092','PCA9685_Adafruit815_PCB','BATTERY' ,'Battery_GEA223S30X6GT','PBAY_P_SYS','PBAY_P_REAR']:
    if n not in s.members:continue
    a=s.bounds(n)
    if np.any(a[:3]>=hi) or np.any(a[3:]<=lo):continue
    op=BRepAlgoAPI_Common(flap,s.shape(n));g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
    if g.Mass()>.001:hits.append([n,round(g.Mass(),3)])
 fuse.append(dict(case=k,space_above_case_mm=21.45,incremental_box=[*lo,*hi],neighbours=hits,procedure='lift the isolated holder from its open seat before unlatching when mounted lift conflicts; release its leads from shared ties and lift adjacent module as necessary'))
wr('assembly-check.json',dict(leg_pose_bounds=leg,added_side_min_z=82,vertical_gap_at_retained_samples=82-max(q['zmax'] for q in leg),rigid_legs_only=True,leg_loom_dress_and_factory_slack_unmeasured=True,five_fuse_covers=fuse,cover_class='conservative handling field; the complete cap can also be opened with holder lifted',battery='isolate; remove RR door and its two inline seats; reach and separate the XT60 halves by their housings before sliding the battery laterally. No pulling the battery to obtain unplug distance. Unmeasured actual lead and boot reach.',physical_PASS=False))
print(len(leg),82-max(q['zmax'] for q in leg),[(q['case'],q['neighbours']) for q in fuse])
