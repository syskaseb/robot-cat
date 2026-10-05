"""Resume saved central endpoints without repeating block-placement searches.

Fixed geometry is the received whole network. PETG needing reconstruction is
kept in a separate, explicit obligation set, never a selected assembly PASS.
The bridge goes north of the Pi landing, instead of the rejected direct arch.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import math
from servo_fuse_inputs_r1 import save, sha
from w5_coupled_corridors import ROOT, PRINTED, spec
from w5_coupled_corridors_r3 import contract
from w5_ground_network_r1 import from_recipe
from w5_rounded_path import corner_offsets

OUT = ROOT/'hardware/electronics/full-cat/w5-central-shared-routes-r1'
FAMILY = ROOT/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json'
CENTRAL = {'W001', 'W003', 'W025', 'W036', 'W060', 'W061', 'W062', 'W063', 'XA05'}


def load_scope(A, Part):
    from w5_ground_entries_r1 import owners, RECEIVED
    bodies, rows, preserved, pins = contract()
    fixed, original_pins = owners(A, Part, json.loads(RECEIVED.read_text(encoding='utf-8')))
    pins += original_pins
    changed = {r['wire'] for r in rows} | CENTRAL
    replaced = []
    for key in list(fixed):
        if (key.startswith(('Source/G1BAT_', 'Input/G1_input_tie_', 'Input/Deck_input_tie_'))
                or key in {'G1_NEW_BODY', 'G2_NEW_BODY'}
                or key in {n+'_NEW_BODY' for n in bodies}
                or key in {n+'_design' for n in bodies}
                or key.startswith('R53BUS/G2shared/')
                or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])', key) for w in changed)):
            replaced.append(key)
            del fixed[key]
    for name, b in bodies.items():
        fixed[name+'_CURRENT_RESERVATION'] = Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    received = ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r3/checks.json'
    proof = json.loads(received.read_text(encoding='utf-8'))
    assert not proof['body_hits'] and not proof['errors']
    pins.extend((received, FAMILY))
    reused = []
    for row in proof['accepted']:
        if row['wire'] in CENTRAL:
            continue
        folders = ('w5-branch-joint-routes-r3', 'w5-branch-joint-routes-r2',
                   'w5-branch-joint-routes-r1', 'w5-coupled-corridors-r3')
        p = next(ROOT/'hardware/electronics/full-cat'/f/(row['wire']+'_WORLD.brep')
                 for f in folders if (ROOT/'hardware/electronics/full-cat'/f/(row['wire']+'_WORLD.brep')).exists())
        fixed[row['wire']] = Part.read(str(p))
        pins.append(p)
        reused.append(row['wire'])
    assert len(reused) == 28
    printed_keys = PRINTED | {'main-positive-complete-r8/positive_portal_seat_DESIGN',
                              'main-positive-complete-r8/splice_seat_DESIGN'}
    printed = {k: fixed.pop(k) for k in printed_keys if k in fixed}
    family = json.loads(FAMILY.read_text(encoding='utf-8'))
    for rel, digest in family['files'].items():
        assert sha(ROOT/rel) == digest, rel
        pins.append(ROOT/rel)
    placement = family['placement']
    for name, dimensions in (('G1', (22, 37, 11)), ('G2', (19, 30, 9))):
        x, y = placement[name.lower()+'_centre']; dx, dy, dz = dimensions
        s = Part.makeBox(dx, dy, dz, A.Vector(x-dx/2, y-dy/2, placement['floor']))
        s.rotate(A.Vector(x, y, placement['floor']), A.Vector(0, 0, 1), placement['angles'][name])
        fixed[name+'_NEW_BODY'] = s
    ends = {w: Part.read(str(FAMILY.parent/(w+'_RECEIVED.brep'))) for w in family['ends'] if w != 'W001'}
    fixed['W001'] = Part.read(str(FAMILY.parent/'W001_FULL_RECEIVED.brep'))
    return fixed, printed, ends, family, rows, pins, reused, replaced


def contacts(shape, obstacles, Part):
    from w5_exact_separation import separated
    hits = []
    for key, obstacle in obstacles.items():
        if not shape.BoundBox.intersect(obstacle.BoundBox):
            continue
        for a in shape.Solids:
            for b in obstacle.Solids:
                if a.BoundBox.intersect(b.BoundBox) and not separated(a, b):
                    common = a.common(b)
                    if common.Volume > 1e-6:
                        hits.append(dict(owner=key, volume_mm3=common.Volume))
                        break
            else:
                continue
            break
    return hits


def bridge_recipe(family, north_y=92, top=185):
    a = family['ends']['W061_A']; b = family['ends']['W061_B']
    p, q = a['tip'], b['tip']
    points = [p, [p[0], p[1], top], [p[0], north_y, top],
              [q[0], north_y, top], [q[0], q[1], top], q]
    corner_offsets(points, 21)
    return dict(wire='W061', a=a, b=b, middle=points, radius_mm=21)


def main():
    import FreeCAD as A, Part
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists(), 'Preserve received result'
    OUT.mkdir(parents=True, exist_ok=True)
    fixed, printed, ends, family, rows, pins, reused, replaced = load_scope(A, Part)
    checks = []; errors = []; selected = None; files = []
    # These are two preplanned northern lanes, not the rejected direct arches.
    for north_y, top in ((92, 185), (104, 197)):
        try:
            recipe = bridge_recipe(family, north_y, top)
            path, body = from_recipe(A, Part, recipe)
            hits = contacts(body, {**fixed, **{w:s for w,s in ends.items() if not w.startswith('W061_')}}, Part)
            row = dict(north_y=north_y, top_mm=top, recipe=recipe, body_mm=path.Length,
                       nominal_mm=path.Length+25, fitting_reserve_mm=30, hits=hits)
            checks.append(row)
            print('CENTRAL_BRIDGE', north_y, top, len(hits), flush=True)
            if not hits:
                selected = row
                for name, s in (('W061_WORLD', body), ('W061_CENTERLINE', path)):
                    p = OUT/(name+'.brep'); s.exportBrep(str(p)); files.append(p)
                break
        except Exception as exc:
            errors.append(dict(north_y=north_y, top_mm=top, error=str(exc)))
        save(OUT/'progress.json', dict(attempts=checks, errors=errors))
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), ROOT/'tools/electronics/w5_ground_network_r1.py',
             ROOT/'tools/electronics/w5_rounded_path.py', ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json', dict(status='CENTRAL_NORTH_BRIDGE_CANDIDATE', solution=selected,
        attempts=checks, errors=errors, reused=reused, replacement_obligations=replaced,
        printed_pending=sorted(printed), remaining_central=['W025','W036','W062','W063','W060','W003','XA05'],
        W001_received_nominal_mm=family['whole_W001']['nominal_mm'],
        full_routes_complete=False, native_complete=False, selected=False, physical_pass=False,
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('CENTRAL_SHARED_DONE', bool(selected), len(errors), flush=True)


if __name__ == '__main__':
    main()
