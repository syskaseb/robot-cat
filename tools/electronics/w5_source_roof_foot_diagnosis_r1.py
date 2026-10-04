"""Locate actual cover material under four proposed roof post feet."""
from pathlib import Path
import json
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[2]
d=A.openDocument(str(ROOT/'hardware/cad/studies/w5-source-grips-native-r2/SourceCarrierInsulationGrips.FCStd'))
s=d.SourceGripCoverFinished.Shape
for x,y in [(-72,5),(-72,-42),(44.5,5),(44.5,-42)]:
    sections=[]
    for z in range(140,186,5):
        probe=Part.makeBox(10,10,1,A.Vector(x-5,y-5,z))
        sections.append([z,s.common(probe).Volume])
    print(json.dumps(dict(x=x,y=y,sections=sections)),flush=True)
