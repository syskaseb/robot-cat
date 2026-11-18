"""Construct occupied station-to-station fields and account separately for each uncut JR unit."""
from pathlib import Path
import math,json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
P=Path(__file__).parent
before=json.loads((P.parent/"day18-open-front-assembly"/"occupied-layout.json").read_bytes())
X,Y,Z=np.eye(3)
def unit(p):return p/np.linalg.norm(p)
def arc(p,t,n,r,a):
    return np.array([p+r*(math.sin(b)*t+(1-math.cos(b))*n) for b in np.linspace(0,a,1+max(3,math.ceil(a*25)))])
def line(p,q):return np.linspace(p,q,1+max(1,math.ceil(np.linalg.norm(p-q)/2.5)))
def join(*data):return np.vstack([data[0],*[q[1:] for q in data[1:]]])
def pack(a):return np.asarray(a).round(6).tolist()
def motion(y,p):
    a,b=map(math.radians,(y,p));yc=np.array([-130,0,127]);pc=np.array([-159,0,121])
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    return rz@ry,yc+rz@(pc-ry@pc-yc)
def left(t):return np.cross(Z,t)
def ccw(u,v):return math.atan2(np.cross(u,v)[2],u@v)%(2*math.pi)
def factory(q,t,length):
    return dict(centreline=pack(q),key_tip=pack(q[-1]+15*t),key_axis=pack(t),free=length,
        stock=250,case_stub=11.45,factory_key=15,profile=[3.5,1.8])
# Static body unit: the return is below the common Pi carrier crossing
# and both legs clear the top of the retained short factory power pair.
r=25.;s=np.array([-119.5,0,53.2]);vz=(80.5-s[2])/50;v=math.sqrt(1-vz**2)*Y+vz*Z
a=arc(s,X,v,r,math.pi/2);b=arc(a[-1],v,X,r,math.pi/2)
c=line(b[-1],b[-1]+30*X);d=arc(c[-1],X,-Y,r,math.pi);e=line(d[-1],d[-1]-(223.55-2*math.pi*r-30)*X)
yaw=factory(join(a,b,c,d,e),-X,223.55)
# The pitch factory lead follows the YAW owner only through its first quarter.
# A changing body-level U bend meets one fixed receiver with the same final tangent.
s=np.array([-159.,-43.8,131.5]);first=arc(s,-Y,X,r,math.pi/2);end=np.array([-66.,38.,131.5]);f=-X
pitch=[]
for y in [-20,-10,0,10,20]:
    R,T=motion(y,0);a=first@R.T+T;t=R@X
    def shape(radius):
        c0=a[-1]+left(t)*radius;c1=end+left(f)*radius;u=unit(c1-c0)
        turn1=ccw(t,u);turn2=ccw(u,f)
        return math.pi*r/2+radius*(turn1+turn2)+np.linalg.norm(c1-c0),u,turn1,turn2
    low,high=24.,57.
    for _ in range(50):
        mid=(low+high)/2
        if shape(mid)[0]>223.55:high=mid
        else:low=mid
    radius=(low+high)/2;length,u,theta,phi=shape(radius)
    b=arc(a[-1],t,left(t),radius,theta);j=end+left(f)*radius-left(u)*radius
    c=line(b[-1],j);d=arc(j,u,left(u),radius,phi)
    bending=join(b,c,d);base=length-math.pi*r/2;rise=0.
    if 223.55-length>.001:
        def developed(h):
            return base*quad(lambda u:math.hypot(1,math.pi*h/base*math.sin(2*math.pi*u)),0,1)[0]
        rise=brentq(lambda h:developed(h)+math.pi*r/2-223.55,0,base)
        walked=np.r_[0,np.cumsum(np.linalg.norm(np.diff(bending,axis=0),axis=1))]
        bending[:,2]+=rise*np.sin(math.pi*walked/walked[-1])**2
        length=developed(rise)+math.pi*r/2
    conservative_R=1/math.hypot(1/radius,2*math.pi**2*rise/base**2)
    rec=factory(join(a,bending),-X,length)
    rec.update(yaw=y,radius=radius,body_arch=rise,remaining=223.55-length,inner_R=min(r,conservative_R)-math.hypot(1.75,.9))
    pitch.append(rec)
# Whole existing JR300 is fixed. Two matching transfer turns descend behind
# its body-owned pair, then one inclined standing U returns toward the three
# insulated joints. All three centers account for their own final fan and lap.
s=end-30*X;v=.30*Y-math.sqrt(1-.30**2)*Z
a=arc(s,-X,v,r,math.pi/2);b=arc(a[-1],v,X,r,math.pi/2);first_leg=57.
c=line(b[-1],b[-1]+first_leg*X);v=-.05*Y+math.sqrt(1-.05**2)*Z
d=arc(c[-1],X,v,35,math.pi);second_leg=280-math.pi*(r+35)-first_leg
e=line(d[-1],d[-1]-(second_leg-34)*X);split=e[-1]
fans=[]
for lateral in (-6.,0.,6.):
    if lateral:
        theta=brentq(lambda x:(1-math.cos(x))/x-abs(lateral)/25,.01,1.5)
        rf=25/(2*theta);n=math.copysign(1,lateral)*Y
        m=arc(split,-X,n,rf,theta);q=arc(m[-1],-X*math.cos(theta)+n*math.sin(theta),-X*math.sin(theta)-n*math.cos(theta),rf,theta)
        ps=join(m,q,line(q[-1],q[-1]-9*X))
    else:rf=None;ps=line(split,split-34*X)
    fans.append(dict(centreline=pack(ps),fan_length=25,land=9,fan_R=rf,lap_center=pack(ps[-1]-4*X),
                     raw=300,key=12,free_before_split=246,free_after_split=34,lap=8,sleeve=20,opposite_land=9))
ext=dict(centreline=pack(join(a,b,c,d,e)),fans=fans,receiver_exit=pack(s),owner="body",minimum_main_R=25,whole_each=300)
# Each 2.1 mm OD core occupies a distinct 2x2 lane on 2.4 mm pitch. The
# four-core outer field includes 0.2 mm per side of assembly allowance.
S=np.array([-151.,47.,105.]);B=np.array([-122.,42.,180.]);pack_half=2.45
todo=[]
for y in (-20,0,20):
    for p in (-10,0,10):
        R,T=motion(y,p);s=R@S+T;t=R@X;angle=math.acos(np.clip(t@X,-1,1))
        first=arc(s,t,unit(X-t*(t@X)),36,angle) if angle>1e-6 else np.array([s])
        delta=B-first[-1];h=delta-X*delta[0];rr=np.linalg.norm(h)/2
        todo.append((y,p,first,36*angle,delta[0],unit(h),rr))
free=5*math.ceil(max(head+math.pi*rr+abs(dx)+16 for y,p,first,head,dx,n,rr in todo)/5)
tof=[]
for y,p,first,head,dx,n,rr in todo:
    l=(free-head-math.pi*rr+dx)/2;a=line(first[-1],first[-1]+l*X);b=arc(a[-1],X,n,rr,math.pi);c=line(b[-1],B)
    ps=join(first,a,b,c);tof.append(dict(yaw=y,pitch=p,centreline=pack(ps),free=free,
        inner_R=min(36 if head else rr,rr)-pack_half*math.sqrt(2),heading_arc=head))
header=[]
for q in before["ToF_header"]:
    p=np.array(q["centreline"][0]);start=p+6*X
    delta=S-start;h=delta-X*delta[0];dist=np.linalg.norm(h);v=unit(h);rh=15.5
    a=arc(start,X,v,rh,math.pi/2);b=line(a[-1],a[-1]+(dist-2*rh)*v);c=arc(b[-1],v,X,rh,math.pi/2);d=line(c[-1],S)
    header.append(dict(centreline=pack(join(line(p,start),a,b,c,d)),length=6+math.pi*rh+dist-2*rh+delta[0]-2*rh,inner_R=rh-1.05))
fixed=[]
lane_allowance=math.ceil(math.hypot(1.2,1.2)*(math.pi+max(q[3] for q in todo)/36))
for j in before["ToF_fixed"]:
    pad=np.array(j["actual_pad"]);dest=np.array([B[0],50.5,pad[2]]);delta=dest-B;rr=np.linalg.norm(delta)/2
    a=arc(B,-X,unit(delta),rr,math.pi);e=np.array([pad[0]-15,50.5,pad[2]])
    b=line(a[-1],e);c=arc(b[-1],X,-Y,15,math.pi/2);d=line(c[-1],pad)
    length=math.pi*rr+np.linalg.norm(e-dest)+15*math.pi/2+np.linalg.norm(pad-c[-1])
    h=math.ceil(max(q["length"] for q in header))
    budget=dict(header=h,moving=free,lane_difference=lane_allowance,fixed=math.ceil(length),ends_total=12,loss=4)
    fixed.append(dict(wire=j["wire"],JP3=j["pad"],centreline=pack(join(a,b,c,d)),length=length,budget=budget,
        inner_R=min(rr,15)-1.05,planned_each=5*math.ceil(sum(budget.values())/5)))
out=dict(yaw=yaw,pitch=pitch,extension=ext,ToF_head=header,ToF_move=tof,ToF_fixed=fixed,
    shared_grips=dict(pitch=pack(S),body=pack(B),OD=2.1,pitch_spacing=2.4,field=[4.9,4.9]),
    physical_PASS=False,actual_cut=None,actual_installed_slack=None)
(P/"reception-layout.json").write_bytes((json.dumps(out,separators=(",",":"))+"\n").encode())
print("pitch",[(q["yaw"],round(q["remaining"],2),round(q["radius"],2)) for q in pitch],"ToF",min(q["inner_R"] for q in tof),[q["planned_each"] for q in fixed])
