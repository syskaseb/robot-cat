"""Nine-pose triangulated-surface rejection screen on four named moving interfaces."""
from pathlib import Path
import runpy,json,ast,math,hashlib,numpy as np
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
import vtk
P=Path(__file__).parent;native=P/"whole-cat19D.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](native)
for fn in ast.parse((P.parent/"day18-open-front-assembly/occupied-gate.py").read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="transforms":exec(compile(ast.Module([fn],type_ignores=[]),str(P),"exec"))
def mesh(n):
    s=D.shape(n);BRepMesh_IncrementalMesh(s,.06,False,.11,True);pts=vtk.vtkPoints();pts.SetDataTypeToDouble();tri=vtk.vtkCellArray()
    ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current());loc=TopLoc_Location();m=BRep_Tool.Triangulation_s(f,loc)
        if m:
            base=pts.GetNumberOfPoints();tr=loc.Transformation()
            for i in range(m.NbNodes()):pts.InsertNextPoint(*m.Node(i+1).Transformed(tr).Coord())
            for i in range(m.NbTriangles()):
                tri.InsertNextCell(3,[base+j-1 for j in m.Triangle(i+1).Get()])
        ex.Next()
    pd=vtk.vtkPolyData();pd.SetPoints(pts);pd.SetPolys(tri);return pd
pairs=[("D19D_PitchBack","pitch","D19D_YawHood","yaw"),("D19D_YawHood","yaw","D19D_Shoulder","fixed"),("D19D_PitchBack","pitch","D19D_Shoulder","fixed"),("D19D_Face","pitch","D19D_Shoulder","fixed"),("D19D_YawHood","yaw","D19D_FrontFloor","fixed")]
geo={n:mesh(n) for pair in pairs for n in (pair[0],pair[2])};rows=[]
for y in [-20,0,20]:
    for p in [-10,0,10]:
        matrices={}
        for o,(R,T) in transforms(y,p).items():
            mat=vtk.vtkMatrix4x4();h=np.eye(4);h[:3,:3]=R;h[:3,3]=T;mat.DeepCopy(h.ravel());matrices[o]=mat
        for a,oa,b,ob in pairs:
            c=vtk.vtkCollisionDetectionFilter()
            for j,(n,o) in enumerate([(a,oa),(b,ob)]):c.SetInputData(j,geo[n]);c.SetMatrix(j,matrices[o])
            c.SetCollisionModeToFirstContact();c.SetBoxTolerance(.0001);c.SetCellTolerance(.0001);c.Update()
            hit=bool(c.GetNumberOfContacts());first=None;inside=None
            if hit:
                first=np.array(c.GetContactsOutput().GetPoint(0));offsets=np.array([[u,v,w] for u in [-.3,-.12,0,.12,.3] for v in [-.3,-.12,0,.12,.3] for w in [-.3,-.12,0,.12,.3]])
                query=first+offsets;Ra,Ta=transforms(y,p)[oa];Rb,Tb=transforms(y,p)[ob]
                for pt in query:
                    if D.inside(a,[(pt-Ta)@Ra]) is not None and D.inside(b,[(pt-Tb)@Rb]) is not None:inside=pt.round(4).tolist();break
            rows.append(dict(a=a,b=b,yaw=y,pitch=p,mesh_surface_hit=hit,first_surface_point=first.round(4).tolist() if hit else None,confirmed_material_point=inside))
(P/"motion-screen.json").write_bytes((json.dumps(dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),linear_deflection=.06,angular_deflection=.11,rows=rows,physical_PASS=False),indent=1)+"\n").encode())
print([(a,b,sum(r["mesh_surface_hit"] for r in rows if r["a"]==a and r["b"]==b)) for a,_,b,_ in pairs])
