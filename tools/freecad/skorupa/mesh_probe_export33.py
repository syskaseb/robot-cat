"""Export independent audit meshes only; never alters a CAD document."""
from pathlib import Path
import hashlib,json
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
OUT.mkdir(exist_ok=True)
path=ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd';d=A.openDocument(str(path))
p=d.getObject('HeadFace33').Placement
shapes={'HeadFace33':d.getObject('HeadFace33').Shape}
for n in ['HeadFront','Muzzle','EarL','EarR']:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache'/(n+'.brep')));shapes[n]=s
o=A.openDocument(str(ROOT/'hardware/skorupa/v32/OpticsDesign32.FCStd'))
for n in ['OpticalReserve32','ToFWireReserve32']:shapes[n]=o.getObject(n).Shape
for i,y in enumerate([2.54,15.24]):
    s=Part.makeCylinder(3.25,40,A.Vector(10.16,y,-45.6));s.Placement=p*s.Placement;shapes['NoseAccess%d'%i]=s
ref=d.getObject('ReSpeaker33')
for i,point in enumerate([(100.44,-105.295,0),(42.73,-76.375,0)]):
    v=ref.Placement.multVec(A.Vector(*point));x,y=v.x,v.y
    shapes['RightAngle%d'%i]=Part.makeCylinder(3.25,10,A.Vector(x,y,143.11)).fuse(Part.makeBox(-120-x,6.5,6.5,A.Vector(x,y-3.25,150)))
    shapes['BottomDriver%d'%i]=Part.makeCylinder(3.25,6,A.Vector(x,y,124)).fuse(Part.makeBox(-120-x,6.5,6.5,A.Vector(x,y-3.25,123.5)))
    shapes['TopWrench%d'%i]=Part.makeBox(-120-x,6,2,A.Vector(x,y-3,141.1))
rows=[]
for n,s in shapes.items():
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    dest=OUT/(n+'.stl');mesh.write(str(dest))
    row=dict(name=n,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),facets=mesh.CountFacets,
             brep_volume_mm3=s.Volume,mesh_volume_mm3=mesh.Volume,freecad_mesh_solid=mesh.isSolid())
    rows.append(row);print(row,flush=True)
(OUT/'index.json').write_text(json.dumps(dict(master_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    linear_deflection_mm=.05,angular_deflection_rad=.15,meshes=rows),indent=2),encoding='utf8',newline='\n')
