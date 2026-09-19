"""Export validated carrier only, not bought hardware/liner/straps."""
from build23 import OUT,sha
import FreeCAD as A
import Part,MeshPart,json
from collections import Counter
r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
c=json.loads((OUT/'assembly-validation.json').read_text(encoding='utf-8'))
assert not r['collisions'] and not c['tool_collisions']
target=OUT/'stl-prototype'; target.mkdir(exist_ok=True)
assert not list(target.glob('*.stl')),'Preserve existing print exports'
rows=[]
for row in r['parts']:
    p=OUT/(row['name']+'.brep'); assert sha(p)==row['sha256']==c['source_breps'][row['name']]
    s=Part.Shape(); s.read(str(p))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    vertices,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    assert all(v==2 for v in edges.values()) and mesh.isSolid()
    b=mesh.BoundBox; dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+16<=256 and dims[1]+16<=256 and dims[2]<=256
    m=A.Matrix(); m.move(A.Vector(-b.XMin,-b.YMin,-b.ZMin)); mesh.transform(m)
    p=target/(row['name']+'.stl'); mesh.write(str(p))
    rows.append(dict(name=row['name'],size_mm=dims,triangles=len(faces),mesh_is_solid=True,non_manifold_edges=0,
                     fits_256_with_8mm_brim=True,sha256=sha(p),orientation='flat base down; inspect 16-mm underside bridges in slicer'))
(OUT/'print-validation.json').write_text(json.dumps(dict(parts=rows,scope='Prototype only; 16-mm bridging/slot fit require PETG coupon and slicer inspection'),indent=2),encoding='utf-8')
print(json.dumps(rows),flush=True)
