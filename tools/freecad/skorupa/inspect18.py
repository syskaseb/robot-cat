"""Read-only FreeCAD inspection; run in FreeCAD via MCP execute_code."""
import FreeCAD as App
import FreeCADGui as Gui
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
source = ROOT / 'hardware/skorupa/Kot_v17_WNETRZE.FCStd'
doc = next((d for d in App.listDocuments().values() if d.FileName == str(source).replace('\\', '/')), None)
if doc is None:
    doc = App.openDocument(str(source))
App.setActiveDocument(doc.Name)
rows = []
for obj in doc.Objects:
    if not obj.isDerivedFrom('Part::Feature') or obj.Shape.isNull():
        continue
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement().multiply(obj.Placement.inverse()).multiply(shape.Placement)
    b = shape.BoundBox
    rows.append(dict(name=obj.Name, label=obj.Label, visible=obj.Visibility,
                     solids=len(shape.Solids), valid=shape.isValid(), volume=shape.Volume,
                     bbox=[round(v, 3) for v in (b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax)],
                     parents=[o.Name for o in obj.InList]))
out = ROOT / 'hardware/skorupa/v18'
out.mkdir(exist_ok=True)
(out / 'baseline-inventory.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
print(json.dumps(dict(document=doc.Name, objects=len(rows), inventory=str(out/'baseline-inventory.json'))))
