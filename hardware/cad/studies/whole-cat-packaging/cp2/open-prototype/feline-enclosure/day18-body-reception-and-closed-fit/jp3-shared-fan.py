"""Carry the four fixed wires in one supported bend, then open into a row on the solder side."""
from pathlib import Path
import json,math
import numpy as np
from scipy.integrate import quad
P=Path(__file__).parent;X,Y,Z=np.eye(3)
r=json.loads((P/"flank-reception.json").read_bytes());B=np.array(r["shared_grips"]["body"])
typed=sorted(json.loads((P/"typed-jp3.json").read_bytes())["rows"],key=lambda q:q["world_center"][2])
Rlast=15.5;Q=np.array([B[0],20.95-Rlast,np.mean([q["world_center"][2] for q in typed])])
d=Q-B;radius=np.linalg.norm(d)/2;n=d/(2*radius);e=np.cross(X,n)
def arc(p,t,n,rr,a):
    u=np.linspace(0,a,1+math.ceil(a*56));return p+rr*(np.sin(u)[:,None]*t+(1-np.cos(u))[:,None]*n)
lanes=[]
for dy,dz in [(-1.2,-1.2),(-1.2,1.2),(1.2,-1.2),(1.2,1.2)]:
    off=dy*Y+dz*Z;rad=radius-off@n
    a=arc(B+off,-X,n,rad,np.pi)
    lanes.append((a[-1,2],a,rad))
def shift(p,l,axis,amt):
    u=np.linspace(0,1,65);f=10*u**3-15*u**4+6*u**5
    pts=p+l*u[:,None]*X+amt*f[:,None]*axis
    length=quad(lambda t:math.hypot(l,amt*(30*t**2-60*t**3+30*t**4)),0,1)[0]
    curvature_bound=5.774*abs(amt)/l**2
    return pts,length,curvature_bound
out=[]
for (z0,a,rad),q in zip(sorted(lanes,key=lambda a:a[0]),typed):
    pad=np.array(q["world_center"]);b,lb,kb=shift(a[-1],46,Z,pad[2]-z0)
    c,lc,kc=shift(b[-1],30,Y,Q[1]-b[-1,1])
    bend_start=pad-Rlast*(X+Y);s=np.linspace(c[-1],bend_start,40)
    assert np.max(abs(s[-1,1:]-s[0,1:]))<1e-7
    t=arc(bend_start,X,Y,Rlast,np.pi/2)
    total=np.pi*rad+lb+lc+np.linalg.norm(s[-1]-s[0])+np.pi*Rlast/2
    original=next(j for j in r["ToF_fixed"] if j["wire"]==q["wire"]);deb={**original["budget"],"fixed":math.ceil(total)}
    out.append(dict(wire=q["wire"],JP3=int(q["pad"].split(".")[1]),PTH_center=pad.tolist(),entry_axis=[0,1,0],centreline=np.vstack([a,b[1:],c[1:],s[1:],t[1:]]).round(6).tolist(),
        fixed_length=total,minimum_fixed_inner_R=min(rad,Rlast,1/max(kb,kc,.00001))-1.05,
        budget=deb,planned_each=5*math.ceil(sum(deb.values())/5),actual_strip=None))
(P/"jp3-shared-fan.json").write_bytes((json.dumps(dict(rows=out,common_width_at_grip=4.9,OD_each=2.1,physical_PASS=False,actual_cut=None),separators=(",",":"))+"\n").encode())
