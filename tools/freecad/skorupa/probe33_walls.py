"""Read-only local shell sections; keep expensive classification out of GUI."""
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache/HeadFront.brep'))
for x,y in [(-133.158487382385,19.19),(-157.078487382385,-38.52)]:
    low,high=(y-2,60) if y>0 else (-60,y+2)
    c=s.common(Part.makeBox(8,high-low,4,A.Vector(x-4,low,132)))
    assert c.isNull() or c.isValid()
    b=c.BoundBox
    print('Wall volume',x,c.Volume,[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],flush=True)
    # Six points per local wall, not thousands of GUI classifications.
    for yy in ([51,52,53,54,55,56] if y>0 else [-49,-50,-51,-52,-53,-54]):
        print(x,yy,s.isInside(A.Vector(x,yy,134),1e-6,True),flush=True)
