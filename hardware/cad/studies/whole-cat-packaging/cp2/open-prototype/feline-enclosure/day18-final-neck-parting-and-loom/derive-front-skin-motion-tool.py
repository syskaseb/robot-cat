import numpy as np,math,json
from scipy.spatial import HalfspaceIntersection,ConvexHull
from pathlib import Path
P=Path(__file__).parent
lobes=[(np.array([-134.,0,150]),np.array([64.,77,64])),(np.array([-180.,-14,111]),np.array([20.,25,24])),(np.array([-180.,14,111]),np.array([20.,25,24]))]
def rot(y,p):
 a,b=map(math.radians,[y,p]);Y=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);B=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]]);Pc=np.array([-135,0,121]);Yc=np.array([-106,0,127]);R=Y@B;t=Y@(Pc-B@Pc-Yc)+Yc;return R,t
def support(n,c,r):
 h=np.linalg.norm(r*n);px=c[0]+r[0]**2*n[0]/h
 if px<=-137:return float(n@c+h)
 u=(-137-c[0])/r[0]
 if u<=-1:return -1e9
 return float(-137*n[0]+c[1]*n[1]+c[2]*n[2]+math.sqrt(max(0,1-u*u))*math.hypot(r[1]*n[1],r[2]*n[2]))
rp=math.hypot(65,93);ry=math.sqrt(65**2+77**2+93**2)+math.hypot(29,6)
motion_error=rp*(1-math.cos(math.radians(5)))+ry*(1-math.cos(math.radians(10)))
margin=1.25+motion_error
normals=[]
for i in range(96):
 z=1-2*(i+.5)/96;t=i*math.pi*(3-math.sqrt(5));normals.append([math.sqrt(1-z*z)*math.cos(t),math.sqrt(1-z*z)*math.sin(t),z])
normals+=np.eye(3).tolist()+(-np.eye(3)).tolist();planes=[]
for q in normals:
 n=np.array(q);hs=[]
 for y in [-20,0,20]:
  for p in [-10,0,10]:
   R,t=rot(y,p);hs.append(max(support(R.T@n,c,r) for c,r in lobes)+n@t)
 planes.append([*q,-max(hs)-margin])
v=HalfspaceIntersection(np.array(planes),np.array([-175.,0,145.])).intersections;h=ConvexHull(v);faces=[]
for ids,eq in zip(h.simplices,h.equations):
 a,b,c=v[ids];ids=ids.tolist()
 if np.dot(np.cross(b-a,c-a),eq[:3])<0:ids=[ids[0],ids[2],ids[1]]
 faces.append(ids)
(P/'front-skin-continuous-motion-cover.json').write_bytes((json.dumps({'vertices':v.tolist(),'faces':faces,'source_front_clip_x':-137,'project_clearance':1.25,'continuous_chord_sag_enclosure':motion_error,'total_outward_support_margin':margin,'proof':'Each source front ellipsoid clipped atX<=-137 has analytic support. Nine correlated endpoint placements enclose tensor-product interpolants. Pitch chord sag <=rp(1-cos5), yaw sag <=ry(1-cos10); outward support margin includes both and1.25. Finite plane intersection is an OUTER convex cover, never an inscribed clearance claim. Ear material below guard height must be separately bounded; witness tests remain explicit.','not_wire_solver':True},indent=2)+'\n').encode());print('ONE_FRONT_TOOL',len(v),len(faces),margin)
