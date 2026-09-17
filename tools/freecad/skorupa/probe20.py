"""Measure potential shell/chassis interfaces, no edits to existing CAD."""
from pathlib import Path
import json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v20'; OUT.mkdir(exist_ok=True)
d=A.openDocument(str(ROOT/'hardware/skorupa/v19/Kot_v19_SKORUPA_PETG_256.FCStd'))
def world(o):
    s=o.Shape.copy(); s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement); return s
shell=world(d.getObject('BackCover18'))
rows=[]
for x in (-80,-75,-70,-65,-60,102,107,112,117,122):
    for z in (40,44,48,52,56):
        hits=shell.common(Part.makeLine(A.Vector(x,0,z),A.Vector(x,80,z)))
        rows.append(dict(x=x,z=z,y=sorted(round(v.Point.y,3) for v in hits.Vertexes)))
print('WALL',json.dumps(rows),flush=True)
features=[(o,world(o)) for o in d.Objects if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull() and o.Name not in ('BackCover','ComputerDeck') and not o.Name.startswith('Axis_')]
audit=[]
for x in (-80,-70,112,122):
    for y in (-31.5,31.5):
        s=Part.makeCylinder(4.5,4.52,A.Vector(x,y,31))
        hits=[]
        for o,t in features:
            if s.BoundBox.intersect(t.BoundBox):
                volume=s.common(t).Volume
                if volume>0.001: hits.append([o.Name,o.Label,volume])
        audit.append(dict(center=[x,y],nut_boss_collisions=hits))
print('UNDER FRAME',json.dumps(audit),flush=True)
(OUT/'interface-probe.json').write_text(json.dumps(dict(wall=rows,under_frame=audit),indent=2),encoding='utf-8')
