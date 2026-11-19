from common import *
import trimesh,manifold3d as mf
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
import vtk
P=Path(__file__).parent;S=Saved(native);n='H19_FrontFrame';s=S.shape(n);g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g,1e-8);vol=g.Mass()
folder=P/'components';folder.mkdir(exist_ok=True);f=folder/(n+'.stl');temp=P/'frame-raw.tmp';status=[];ok=False
for lin,ang in [(.018,.085),(.04,.13),(.008,.05)]:
 BRepTools.Clean_s(s);BRepMesh_IncrementalMesh(s,lin,False,ang,True);w=StlAPI_Writer();w.ASCIIMode=False;assert w.Write(s,str(temp))
 orig=trimesh.load(temp,file_type='stl',force='mesh')
 for digits in [7,6,5,4,3]:
    m=orig.copy();m.merge_vertices(digits_vertex=digits);m.update_faces(m.unique_faces()&m.nondegenerate_faces(height=1e-9));m.remove_unreferenced_vertices()
    e=np.bincount(m.edges_unique_inverse);bad=m.edges_unique[e!=2];coords=m.vertices[np.unique(bad)] if len(bad) else np.empty((0,3))
    status.append(dict(lin=lin,ang=ang,digits=digits,boundary=len(bad),extremes=np.round(coords,3).tolist()[:16]))
    if not m.is_watertight:trimesh.repair.fill_holes(m)
    if not m.is_watertight:
        # The manifold constructor can separate coincident topological edges without filling geometry.
        mesh=mf.Mesh(np.array(m.vertices,dtype='f'),np.array(m.faces,dtype='uint32'));mesh.merge();man=mf.Manifold(mesh)
        if man.status()==mf.Error.NoError and man.num_tri()>0:
            mm=man.to_mesh();m=trimesh.Trimesh(vertices=mm.vert_properties[:,:3],faces=mm.tri_verts,process=False)
    if m.is_watertight and m.is_volume and abs(m.volume-vol)/vol<.001:
        ok=True;break
 if ok:break
wr('frame-mesh-proof.json',dict(attempts=status,valid=ok))
if not ok:raise RuntimeError(status[-1])
mat=np.eye(4);mat[:3,3]=-m.bounds[0];m.apply_transform(mat)
# STL uses float32 triangles and carries no topological IDs. Simplify coincident native
# micro-edges first, then separate only coincident vertex fans along their own normals.
base=mf.Manifold(mf.Mesh(np.array(m.vertices,dtype='f'),np.array(m.faces,dtype='uint32')))
assert base.status()==mf.Error.NoError
accepted=False
for tol in [0.002,0.006,0.012,0.023]:
 mm=base.simplify(tol).to_mesh();vertices=np.array(mm.vert_properties[:,:3],float);tri=np.array(mm.tri_verts)
 mesh=trimesh.Trimesh(vertices=vertices,faces=tri,process=False);unique,inv,cnt=np.unique(np.asarray(vertices,dtype='f'),axis=0,return_inverse=True,return_counts=True);dup=cnt[inv]>1
 if dup.any():vertices[dup]+=np.asarray(mesh.vertex_normals)[dup]*tol
 mesh=trimesh.Trimesh(vertices=vertices,faces=tri,process=False);mesh.export(f)
 re=trimesh.load_mesh(f)
 if re.is_watertight and re.is_volume and abs(re.volume-vol)/vol<.001:
    accepted=True;break
wr('frame-mesh-proof.json',dict(attempts=status,stl_reopened=accepted,simplification_mm=tol,coincident_fan_offset_mm=tol if dup.any() else 0,adjusted_vertices=int(dup.sum()),native_volume=vol,mesh_volume=re.volume))
if not accepted:raise RuntimeError('unclosed final STL')
env=re.extents+[16,16,4];assert max(env)<=256
idx=rd(P/'material-index.json');q=next(r for r in idx['parts'] if r['part']==n);q.update(stl='components/'+f.name,sha256=sha(f),print_pose='native floor down; 8 mm brim/side and 4 mm Z support allowance',native_to_mesh=mat.tolist(),envelope_with_allowance=env.tolist(),mesh_volume_error=abs(re.volume-vol)/vol,reopened_watertight=True,export_state='individual component dry-fit',solids=1,valid=True)
f=folder/(n+'.step');w=STEPControl_Writer();assert w.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone and w.Write(str(f))==IFSelect_RetDone
r=STEPControl_Reader();assert r.ReadFile(str(f))==IFSelect_RetDone and r.TransferRoots()>0;rshape=r.OneShape();ex=TopExp_Explorer(rshape,TopAbs_SOLID);assert ex.More();ex.Next();assert not ex.More() and BRepCheck_Analyzer(rshape).IsValid()
idx['steps']=[q for q in idx['steps'] if q['part']!=n]+[dict(part=n,step='components/'+f.name,sha256=sha(f))];wr('material-index.json',idx);print('frame',env,re.volume,vol)
