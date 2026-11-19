from pathlib import Path
import runpy,zipfile,json,io,numpy as np
from xml.etree import ElementTree as X
from OCP.BRep import BRep_Builder,BRep_Tool
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape,TopoDS
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX,TopAbs_FACE
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
P=Path(__file__).parent;F=P.parent/'FelineInteriorMotion.FCStd'
z=zipfile.ZipFile(F);os=X.fromstring(z.read('Document.xml')).findall('./ObjectData/Object')
o=next(o for o in os if o.get('name').startswith('Ref_Material_MAIN_CurrentMainSupplierReference'))
ref=o.find("./Properties/Property[@name='Shape']/Part");s=TopoDS_Shape();BRepTools.Read_s(s,io.BytesIO(z.read(ref.get('file'))),BRep_Builder())
sv=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](P/'whole-cat19G.FCStd')
def vertices(s):
 ex=TopExp_Explorer(s,TopAbs_VERTEX);a=[]
 while ex.More():a.append(BRep_Tool.Pnt_s(TopoDS.Vertex(ex.Current())).Coord());ex.Next()
 return np.array(a)
a,b=vertices(s),vertices(sv.shape('MAIN_Pololu4853'))
R=None
if a.shape==b.shape:
 m,n=a.mean(0),b.mean(0);u,ss,vh=np.linalg.svd((a-m).T@(b-n));R=u@vh;t=n-m@R;err=np.linalg.norm(a@R+t-b,axis=1).max()
 if err>.001:R=None
holes=[];ex=TopExp_Explorer(sv.shape('MAIN_Pololu4853'),TopAbs_FACE)
while ex.More():
 f=BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
 if f.GetType()==GeomAbs_Cylinder:
    c=f.Cylinder()
    if .55<c.Radius()<1.25 and abs(c.Axis().Direction().Z())>.999:holes.append(np.round(c.Location().Coord()[:2],3).tolist())
 ex.Next()
roles={}
for q in json.loads((P.parent/'endpoint-current-receivers.json').read_bytes())['endpoints']:
 if q['role'] in ['MAIN.GND','MAIN.VOUT','MAIN.VIN'] and R is not None:
    p=np.array(q['candidate_point_mm'])@R+t;near=min(holes,key=lambda h:np.linalg.norm(np.array(h)-p[:2]))
    roles.setdefault(q['role'],[]).append(dict(source=q['id'],registered=p.round(4).tolist(),nearest_hole=near,dxy=float(np.linalg.norm(near-p[:2]))))
res=dict(old_member=o.get('name'),source_matched=R is not None,source_bounds=np.r_[a.min(0),a.max(0)].round(4).tolist(),installed_holes=sorted(set(map(tuple,holes))),roles=roles)
(P/'main-registration.json').write_bytes((json.dumps(res,indent=1)+'\n').encode());print(roles,([a.shape,b.shape]))
