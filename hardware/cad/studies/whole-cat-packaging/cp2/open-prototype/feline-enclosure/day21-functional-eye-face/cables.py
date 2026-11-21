"""Screen the FFC200 feed and keep the existing four-wire ToF handoff."""
from pathlib import Path
import json
import math
import sys

import FreeCAD as A
import numpy as np
import Part

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from layout import V, Z, Y, articulated as artis, load_saved, tof_geometry, write_json

FIXED = np.array([-62.5,-16.5,105.1])
R = 22.
ARRAY = lambda v: np.array(list(v),dtype=float)

def unit(v):
    return v/np.linalg.norm(v)

def quat_turn(v,a,angle):
    return v*math.cos(angle)+np.cross(a,v)*math.sin(angle)+a*np.dot(a,v)*(1-math.cos(angle))

def allowance(direction,t0,t1):
    return sum((R*math.tan(math.acos(float(np.clip(q@direction,-1,1)))/2)*(q+direction)
                for q in (t0,t1)),np.zeros(3))

def tangency(delta,t0,t1):
    def residual(p):
        d=p[:3]
        return np.r_[allowance(d,t0,t1)+p[3]*d-delta, d@d-1.]
    v=unit(delta)
    p=np.r_[v,max(1.,np.linalg.norm(delta-allowance(v,t0,t1)))]
    for _ in range(13):
        error=residual(p)
        if np.linalg.norm(error)<1e-7:
            return p[:3],float(p[3])
        jac=np.column_stack([(residual(p+np.eye(4)[i]*1.e-5)-error)/1.e-5 for i in range(4)])
        p-=np.linalg.solve(jac,error)
    raise ValueError("two-arc tangency not converged")

def make_fan(connector,yaw,pitch,launch=Z,clock_width=Y):
    pose=artis(yaw,pitch)
    beginning=ARRAY(pose.multVec(connector))
    t0=ARRAY(pose.Rotation.multVec(launch))
    w0=ARRAY(pose.Rotation.multVec(clock_width))
    t1=np.array([0.,0.,-1.])
    w1=np.array([0.,1.,0.])
    start=beginning+2*t0
    finish=FIXED-2*t1
    direction,distance=tangency(finish-start,t0,t1)
    assert distance>0
    a0=math.acos(t0@direction)
    a1=math.acos(direction@t1)
    n0=unit(np.cross(t0,direction))
    n1=unit(np.cross(direction,t1))
    back_w=quat_turn(w1,n1,-a1)
    initial_w=quat_turn(w0,n0,a0)
    roll=math.atan2(direction@np.cross(initial_w,back_w),initial_w@back_w)
    c0=start+R*np.cross(n0,t0)
    samples=[(beginning,t0,w0)]
    arcs=[]
    for q in np.linspace(0,a0,29):
        samples.append((c0+quat_turn(start-c0,n0,q),quat_turn(t0,n0,q),quat_turn(w0,n0,q)))
    before_line=samples[-1][0]
    after_line=before_line+distance*direction
    for fraction in np.linspace(0,1,25)[1:]:
        samples.append((before_line+distance*fraction*direction,direction,quat_turn(initial_w,direction,roll*fraction)))
    c1=after_line+R*np.cross(n1,direction)
    for q in np.linspace(0,a1,29)[1:]:
        samples.append((c1+quat_turn(after_line-c1,n1,q),quat_turn(direction,n1,q),quat_turn(back_w,n1,q)))
    assert np.linalg.norm(samples[-1][0]-finish)<1e-5
    samples.append((FIXED,t1,w1))
    a0rad=abs(w0@np.cross(n0,t0))*8.4+abs(w0@ n0)*.9
    a1rad=abs(w1@np.cross(n1,t1))*8.4+abs(w1@n1)*.9
    details={"yaw":yaw,"pitch":pitch,"free_path_mm":round(4+distance+R*(a0+a1),4),
             "min_inner_radius_mm":round(R-max(a0rad,a1rad),4),
             "wire_roll_deg":round(math.degrees(roll),4),
             "distance_below_free_190_mm":round(190-(4+distance+R*(a0+a1)),4)}
    return samples,details

def occupied(samples):
    profiles=[]
    for centre,tangent,width in samples:
        height=unit(np.cross(tangent,width))
        vertices=[V(*(centre+sy*8.4*width+sz*.9*height)) for sy,sz in
                  [(-1,-1),(1,-1),(1,1),(-1,1)]]
        profiles.append(Part.Wire(Part.makePolygon(vertices+[vertices[0]]).Edges))
    # Short, independent sections avoid declaring the flexible cable rigid
    # and let the named aperture contact be attributed to the right interval.
    return [Part.makeLoft(profiles[i:i+2],True,True) for i in range(len(profiles)-1)]

def build_tof_track(tof_pose):
    p=HERE.parent/"day19-whole-appearance-and-moving-neck-correction/bus-return.json"
    old=json.loads(p.read_bytes())
    paths=[]
    for i,source in enumerate(old["head"]):
        start=tof_pose.multVec(V(*source[0]))
        finish=V(*source[-1])
        # Route above the board pad edge and then inboard of the eye cradle,
        # into the existing moving tie seat, before the original yaw loop.
        guides=[start,start+V(4.5,0,0),
                V(-196,start.y,158.7+(i%2)*1.65),
                V(-167,finish.y,finish.z+1.7),finish]
        line=Part.BSplineCurve()
        line.interpolate(guides)
        paths.append(line.toShape())
    prior=[sum((V(*a)-V(*b)).Length for a,b in zip(s,s[1:])) for s in old["head"]]
    return paths,{"new_head_path_mm":[round(s.Length,4) for s in paths],
                  "old_head_path_mm":[round(n,4) for n in prior],
                  "retained_moving_anchor_xyz":old["head_receiver"],
                  "retained_fixed_anchor_xyz":old["fixed_receiver"],
                  "physical_route_and_radius_unverified":True}

def write_kit():
    """Supply reference curves, leaving the unqualified FFC hidden by default."""
    from tempfile import gettempdir

    directory=Path(gettempdir())/"robot-cat21-camera-oem/native-kit"
    entries=json.loads((directory/"objects.json").read_bytes())
    old=load_saved(["VL53L5CX"])
    tof_pose,_=tof_geometry(old["VL53L5CX"])
    tof_wires,tof=build_tof_track(tof_pose)
    actual=V(-208.895,40,151.092)
    track,_=make_fan(actual,0,0)
    refs={
        "D21_ToF_Lead_Prototype":(Part.makeCompound(tof_wires),(.75,.5,.1)),
        "D21_FFC_Screen_Unqualified":(Part.makePolygon([V(*q[0]) for q in track]),(.55,.35,.72)),
    }
    for name,(shape,colour) in refs.items():
        (directory/(name+".brep")).write_bytes(shape.exportBrepToString().encode("ascii"))
        entries[name]={"color":colour,"volume":0.,"solids":0}
    write_json(directory/"objects.json",entries)
    configurations=[("installed_camera_clock_upper_exit",actual,Z,Y),
                    ("alternative_180deg_lower_exit",V(-208.895,40,132.908),-Z,Y),
                    ("alternative_clock_90deg_inside",V(-208.895,30.908,142),-Y,Z)]
    data={}
    for label,begin,t,w in configurations:
        data[label]=[make_fan(begin,y,p,t,w)[1] for y in (-20,0,20) for p in (-10,0,10)]
    write_json(HERE/"cable-gate.json",{"camera_FFC_stock_mm":200,"two_ends_debit_mm":10,
        "free_budget_mm":190,"inner_bend_requirement_mm":12.5,"chord_reference_mm":None,
        "pose_samples":data,"ToF":tof,"physical_usable_length":None,"continuous_motion_qualified":False})

if __name__=="__main__":
    write_kit()
