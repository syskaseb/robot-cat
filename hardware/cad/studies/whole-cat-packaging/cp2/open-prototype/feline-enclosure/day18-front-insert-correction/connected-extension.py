"""Carry the uncut 300 mm extension directly between the yaw plug and the three body joins."""
import json, math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
P=Path(__file__).parent
data=json.loads((P/"insert-regions.json").read_bytes())
pitch=data["JR_factory"][1]
t=np.array(pitch["key_axis"]);p=np.array(pitch["key_tip"])+15*t
Z=np.array([0.,0.,1.]);X=np.array([1.,0.,0.])
def unit(v):return v/np.linalg.norm(v)
def arc(p,t,n,r,a):
    return np.array([p+r*(math.sin(b)*t+(1-math.cos(b))*n) for b in np.linspace(0,a,1+max(5,math.ceil(abs(a)*30)))])
def line(a,b):return np.linspace(a,b,1+max(2,math.ceil(np.linalg.norm(b-a)/2)))
def cw(u,v):return (-math.atan2(u[0]*v[1]-u[1]*v[0],u@v))%(2*math.pi)
def right(t):return np.array([t[1],-t[0],0.])
def join(*arrays):return np.vstack([arrays[0],*[a[1:] for a in arrays[1:]]])
# First roll follows the real mated pair direction. S-drop is fixed on body;
# sleeve axes are parallel, with individually separated lands at y=-46/-40/-34.
h=unit(t-t[2]*Z);angle=math.asin(t[2]);lead=arc(p,t,unit(h-t*(t@h)),25,angle)
z=lead[-1][2];end=np.array([-46.,-40.,108.]);theta=math.acos(1-(z-end[2])/50)
E=end+np.array([9+50*math.sin(theta),0.,z-end[2]])
drop1=arc(E,-X,-Z,25,theta)
td=-X*math.cos(theta)-Z*math.sin(theta)
drop2=arc(drop1[-1],td,-X*math.sin(theta)+Z*math.cos(theta),25,theta)
tail=join(drop1,drop2,line(drop2[-1],end))
fixed=50*theta+9
planar=300-12-8-25*angle-fixed
rows=[]
for yaw in [-20,-10,0,10,20]:
    a=math.radians(yaw);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    pivot=np.array([-130.,0.,127.]);q=(lead-pivot)@R.T+pivot
    start=q[-1];u=R@h;f=-X
    def geom(r):
        c=start+right(u)*r;d=E+right(f)*r
        tangent=unit(d-c);a0=cw(u,tangent);a1=cw(tangent,f)
        return r*(a0+a1)+np.linalg.norm(d-c),tangent,a0,a1
    r=brentq(lambda r:geom(r)[0]-planar,24.0,40)
    L,v,a0,a1=geom(r)
    a=arc(start,u,right(u),r,a0)
    last=E+right(f)*r-right(v)*r
    b=arc(last,v,right(v),r,a1)
    pts=join(q,a,line(a[-1],last),b,tail)
    rows.append(dict(yaw=yaw,centreline=pts.round(6).tolist(),source=q[0].tolist(),landing=E.tolist(),
                     free_length=25*angle+L+fixed,raw=300,key_once=12,lap_once=8,residual_unallocated=0,
                     variable_planar_radius=r,minimum_centre_R=min(25,r),inner_R_conservative=min(r,25)-math.hypot(1.75,.9),
                     three_lap_centers=[[-50,-46,108],[-50,-40,108],[-50,-34,108]],sleeves=[20,20,20],
                     last_insulated_straight=9,fanout="6 mm lateral spreading to outer insulated joins is a local routing allowance still to verify; no offcut credit",endpoint_error=np.linalg.norm(b[-1]-E)))
doc=dict(poses=rows,original_short_bridge="rejected on radius; unspent length was not housed",
    length_account="actual whole uncut unit in a changing bend; no separate counted loop. Source male housing length15 from pitch key, cable debit12. Far-board cut none.",
    physical_PASS=False)
(P/"connected-JR300.json").write_bytes((json.dumps(doc,separators=(",",":"))+"\n").encode())
print([(q["yaw"],round(q["variable_planar_radius"],2),round(q["inner_R_conservative"],2),round(q["free_length"],3)) for q in rows])
