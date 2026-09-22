"""Rebuild ignored world BReps from saved/resting v29; does not save CAD."""
from pathlib import Path
import hashlib,json
import FreeCAD as A

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v29'
source=OUT/'Kot_v29_OGON_PROTOTYP.FCStd'
plan=json.loads((OUT/'assembly-plan.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==plan['source_sha256']
d=A.openDocument(str(source))
cache=OUT/'shape-cache';cache.mkdir(exist_ok=True)
for row in plan['components']:
    assert d.getObject('Rigid_'+row['name']).Placement.isSame(A.Placement(),1e-6)
    o=d.getObject(row['name']);s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
    assert s.isValid() and s.Solids,row['name']
    s.exportBrep(str(cache/(o.Name+'.brep')))
(cache/'index.json').write_text(json.dumps(dict(source_sha256=plan['source_sha256'],objects=[r['name'] for r in plan['components']]),indent=2),encoding='utf8')
print('Saved',len(plan['components']),'world shapes; native CAD untouched',flush=True)
