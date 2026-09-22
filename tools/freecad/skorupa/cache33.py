"""Restore v33 world BReps from signed resting CAD, without saving the source."""
from pathlib import Path
import hashlib,json
import FreeCAD as A
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33'
plan=json.loads((OUT/'assembly-plan.json').read_text());source=OUT/plan['cad_filename']
assert hashlib.sha256(source.read_bytes()).hexdigest()==plan['source_sha256']
d=A.openDocument(str(source));cache=OUT/'shape-cache';cache.mkdir(exist_ok=True)
for r in plan['components']:
    assert d.getObject('Rigid_'+r['name']).Placement.isSame(A.Placement(),1e-6)
    o=d.getObject(r['name']);s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
    assert s.isValid() and s.Solids,r['name'];s.exportBrep(str(cache/(o.Name+'.brep')))
(cache/'index.json').write_text(json.dumps(dict(source_sha256=plan['source_sha256'],objects=[r['name'] for r in plan['components']]),indent=2),encoding='utf8',newline='\n')
print('Restored',len(plan['components']),'BReps; CAD source untouched')
