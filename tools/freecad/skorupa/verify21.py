"""Reopen and verify native v21, original placements/shapes and visibility."""
from probe21 import ROOT, SOURCE, OUT, visible_names
import json,hashlib
import FreeCAD as A
path=OUT/'Kot_v21_BOKI_PETG.FCStd'
r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
d=A.openDocument(str(path)); base=A.openDocument(str(SOURCE))
maximum=0.; count=0
for o in base.Objects:
    if not o.isDerivedFrom('Part::Feature') or o.Shape.isNull(): continue
    n=d.getObject(o.Name)
    assert n and n.getGlobalPlacement().isSame(o.getGlobalPlacement(),1e-8),o.Name
    before=o.Shape.exportBrepToString().split(); after=n.Shape.exportBrepToString().split()
    assert len(before)==len(after),o.Name
    for a,b in zip(before,after):
        if a==b: continue
        delta=abs(float(a)-float(b)); assert delta<=1e-9,(o.Name,a,b)
        maximum=max(maximum,delta)
    count+=1
vis=visible_names(path); oldvis=visible_names(SOURCE)
assert vis & set(o.Name for o in base.Objects)==oldvis-{p['replaces'] for p in r['parts']}
for p in r['parts']:
    s=d.getObject(p['name']).Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0
    s.check(True)
    assert abs(s.Volume-p['volume_mm3'])<.001
    assert p['name'] in vis and p['replaces'] not in vis
assert 'ShellMounted20' in vis
result=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    reopened=True,retained_source_objects=count,maximum_brep_numeric_delta=maximum,
    original_objects_preserved=True,new_solids=2,bop_check_passed=True,whole_cat_visible=True,
    scope='Central rails only; inherited belly intersections explicitly unresolved')
(OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
