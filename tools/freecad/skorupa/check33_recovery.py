"""Read-only independent FreeCAD check of recovered OCC cells."""
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
for name in ['maker_volume_all','oriented']:
    if not (OUT/(name+'.brep')).exists():continue
    s=Part.Shape();s.read(str(OUT/(name+'.brep')))
    print(name,'solids',len(s.Solids),'valid',s.isValid(),flush=True)
    for i,c in enumerate(s.Solids):
        m=MeshPart.meshFromShape(Shape=c,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
        n=name+'_%d'%i;c.exportBrep(str(OUT/(n+'.brep')));m.write(str(OUT/(n+'.stl')))
        print(n,'volume',c.Volume,'solid_mesh',m.isSolid(),'far_inside',c.isInside(A.Vector(-240,0,119),1e-6,True),flush=True)
