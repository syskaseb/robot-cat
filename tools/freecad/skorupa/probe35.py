"""Read-only AUX placement study against the signed v34 shapes (millimetres)."""
from pathlib import Path
import hashlib
import json
import FreeCAD as A
import Part

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'hardware/skorupa/v34'


def exact(a, b):
    return sum(abs(sa.common(sb).Volume) for sa in a.Solids for sb in b.Solids
               if sa.BoundBox.intersect(sb.BoundBox))


def main():
    plan = json.loads((OLD / 'assembly-plan.json').read_text())
    assert hashlib.sha256((OLD / plan['cad_filename']).read_bytes()).hexdigest() == plan['source_sha256']
    assert json.loads((OLD / 'shape-cache/index.json').read_text())['source_sha256'] == plan['source_sha256']
    shapes = {}
    for row in plan['components']:
        s = Part.Shape()
        s.read(str(OLD / 'shape-cache' / (row['name'] + '.brep')))
        shapes[row['name']] = s
    # Re-use the exact main-regulator/terminal envelopes; the second board is
    # the candidate already documented in the component-selection package.
    new = {}
    for n in ['Pololu', 'PowerTerminal31_0', 'PowerTerminal31_1']:
        s = shapes[n].copy()
        s.translate(A.Vector(0, -22, 0))
        new[n] = s
    for i, (x, y) in enumerate((x, y) for x in (88.04, 123.6) for y in (-21.46, -6.22)):
        z = 38.52 if i < 2 else 44
        new['post' + str(i)] = Part.makeCylinder(3, 52-z, A.Vector(x,y,z)).cut(
            Part.makeCylinder(1.2, 52-z, A.Vector(x,y,z)))
        if i >= 2:
            new['gap' + str(i)] = Part.makeCylinder(3, 2.48, A.Vector(x,y,38.52)).cut(
                Part.makeCylinder(1.2, 2.48, A.Vector(x,y,38.52)))
    print('Loaded reference shapes', flush=True)
    hits = []
    for n, s in new.items():
        for other, t in shapes.items():
            if other == 'AuxBuck' or not s.BoundBox.intersect(t.BoundBox):
                continue
            print('Pair', n, other, flush=True)
            if n == 'Pololu':
                b=s.BoundBox
                env=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))
                if exact(env,t) < 1e-8:
                    continue
            v = exact(s,t)
            if v > .01:
                hits.append(dict(new=n, old=other, volume_mm3=v))
    print(json.dumps(dict(base=[85.5,-24,52], hits=hits), indent=2), flush=True)
    for n in ['Part__Feature038', 'ShellMounted20', 'TailBridge29']:
        for x in [88.04,123.6]:
            for y in [-21.46,-6.22]:
                axis=Part.makeCylinder(1.2,25,A.Vector(x,y,30))
                common=shapes[n].common(axis)
                b=common.BoundBox
                print(n,x,y,'axis-material',common.Volume,'Z',b.ZMin,b.ZMax,flush=True)


if __name__ == '__main__':
    main()
