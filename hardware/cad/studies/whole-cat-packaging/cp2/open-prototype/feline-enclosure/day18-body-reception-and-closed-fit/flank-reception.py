"""Use low body stations and segregate moving cheek, static JR and upper ToF fields."""
import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
P=Path(__file__).parent
src=json.loads((P/"reception-layout.json").read_bytes())
old=json.loads((P.parent/"day18-open-front-assembly"/"occupied-layout.json").read_bytes())
X,Y,Z=np.eye(3);C=np.array([-130.,0,127]);PC=np.array([-159.,0,121])
def unit(q):return q/np.linalg.norm(q)
def arc(p,t,n,r,a):
    b=np.linspace(0,a,1+max(4,math.ceil(32*a)));return p+r*(np.sin(b)[:,None]*t+(1-np.cos(b))[:,None]*n)
def line(a,b):return np.linspace(a,b,1+max(1,math.ceil(np.linalg.norm(a-b)/2)))
def join(*q):return np.vstack([q[0],*[a[1:] for a in q[1:]]])
def pack(q):return np.array(q).round(6).tolist()
def pose(y,p):
    a,b=np.radians([y,p]);rz=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
    ry=np.array([[np.cos(b),0,np.sin(b)],[0,1,0],[-np.sin(b),0,np.cos(b)]])
    return rz@ry,C+rz@(PC-ry@PC-C)
def aim(p,t):
    angle=math.acos(np.clip(t@X,-1,1))
    return (arc(p,t,unit(X-t*(t@X)),36,angle),36*angle) if angle>1e-6 else (np.array([p]),0.)
def reach(first,B,free,spent):
    s=first[-1];d=B-s;h=d-d[0]*X;r=np.linalg.norm(h)/2;n=unit(h)
    f=(free-spent-np.pi*r+d[0])/2;back=f-d[0]
    assert min(f,back)>0,(f,back)
    a=line(s,s+f*X);b=arc(a[-1],X,n,r,np.pi);return join(first,a,b,line(b[-1],B)),r,f,back
pitch=[];B=np.array([-81.,-51.,80.5]);s=np.array([-159.,-43.8,131.5])
for y in (-20,-10,0,10,20):
    R,T=pose(y,0);root=arc(s,-Y,X,25,np.pi/2)@R.T+T
    a,la=aim(root[-1],R@X);path,r,l1,l2=reach(join(root,a),B,223.55,np.pi*12.5+la)
    pitch.append(dict(yaw=y,centreline=pack(path),key_tip=pack(B-15*X),key_axis=pack(-X),inner_R=min(25,36,r)-math.hypot(1.75,.9),
                      stock=250,case_stub=11.45,free=223.55,factory_key=15,straight_legs=[l1,l2],bight_axial_R=r))
# The next whole unit goes up the negative shoulder, outside the terminals;
# it then crosses ABOVE their tops once and fans on the positive splice tray.
s=B-30*X;a=arc(s,-X,Z,39,np.pi);b=line(a[-1],a[-1]+43*X);c=arc(b[-1],X,Y,25,np.pi/2)
last=280-(39*np.pi+43+25*np.pi/2)
d=line(c[-1],c[-1]+(last-34)*Y);split=d[-1];fans=[]
for shift in (-6.,0.,6.):
    if shift:
        ang=brentq(lambda t:(1-math.cos(t))/t-abs(shift)/25,.01,1.5);r=25/(2*ang);n=np.sign(shift)*X
        j=arc(split,Y,n,r,ang);k=arc(j[-1],Y*np.cos(ang)+n*np.sin(ang),Y*np.sin(ang)-n*np.cos(ang),r,ang);q=join(j,k,line(k[-1],k[-1]+9*Y))
    else:q=line(split,split+34*Y);r=None
    fans.append(dict(centreline=pack(q),lap_center=pack(q[-1]+4*Y),fan=25,land=9,opposite_land=9,sleeve=20,proper_lap=8,raw=300,plug=12,common_free=246,individual_free=34))
extension=dict(centreline=pack(join(a,b,c,d)),fans=fans,owner="body",raw_each=300,key=12,free=280,lap=8,min_inner_R=25-math.hypot(1.75,.9))
S=np.array(src["shared_grips"]["pitch"]);B=np.array([-145.,58.,178.]);first=[]
for y in (-20,0,20):
    for p in (-10,0,10):
        R,T=pose(y,p);q,l=aim(R@S+T,R@X);delta=B-q[-1];radius=np.linalg.norm(delta-delta[0]*X)/2
        first.append((y,p,q,l,l+np.pi*radius+abs(delta[0])+12))
free=5*math.ceil(max(v[-1] for v in first)/5);tof=[]
for y,p,q,l,_ in first:
    path,r,f,b=reach(q,B,free,l)
    tof.append(dict(yaw=y,pitch=p,centreline=pack(path),free=free,inner_R=min(36 if l else r,r)-2.45*np.sqrt(2),legs=[f,b]))
fixed=[]
for i,j in enumerate(old["ToF_fixed"]):
    pad=np.array(j["actual_pad"]);sy,sz=[(-1.2,-1.2),(1.2,1.2),(-1.2,1.2),(1.2,-1.2)][i];g=B+sy*Y+sz*Z
    ang=np.radians([-10,10,-3.5,3.5][i]);v=np.sin(ang)*Y-np.cos(ang)*Z;rr=14.3
    down=(g[2]-pad[2])/np.cos(ang);length=down-2*rr;assert length>0
    q0=pad-2*rr*X-down*v
    radius=(g[1]-q0[1])/2;assert radius-1.05>=12.6
    a=arc(g,-X,-Y,radius,np.pi);b=line(a[-1],q0)
    c=arc(q0,X,v,rr,np.pi/2);d=line(c[-1],c[-1]+length*v);e=arc(d[-1],v,X,rr,np.pi/2)
    assert np.linalg.norm(e[-1]-pad)<1e-4
    stock=np.pi*(radius+rr)+np.linalg.norm(q0-a[-1])+length
    budget=dict(header=max(q["budget"]["header"] for q in src["ToF_fixed"]),moving=free,lane_difference=7,fixed=math.ceil(stock),ends_once=12,loss=4)
    fixed.append(dict(wire=j["wire"],JP3=j["pad"],centreline=pack(join(a,b,c,d,e)),length=stock,inner_R=min(radius,rr)-1.05,budget=budget,planned_each=5*math.ceil(sum(budget.values())/5)))
out=dict(yaw=src["yaw"],pitch=pitch,extension=extension,ToF_head=src["ToF_head"],ToF_move=tof,ToF_fixed=fixed,
         shared_grips=dict(pitch=pack(S),body=pack(B),field=[4.9,4.9]),physical_PASS=False,actual_cut=None)
(P/"flank-reception.json").write_bytes((json.dumps(out,separators=(",",":"))+"\n").encode())
print("pitch inner R",min(q["inner_R"] for q in pitch),"ToF inner",min(q["inner_R"] for q in tof),"four cuts PLAN",[(q["wire"],q["planned_each"]) for q in fixed])
