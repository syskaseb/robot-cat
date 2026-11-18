"""Bound the stationary throat in the moving skull frame, keeping the complete headback joints."""
from pathlib import Path
import ast,json,math
import numpy as np
from scipy.spatial import ConvexHull,HalfspaceIntersection
P=Path(__file__).parent
rows=[(-165,41,85,170,.84),(-153,48,80,174,.82),(-133,57,72,175,.77),(-111,65,59,176,.74),(-96,77,43,178,.72),(-84,90.1,13,185,.57),(-76,94,9,185,.53)]
Y=np.array([-130.,0,127]);H=np.array([-159.,0,121]);angles=np.linspace(0,2*np.pi,112,endpoint=False)
groups=[]
for x,w,lo,hi,p in rows:
    signed=lambda a:np.sign(a)*np.abs(a)**p
    groups.append(np.column_stack([np.full_like(angles,x),w*signed(np.cos(angles)),(lo+hi)/2+(hi-lo)/2*signed(np.sin(angles))]))
def matrix(y,p):
    a,b=np.radians([y,p]);z=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);v=np.array([[np.cos(b),0,np.sin(b)],[0,1,0],[-np.sin(b),0,np.cos(b)]])
    return z@v,Y+z@(H-v@H-Y)
# Supporting planes give an outer polyhedron. The chord bound covers angular
# interpolation of the checked moving frame. Loft interpolation stays a CAD check.
dirs=list(np.eye(3))+list(-np.eye(3))
for a in np.linspace(-np.pi/2,np.pi/2,13)[1:-1]:
    for b in np.linspace(0,2*np.pi,24,endpoint=False):dirs.append([np.sin(a),np.cos(a)*np.cos(b),np.cos(a)*np.sin(b)])
N=np.array(dirs);out=[]
for a,b in [(0,2),(2,4),(4,6)]:
    pts=np.vstack(groups[a:b+1]);cloud=[]
    for y in (-20,-10,0,10,20):
        for p in (-10,0,10):
            R,t=matrix(y,p);cloud.append((pts-t)@R)
    cloud=np.vstack(cloud);Ry=np.max(np.linalg.norm((pts-Y)[:,:2],axis=1));Rp=np.max(np.linalg.norm((cloud-H)[:,[0,2]],axis=1))
    sag=(Ry+Rp)*(1-np.cos(np.radians(5)))
    padding=1.35+.35+sag
    support=(cloud@N.T).max(axis=0)+padding
    v=HalfspaceIntersection(np.column_stack([N,-support]),cloud.mean(axis=0)).intersections;h=ConvexHull(v)
    triangles=[]
    for face,eq in zip(h.simplices,h.equations):
        i,j,k=map(int,face);u=v[j]-v[i];w=v[k]-v[i]
        if np.cross(u,w)@eq[:3]<0:j,k=k,j
        triangles.append([i,j,k])
    out.append(dict(vertices=v.round(6).tolist(),faces=triangles,frame_sagitta_bound=sag,base_gap=1.35,tessellation_allowance=.35))
(P/"joint-portal.json").write_bytes((json.dumps(dict(rows=rows,pieces=out),separators=(",",":"))+"\n").encode())
