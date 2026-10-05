"""A low, exact-radius bridge loop below the received leg routing planes.

Material witness at XL01 is Y44.3..45.6,Z150.8..152.2 near X72.
Turn south immediately at the received A tip; do not extend vertically into
that crossing or send a new loop through the upper leg departures.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul
from servo_fuse_inputs_r1 import save, sha

OUT = scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1'


def recipe(family):
    a = family['ends']['W061_A']; b = family['ends']['W061_B']
    c = CentreLine(a['tip'], [0, 0, 1])
    c.arc([0, -1, 0], radius=21)
    c.line([c.p[0], b['tip'][1]-21, c.p[2]])
    c.arc([1, 0, 0], radius=21)
    c.line([b['tip'][0]-21, c.p[1], c.p[2]])
    c.arc([0, 1, 0], radius=21)
    c.arc([0, 0, -1], radius=21)
    assert math.dist(c.p, b['tip']) < 1e-7
    assert math.dist(c.t, [0, 0, -1]) < 1e-7
    return dict(wire='W061', a=dict(edges=a['edges']+c.edges), b=b,
                radius_mm=21, middle=None, bridge_edges=c.edges)


def build(A, Part, row):
    from w5_ground_network_r1 import reverse
    def edges(rows):
        return [Part.makeLine(A.Vector(*e['start']), A.Vector(*e['end'])) if e['kind']=='line'
                else Part.Arc(A.Vector(*e['start']), A.Vector(*e['mid']), A.Vector(*e['end'])).toShape() for e in rows]
    es = edges(row['a']['edges'])+reverse(A, Part, edges(row['b']['edges']))
    for a, b in zip(es, es[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length < 1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length < 1e-7
    pieces = [Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(2.1,
               e.valueAt(e.FirstParameter), e.tangentAt(e.FirstParameter))])], True, False) for e in es]
    assert all(s.isValid() and len(s.Solids)==1 and not s.check(True) for s in pieces)
    return Part.Wire(es), Part.makeCompound(pieces)


def main():
    import FreeCAD as A, Part
    start = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    fixed, printed, ends, family, rows, pins, reused, replaced = scope.load_scope(A, Part)
    row = recipe(family)
    path, shape = build(A, Part, row)
    obstacles = {**fixed, **{w:s for w,s in ends.items() if not w.startswith('W061_')}}
    hits = scope.contacts(shape, obstacles, Part)
    files = []
    for name, s in (('W061_WORLD', shape), ('W061_CENTERLINE', path)):
        p = OUT/(name+'.brep'); s.exportBrep(str(p)); files.append(p)
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), Path(scope.__file__), scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
             scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',
             scope.ROOT/'tools/electronics/w5_ground_network_r1.py',
             scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json', dict(status='LOW_SOUTH_BRIDGE_CANDIDATE', recipe=row, hits=hits, errors=[],
        bridge_complete=not hits, body_mm=path.Length, nominal_mm=path.Length+25,
        trial_blank_mm=math.ceil((path.Length+25+30)/10)*10, radius_mm=21,
        reused=reused, printed_pending=sorted(printed), replacement_obligations=replaced,
        full_central_routes_complete=False, selected=False, physical_pass=False,
        started_utc=start.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('SOUTH_BRIDGE_DONE', len(hits), round(path.Length,3), flush=True)


if __name__ == '__main__':
    main()
