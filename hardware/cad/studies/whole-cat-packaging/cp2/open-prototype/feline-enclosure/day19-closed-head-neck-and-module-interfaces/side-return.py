"""Head and shoulder share an open horizontal rolling loop, above the positive cheek."""
from pathlib import Path
import numpy as np,math,json
P=Path(__file__).parent
exec((P/"shoulder-layout.py").read_text().split("# Head lead routing")[0])
S=A([-146.,22.,168.]);B=A([-56.,17.,138.]);rs=14.3
offsets=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)]
heads=[];fixed=[];motion=[];data=[]
for i,record in enumerate(receipt["ToF_head"]):
    dx,dz=offsets[i];start=A([-206.,5.08,[107.97,105.43,102.89,100.35][i]]);e=S+dx*X+dz*Z
    # A radiused rise above the pitch shaft, then a lateral tangent at the cheek.
    endX=e-rs*(X+Y);delta=endX-start;tr=delta-X*delta[0];n=unit(tr);h=np.linalg.norm(tr)
    if h>=2*rs:ang=math.pi/2;straight=h-2*rs
    else:ang=math.acos(1-h/(2*rs));straight=0.
    a=arc(start+5.3*X,X,n,rs,ang);t=math.cos(ang)*X+math.sin(ang)*n
    b=arc(a[-1]+straight*t,t,math.sin(ang)*X-math.cos(ang)*n,rs,ang)
    assert endX[0]>=b[-1,0]
    q=join(line(start,start+5.3*X),a,line(a[-1],b[0]),b,line(b[-1],endX),arc(endX,X,Y,rs,math.pi/2))
    heads.append(pack(q))
    f=next(q for q in prior["fixed_fans"] if q["JP3"]==receipt["ToF_fixed"][i]["JP3"]);pad=A(f["PTH_center"])
    g=B+dx*X+dz*Z
    # Centre bay below BUS and audio. The final turn into JP3 includes a
    # vertical S on the positive-Y approach, outside the speaker envelope.
    startdrop=g-12*Y;turn=arc(startdrop,-Y,X,rs,math.pi/2)
    low=116.2+dz
    angle=math.acos(1-(turn[-1,2]-low)/(2*rs))
    v=arc(turn[-1]+15*X,X,-Z,rs,angle)
    w=arc(v[-1],math.cos(angle)*X-math.sin(angle)*Z,math.sin(angle)*X+math.cos(angle)*Z,rs,angle)
    e0=A([pad[0]-rs,w[-1,1],low])
    endturn=arc(e0,X,Y,rs,math.pi/2)
    rise=pad[2]-low;theta=math.acos(1-rise/(2*rs))
    a=arc(endturn[-1],Y,Z,rs,theta)
    b=arc(a[-1],math.cos(theta)*Y+math.sin(theta)*Z,math.sin(theta)*Y-math.cos(theta)*Z,rs,theta)
    assert b[-1,1]<=pad[1] and np.linalg.norm(b[-1,[0,2]]-pad[[0,2]])<1e-5
    path=join(line(g,startdrop),turn,line(turn[-1],v[0]),v,w,line(w[-1],e0),endturn,a,b,line(b[-1],pad))
    fixed.append(dict(wire=f["wire"],JP3=f["JP3"],centreline=pack(path),mm=round(length(path),3)))
spec=[]
for y in (-20,0,20):
    for p in (-10,0,10):
        R,T=transforms(y,p)["pitch"];s=R@S+T;t=R@Y
        ang=math.acos(np.clip(t@Y,-1,1))
        pre=arc(s,t,unit(Y-t*(t@Y)),36,ang) if ang>1e-7 else np.array([s])
        d=B-pre[-1];v=d-Y*d[1];rr=np.linalg.norm(v)/2
        spec.append((y,p,pre,36*ang,rr,unit(v),d[1]))
L=math.ceil(max(l+math.pi*rr+abs(d)+4 for y,p,pre,l,rr,n,d in spec))
for y,p,pre,l,rr,n,d in spec:
    a=(L-l-math.pi*rr+d)/2;b=a-d
    q=arc(pre[-1]+a*Y,Y,n,rr,math.pi)
    path=join(pre,line(pre[-1],q[0]),q,line(q[-1],B))
    motion.append(dict(yaw=y,pitch=p,centreline=pack(path),inner_R_min=min(36,rr)-math.sqrt(2)*2.45,length=L,legs=[a,b]))
for h,f in zip(heads,fixed):
    d=dict(wire=f["wire"],JP3=f["JP3"],head=round(length(h),3),moving=L,lane_allowance=6,fixed=f["mm"],ends_once=12,cut_loss=4)
    d["plan_mm"]=math.ceil(sum(d[k] for k in ("head","moving","lane_allowance","fixed","ends_once","cut_loss")));d["actual_cut"]=None;data.append(d)
out=dict(head_receiver=pack(S),fixed_receiver=pack(B),head=heads,motion=motion,fixed=fixed,debits=data,physical_PASS=False)
(P/"side-return.json").write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf8")
print(data, "inner R",min(q["inner_R_min"] for q in motion),"lateral max",max(np.array(q["centreline"])[:,1].max() for q in motion))

