"""Export only validated v20 changed parts, preserving earlier versions."""
from pathlib import Path
from collections import Counter
import json,hashlib
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v20'
report=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
assert not report['collisions'] and not report['tool_collisions']
assert all(v<.001 for z,n,v in report['mount_extraction_checks'])
target=OUT/'stl-prototype'; target.mkdir(exist_ok=True)
if list(target.glob('*.stl')): raise RuntimeError('Preserve previous STL exports; choose a new variant')
rows=[]; pending=[]
for p in report['parts']:
    name=p['name']; path=OUT/(name+'.brep')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
    s=Part.Shape(); s.read(str(path))
    axis=A.Vector(0,0,1); angle=0
    if name.startswith(('Mount','Frame')): axis=A.Vector(0,1,0); angle=90
    elif name.startswith('NutShoe'): axis=A.Vector(1,0,0); angle=180
    elif name.startswith('Side'): axis=A.Vector(1,0,0); angle=90
    transform=A.Placement(A.Vector(),A.Rotation(axis,angle)); s.Placement=transform.multiply(s.Placement)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.2,Relative=False)
    verts,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    bad=sum(v!=2 for v in edges.values())
    assert bad==0 and mesh.isSolid(),name
    b=mesh.BoundBox
    sizes=[b.XLength,b.YLength,b.ZLength]
    assert sizes[0]+16<=256 and sizes[1]+16<=256 and sizes[2]<=256,(name,sizes)
    m=A.Matrix(); m.move(A.Vector(-b.XMin,-b.YMin,-b.ZMin)); mesh.transform(m)
    dest=target/(name+'.stl'); pending.append((dest,mesh))
    rows.append(dict(name=name,size_mm=sizes,triangles=len(faces),non_manifold_edges=bad,
        mesh_is_solid=True,fits_256_with_8mm_brim=True,rotation_axis=list(axis),rotation_deg=angle))
    print(name,sizes,flush=True)
for row,(dest,mesh) in zip(rows,pending):
    mesh.write(str(dest)); row['stl_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
(OUT/'print-validation.json').write_text(json.dumps(dict(parts=rows,
    status='prototype geometry only; support planning and PETG strength testing required'),indent=2),encoding='utf-8')
