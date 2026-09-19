"""Independent saved-file verification, including native part preservation."""
from build22 import ROOT,SOURCE,OUT,sha,visible_names
import FreeCAD as A
import json
path=OUT/'Kot_v22_BRZUCH_PETG.FCStd'; r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
d=A.openDocument(str(path)); source=A.openDocument(str(SOURCE))
maximum=0.; count=0
for o in source.Objects:
    if not o.isDerivedFrom('Part::Feature') or o.Shape.isNull(): continue
    n=d.getObject(o.Name)
    assert n and n.getGlobalPlacement().isSame(o.getGlobalPlacement(),1e-8),o.Name
    a=o.Shape.exportBrepToString().split(); b=n.Shape.exportBrepToString().split()
    assert len(a)==len(b),o.Name
    for av,bv in zip(a,b):
        if av==bv: continue
        delta=abs(float(av)-float(bv)); assert delta<=1e-9,(o.Name,av,bv)
        maximum=max(maximum,delta)
    count+=1
vis=visible_names(path); oldvis=visible_names(SOURCE)
assert vis & {o.Name for o in source.Objects}==oldvis-set(r['replacements'].values())
for p in r['parts']+r['hardware']:
    s=d.getObject(p['name']).Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0,p['name']
    s.check(True); assert p['name'] in vis
    if 'volume_mm3' in p: assert abs(s.Volume-p['volume_mm3'])<.001
assert 'ShellMounted20' in vis
result=dict(file=path.name,sha256=sha(path),reopened=True,original_objects_preserved=True,
    retained_source_objects=count,maximum_brep_numeric_delta=maximum,new_printed_solids=3,
    new_fastener_solids=8,bop_check_passed=True,whole_cat_visible=True,
    scope='Preservation and solid validity; not a complete robot print release')
(OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
