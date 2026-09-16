"""Check added geometry against v17's actual placed parts (not scene groups)."""
from brep_inventory import ROOT, OUT, SOURCE
import FreeCAD as App
import Part, json, hashlib

doc=App.openDocument(str(SOURCE))
def placed(o):
    s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement)
    return s
tray=Part.Shape(); tray.read(str(OUT/'PiTray18.brep'))
cover=Part.Shape(); cover.read(str(OUT/'BackCover18.brep'))
old=placed(doc.getObject('BackCover'))
# Bound the new receiver before checking parts. Subtracting two entire nearly
# identical organic shells is unnecessarily expensive in OCCT.
receiver_bounds=Part.makeBox(97,85,6,App.Vector(-25,-42.5,39))
skip={'BackCover','ComputerDeck'}
report={'method':'exact common volumes of added receiver and tray vs placed Part features',
        'receiver_bounds_mm':[-25,72,-42.5,42.5,39,45],'collisions':[],'checked':[],
        'brep_sha256':{n:hashlib.sha256((OUT/(n+'.brep')).read_bytes()).hexdigest() for n in ('PiTray18','BackCover18')}}
for obj in doc.Objects:
    if not obj.isDerivedFrom('Part::Feature') or obj.Name in skip or obj.Shape.isNull():
        continue
    if obj.Name.startswith('Axis_'):
        continue
    s=placed(obj)
    for label,new in [('tray',tray),('added_receiver',receiver_bounds)]:
        if not new.BoundBox.intersect(s.BoundBox):
            continue
        print('checking',label,obj.Name,flush=True)
        if label=='added_receiver':
            candidate=s.common(receiver_bounds)
            overlap=cover.common(candidate).cut(old).Volume if candidate.Volume>0.001 else 0.0
        else:
            overlap=new.common(s).Volume
        report['checked'].append([label,obj.Name,overlap])
        if overlap>0.001:
            report['collisions'].append([label,obj.Name,obj.Label,overlap])
            print('COLLISION',report['collisions'][-1],flush=True)
(OUT/'static-clearance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
assert not report['collisions'], report['collisions']
