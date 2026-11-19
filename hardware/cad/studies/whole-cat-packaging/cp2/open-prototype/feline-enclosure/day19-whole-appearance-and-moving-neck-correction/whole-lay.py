"""Tilted rolling return with four transported circular jacket lanes and separate head-servo units."""
from pathlib import Path
import json,numpy as np,math,ast
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
exec((C/"shoulder-layout.py").read_text().split("# Head lead routing")[0].replace("P=Path(__file__).parent;",""))
old=json.loads((C/"side-return.json").read_bytes());heads=[];fixed=[];motion=[]
ang=math.radians(35);t=math.cos(ang)*Y+math.sin(ang)*Z
rc=14.3
transition=arc(np.zeros(3),Y,Z,rc,ang)
delta=transition[-1];S=A(old["head_receiver"])+delta;B=A(old["fixed_receiver"])+delta
for h,f in zip(old["head"],old["fixed"]):
    h=A(h);g=A(f["centreline"])
    heads.append(pack(join(h,h[-1]+transition)))
    fixed.append({**f,"centreline":pack(join(g[0]+transition[::-1],g)),"mm":round(length(g)+rc*ang,3)})
spec=[]
for y in [-20,0,20]:
 for p in [-10,0,10]:
    R,T=transforms(y,p)["pitch"];s=R@S+T;u=R@t;angle=math.acos(np.clip(u@t,-1,1))
    pre=arc(s,u,unit(t-u*(t@u)),36,angle) if angle>1e-7 else np.array([s])
    d=B-pre[-1];v=d-t*(d@t);r=np.linalg.norm(v)/2
    spec.append((y,p,pre,36*angle,r,unit(v),d@t,R,T))
L=math.ceil(max(l+math.pi*r+abs(d)+1 for y,p,pre,l,r,n,d,R,T in spec))
# At each endpoint, lay the four real jackets in the X / tangent-normal plane.
# Clock continuously from the moving printed seat to the fixed printed seat.
offsets=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)]
for y,p,pre,l,r,n,d,R,T in spec:
    a=(L-l-math.pi*r+d)/2;b=a-d
    q=arc(pre[-1]+a*t,t,n,r,math.pi);path=join(pre,line(pre[-1],q[0]),q,line(q[-1],B))
    tang=np.array([unit(v) for v in np.gradient(path,axis=0)]);arc_s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))];alpha=arc_s/arc_s[-1]
    vx=R@X;axes=[]
    for u in tang:
        vx=unit(vx-u*(vx@u));axes.append(vx.copy())
    axes=np.array(axes);desired=X;endrot=math.atan2(np.cross(axes[-1],desired)@tang[-1],axes[-1]@desired)
    cores=[]
    for dx,dz in offsets:
        clock=alpha*endrot;c=np.cos(clock)[:,None];sn=np.sin(clock)[:,None]
        v=axes*c+np.cross(tang,axes)*sn
        # fixed and moving ducts end with all lanes at identical ordering in world Z.
        # The half turn interchanges local handedness; identify each real fixed pad
        # run at the matching lateral position below.
        w=np.cross(v,tang)
        core=path+dx*v+dz*w;cores.append(pack(core))
    motion.append(dict(yaw=y,pitch=p,centreline=pack(path),cores=cores,mm=L,minimum_design_inner_R=min(36,r)-1.2*math.sqrt(2)-1.05,legs=[a,b]))
# Match physical square bundle offsets and fan-outs to the real tilted mouths.
# Duct changes clock through each static 35-degree elbow as well.
for i,(dx,dz) in enumerate(offsets):
    oldh=A(old["head"][i]);oldf=A(old["fixed"][i]["centreline"])
    theta=np.linspace(0,ang,len(transition))
    factor=np.cos(theta)[:,None]*Z-np.sin(theta)[:,None]*Y
    headturn=A(old["head_receiver"])+transition+dx*X+dz*factor
    # Return tangent reverses the normal under transport. Cross over the four lanes
    # in the open fixed bank by permuting the fan entry and route to its own pad.
    fturn=A(old["fixed_receiver"])+transition+dx*X-dz*factor
    # Retain the individual pad. Spread the 2.4-mm difference over the existing
    # fixed-side transport rather than creating an electrical splice.
    run=oldf.copy();dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(run,axis=0),axis=1))]
    blend=np.clip(dist/47,0,1);run-=2*dz*(1-3*blend**2+2*blend**3)[:,None]*Z
    heads[i]=pack(join(oldh,headturn));fixed[i]["centreline"]=pack(join(fturn[::-1],run));fixed[i]["mm"]=length(fixed[i]["centreline"])
debits=[]
for i in range(4):
    h=length(heads[i]);f=fixed[i]["mm"];qs=[length(q["cores"][i]) for q in motion]
    debits.append(dict(wire=fixed[i]["wire"],JP3=fixed[i]["JP3"],head=h,fixed=f,moving_min=min(qs),moving_max=max(qs),reserve_extra=3,ends_once=12,loss=4,planned=math.ceil(h+f+max(qs)+3+12+4),actual_cut=None))
fac=json.loads((P.parent/"day18-body-reception-and-closed-fit/flank-reception.json").read_bytes())["yaw"]
s=A(fac["centreline"][0]);a=arc(s+2*X,X,Z,22,math.pi/2);b=arc(a[-1]+19*Z,Z,X,19,math.pi/2)
c=arc(b[-1]+30*X,X,Y,23,math.pi);stem=2+22*math.pi/2+19+19*math.pi/2+30+23*math.pi
yline=join(line(s,a[0]),a,line(a[-1],b[0]),b,line(b[-1],c[0]),c,line(c[-1],c[-1]-(223.55-stem)*X))
shift=yline[-1]-A(fac["centreline"][-1])
jr=json.loads((C/"two-head-jr-units.json").read_bytes())
for j in jr:
    p=A(j["mated_at"])+(shift if j["role"]=="yaw" else 0);r=23 if j["role"]=="pitch" else 24
    n=Y if j["role"]=="pitch" else -Y
    bend=arc(p,-X,n,r,math.pi);end=bend[-1]+(246-r*math.pi)*X
    j.update(mated_at=pack(p),centreline=pack(join(bend,line(bend[-1],end))),transport_positive_X=246-r*math.pi,return_bight=r*math.pi,inner_R=r-math.hypot(1.75,.9))
    for k,fan in enumerate(j["fans"]):
        u=math.cos(.125*(k-1))*X+math.sin(.125*(k-1))*Y;fan["centreline"]=pack(join(line(end,end+25*u),line(end+25*u,end+42*u)))
data=dict(head_receiver=pack(S),fixed_receiver=pack(B),head=heads,fixed=fixed,motion=motion,debits=debits,yaw_factory={**fac,"centreline":pack(yline),"key_tip":pack(A(fac["key_tip"])+shift)},yaw_pair_translation=pack(shift),jr=jr,physical_PASS=False)
(P/"whole-lay.json").write_bytes((json.dumps(data,separators=(",",":"))+"\n").encode());print(L,min(q["minimum_design_inner_R"] for q in motion),[q["planned"] for q in debits],pack(shift))

