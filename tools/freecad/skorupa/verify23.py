"""Reopen native assembly and prove original geometry/placements unchanged."""
from build23 import OUT,SOURCE,sha,visible_names
import FreeCAD as A
import json
path=OUT/'Kot_v23_AKUMULATOR_PETG.FCStd'
r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
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
assert vis & {o.Name for o in source.Objects}==oldvis-{'BatteryTray'}
for p in r['parts']+r['hardware']:
    s=d.getObject(p['name']).Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0 and p['name'] in vis,p['name']
    s.check(True); assert abs(s.Volume-p['volume_mm3'])<.001
assert {'ShellMounted20','Belly22'}<=vis
result=dict(file=path.name,sha256=sha(path),reopened=True,retained_source_shapes=count,
    maximum_brep_numeric_delta=maximum,original_geometry_and_placements_preserved=True,
    new_printed_solids=len(r['parts']),new_bought_envelopes=len(r['hardware']),bop_check_passed=True,
    whole_cat_visible=True,scope='Saved-state and geometry verification, not full print/load approval')
(OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
