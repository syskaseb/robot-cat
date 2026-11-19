"""19C upper interface in mm. New ToF stations, constant-length moving bight, source-bound FFC."""
import json,math,ast
from pathlib import Path
import numpy as np
P=Path(__file__).parent;old=P.parent/"day18-body-reception-and-closed-fit"
X,Y,Z=np.eye(3);A=np.array
def unit(q):return q/np.linalg.norm(q)
def line(a,b):return np.linspace(a,b,max(2,1+math.ceil(np.linalg.norm(b-a)/1.3)))
def arc(p,t,n,r,ang):
    u=np.linspace(0,ang,1+max(4,math.ceil(55*abs(ang))));return p+r*(np.sin(u)[:,None]*t+(1-np.cos(u))[:,None]*n)
def join(*rows):return np.vstack([rows[0],*[q[1:] for q in rows[1:]]])
def pack(q):return np.asarray(q).round(5).tolist()
def length(q):return np.linalg.norm(np.diff(q,axis=0),axis=1).sum()
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for fn in ast.parse(lib.read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(lib),"exec"))
receipt=json.loads((old/"flank-reception.json").read_bytes())
prior=json.loads((P.parent/"day19-common-floor-and-bundle-assembly"/"head-field-result.json").read_bytes())
# Head lead routing retains an open solder approach parallel to X. Two tangent
# elbows swing the four leads up the cheek. The final quadrant ends vertical.
S=A([-179.,40.,135.]);B=A([-65.,44.,115.]);rad=14.8
tilt=math.radians(33);up=math.cos(tilt)*Z+math.sin(tilt)*Y
heads=[];fixed=[];moving=[];debits=[]
for i,h in enumerate(receipt["ToF_head"]):
    dx,dy=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)][i]
    pad=A(h["centreline"][0]);g=S+dx*X+dy*Y
    finish=g.copy();g=g-rad*(math.sin(tilt)*Z+(1-math.cos(tilt))*Y)
    b0=A([g[0]-rad,pad[1],pad[2]]);u=arc(b0,X,Y,rad,math.pi/2);v=arc(A([g[0],g[1]-rad,pad[2]]),Y,Z,rad,math.pi/2)
    assert b0[0]>pad[0] and v[0,1]>=u[-1,1] and g[2]>=v[-1,2]
    head=join(line(pad,b0),u,line(u[-1],v[0]),v,line(v[-1],g),arc(g,Z,Y,rad,tilt));heads.append(pack(head))
    # At body entry turn forward into the open fixed trunk. Two smooth changes
    # take each lane to the correct face of the PCB; terminal ends along +Y.
    f=next(q for q in prior["fixed_fans"] if q["JP3"]==receipt["ToF_fixed"][i]["JP3"])
    e=A(f["PTH_center"]);g=B+dx*X+dy*Y
    # Move laterally inside the unfilled space before the PCB. Each normalised
    # tangent is shared across adjacent arcs and straight sections.
    q=arc(g,-up,X,rad,math.pi/2)
    # Common low trunk at y~37 leaves only 3 mm to the target solder face.
    # S-curve towards the middle frees a complete final 90-degree solder approach.
    shift=q[-1,1]-(e[1]-rad);a=math.acos(1-shift/(2*rad))
    w=arc(q[-1],X,-Y,rad,a);t=math.cos(a)*X-math.sin(a)*Y
    v=arc(w[-1],t,math.sin(a)*X+math.cos(a)*Y,rad,a)
    dz=e[2]-v[-1,2];ang=math.acos(1-dz/(2*rad)) if dz<2*rad else math.pi/2
    j=arc(v[-1],X,Z,rad,ang);t=math.cos(ang)*X+math.sin(ang)*Z
    j2start=j[-1]+max(0.,dz-2*rad)*Z
    k=arc(j2start,t,math.sin(ang)*X-math.cos(ang)*Z,rad,ang)
    e0=e-rad*X-rad*Y;assert e0[0]>k[-1,0] and np.linalg.norm(e0[1:]-k[-1,1:])<1e-5
    final=arc(e0,X,Y,rad,math.pi/2)
    path=join(q,w,v,j,line(j[-1],j2start),k,line(k[-1],e0),final)
    fixed.append(dict(wire=f["wire"],pad=f["JP3"],centreline=pack(path),inner_R=rad-1.05,mm=round(length(path),3)))
# At every pose a tangent alignment arc flows into a vertical rolling bight;
# two straight lengths share the surplus. No independent gains in wire stock.
poses=[(y,p) for y in (-20,0,20) for p in (-10,0,10)]
spec=[]
for y,p in poses:
    R,T=transforms(y,p)["pitch"];s=R@S+T;t=R@up
    angle=math.acos(np.clip(t@up,-1,1));rr=36.
    pre=arc(s,t,unit(up-t*(t@up)),rr,angle) if angle>1e-7 else np.array([s])
    delta=B-pre[-1];span=delta-up*(delta@up);r=np.linalg.norm(span)/2
    spec.append((y,p,pre,rr*angle,r,unit(span),delta@up))
L=math.ceil(max(l+math.pi*r+abs(dz)+6 for _,_,_,l,r,n,dz in spec))
for y,p,pre,l,r,n,dz in spec:
    lead=(L-l-math.pi*r+dz)/2;ret=lead-dz
    assert min(lead,ret)>=2 and min(36,r)-math.sqrt(2)*2.45>=31.5
    a=line(pre[-1],pre[-1]+lead*up);b=arc(a[-1],up,n,r,math.pi)
    path=join(pre,a,b,line(b[-1],B))
    moving.append(dict(yaw=y,pitch=p,centreline=pack(path),arc_R=r,inner_R_min=min(36,r)-math.sqrt(2)*2.45,length=L,legs=[lead,ret]))
for i,(h,f) in enumerate(zip(heads,fixed)):
    # 2x2 lanes offset from centre on a half-turn; account for possible lane
    # difference once. Other ends and cut loss are explicit separate quantities.
    delta=math.ceil(math.hypot(1.2,1.2)*(math.pi+math.radians(10)))
    total=length(h)+L+delta+f["mm"]+12+4
    debits.append(dict(wire=f["wire"],JP3=f["pad"],head=round(length(h),3),moving=L,lane_allowance=delta,stationary=f["mm"],both_ends_once=12,cut_loss=4,uncut_plan_mm=math.ceil(total),delivered_stock=None,actual_cut=None))
out=dict(moving_head_station=pack(S),fixed_shoulder_station=pack(B),head=heads,motion=moving,fixed=fixed,debits=debits,actual_slack=None,physical_PASS=False)
(P/"whole-head-lay.json").write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf8")
print("moving",L,"head, fixed, full",[(d["head"],d["stationary"],d["uncut_plan_mm"]) for d in debits],"maximum z",max(np.max(np.asarray(q["centreline"])[:,2]) for q in moving))

