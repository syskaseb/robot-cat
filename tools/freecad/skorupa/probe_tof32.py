"""Read-only occupancy sampling for the inherited muzzle / optical layout."""
from pathlib import Path
import json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
cache=ROOT/'hardware/skorupa/v31/shape-cache'
s=Part.Shape();s.read(str(cache/'Muzzle.brep'))
for z in [101,104,107,108.17418,111,114.625,118,120.87418,124,127,130]:
    row={}
    for y in [0,2.4674,6,9,12,15,18]:
        ray=Part.makeCylinder(.05,80,A.Vector(-215,y,z),A.Vector(1,0,0))
        common=s.common(ray)
        row[y]=[[round(a.optimalBoundingBox().XMin,3),round(a.optimalBoundingBox().XMax,3)] for a in common.Solids]
    print(z,json.dumps(row),flush=True)
