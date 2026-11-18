"""Functional occupied groups and whole physical unit budgets for the front insert."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

P=Path(__file__).parent
old=P.parent/"day18-latest-whole-front"
base=P.parent/"day18-closed-whole-common-assembly"
source=json.loads((base/"ToF4-full-connected-family-and-unit-plan.json").read_bytes())
ffc=json.loads((old/"front-flex.json").read_bytes())["FFC"]
def unit(v):
    return np.asarray(v)/np.linalg.norm(v)
def arc(a,u,v,r,angle):
    a=np.array(a); u=unit(u); v=unit(v)
    return [a+r*(math.sin(x)*u+(1-math.cos(x))*v) for x in np.linspace(0,angle,max(8,math.ceil(abs(angle)*24))+1)]
def line(a,b):
    a,b=np.array(a),np.array(b)
    return list(np.linspace(a,b,max(2,math.ceil(np.linalg.norm(a-b)/2)+1)))
def array(ps):
    return np.array(ps).round(6).tolist()
def motion(y,p):
    a,b=map(math.radians,[y,p])
    Y=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    B=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    pc=np.array([-159.,0,121.]);yc=np.array([-130.,0,127.])
    return Y@B,Y@(pc-B@pc-yc)+yc

# Source four solder approaches and shared moving grip shift with their pitch
# owner. At both ends of the moving bight, preserve the complete 10.4x2.9 field.
S=np.array([-132.,45.,108.])
B=np.array([-99.,48.,180.])
Z=np.array([0.,0.,1.])
trials=[]
for q in source["poses"]:
    y,p=q["yaw"],q["pitch"];R,T=motion(y,p)
    s=R@S+T
    d=np.linalg.norm(B[:2]-s[:2]);h=unit(np.r_[B[:2]-s[:2],0])
    r=(B[2]-s[2])/2
    a0=math.acos(np.clip((R@np.array([1,0,0]))@h,-1,1))
    a1=math.acos(np.clip(h[0],-1,1))
    need=max(math.pi*r+d+2*(33*a1+3),math.pi*r-d+2*(33*a0+3))
    trials.append((y,p,s,h,d,r,need))
free=5*math.ceil((max(i[-1] for i in trials)+5)/5)
tof=[]
for y,p,s,h,d,r,need in trials:
    l1=(free-math.pi*r+d)/2;l2=(free-math.pi*r-d)/2
    top=s+l1*h
    turn=arc(top,h,Z,r,math.pi)
    pts=np.array(line(s,top)[:-1]+turn+line(turn[-1],B)[1:])
    tangent=np.array([unit(v) for v in np.gradient(pts,axis=0)])
    w=unit(np.cross(h,Z))
    t=np.cross(tangent,w)
    corners=np.stack([pts+a*5.2*w+b*1.45*t for a,b in [(-1,-1),(-1,1),(1,1),(1,-1)]],axis=1)
    tof.append(dict(yaw=y,pitch=p,centreline=array(pts),corners=array(corners),total=free,minimum_leg=min(l1,l2),
                    inner_R=r-1.45,heading_transition_allowance=10))
fixed=[]
for i,f in enumerate(source["fixed_fans"]):
    pad=np.array(f["actual_primary_pad"])
    end=np.array([B[0],-2.+i*2,pad[2]])
    delta=end-B; r=np.linalg.norm(delta)/2
    curve=arc(B,[-1,0,0],unit(delta),r,math.pi)
    rf=14.5
    q=np.array([pad[0]-rf,end[1],end[2]])
    turn=arc(q,[1,0,0],[0,1,0],rf,math.pi/2)
    pts=curve+line(end,q)[1:]+turn[1:]+line(turn[-1],pad)[1:]
    l=math.pi*r+np.linalg.norm(q-end)+math.pi*rf/2+np.linalg.norm(pad-turn[-1])
    fixed.append(dict(wire=f["wire"],pad=f["JP3_pad"],actual_pad=pad.tolist(),centreline=array(pts),
                      length=l,inner_R=min(r,rf)-1.05))
header=[]
for f in source["header_corner_bounds"]:
    pt=np.array(f["source_bare_pad_back"])+[-24,0,0]
    begin=pt+[6,0,0]
    d=S-begin;h=unit(np.r_[0,d[1:]])
    height=np.linalg.norm(d[1:])
    r=(d[0]**2+height**2)/(4*height);a=2*math.atan2(height,d[0])
    first=arc(begin,[1,0,0],h,r,a)
    t=np.array([1,0,0])*math.cos(a)+h*math.sin(a)
    n=np.array([1,0,0])*math.sin(a)-h*math.cos(a)
    second=arc(first[-1],t,n,r,a)
    header.append(dict(centreline=array(line(pt,begin)[:-1]+first+second[1:]),length=6+2*r*a,inner_R=r-1.45,end_error=np.linalg.norm(second[-1]-S)))
deb=dict(header=math.ceil(max(x["length"] for x in header)),moving=free,fixed=math.ceil(max(x["length"] for x in fixed)),heading=10,proper_ends=12,loss=4)

# One smooth hand-laid bight per factory unit. Radius and length are computed
# from the analytic path. Axial drift separates consecutive turns. Zero axial
# slope at both ends preserves the case/key tangent. The entire pitch unit and
# its two-piece keyed housing follow yaw, never pitch.
def bight(name,s,t,u,v,r,axial,raw,stub,key,owner):
    s,t,u,v=map(np.array,(s,t,u,v))
    available=raw-stub-key
    def speed(th,extent):
        return math.hypot(r,axial/extent*(1-math.cos(2*math.pi*th/extent)))
    def length(extent):
        return quad(lambda a:speed(a,extent),0,extent)[0]
    sweep=brentq(lambda a:length(a)-available,.3,14)
    tt=np.linspace(0,sweep,151)
    pts=[];rs=[]
    for a in tt:
        k=a/sweep
        g=k-math.sin(2*math.pi*k)/(2*math.pi)
        dp=r*(math.cos(a)*t+math.sin(a)*u)+axial/sweep*(1-math.cos(2*math.pi*k))*v
        dd=r*(-math.sin(a)*t+math.cos(a)*u)+axial*2*math.pi/sweep**2*math.sin(2*math.pi*k)*v
        rs.append(np.linalg.norm(dp)**3/np.linalg.norm(np.cross(dp,dd)))
        pts.append(s+r*(math.sin(a)*t+(1-math.cos(a))*u)+axial*g*v)
    tangent=unit(dp)
    end=pts[-1]+key*tangent
    return dict(name=name,owner=owner,raw=raw,nominal_case_stub=stub,full_key_debit=key,free=length(sweep),
                total=length(sweep)+key+stub,centreline=array(pts),minimum_sampled_centre_R=min(rs),
                conservative_inner_R=min(rs)-math.hypot(1.75,.9),key_tip=array(end),key_axis=array(tangent),
                turns=sweep/(2*math.pi))
jr_yaw=bight("factory_yaw",[-119.5,0,53.2],[1,0,0],[0,0,1],[0,-1,0],25,35,250,11.45,15,"fixed")
jr_pitch=bight("factory_pitch",[-159,-43.8,131.5],[0,-1,0],[.8,0,.6],[.6,0,-.8],25,34,250,11.45,15,"yaw")
# Extension follows the connected key into its own moving approach. Body side
# contains a variable-length reserve ahead of the proper three insulated laps.
# Keep every millimetre of the uncut unit in the initial open assembly.
plug=np.array(jr_pitch["key_tip"]);tipdir=np.array(jr_pitch["key_axis"])
plug_exit=plug+15*tipdir
body_anchor=np.array([-71.,-38.,140.])
splices=np.array([[-48.,-40.,108.],[-42.,-40.,108.],[-36.,-40.,108.]])
extensions=[]
def bezier(a,b,c,d):
    t=np.linspace(0,1,65)[:,None]
    pts=(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
    dp=3*((1-t)**2*(b-a)+2*t*(1-t)*(c-b)+t*t*(d-c))
    dd=6*((1-t)*(c-2*b+a)+t*(d-2*c+b))
    radii=np.linalg.norm(dp,axis=1)**3/np.maximum(1e-10,np.linalg.norm(np.cross(dp,dd),axis=1))
    length=quad(lambda u:np.linalg.norm(3*((1-u)**2*(b-a)+2*u*(1-u)*(c-b)+u*u*(d-c))),0,1)[0]
    return pts,length,min(radii)
for y in [-20,0,20]:
    R,T=motion(y,0);start=R@plug_exit+T;direct=R@tipdir
    pts,l,r=bezier(start,start+37*direct,body_anchor-np.array([26.,0,0]),body_anchor)
    fixed_endpoint_upper=max(np.sum(np.abs(splices-body_anchor),axis=1))
    residual=300-12-8-l-fixed_endpoint_upper
    extensions.append(dict(yaw=y,centreline=array(pts),moving_length=l,inner_R_screen=r-math.hypot(1.75,.9),
                           fixed_three_join_region_upper=fixed_endpoint_upper,join_centers=array(splices),lap=8,each_sleeve=20,
                           reserve_to_park_before_trim=residual,full_300_pretrim_length=l+fixed_endpoint_upper+residual+12+8,
                           key_body_length=15,key_cable_debit=12))
result=dict(FFC=ffc,ToF_moving=tof,ToF_header=header,ToF_fixed=fixed,ToF_debits=deb,ToF_plan_per_core=5*math.ceil(sum(deb.values())/5),
            JR_factory=[jr_yaw,jr_pitch],JR_extension=extensions,source_ended_units="Separate physical 250/250/300; mouth and engagement project datums, no pooling. Extension residual requires an actual available >=R23.5 reserve; scalar sum alone is not acceptance.",
            actual_fit=None,actual_slack=None,actual_cut=None,physical_PASS=False)
(P/"insert-regions.json").write_bytes((json.dumps(result,separators=(",",":"))+"\n").encode())
print("ToF",free,result["ToF_plan_per_core"],min(q["inner_R"] for q in tof),"JR",[(q["name"],q["turns"],q["conservative_inner_R"],q["key_tip"]) for q in result["JR_factory"]])
print("JR300",[(q["yaw"],q["moving_length"],q["inner_R_screen"],q["reserve_to_park_before_trim"]) for q in extensions])
