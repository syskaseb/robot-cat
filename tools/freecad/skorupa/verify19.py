"""Verify persisted native v19 against its unchanged source and gauge recipe."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import FreeCAD as App

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v19'
report=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
path=OUT/'Kot_v19_SKORUPA_PETG_256.FCStd'
doc=App.openDocument(str(path))
source=App.openDocument(str(ROOT/report['source']))
for name,p in zip(('BackCover18','PiTray18'),report['parts'][:2]):
    o=doc.getObject(name)
    assert o.Shape.isValid() and len(o.Shape.Solids)==1,name
    assert abs(o.Shape.Volume-p['volume_mm3'])<0.001,name
    assert o.MaterialNote.startswith('PETG'),name
unchanged=[]
maximum_brep_numeric_delta=0.0
for o in source.Objects:
    if not o.isDerivedFrom('Part::Feature') or o.Shape.isNull(): continue
    n=doc.getObject(o.Name)
    assert n and abs(n.Shape.Volume-o.Shape.Volume)<0.001,o.Name
    assert n.getGlobalPlacement().isSame(o.getGlobalPlacement(),1e-8),o.Name
    # Saving/reopening OCCT normalises some unit directions by ~1e-16.
    # Compare every BRep token, not brittle byte hashes or only equal volumes.
    left=n.Shape.exportBrepToString().split(); right=o.Shape.exportBrepToString().split()
    assert len(left)==len(right),(o.Name,'BRep structure changed')
    for a,b in zip(left,right):
        if a==b: continue
        try: delta=abs(float(a)-float(b))
        except ValueError: raise AssertionError((o.Name,'BRep token changed',a,b))
        assert delta<=1e-9,(o.Name,'BRep geometry changed',a,b)
        maximum_brep_numeric_delta=max(maximum_brep_numeric_delta,delta)
    unchanged.append(o.Name)
assert not doc.getObject('ShellFront18') and not doc.getObject('ShellJoinL')
with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('GuiDocument.xml'))
vis={v.get('name'):v.find(".//Property[@name='Visibility']/Bool").get('value')=='true' for v in root.findall('.//ViewProvider') if v.find(".//Property[@name='Visibility']/Bool") is not None}
assert vis['BackCover18'] and vis['PiTray18']
assert not vis['BackCover'] and not vis['ComputerDeck']
g=App.openDocument(str(OUT/'PETG_FitGauge19.FCStd'))
g.recompute()
assert g.getObject('NutDepth2_8mm').Shape.isValid()
assert abs(g.getObject('NutDepth2_8mm').Shape.Volume-report['parts'][2]['volume_mm3'])<0.001
result=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reopened=True,
    source_geometry_and_placements_preserved=len(unchanged),continuous_shell_visible=True,
    brep_comparison='all tokens identical or numeric within absolute 1e-9',
    maximum_brep_numeric_delta=maximum_brep_numeric_delta,
    split_shell_objects_absent=True,parametric_gauge_reopened_and_recomputed=True,
    scope='Static geometry and persistence only; not print or robot release approval')
(OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
