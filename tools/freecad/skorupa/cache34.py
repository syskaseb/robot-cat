"""Read-only cache restoration from the signed v34 CAD, outside the GUI."""
import hashlib
import json
import FreeCAD as A
from support34 import OUT, TARGET


def main():
    plan = json.loads((OUT / 'assembly-plan.json').read_text())
    digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert digest == plan['source_sha256']
    d = A.openDocument(str(TARGET))
    cache = OUT / 'shape-cache'
    cache.mkdir(exist_ok=True)
    for row in plan['components']:
        obj = d.getObject(row['name'])
        s = obj.Shape.copy()
        s.Placement = obj.getGlobalPlacement() * obj.Placement.inverse() * s.Placement
        s.exportBrep(str(cache / (obj.Name + '.brep')))
    assert hashlib.sha256(TARGET.read_bytes()).hexdigest() == digest
    (cache / 'index.json').write_text(json.dumps(dict(source_sha256=digest,
        objects=[r['name'] for r in plan['components']]), indent=2), encoding='utf8', newline='\n')
    print('Cached', len(plan['components']), 'signed shapes; source unchanged')


if __name__ == '__main__':
    main()
