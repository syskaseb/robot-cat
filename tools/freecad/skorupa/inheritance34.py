"""Read-only strict retained geometry/snapshot check; run with FreeCAD Python.

Only tessellation is stripped; numeric tolerances remain 1e-9 abs / 1e-12 rel.
No topology repair, scaling, placement alignment or geometric simplification.
"""
import json
import FreeCAD as A
import Part
from inheritance30 import compare_text, sha
from support34 import OUT, SOURCE, SOURCE_SHA, MASTER, TARGET, ADDITIONS, REPLACEMENTS, instance


def read_shape(path):
    s = Part.Shape()
    s.read(str(path))
    return s


def text(shape):
    return shape.cleaned().exportBrepToString()


def main():
    old = json.loads((SOURCE / 'assembly-plan.json').read_text())
    new = json.loads((OUT / 'assembly-plan.json').read_text())
    assert sha(SOURCE / old['cad_filename']) == SOURCE_SHA
    assert sha(TARGET) == new['source_sha256']
    assert sha(MASTER) == new['master_sha256']
    for folder, plan in [(SOURCE, old), (OUT, new)]:
        assert json.loads((folder / 'shape-cache/index.json').read_text())['source_sha256'] == plan['source_sha256']
    unchanged = {r['name'] for r in old['components']} - set(REPLACEMENTS)
    assert len(unchanged) == 279
    rows = []
    for n in sorted(unchanged):
        shapes = [read_shape(p / 'shape-cache' / (n + '.brep')) for p in [SOURCE, OUT]]
        rows.append(dict(name=n, **compare_text(*(text(s) for s in shapes))))
    master = A.openDocument(str(MASTER))
    snapshots = []
    expected = dict(REPLACEMENTS)
    expected.update({n: (r[0], r[4]) for n, r in ADDITIONS.items()})
    for n, (src, xyz) in sorted(expected.items()):
        source = instance(master, src, xyz)
        target = read_shape(OUT / 'shape-cache' / (n + '.brep'))
        snapshots.append(dict(name=n, **compare_text(text(source), text(target))))
    report = dict(source_sha256=new['source_sha256'], inherited_from_sha256=SOURCE_SHA,
                  master_sha256=new['master_sha256'], verified=True, inherited_parts=len(rows),
                  absolute_tolerance=1e-9, relative_tolerance=1e-12,
                  max_absolute_delta=max(r['max_absolute_delta'] for r in rows + snapshots),
                  inherited_geometry=rows, master_snapshot_checks=snapshots, scope=__doc__)
    (OUT / 'inheritance-check.json').write_text(json.dumps(report, indent=2), encoding='utf8', newline='\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['inherited_geometry', 'master_snapshot_checks']}, indent=2))


if __name__ == '__main__':
    main()
