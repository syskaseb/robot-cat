"""Export the three validated PETG parts, preserving old checkpoints."""
from build22 import OUT,sha
from collections import Counter
import json
import FreeCAD as A
import Part,MeshPart
r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
checks=json.loads((OUT/'assembly-validation.json').read_text(encoding='utf-8'))
assert not r['collisions'] and not checks['nut_insertion_collisions'] and not checks['tool_collisions']
assert all(not row['collisions'] for row in checks['removal_samples'])
target=OUT/'stl-prototype'; target.mkdir(exist_ok=True)
if list(target.glob('*.stl')): raise RuntimeError('Preserve existing exports')
pending=[]; rows=[]
for p in r['parts']:
    path=OUT/(p['name']+'.brep'); assert sha(path)==p['sha256']
    assert checks['source_breps'][p['name']]==p['sha256']
    s=Part.Shape(); s.read(str(path)); angle=90 if p['name'].startswith('Side') else 0
    if angle: s.rotate(A.Vector(),A.Vector(1,0,0),angle)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.2,Relative=False)
    verts,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    assert all(n==2 for n in edges.values()) and mesh.isSolid(),p['name']
    b=mesh.BoundBox; size=[b.XLength,b.YLength,b.ZLength]
    assert size[0]+16<=256 and size[1]+16<=256 and size[2]<=256
    m=A.Matrix(); m.move(A.Vector(-b.XMin,-b.YMin,-b.ZMin)); mesh.transform(m)
    pending.append((target/(p['name']+'.stl'),mesh))
    rows.append(dict(name=p['name'],size_mm=size,triangles=len(faces),mesh_is_solid=True,
        non_manifold_edges=0,fits_256_with_8mm_brim=True,rotation_axis=[1,0,0],rotation_deg=angle))
for row,(path,mesh) in zip(rows,pending):
    mesh.write(str(path)); row['stl_sha256']=sha(path)
(OUT/'print-validation.json').write_text(json.dumps(dict(parts=rows,
    scope='Belly and two revised rails; slicer and physical PETG tests pending'),indent=2),encoding='utf-8')
print(json.dumps(rows),flush=True)
