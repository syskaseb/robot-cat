"""Read-only diagnosis of OCC head solid classification, no CAD writes."""
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
d=A.openDocument(str(ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd'))
p=d.getObject('HeadFace33').Placement
shapes={}
for n in ['HeadFront','Muzzle']:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache'/(n+'.brep')));shapes[n]=s
for n in ['IntegralPETGFace33','NoseNutAndWireAccess33','IntegralMicSupport33_B']:
    s=d.getObject(n).Shape.copy();s.Placement=p*s.Placement;shapes[n]=s
probe=Part.makeCylinder(3.25,40,A.Vector(10.16,2.54,-45.6));probe.Placement=p*probe.Placement
for n,s in shapes.items():
    print(n,'valid',s.isValid(),'closed',s.isClosed(),'orientation',s.Orientation,'solids',len(s.Solids),'volume',s.Volume,flush=True)
    for v in [A.Vector(-240,0,119),A.Vector(-180,0,117),A.Vector(-150,0,140)]:
        print(' inside',list(v),s.isInside(v,1e-6,True),flush=True)
    for tol in [0,1e-5]:
        c=s.common(probe,tol)
        print(' probe',tol,c.isValid(),c.Volume,'probe volume',probe.Volume,flush=True)
