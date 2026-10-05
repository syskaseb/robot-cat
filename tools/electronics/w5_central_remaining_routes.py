"""Joint finite-corridor allocation for all seven remaining central wires.

Keep the received W001, south W061 and all28 leg/backbone routes. Do not
search block placements again. Evaluate whole routes, retain endpoint
geometry and give each corridor one material check. PETG remains explicit.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from itertools import product
import json
import math
import time
import w5_central_shared_routes as scope
from w5_coupled_corridors import prefix
from w5_ground_network_r1 import from_recipe
from w5_rounded_path import corner_offsets
from servo_fuse_inputs_r1 import save, sha

OUT = scope.ROOT/'hardware/electronics/full-cat/w5-central-remaining-routes-r1'
BRIDGE = scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1/checks.json'
ORDER = ('W003', 'W060', 'XA05', 'W025', 'W036', 'W062', 'W063')


def choices(row, a, b):
    wire = row['wire']; p = a['tip']; q = b['tip'] if b else row['target']
    radius = scope.spec(wire)['radius_mm']
    low = math.ceil(max(p[2], q[2])+radius+1)
    options = []
    for h, turn in product((low, low+12, low+24, low+36, low+48), ('direct', 'x-first', 'y-first')):
        first = [p[0], p[1], h]; last = [q[0], q[1], h]
        middle = [p, first]
        if turn != 'direct':
            middle.append([last[0], first[1], h] if turn == 'x-first' else [first[0], last[1], h])
        middle += [last, q]
        if row.get('lead_in'):
            middle = list(reversed(middle))
        try:
            corner_offsets(middle, radius)
        except AssertionError:
            continue
        candidate = dict(row, a=a, b=b, middle=middle, radius_mm=radius)
        options.append((sum(math.dist(x,y) for x,y in zip(middle,middle[1:])), candidate))
    return [r for _,r in sorted(options, key=lambda item:item[0])]


def main():
    import FreeCAD as A, Part
    start = datetime.now(timezone.utc); tic = time.monotonic()
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    fixed, printed, ends, family, rows, pins, reused, replaced = scope.load_scope(A, Part)
    bridge = json.loads(BRIDGE.read_text(encoding='utf-8'))
    assert bridge['bridge_complete'] and not bridge['hits'] and not bridge['errors']
    for rel,digest in bridge['files'].items():
        assert sha(scope.ROOT/rel)==digest
        pins.append(scope.ROOT/rel)
    fixed['W061'] = Part.read(str(BRIDGE.parent/'W061_WORLD.brep'))
    pins.append(BRIDGE)
    rows = {r['wire']:r for r in rows if r['wire'] in ORDER}
    bus_path = scope.ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    source = json.loads(bus_path.read_text(encoding='utf-8'))['source_lead_datums']['W003']
    rows['W003'] = dict(wire='W003', target=source, lead_in=True)
    pins.append(bus_path)
    options = {}; rejected = {}; lengths = {}; errors = []; timeout = False
    for wire in ORDER:
        row = rows[wire]; a = family['ends'][wire]
        variants = [prefix(row['b_datum'], wire, o) for o in ('up','left','right')] if 'b_datum' in row else [None]
        options[wire] = []; reasons = Counter()
        for b in variants:
            for candidate in choices(row, a, b):
                if time.monotonic()-tic > 240:
                    timeout = True; break
                try:
                    path, shape = from_recipe(A, Part, candidate)
                    embedded = 41 if wire=='W003' else 17 if wire=='W060' else 25 if wire in ('W025','W036') else 22
                    nominal = path.Length+embedded
                    if wire=='W003' and nominal+30>300:
                        reasons['factory300_budget'] += 1; continue
                    obstacles = {**fixed, **{w:s for w,s in ends.items() if w != wire and not w.startswith('W061_')}}
                    hits = scope.contacts(shape, obstacles, Part)
                    if hits:
                        reasons.update(h['owner'] for h in hits); continue
                    info = dict(candidate, body_mm=path.Length, embedded_mm=embedded,
                                nominal_mm=nominal, trial_blank_mm=math.ceil((nominal+30)/10)*10)
                    options[wire].append((info, path, shape))
                except Exception as exc:
                    errors.append(dict(wire=wire, error=str(exc)))
        rejected[wire] = dict(reasons)
        print('CENTRAL_ROUTE_OPTIONS', wire, len(options[wire]), flush=True)
        save(OUT/'progress.json', dict(options={w:len(v) for w,v in options.items()}, rejected=rejected,
                                      errors=errors, timed_out=timeout))
        if timeout:
            break
    chosen = {}; nodes = 0
    ordered = sorted(ORDER, key=lambda w:len(options.get(w,[])))
    def joint(index):
        nonlocal nodes
        nodes += 1
        if nodes>4096 or time.monotonic()-tic>300:
            return False
        if index==len(ordered):
            return True
        wire = ordered[index]
        for row,path,shape in options.get(wire,[]):
            if scope.contacts(shape, {w:v[2] for w,v in chosen.items()}, Part):
                continue
            chosen[wire] = (row,path,shape)
            if joint(index+1):
                return True
            del chosen[wire]
        return False
    complete = joint(0)
    files = []
    if complete:
        for wire,(row,path,shape) in chosen.items():
            for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
                p=OUT/(wire+'_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), Path(scope.__file__), scope.ROOT/'tools/electronics/w5_coupled_corridors.py',
             scope.ROOT/'tools/electronics/w5_ground_network_r1.py', scope.ROOT/'tools/electronics/w5_rounded_path.py',
             scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='CENTRAL_SEVEN_COMPLETE_ROUTE_ALLOCATION',
        complete=complete, routes={w:v[0] for w,v in chosen.items()} if complete else {},
        options={w:len(v) for w,v in options.items()}, rejected=rejected, errors=errors, timed_out=timeout,
        search_nodes=nodes, reused=reused, printed_pending=sorted(printed), replacement_obligations=replaced,
        native_complete=False, selected=False, physical_pass=False,
        started_utc=start.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('CENTRAL_SEVEN_DONE', complete, len(errors), flush=True)


if __name__ == '__main__':
    main()
