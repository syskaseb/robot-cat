"""Prototype exports, manifold check and 256 mm bed envelope."""
from pathlib import Path
from collections import Counter
import json,hashlib
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v21'
report=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
assert not report['collisions']
target=OUT/'stl-prototype'; target.mkdir(exist_ok=True)
if list(target.glob('*.stl')): raise RuntimeError('Preserve existing exports')
rows=[]; pending=[]
for p in report['parts']:
    path=OUT/(p['name']+'.brep')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
    s=Part.Shape(); s.read(str(path))
    s.rotate(A.Vector(),A.Vector(1,0,0),90)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.2,Relative=False)
    verts,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    assert all(n==2 for n in edges.values()) and mesh.isSolid(),p['name']
    b=mesh.BoundBox; sizes=[b.XLength,b.YLength,b.ZLength]
    assert sizes[0]+16<=256 and sizes[1]+16<=256 and sizes[2]<=256
    m=A.Matrix(); m.move(A.Vector(-b.XMin,-b.YMin,-b.ZMin)); mesh.transform(m)
    dest=target/(p['name']+'.stl'); pending.append((dest,mesh))
    rows.append(dict(name=p['name'],size_mm=sizes,triangles=len(faces),non_manifold_edges=0,
        mesh_is_solid=True,fits_256_with_8mm_brim=True,rotation_axis=[1,0,0],rotation_deg=90))
for row,(dest,mesh) in zip(rows,pending):
    mesh.write(str(dest)); row['stl_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
(OUT/'print-validation.json').write_text(json.dumps(dict(parts=rows,
    scope='Two rail prototypes; slicer and load testing pending'),indent=2),encoding='utf-8')
print(json.dumps(rows),flush=True)
