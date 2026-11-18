"""Sample the changed contacts using a sloped FFC transport and the side ToF bight."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

out = Path(__file__).parent
source = out.parent / "day18-connected-storage-pitch-frame" / "separate-FFC200-storage-plan.json"
tof_source = out.parent / "day18-closed-whole-common-assembly" / "ToF4-full-connected-family-and-unit-plan.json"
ffc = json.loads(source.read_bytes())
tof = json.loads(tof_source.read_bytes())
shift = np.array([-24., 0., 0.])
Z = np.array([0., 0., 1.])
fixed = np.array(ffc["fixed_Pe"])

def unit(v):
    return v / np.linalg.norm(v)

def rotate(v, axis, angle):
    return v*math.cos(angle) + np.cross(axis,v)*math.sin(angle) + axis*np.dot(axis,v)*(1-math.cos(angle))

def apply_arc(points, radius, axis, angle, inward):
    p,t,w = points[-1]
    center = p + inward*radius
    min_inner = radius
    for k in range(1, 1+max(4,math.ceil(angle*18))):
        a = k*angle/max(4,math.ceil(angle*18))
        pp = center+rotate(p-center,axis,a)
        tt,ww = rotate(t,axis,a), rotate(w,axis,a)
        inward_dir = unit(center-pp)
        min_inner = min(min_inner,radius - 8.4*abs(ww@inward_dir) - .9*abs(np.cross(tt,ww)@inward_dir))
        points.append((pp,tt,ww))
    return min_inner

def straight(points, length, target_width=None):
    p,t,w = points[-1]
    angle = 0 if target_width is None else math.atan2(np.cross(w,target_width)@t,w@target_width)
    for f in np.linspace(0,1,max(3,math.ceil(length/2)))[1:]:
        points.append((p+f*length*t,t,rotate(w,t,angle*f)))

ribbon = []
for row in ffc["rows"]:
    yaw = math.radians(row["yaw"])
    p = np.array(row["C0"])+shift
    t = np.array(row["source_tangent"])
    points = [(p,t,np.array([math.sin(yaw),-math.cos(yaw),0.]))]
    r = row["quarter_R"]
    first_angle = math.acos(np.clip(t@Z,-1,1))
    radii = []
    if first_angle > 1e-8:
        axis = unit(np.cross(t,Z))
        radii.append(apply_arc(points,r,axis,first_angle,unit(Z-t*math.cos(first_angle))))
    start = points[-1][0]
    d = fixed-start
    hvec = unit(np.array([d[0],d[1],0.]))
    delta_xy = np.linalg.norm(d[:2])-2*r
    length = math.hypot(delta_xy,d[2])
    angle = math.atan2(delta_xy,d[2])
    leg = (190 - first_angle*r - math.pi*r - length)/2
    if leg < 0:
        raise ValueError(("FFC length",row["yaw"],row["pitch"],leg))
    straight(points,leg)
    normal = unit(np.cross(Z,hvec))
    radii.append(apply_arc(points,r,normal,angle,hvec))
    target = normal if points[-1][2]@normal>=0 else -normal
    straight(points,length,target)
    radii.append(apply_arc(points,r,normal,math.pi-angle,unit(np.cross(normal,points[-1][1]))))
    straight(points,leg,np.array([0.,-1.,0.]))
    corners = [[(p+a*8.4*w+b*.9*np.cross(t,w)).tolist() for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]] for p,t,w in points]
    ribbon.append(dict(yaw=row["yaw"],pitch=row["pitch"],terminal_leg=leg,source_approach=first_angle*r,
                       free_length=first_angle*r+math.pi*r+length+2*leg, stock=200,end_debit_total=10,
                       profile_arc_inner_min=min(radii),end_error=float(np.linalg.norm(points[-1][0]-fixed)),
                       corners=corners,centreline=[p.tolist() for p,t,w in points]))
# ToF: changed grip follows the whole moving assembly. Fixed fan endpoints stay
# on the original four JP3 pads. The factory soldered electronics stay together.
B = np.array(tof["fixed_body_grip"])
trials=[]
for q in tof["poses"]:
    s = np.array(q["source"])+shift
    h = unit(np.r_[B[:2]-s[:2],0.])
    d = np.linalg.norm(B[:2]-s[:2])
    r = (B[2]-s[2])/2
    rot_y = math.radians(q["yaw"])
    rot_p = math.radians(q["pitch"])
    moving = np.array([math.cos(rot_y)*math.cos(rot_p),math.sin(rot_y)*math.cos(rot_p),-math.sin(rot_p)])
    a0 = math.acos(np.clip(moving@h,-1,1))
    a1 = math.acos(np.clip(h[0],-1,1))
    need = max(math.pi*r+d+2*(33*a1+3), math.pi*r-d+2*(33*a0+3))
    trials.append((q,s,h,d,r,need))
free = 5*math.ceil((max(v[-1] for v in trials)+5)/5)
side=[]
for q,s,h,d,r,_ in trials:
    l1=(free-math.pi*r+d)/2
    l2=(free-math.pi*r-d)/2
    top=s+l1*h
    points=[s,top]+[top+r*math.sin(a)*h+Z*r*(1-math.cos(a)) for a in np.linspace(0,math.pi,61)[1:]]+[B]
    side.append(dict(yaw=q["yaw"],pitch=q["pitch"],inner_R=r-1.45,first_leg=l1,return_leg=l2,
                     free_length=free,centreline=[p.tolist() for p in points],profile=[10.4,2.9]))
debits=dict(tof["per_core_upper_debits"],moving_U=free)
result=dict(FFC=ribbon,ToF=side,ToF_debits=debits,ToF_planned_blank_per_core=5*math.ceil(sum(debits.values())/5),
            unchanged_ToF_fan_source_sha256=hashlib.sha256(tof_source.read_bytes()).hexdigest(),
            original_FFC_contacts_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            scope="Nine correlated poses, explicit connector directions, sampled profile and analytic length. Local twists, obstacles, continuous motion and actual installed slack require separate evidence.",
            physical_PASS=False)
(out/"front-flex.json").write_bytes((json.dumps(result,separators=(",",":"))+"\n").encode())
print("FFC",min(x["terminal_leg"] for x in ribbon),min(x["profile_arc_inner_min"] for x in ribbon),max(x["end_error"] for x in ribbon))
print("ToF",min(x["inner_R"] for x in side),free,result["ToF_planned_blank_per_core"])
