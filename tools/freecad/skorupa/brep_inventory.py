"""Inspect v17 BReps directly using FreeCAD's bundled Python (no GUI)."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'hardware/skorupa/v18'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT / 'hardware/skorupa/Kot_v17_WNETRZE.FCStd'

def read_shapes():
    result = {}
    with zipfile.ZipFile(SOURCE) as z:
        root = ET.fromstring(z.read('Document.xml'))
        for obj in root.find('ObjectData').findall('Object'):
            props = {p.get('name'): p for p in obj.find('Properties')}
            p = props.get('Shape')
            if p is None:
                continue
            file = p.find('Part').get('file')
            shape = Part.Shape()
            shape.importBrepFromString(z.read(file).decode('ascii'))
            label = props['Label'].find('String').get('value')
            result[obj.get('name')] = (shape, label)
    return result

if __name__ == '__main__':
    shapes = read_shapes()
    rows = []
    # v17's CatConcept child geometry is already placed within its parent frame.
    flip = App.Placement(App.Vector(42,0,0), App.Rotation(App.Vector(0,0,1),180))
    selected = False
    for name, (shape, label) in shapes.items():
        if name == 'Battery':
            selected = True
        if not selected:
            continue
        shape.Placement = flip.multiply(shape.Placement)
        b = shape.BoundBox
        rows.append(dict(name=name, label=label, solids=len(shape.Solids), volume=round(shape.Volume,3),
                         bbox=[round(v,3) for v in (b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax)]))
        print(name, rows[-1]['bbox'], flush=True)
    (OUT/'brep-inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
