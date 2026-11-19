"""Length-retaining return behind the head. Both free legs point into the body."""
from pathlib import Path
import json,math,numpy as np
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
exec((C/"shoulder-layout.py").read_text().split("# Head lead routing")[0].replace("P=Path(__file__).parent;",""))
old=json.loads((C/"side-return.json").read_bytes());src=(P/"whole-lay.py").read_text()
S=A([-151.,-40.,161.]);B=A([-57.,49.,138.]);t=X;offsets=[(-1.2,-1.2),(1.2,-1.2),(-1.2,1.2),(1.2,1.2)]
heads=[];fixed=[];motion=[];rs=15.8
for i,(dy,dz) in enumerate(offsets):
    start=A(old["head"][i][0]);end=S+dy*Y+dz*Z
    delta=end-start;v=delta-X*delta[0];n=unit(v);h=np.linalg.norm(v)
    a=arc(start+4.5*X,X,n,rs,math.pi/2);b=arc(a[-1]+(h-2*rs)*n,n,X,rs,math.pi/2)
    heads.append(pack(join(line(start,a[0]),a,line(a[-1],b[0]),b,line(b[-1],end))))
    g=B-dy*Y+dz*Z;p=A(old["fixed"][i]["centreline"][-1]);target_y=-10+dy
    ra=(g[1]-target_y)/2;turn=arc(g,-X,-Y,ra,math.pi)
    low=116+dz;angle=math.acos(1-(turn[-1,2]-low)/(2*rs))
    down=arc(turn[-1]+25*X,X,-Z,rs,angle);up=arc(down[-1],math.cos(angle)*X-math.sin(angle)*Z,math.sin(angle)*X+math.cos(angle)*Z,rs,angle)
    e0=A([p[0]-rs,up[-1,1],low]);f=arc(e0,X,Y,rs,math.pi/2)
    angle=math.acos(1-(p[2]-low)/(2*rs));a=arc(f[-1],Y,Z,rs,angle);b=arc(a[-1],math.cos(angle)*Y+math.sin(angle)*Z,math.sin(angle)*Y-math.cos(angle)*Z,rs,angle)
    path=join(turn,line(turn[-1],down[0]),down,up,line(up[-1],e0),f,a,b,line(b[-1],p))
    fixed.append(dict(wire=old["fixed"][i]["wire"],JP3=old["fixed"][i]["JP3"],centreline=pack(path),mm=length(path)))
active=src[src.index("spec=[]"):src.index("# Match physical")]
active=active.replace("vx=R@X","vx=R@Y").replace("desired=X","desired=-Y").replace("w=np.cross(v,tang)","w=np.cross(tang,v)")
exec(active)
exec(src[src.index("debits=[]"):src.index("fac=json.loads")])
# Yaw supply: keep live case approach and first lead below the Pi until beyond
# its forward edge. Shift the purchased keyed pair wholly with the new delivery.
fac=json.loads((P.parent/"day18-body-reception-and-closed-fit/flank-reception.json").read_bytes())["yaw"]
s=A(fac["centreline"][0]);a=arc(s+3*X,X,-Y,22,math.pi/2);b=arc(a[-1]-4*Y,-Y,Z,20,math.pi/2)
c=arc(b[-1]+14*Z,Z,X,21,math.pi/2);u=arc(c[-1]+10*X,X,Y,22,math.pi)
remain=223.55-3-4-14-10-(22+20+21+22)*math.pi/2-22*math.pi/2
assert remain>0
yline=join(line(s,a[0]),a,line(a[-1],b[0]),b,line(b[-1],c[0]),c,line(c[-1],u[0]),u,line(u[-1],u[-1]-remain*X))
shift=yline[-1]-A(fac["centreline"][-1]);jr=json.loads((C/"two-head-jr-units.json").read_bytes())
# Both mated exits point toward -X. Curl away from their own full housing;
# pitch occupies negative Y, yaw positive Y, sharing no purchased length.
for j in jr:
    p=A(j["mated_at"])+(shift if j["role"]=="yaw" else 0);r=22.5
    n=unit((Y+.35*Z) if j["role"]=="yaw" else (-Y+.23*Z))
    bend=arc(p,-X,n,r,math.pi);end=bend[-1]+(246-r*math.pi)*X
    j.update(mated_at=pack(p),centreline=pack(join(bend,line(bend[-1],end))),transport_positive_X=246-r*math.pi,return_bight=r*math.pi,inner_R=r-math.hypot(1.75,.9))
    for k,fan in enumerate(j["fans"]):
        u=math.cos(.125*(k-1))*X+math.sin(.125*(k-1))*Y;fan["centreline"]=pack(join(line(end,end+25*u),line(end+25*u,end+42*u)))
exec(src[src.index("data=dict"):])

