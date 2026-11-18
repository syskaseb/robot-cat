"""A flat four-lane approach opens toward the front solder face normal to the PCB."""
from pathlib import Path
import json,math
import numpy as np
P=Path(__file__).parent;r=json.loads((P/"flank-reception.json").read_bytes())
typed={q["wire"]:q for q in json.loads((P/"typed-jp3.json").read_bytes())["rows"]}
X,Y,Z=np.eye(3);B=np.array(r["shared_grips"]["body"]);rows=[]
def line(p,q):return np.linspace(p,q,1+max(1,math.ceil(np.linalg.norm(q-p)/1.2)))
def arc(p,t,n,rad,ang):
    u=np.linspace(0,ang,1+math.ceil(ang*40))
    return p+rad*(np.sin(u)[:,None]*t+(1-np.cos(u))[:,None]*n)
def join(*v):return np.vstack([v[0],*[x[1:] for x in v[1:]]])
# At the return each finished lead bends up to the PCB at +Y. Ordered radii
# place the straight drop legs on 2.4 mm centers beside the board nose.
for i in (0,2,3,1):
    q=r["ToF_fixed"][i];idx=len(rows);pad=np.array(typed[q["wire"]]["world_center"])
    last=14.3+2.4*(idx//2);first=14.5;dy,dz=[(-1.2,-1.2),(-1.2,1.2),(1.2,-1.2),(1.2,1.2)][idx];g=B+dy*Y+dz*Z
    alpha=np.radians(-7 if idx%2==0 else 7);v=np.sin(alpha)*X-np.cos(alpha)*Z;turn=np.pi/2-alpha
    y=pad[1]-last;rr=(g[1]-y)/2
    a=arc(g,-X,-Y,rr,np.pi);end_drop=pad-last*(v+Y)
    fall=(g[2]-first*(1-np.cos(turn))-end_drop[2])/np.cos(alpha)
    p0=end_drop-fall*v-first*(np.sin(turn)*X-(1-np.cos(turn))*Z)
    b=line(a[-1],p0);c=arc(p0,X,-Z,first,turn);d=line(c[-1],end_drop)
    assert d[-1,2]<d[0,2]
    e=arc(d[-1],v,Y,last,np.pi/2);assert np.linalg.norm(e[-1]-pad)<1e-6
    length=np.pi*(rr+last/2)+first*turn+np.linalg.norm(b[-1]-b[0])+np.linalg.norm(d[-1]-d[0])
    budget={**q["budget"],"fixed":math.ceil(length)}
    rows.append(dict(wire=q["wire"],JP3=q["JP3"],PTH_center=pad.tolist(),entry_axis=[0,1,0],upstream_profile_OD=2.1,
        terminal="Soldered conductor enters the existing 1.016 mm hole from the lower-Y face. Exact insulation setback, copper and solder geometry are unmeasured.",
        centreline=join(a,b,c,d,e).round(6).tolist(),fixed_field_length=length,fixed_inner_R=min(rr,first,last)-1.05,budget=budget,planned_each=5*math.ceil(sum(budget.values())/5)))
(P/"jp3-body-lane.json").write_bytes((json.dumps(dict(rows=rows,physical_PASS=False,actual_cut=None,strip=None),separators=(",",":"))+"\n").encode())
