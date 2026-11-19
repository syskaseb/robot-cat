"""Allow the free return to camber over BUS25514 at positive yaw. Solve each installed length."""
from pathlib import Path
import json,math,numpy as np
from scipy.optimize import brentq
from scipy.spatial import cKDTree
P=Path(__file__).parent;initial=json.loads((P/"whole-lay.json").read_bytes())
def cumulative(p):return np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
def length(p):return cumulative(p)[-1]
def arch(m,i,shift):
    c=np.asarray(m["cores"][i]);s=cumulative(c);u=s/s[-1];a,b=m["legs"]
    # Transport length is taken up by the straight legs of the rolling U.
    # The bend translates longitudinally. Both gripped ends retain their tangent.
    weight=np.minimum(1,np.minimum(s/max(1,a), (s[-1]-s)/max(1,b)))
    q=c.copy();q[:,0]+=shift*weight
    h=17*max(0,m["yaw"]/20)
    q[:,2]+=h*np.sin(np.pi*u)**2
    return q
targets=[math.ceil(max(length(arch(m,i,0)) for m in initial["motion"]))+.5 for i in range(4)]
rows=[]
for m in initial["motion"]:
    cores=[]
    for i,t in enumerate(targets):
        d=brentq(lambda d:length(arch(m,i,d))-t,-2,5)
        q=arch(m,i,d);cores.append(q);rows.append(dict(yaw=m["yaw"],pitch=m["pitch"],wire=i+1,constant_free_mm=t,bight_translation=d,actual_polyline_mm=length(q)))
    m["cores"]=[c.round(6).tolist() for c in cores];m["centreline"]=np.mean(cores,axis=0).round(6).tolist()
    # Centreline cross-check between independent lanes on a dense section of
    # the complete U; per-wire material is constant through all sampled poses.
    kd=[]
    for q in cores:
        ss=cumulative(q);ssnew=np.linspace(0,ss[-1],int(ss[-1]/.25)+1)
        pts=np.column_stack([np.interp(ssnew,ss,q[:,j]) for j in range(3)])
        kd.append((pts,cKDTree(pts)))
    m["min_jacket_pair_gap_sampled"]=float(min(kd[i][1].query(kd[j][0],k=1)[0].min()-2.1 for i in range(4) for j in range(i)))
for d,t in zip(initial["debits"],targets):
    d.update(moving_installed=t,moving_min=t,moving_max=t,reserve_extra=0,planned=math.ceil(t+d["head"]+d["fixed"]+d["ends_once"]+d["loss"]))
initial["constant_length_checks"]=rows;initial["bight_cross_section"]="variable free shape, over BUS at positive yaw; 17 mm maximum rise across 248 mm transport"
(P/"bus-return.json").write_bytes((json.dumps(initial,separators=(",",":"))+"\n").encode())
print(targets,min(m["min_jacket_pair_gap_sampled"] for m in initial["motion"]),[d["planned"] for d in initial["debits"]])

