"""Closed planar material around the pitch and yaw interfaces, from the actual swept sections."""
from pathlib import Path
import runpy,json,numpy as np,ast,math
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](P/"whole-cat19D.FCStd")
for fn in ast.parse((P.parent/"day18-open-front-assembly/occupied-gate.py").read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(P),"exec"))
cache={}
def edges(name):
    if name in cache:return cache[name]
    s=D.shape(name);BRepMesh_IncrementalMesh(s,.32,False,.24,True)
    e=TopExp_Explorer(s,TopAbs_FACE);allpts=[]
    while e.More():
        f=TopoDS.Face(e.Current());loc=TopLoc_Location();m=BRep_Tool.Triangulation_s(f,loc)
        if m:
            tr=loc.Transformation();v=np.array([m.Node(i+1).Transformed(tr).Coord() for i in range(m.NbNodes())])
            ids=np.array([m.Triangle(i+1).Get() for i in range(m.NbTriangles())])-1
            allpts.extend([v[ids[:,[0,1]]],v[ids[:,[1,2]]],v[ids[:,[2,0]]]])
        e.Next()
    cache[name]=np.concatenate(allpts);return cache[name]
def crossing(es,R,T,x,points):
    es=es@R.T+T;a,b=es[:,0],es[:,1]
    for xx in [x-1.8,x+.7,x+2.8]:
        d=b[:,0]-a[:,0];k=(abs(d)>1e-9)&((a[:,0]-xx)*(b[:,0]-xx)<=0)
        if k.any():points.append((a[k]+((xx-a[k,0])/d[k])[:,None]*(b[k]-a[k]))[:,1:])
def hull(pts,margin):
    p=np.concatenate(pts);return MultiPoint(p[ConvexHull(p).vertices]).convex_hull.buffer(margin,quad_segs=3)
lay=json.loads((P/"whole-lay.json").read_bytes());out={}
for side,x in [("yaw",-137.9),("fixed",-109.9)]:
    holes=[]
    for name,owner in [("D19D_PitchBack","pitch"),("D19D_Face","pitch"),("D19D_OpticsCarrier","pitch"),("BR_FINISHED_YAW_SADDLE","yaw"),("MG92B_Head_pitch","yaw"),("MG92B_Head_yaw","fixed"),("B19_FrontFloor","fixed"),("D19D_YawHood","yaw")]:
        if (side=="yaw" and name=="D19D_YawHood") or (side=="fixed" and owner=="fixed"):continue
        pts=[];es=edges(name)
        for y in (range(-20,21,4) if (side=="fixed" or owner=="fixed") else [0]):
            for p in (range(-10,11,4) if owner=="pitch" else [0]):
                t=transforms(y,p);R0,T0=t[side];R,T=t[owner];crossing(es,R0.T@R,R0.T@(T-T0),x,pts)
        if pts:holes.append(hull(pts,4.2))
    pts=[]
    for q in lay["motion"]:
        R,T=transforms(q["yaw"],q["pitch"])[side]
        for c in q["cores"]:
            a=(np.array(c)-T)@R;hit=a[abs(a[:,0]-x)<3.5,1:]
            if len(hit):pts.append(hit)
    if pts:holes.append(hull(pts,3.5))
    wires=json.loads((P.parent/"day18-open-front-assembly/occupied-layout.json").read_bytes())["FFC"]
    pts=[]
    for q in wires:
        R,T=transforms(q["yaw"],q["pitch"])[side]
        a=(np.asarray(q["corners"]).reshape(-1,3)-T)@R;hit=a[abs(a[:,0]-x)<4,1:]
        if len(hit):pts.append(hit)
    if pts:holes.append(hull(pts,3.5))
    u=unary_union(holes);polys=list(u.geoms) if u.geom_type=="MultiPolygon" else [u]
    out[side]=[np.array(poly.exterior.coords).round(4).tolist() for poly in polys]
(P/"seam-profiles.json").write_bytes((json.dumps(out,separators=(",",":"))+"\n").encode())
print({k:len(v) for k,v in out.items()})

