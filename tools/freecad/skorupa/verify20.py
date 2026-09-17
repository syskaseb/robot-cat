"""Independent saved-file check of v20 parts, retained objects and bores."""
from pathlib import Path
import json,math,hashlib,zipfile,xml.etree.ElementTree as ET
import FreeCAD as A

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v20'
report=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
path=OUT/'Kot_v20_MOCOWANIA_PETG.FCStd'
doc=A.openDocument(str(path))
source=A.openDocument(str(ROOT/'hardware/skorupa/v19/Kot_v19_SKORUPA_PETG_256.FCStd'))
for p in report['parts']:
    o=doc.getObject(p['name']); s=o.Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0,p['name']
    assert abs(s.Volume-p['volume_mm3'])<.001,p['name']
for p in report['hardware']:
    s=doc.getObject(p['name']).Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0,p['name']
unchanged=[]; maximum_delta=0
for o in source.Objects:
    if not o.isDerivedFrom('Part::Feature') or o.Shape.isNull(): continue
    n=doc.getObject(o.Name)
    assert n and n.getGlobalPlacement().isSame(o.getGlobalPlacement(),1e-8),o.Name
    a=n.Shape.exportBrepToString().split(); b=o.Shape.exportBrepToString().split()
    assert len(a)==len(b),o.Name
    for av,bv in zip(a,b):
        if av==bv: continue
        try: delta=abs(float(av)-float(bv))
        except ValueError: raise AssertionError((o.Name,av,bv))
        assert delta<=1e-9,(o.Name,av,bv)
        maximum_delta=max(maximum_delta,delta)
    unchanged.append(o.Name)
flanges=[]
for name,old in report['replacements'].items():
    if name=='ShellMounted20': continue
    radius=1.025 if name.startswith('Frame') else 1.3
    expected=4*1.5*math.pi*(1.45**2-radius**2)
    actual=doc.getObject(old).Shape.Volume-doc.getObject(name).Shape.Volume
    assert abs(actual-expected)<.001,(name,actual,expected)
    flanges.append(dict(name=name,upper_holes_changed=4,diameter_mm=2.9,volume_removed_mm3=actual,analytical_volume_mm3=expected))
with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('GuiDocument.xml'))
vis={vp.get('name'):vp.find(".//Property[@name='Visibility']/Bool").get('value')=='true' for vp in root.findall('.//ViewProvider') if vp.find(".//Property[@name='Visibility']/Bool") is not None}
assert all(vis[p['name']] for p in report['parts']+report['hardware'])
assert all(not vis[n] for n in report['replacements'].values())
assert not vis['BackCover'] and not vis['ComputerDeck']
result=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reopened=True,
    new_printed_solids=len(report['parts']),fastener_solids=len(report['hardware']),
    retained_source_objects=len(unchanged),maximum_brep_numeric_delta=maximum_delta,
    original_objects_preserved=True,whole_cat_visible=True,flange_checks=flanges,
    scope='Static model verification; no strength, dynamic, cable or physical assembly approval')
(OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
