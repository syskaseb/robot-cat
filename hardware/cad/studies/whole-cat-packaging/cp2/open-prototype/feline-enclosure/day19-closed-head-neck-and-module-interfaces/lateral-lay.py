"""Open lateral moving bay from cheek to body. Equal-length bows at the nine source poses."""
from pathlib import Path
import numpy as np, math,json
from scipy.optimize import brentq
P=Path(__file__).parent
exec((P/"shoulder-layout.py").read_text().split("# Head lead routing")[0])
S=A([-139.,12.,149.]);B=A([26.,41.,118.]);r=14.8
heads=[];paths=[];fixed=[];debits=[];poses=[];u=np.linspace(0,1,181)[:,None]
for i,h in enumerate(receipt["ToF_head"]):
    start=A(h["centreline"][0]);dy,dz=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)][i]
    s=S+dy*Y+dz*Z;lead=start+6*X;tr=s-lead;tr-=X*tr[0];n=unit(tr)
    a=arc(lead,X,n,r,math.pi/2);b=arc(a[-1]+(np.linalg.norm(tr)-2*r)*n,n,X,r,math.pi/2)
    heads.append(pack(join(line(start,lead),a,line(a[-1],b[0]),b,line(b[-1],s))))
def curve(y,p,amp):
    R,T=transforms(y,p)["pitch"];s=R@S+T;L=np.linalg.norm(B-s);t0=R@X*L;t1=X*L
    base=(2*u**3-3*u**2+1)*s+(u**3-2*u**2+u)*t0+(-2*u**3+3*u**2)*B+(u**3-u**2)*t1
    return base+amp*np.sin(math.pi*u)**2*unit(.97*Y+.24*Z)
for y in (-20,0,20):
    for p in (-10,0,10):poses.append((y,p,length(curve(y,p,0))))
stock=math.ceil(max(q[2] for q in poses))+1
for y,p,_ in poses:
    a=brentq(lambda h:length(curve(y,p,h))-stock,0,110);q=curve(y,p,a)
    d1=np.gradient(q,axis=0,edge_order=2);d2=np.gradient(d1,axis=0,edge_order=2)
    radii=np.linalg.norm(d1,axis=1)**3/np.maximum(np.linalg.norm(np.cross(d1,d2),axis=1),1e-10)
    paths.append(dict(yaw=y,pitch=p,centreline=pack(q),length=stock,inner_R_min=float(min(radii)-2.45*math.sqrt(2)),bow=a))
# Fixed lanes go forward along X, drop below the BUS work area, then approach
# the actual JP3 pad in +Y. No full-PVC radius is assigned to a solder land.
for i,h in enumerate(heads):
    f=next(q for q in prior["fixed_fans"] if q["JP3"]==receipt["ToF_fixed"][i]["JP3"])
    e=A(f["PTH_center"]);dy,dz=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)][i];g=B+dy*Y+dz*Z
    # Combined lateral/height adjustment arrives one radius before the final turn.
    e0=e-r*X-r*Y;tr=e0-g;tr-=X*tr[0];n=unit(tr);a=math.acos(1-np.linalg.norm(tr)/(2*r))
    v=arc(g,X,n,r,a);w=arc(v[-1],math.cos(a)*X+math.sin(a)*n,math.sin(a)*X-math.cos(a)*n,r,a)
    assert e0[0]>w[-1,0] and np.linalg.norm(e0[1:]-w[-1,1:])<1e-5
    path=join(v,w,line(w[-1],e0),arc(e0,X,Y,r,math.pi/2))
    fixed.append(dict(wire=f["wire"],pad=f["JP3"],centreline=pack(path),inner_R=r-1.05,mm=length(path)))
    d=dict(wire=f["wire"],JP3=f["JP3"],header=round(length(h),3),moving=stock,lane_allowance=6,fixed=round(length(path),3),ends_once=12,loss=4)
    d["uncut_plan_mm"]=math.ceil(sum(d[k] for k in ("header","moving","lane_allowance","fixed","ends_once","loss")));d["actual_cut"]=None;debits.append(d)
out=dict(moving_head_station=pack(S),fixed_shoulder_station=pack(B),head=heads,motion=paths,fixed=fixed,debits=debits,physical_PASS=False)
(P/"lateral-whole-lay.json").write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf8")
print(stock,[(q["yaw"],q["pitch"],round(q["inner_R_min"],1),round(q["bow"],1)) for q in paths], [q["uncut_plan_mm"] for q in debits])

