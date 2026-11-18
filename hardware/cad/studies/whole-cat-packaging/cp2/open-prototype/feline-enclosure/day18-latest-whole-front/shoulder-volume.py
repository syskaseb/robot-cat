"""Conservative support planes for the known moving skull lobes at the new pivots."""
from pathlib import Path
import math
import json
import numpy as np
from scipy.spatial import ConvexHull, HalfspaceIntersection

out=Path(__file__).parent
pitch=np.array([-159.,0.,121.])
yaw=np.array([-130.,0.,127.])
# Source analytic skull/cheeks. Ears, steel and later face insert get their
# own actual material checks; these planes claim only the three source lobes.
lobes=[(np.array([-158.,0.,150.]),np.array([64.,77.,64.])),
       (np.array([-204.,-14.,111.]),np.array([20.,25.,24.])),
       (np.array([-204.,14.,111.]),np.array([20.,25.,24.]))]
def posed(y,p):
    a,b=map(math.radians,[y,p])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    return rz@ry, rz@(pitch-ry@pitch-yaw)+yaw
normals=[]
for i in range(84):
    z=1-2*(i+.5)/84
    t=i*math.pi*(3-math.sqrt(5))
    normals.append([math.sqrt(1-z*z)*math.cos(t),math.sqrt(1-z*z)*math.sin(t),z])
normals=np.array(normals+np.eye(3).tolist()+(-np.eye(3)).tolist())
support=np.full(len(normals),-np.inf)
for y in range(-20,21,5):
    for p in range(-10,11,5):
        r,t=posed(y,p)
        for c,axes in lobes:
            support=np.maximum(support,normals@(r@c+t)+np.linalg.norm((normals@r)*axes,axis=1))
arm=max(np.linalg.norm(c-pitch)+max(axes) for c,axes in lobes)
error=(arm+arm+np.linalg.norm(pitch-yaw))*(1-math.cos(math.radians(2.5)))
def shell(clear):
    v=HalfspaceIntersection(np.column_stack([normals,-support-clear-error]),lobes[0][0]).intersections
    hull=ConvexHull(v)
    faces=[]
    for f,eq in zip(hull.simplices,hull.equations):
        a,b,c=v[f]
        faces.append((f if np.cross(b-a,c-a)@eq[:3]>0 else f[[0,2,1]]).tolist())
    return dict(vertices=v.tolist(),faces=faces)
payload=dict(small=shell(1.25),large=shell(3.05),samples=45,interpolation_sag_bound=error,
             clearance=1.25,wall=1.8,source="98 closed whole common assembly / whole-working-form.py, rigid head moved -24 X")
(out/"shoulder-volume.json").write_bytes((json.dumps(payload,separators=(",",":"))+"\n").encode())
print(len(payload["small"]["faces"]),error)
