"""Read-only audit of the existing chassis attachment interfaces."""
from pathlib import Path
import json
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v19'
OUT.mkdir(exist_ok=True)
doc=App.openDocument(str(ROOT/'hardware/skorupa/v18/Kot_v18_TRAY_CHECKPOINT.FCStd'))
rows=[]
for name in ('Part__Feature002','Part__Feature111','Part__Feature003','Part__Feature112','Part__Feature038','BellyPod','BatteryTray','BackCover18'):
    o=doc.getObject(name)
    if not o: continue
    s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement)
    vertices=s.tessellate(0.2)[0]
    row=dict(name=name,label=o.Label,bounds=[[min(getattr(p,a) for p in vertices),max(getattr(p,a) for p in vertices)] for a in ('x','y','z')],cylinders=[])
    for i,f in enumerate(s.Faces):
        surf=f.Surface
        if isinstance(surf,Part.Cylinder):
            row['cylinders'].append(dict(face=i+1,radius=surf.Radius,center=list(surf.Center),axis=list(surf.Axis),area=f.Area))
    rows.append(row)
(OUT/'interface-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('Measured',len(rows),'native chassis/shell parts',flush=True)
features=[]
for o in doc.Objects:
    if not o.isDerivedFrom('Part::Feature') or o.Shape.isNull() or o.Name in ('BackCover','ComputerDeck') or o.Name.startswith('Axis_'): continue
    s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement)
    features.append((o,s))
audit=[]
for x in (-70,112):
    for y in (-31.5,31.5):
        pad=Part.makeBox(12,12,4,App.Vector(x-6,y-6,38.52))
        entry=Part.makeCylinder(1.25,14,App.Vector(x,y,28.52))
        hits=[]
        for o,s in features:
            for label,new in [('candidate_pad',pad),('M2.5_shaft_envelope',entry)]:
                if new.BoundBox.intersect(s.BoundBox):
                    volume=new.common(s).Volume
                    if volume>0.001: hits.append(dict(envelope=label,name=o.Name,label=o.Label,overlap_mm3=volume))
        audit.append(dict(center=[x,y,38.52],interferences=hits))
(OUT/'mount-candidate-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print('Mount candidates',json.dumps(audit),flush=True)
