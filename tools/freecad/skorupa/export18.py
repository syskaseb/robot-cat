"""Export only the newly designed prototype parts, in print orientation."""
from pathlib import Path
from collections import Counter
import json,hashlib
import FreeCAD as App
import Part,MeshPart
from brep_inventory import OUT

def main():
    report=json.loads((OUT/'shell-validation.json').read_text(encoding='utf-8'))
    assert not report['collisions']
    assert all(abs(v)<0.001 for v in report['checks'].values())
    target=OUT/'stl-prototype'
    target.mkdir(exist_ok=True)
    results=[]
    for name in ['ShellFront18','ShellRear18','ShellJoinL','ShellJoinR','PiTray18']:
        path=OUT/(name+'.brep')
        s=Part.Shape(); s.read(str(path))
        if name=='ShellFront18':
            transform=App.Placement(App.Vector(),App.Rotation(App.Vector(0,1,0),90))
        elif name=='ShellRear18':
            transform=App.Placement(App.Vector(),App.Rotation(App.Vector(0,1,0),-90))
        elif name.startswith('ShellJoin'):
            p=report['print_placements'][name]
            transform=App.Placement(App.Vector(*p['base']),App.Rotation(*p['quaternion'])).inverse()
        else:
            transform=App.Placement()
        s.Placement=transform.multiply(s.Placement)
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=0.10,AngularDeflection=0.20,Relative=False)
        vertices,faces=mesh.Topology
        edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
        bad=sum(v!=2 for v in edges.values())
        assert bad==0,(name,'non-manifold edges',bad)
        b=mesh.BoundBox
        tr=App.Matrix(); tr.move(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
        mesh.transform(tr)
        destination=target/(name+'.stl')
        if destination.exists():
            raise RuntimeError('Refusing to overwrite existing STL: '+str(destination))
        mesh.write(str(destination))
        b=mesh.BoundBox
        sizes=[b.XLength,b.YLength,b.ZLength]
        results.append(dict(name=name,triangles=len(faces),non_manifold_edges=bad,
                            size_mm=sizes,fits_180_cube_with_8mm_brim=all(v<=164 for v in sizes[:2]) and sizes[2]<=180,
                            source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            stl_sha256=hashlib.sha256(destination.read_bytes()).hexdigest()))
        print(name,sizes,'triangles',len(faces),flush=True)
    (OUT/'print-validation.json').write_text(json.dumps(dict(parts=results,
        release='PROTOTYPE: inspect supports, fasteners and fit before printing the robot'),indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
