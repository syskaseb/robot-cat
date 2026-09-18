"""Read-only candidate reinforcement audit; source saved document is untouched."""
from pathlib import Path
import json, zipfile, xml.etree.ElementTree as ET
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'hardware/skorupa/v20/Kot_v20_MOCOWANIA_PETG.FCStd'
OUT=ROOT/'hardware/skorupa/v21'
V=A.Vector

def world(o):
    s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement)
    return s

def visible_names(path):
    with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('GuiDocument.xml'))
    return {vp.get('name') for vp in root.findall('.//ViewProvider')
        if vp.find(".//Property[@name='Visibility']/Bool[@value='true']") is not None}

def main():
    OUT.mkdir(exist_ok=True)
    doc=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    objects={o.Name:(o.Label,world(o)) for o in doc.Objects
             if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
             and o.Name in vis and not o.Name.startswith('Axis_')}
    rows=[]
    for name,indices in [('FrameFront20',[17,100]),('FrameRear20',[17,100]),
                         ('SideLeft20',[1,4,6,9,20,21]),('SideRight20',[1,4,6,9,20,21])]:
        original=objects[name][1]
        for i in indices:
            f=original.Faces[i-1]; normal=f.normalAt(0,0)
            layer=f.extrude(normal*1.5)
            # Probe face extension, not a free offset that would move datums.
            hits=[]
            for other,(label,s) in objects.items():
                if other==name or not layer.BoundBox.intersect(s.BoundBox): continue
                v=layer.common(s).Volume
                if v>.001: hits.append(dict(name=other,label=label,volume_mm3=v))
            row=dict(name=name,face=i,normal=list(normal),volume_mm3=layer.Volume,hits=hits)
            rows.append(row); print(json.dumps(row),flush=True)
    (OUT/'candidate-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')

if __name__=='__main__': main()
