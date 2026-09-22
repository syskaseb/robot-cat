"""Read-only Boolean-order diagnosis on actual native source shapes."""
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
def read(n):
    s=Part.Shape();s.read(str(OUT/(n+'.brep')));return s
def check(n,s):
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    m.write(str(OUT/(n+'.stl')));s.exportBrep(str(OUT/(n+'.brep')))
    print(n,s.isValid(),len(s.Solids),s.Volume,m.isSolid(),s.isInside(A.Vector(-240,0,119),1e-6,True),flush=True)
    return s
head=read('current_HeadShellRecovered33');muzzle=Part.Shape();muzzle.read(str(ROOT/'hardware/skorupa/v32/shape-cache/Muzzle.brep'))
for n in ['current_HeadShellRecovered33','current_IntegralPETGFace33','current_NoseNutAndWireAccess33','current_IntegralMicSupport33_A']:check(n,read(n))
doc=A.openDocument(str(ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd'));sk=doc.getObject('NoseServiceOpening33')
wire=sk.Shape.Wires[0].copy();wire.Placement=sk.getGlobalPlacement()*sk.Placement.inverse()*wire.Placement
cutter=Part.Face(wire).extrude(A.Vector(40,0,0));check('service_cutter',cutter)
cut=check('head_cut_first',head.cut(cutter,1e-5).removeSplitter())
check('face_after_cut',cut.fuse(muzzle,1e-5).removeSplitter())
check('muzzle_alone',muzzle)
