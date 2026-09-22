"""Read-only topology lineage; diagnostic meshes only, never source CAD."""
from pathlib import Path
import FreeCAD as A
import Part, MeshPart
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
for v in ['v31','v30','v29','v28']:
    path=ROOT/'hardware/skorupa'/v/'shape-cache/HeadFront.brep'
    if not path.exists():continue
    s=Part.Shape();s.read(str(path))
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    m.write(str(OUT/('HeadFront_'+v+'.stl')))
    print(v,s.isValid(),s.Volume,m.isSolid(),s.isInside(A.Vector(-240,0,119),1e-6,True),flush=True)
doc=A.openDocument(str(ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd'))
for n in ['HeadFrontSource32','IntegralPETGFace33','NoseNutAndWireAccess33']:
    o=doc.getObject(n);s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    m.write(str(OUT/(n+'.stl')))
    print(n,o.State,o.getStatusString(),s.Volume,len(s.Solids),m.isSolid(),flush=True)
