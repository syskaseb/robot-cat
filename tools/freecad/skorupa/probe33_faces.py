"""Inspect old central mounting feature topology without modifying CAD."""
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache/HeadFront.brep'))
for i,f in enumerate(s.Faces):
    b=f.BoundBox
    print(i+1,str(type(f.Surface)),f.Orientation,round(f.Area,5),[round(v,4) for v in [b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]],flush=True)
for i,e in enumerate(s.Edges):
    adjacent=[j+1 for j,f in enumerate(s.Faces) if any(e.isSame(q) for q in f.Edges)]
    if len(adjacent)!=2:print('EDGE',i+1,len(adjacent),adjacent,str(e.BoundBox),flush=True)
