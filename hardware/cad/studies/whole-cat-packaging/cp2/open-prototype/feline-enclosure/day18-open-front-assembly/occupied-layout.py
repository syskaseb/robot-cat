"""One open-floor fixed yaw lay, yaw-carried pitch unit and connected upper ToF bight."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
P=Path(__file__).parent
previous=json.loads((P.parent/"day18-front-insert-correction"/"insert-regions.json").read_bytes())
X,Y,Z=np.eye(3)
def unit(a):return a/np.linalg.norm(a)
def arc(p,t,n,r,a):
    return np.array([p+r*(math.sin(b)*t+(1-math.cos(b))*n) for b in np.linspace(0,a,max(5,1+math.ceil(a*26)))])
def line(p,q):return np.linspace(p,q,max(2,1+math.ceil(np.linalg.norm(q-p)/2)))
def join(*aa):return np.vstack([aa[0],*[a[1:] for a in aa[1:]]])
def pack(a):return np.array(a).round(6).tolist()
def motion(y,p):
    a,b=map(math.radians,(y,p));yc=np.array([-130,0,127]);pc=np.array([-159,0,121])
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    return rz@ry,yc+rz@(pc-ry@pc-yc)
r=25
# Rise diagonally around the stepped front of the real P02 floor. The fixed
# flat return is below the Pi PCB and above the short factory power pair.
s=np.array([-119.5,0,53.2]);v=unit(.68*Y+math.sqrt(1-.68**2)*Z)
a=arc(s,X,v,r,math.pi/2);b=arc(a[-1],v,X,r,math.pi/2)
c=line(b[-1],b[-1]+30*X);d=arc(c[-1],X,-Y,r,math.pi)
remaining=250-11.45-15-2*math.pi*r-30
e=line(d[-1],d[-1]-remaining*X)
yaw=join(a,b,c,d,e)
def factory(name,ps,t):
    return dict(name=name,centreline=pack(ps),key_tip=pack(ps[-1]+15*t),key_axis=pack(t),free=223.55,stub=11.45,key=15,raw=250)
jr=[factory("factory_yaw",yaw,-X)]
# The second real factory unit leaves the fork outboard and turns toward the
# rear before its one complete roll in the yaw-only cheek. Drift separates turns.
s=np.array([-159.,-43.8,131.5]);a=arc(s,-Y,X,25,math.pi/2)
angle=2*math.pi
q=np.linspace(0,angle,163);drift=18.
b=np.array([a[-1]+25*(math.sin(t)*X+(1-math.cos(t))*Z)+drift*(t/angle-math.sin(t)/angle)*Y for t in q])
roll=quad(lambda t:math.hypot(25,drift*(1-math.cos(t))/angle),0,angle)[0]
c=line(b[-1],b[-1]+(223.55-math.pi*12.5-roll)*X)
jr.append(factory("factory_pitch",join(a,b,c),X))
# Upper moving ToF return changes primarily across Y. Build each pose from
# real owners and a constant moving stock, maintaining full width and thickness.
S=np.array([-139.,40.,148.]);B=np.array([-104.,-46.,158.]);poses=[]
for y in (-20,0,20):
    for p in (-10,0,10):
        R,T=motion(y,p);s=R@S+T;delta=B-s;trans=delta-X*delta[0];rr=np.linalg.norm(trans)/2
        poses.append((y,p,s,delta[0],unit(trans),rr))
free=5*math.ceil(max(math.pi*q[-1]+abs(q[3])+26 for q in poses)/5)
tof=[]
for y,p,s,dx,n,rr in poses:
    l=(free-math.pi*rr+dx)/2
    a=line(s,s+l*X);b=arc(a[-1],X,n,rr,math.pi);c=line(b[-1],B)
    ps=join(a,b,c);w=unit(np.cross(X,n));t=np.array([unit(h) for h in np.gradient(ps,axis=0)])
    h=np.cross(t,w);corners=np.stack([ps+i*5.2*w+j*1.45*h for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]],axis=1)
    tof.append(dict(yaw=y,pitch=p,centreline=pack(ps),corners=pack(corners),total=free,inner_R=rr-1.45))
header=[]
for src in previous["ToF_header"]:
    pt=np.array(src["centreline"][0]);begin=pt+6*X;delta=S-begin
    n=unit(delta-X*delta[0]);dv=np.linalg.norm(delta-X*delta[0]);rr=(delta[0]**2+dv**2)/(4*dv);ang=2*math.atan2(dv,delta[0])
    a=arc(begin,X,n,rr,ang);v=math.cos(ang)*X+math.sin(ang)*n;b=arc(a[-1],v,math.sin(ang)*X-math.cos(ang)*n,rr,ang)
    header.append(dict(centreline=pack(join(line(pt,begin),a,b)),length=6+2*rr*ang,inner_R=rr-1.45))
fixed=[]
for i,ref in enumerate(previous["ToF_fixed"]):
    pad=np.array(ref["actual_pad"]);end=np.array([B[0],-2+i*2,pad[2]]);delta=end-B;rr=np.linalg.norm(delta)/2
    a=arc(B,-X,unit(delta),rr,math.pi);el=np.array([pad[0]-14.5,end[1],end[2]])
    b=line(a[-1],el);c=arc(el,X,Y,14.5,math.pi/2);d=line(c[-1],pad)
    fixed.append(dict(wire=ref["wire"],pad=ref["pad"],actual_pad=pack(pad),centreline=pack(join(a,b,c,d)),
        length=math.pi*rr+np.linalg.norm(el-end)+14.5*math.pi/2+np.linalg.norm(pad-c[-1]),inner_R=min(rr,14.5)-1.05))
debits=dict(header=math.ceil(max(q["length"] for q in header)),moving=free,fixed=math.ceil(max(q["length"] for q in fixed)),heading=10,proper_ends=12,loss=4)
# Route the 300 cable below the Pi. Two quarters take it down to a stationary
# horizontal storage layer. A changing radius in that layer houses the whole unit.
s=np.array(jr[1]["key_tip"])+15*X
a=arc(s,X,-Z,r,math.pi/2);b=arc(a[-1],-Z,X,r,math.pi/2);drop=join(a,b)
E=np.array([-130.,49.,b[-1][2]]);out=[]
left=lambda t:np.array([-t[1],t[0],0])
def angle_ccw(u,v):return math.atan2(np.cross(u,v)[2],u@v)%(2*math.pi)
for y in (-20,-10,0,10,20):
    R,T=motion(y,0);q=drop@R.T+T;t=R@X;f=-X
    def geom(rr):
        c0=q[-1]+left(t)*rr;c1=E+left(f)*rr;u=unit(c1-c0);a0=angle_ccw(t,u);a1=angle_ccw(u,f)
        return r*math.pi+rr*(a0+a1)+np.linalg.norm(c1-c0),u,a0,a1
    low,hi=24.,65.;target=280.
    while hi-low>.001:
        mid=(hi+low)/2
        if geom(mid)[0]>target:hi=mid
        else:low=mid
    rr=(low+hi)/2;L,u,a0,a1=geom(rr)
    c=arc(q[-1],t,left(t),rr,a0);end=E+left(f)*rr-left(u)*rr
    d=line(c[-1],end);e=arc(end,u,left(u),rr,a1)
    out.append(dict(yaw=y,centreline=pack(join(q,c,d,e)),radius=rr,actual_route_length=L,free_stock=280,
      residual=280-L,inner_R=min(25,rr)-math.hypot(1.75,.9),raw=300,key=12,lap=8,endpoint=pack(E),
      three_lap_centers=[pack(E-4*X+k*6*Y) for k in (-1,0,1)],sleeves=[20]*3,
      qualification="Only rows with zero residual within 0.01 mm house the nominal full centerline. Outer fanout, two intact lands and usable slack conditional."))
result=dict(FFC=previous["FFC"],JR_factory=jr,extension=out,ToF_moving=tof,ToF_header=header,ToF_fixed=fixed,ToF_debits=debits,
    ToF_per_core=5*math.ceil(sum(debits.values())/5),fixed_yaw_assumed_case=[-119.5,0,53.2],physical_PASS=False)
(P/"occupied-layout.json").write_bytes((json.dumps(result,separators=(",",":"))+"\n").encode())
print("300",[(q["yaw"],round(q["residual"],3),round(q["radius"],2)) for q in out],"ToF",debits,result["ToF_per_core"],min(q["inner_R"] for q in tof))
