"""Build all 21 body-ground paths, then check their joint installed scope.

Old whole conductors are superseded ONLY by complete paths of the same net.
Their old PETG seats and straps are retained as open native dependencies.
Nothing is selected and no physical or moving-cable qualification is implied.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import re
from w5_ground_network_plan import ROOT, recipes, profile
from servo_fuse_inputs_r1 import save, sha

OUT = ROOT / 'hardware/electronics/full-cat/w5-ground-network-r1'


def reverse(A, Part, edges):
    result = []
    for e in reversed(edges):
        p, q = e.valueAt(e.LastParameter), e.valueAt(e.FirstParameter)
        result.append(Part.Arc(p, e.valueAt((e.FirstParameter + e.LastParameter) / 2), q).toShape()
                      if isinstance(e.Curve, Part.Circle) else Part.makeLine(p, q))
    return result


def from_recipe(A, Part, row):
    from w5_rounded_path import rounded

    def build(prefix):
        return [Part.makeLine(A.Vector(*e['start']), A.Vector(*e['end'])) if e['kind'] == 'line'
                else Part.Arc(A.Vector(*e['start']), A.Vector(*e['mid']), A.Vector(*e['end'])).toShape()
                for e in prefix['edges']]

    a = build(row['a'])
    middle = rounded(A, Part, [A.Vector(*p) for p in row['middle']], row['radius_mm'])
    if row.get('lead_in'):
        edges = [*middle.Edges, *reverse(A, Part, a)]
    else:
        edges = [*a, *middle.Edges]
        if row['b'] is not None:
            edges.extend(reverse(A, Part, build(row['b'])))
    if row.get('retained_MAIN_tail'):
        from main_input_return_r4 import M
        curve = Part.BezierCurve(); curve.setPoles([A.Vector(*p) for p in M.POLES])
        edges.extend([curve.toShape(), Part.makeLine(A.Vector(*M.POLES[-1]), A.Vector(*M.B.PAD))])
    for p, q in zip(edges, edges[1:]):
        assert (p.valueAt(p.LastParameter) - q.valueAt(q.FirstParameter)).Length < 1e-6, row['wire']
        assert (p.tangentAt(p.LastParameter) - q.tangentAt(q.FirstParameter)).Length < 1e-6, row['wire']
    for edge in edges:
        if isinstance(edge.Curve, Part.Circle):
            assert edge.Curve.Radius >= profile(row['wire'])['radius_mm'] - 1e-6
    path = Part.Wire(edges); assert path.isValid()
    pieces = []
    for i, edge in enumerate(edges):
        radius = math.sqrt(.823 / math.pi) if row.get('retained_MAIN_tail') and i == len(edges) - 1 else profile(row['wire'])['OD_mm'] / 2
        section = Part.Wire([Part.makeCircle(radius, edge.valueAt(edge.FirstParameter), edge.tangentAt(edge.FirstParameter))])
        solid = Part.Wire([edge]).makePipeShell([section], True, False)
        assert solid.isValid() and len(solid.Solids) == 1 and not solid.check(True)
        pieces.append(solid)
    return path, Part.makeCompound(pieces)


def is_old_conductor(owner, wires):
    leaf = owner.rsplit('/', 1)[-1]
    if any(word in leaf.lower() for word in ('tie', 'band', 'grip', 'seat', 'restraint', 'clamp', 'support')):
        return False
    return any(leaf == wire or re.match(re.escape(wire) + r'_\d+_(DESIGN|WORLD)$', leaf)
               or leaf == wire + '_DESIGN' or leaf == wire + '_WORLD' for wire in wires)


def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners as received_owners, RECEIVED
    from w5_exact_separation import separated
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'checks.json').exists(), 'Preserve old variants'
    OUT.mkdir(parents=True, exist_ok=True)
    entries, routes = recipes()
    receipt = json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert not receipt['fixed_wire_or_bought_body_contacts'] and not receipt['errors']
    fixed, pins = received_owners(A, Part, receipt)
    wires = {r['wire'] for r in routes}
    superseded = {k: fixed.pop(k) for k in list(fixed) if is_old_conductor(k, wires)}
    # Whole network endpoints, NOT unconnected prefixes, supersede these wires.
    assert 'R53BUS/W003' in superseded
    body = fixed['G2_NEW_BODY'].copy(); body.translate(A.Vector(0, 0, 6)); fixed['G2_NEW_BODY'] = body
    body.exportBrep(str(OUT / 'G2_STANDOFF_BODY_WORLD.brep'))
    # D wires were absent in the end-only check. Keep their actual candidate
    # paths alongside the V paths rather than claiming an empty D corridor.
    fanouts = ROOT / 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    info = json.loads((fanouts / 'checks.json').read_text(encoding='utf-8'))
    shapes = Part.read(str(fanouts / 'FANOUTS_WORLD.brep')).childShapes()
    for row, shape in zip(info['routes'], shapes):
        if row['role'] == 'D':
            fixed['ReceivedD/' + row['wire']] = shape
    pins.extend((fanouts / 'checks.json', fanouts / 'FANOUTS_WORLD.brep'))
    intent = OUT / 'intent.json'
    save(intent, dict(routes=routes, attached_ends=entries, wire_count=21, attached_end_count=26,
        fixed_cage_registration_provisional=True, G2_native_standoff_pending_mm=6,
        G1_same_original_labels=True, W001_corrected_to_selected_LAPP=True,
        superseded_complete_conductor_owners=sorted(superseded),
        old_straps_and_PETG_preserved=True, retained_D_candidates_not_selected=True,
        moving_loom_breakouts_retained=True, selected=False, W5_complete=False, physical_pass=False))
    built = {}; lengths = []; errors = []; files = [intent, OUT / 'G2_STANDOFF_BODY_WORLD.brep']
    for row in routes:
        key = row['wire']
        try:
            path, shape = from_recipe(A, Part, row)
            for suffix, q in (('WORLD', shape), ('CENTERLINE_WORLD', path)):
                p = OUT / (key + '_' + suffix + '.brep'); q.exportBrep(str(p)); files.append(p)
            built[key] = shape
            embedded = (25 if key == 'W061' else 22 if key in ('W062', 'W063', 'XA05') else
                        25 if key in ('W025', 'W036') else 19 if key == 'W001' else
                        17 if key == 'W060' else 11)
            reserve = 10 if key == 'W001' else 30
            external = path.Length + row.get('retained_moving_candidate_mm', 0)
            required = external + embedded
            lengths.append(dict(wire=key, body_centreline_mm=path.Length,
                retained_moving_candidate_mm=row.get('retained_moving_candidate_mm', 0),
                connected_external_mm=external, embedded_allowance_mm=embedded,
                required_nominal_mm=required, fitting_reserve_mm=reserve,
                unselected_stock_blank_mm=math.ceil((required + reserve) / 10) * 10,
                actual_cut_mm=None, **profile(key),
                nominal_900_cable_check=required + reserve <= 900 if row['moving_route'] else None,
                W001_existing150_limit_check=required <= 150 if key == 'W001' else None,
                BUS_existing300_check=required + reserve <= 300 if key == 'W003' else None))
            print('GROUND_NETWORK_BUILT', key, round(path.Length, 3), flush=True)
        except Exception as exc:
            errors.append(dict(wire=key, stage='build', error=str(exc)))
            print('GROUND_NETWORK_BUILD_ERROR', key, str(exc), flush=True)
    save(OUT / 'lengths.json', lengths); files.append(OUT / 'lengths.json')
    hits = []; pairs = 0

    def category(owner):
        if owner in built or owner.endswith('_NEW_BODY'):
            return 'new_ground_interface'
        if owner in receipt['owner_dependencies'] or any(
                re.search(r'(?<![A-Za-z0-9])' + re.escape(w) + r'(?![A-Za-z0-9])', owner) for w in wires):
            return 'old_ground_mount_requires_rebuild'
        if owner in ('SourceDeck', 'SourceCover', 'SourceCarrier', 'SourceBankLeft', 'BankRight'):
            return 'printed_owner_requires_native_resolution'
        return 'other_fixed_obstacle'

    def check(key, shape, owner, obstacle):
        nonlocal pairs
        if not shape.BoundBox.intersect(obstacle.BoundBox):
            return
        for a in shape.Solids:
            for b in obstacle.Solids:
                if not a.BoundBox.intersect(b.BoundBox):
                    continue
                pairs += 1
                if separated(a, b):
                    continue
                try:
                    common = a.common(b)
                    if common.Volume > 1e-5:
                        bb = common.BoundBox
                        hits.append(dict(wire=key, owner=owner, category=category(owner), mm3=common.Volume,
                            bounds_mm=[getattr(bb, k) for k in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]))
                except Exception as exc:
                    errors.append(dict(wire=key, owner=owner, stage='intersection', error=str(exc)))

    for key in ('G2_NEW_BODY',):
        for owner, obstacle in fixed.items():
            if owner != key:
                check(key, fixed[key], owner, obstacle)
    for index, (key, shape) in enumerate(built.items()):
        for owner, obstacle in fixed.items():
            check(key, shape, owner, obstacle)
        for other, obstacle in list(built.items())[:index]:
            check(key, shape, other, obstacle)
        save(OUT / 'progress.json', dict(completed_checked_routes=index + 1, total_checked_routes=21,
             pairs=pairs, hits=hits, errors=errors, lengths=lengths))
        print('GROUND_NETWORK_CHECKED', key, pairs, len(hits), len(errors), flush=True)
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), ROOT / 'tools/electronics/w5_ground_network_plan.py',
             ROOT / 'tools/electronics/w5_ground_entries_r1.py', ROOT / 'tools/electronics/w5_ground_joint_layout_r4.py',
             ROOT / 'tools/electronics/w5_ground_joint_layout_r2.py', ROOT / 'tools/electronics/w5_ground_joint_layout_r1.py',
             ROOT / 'tools/electronics/w5_s1_source_layout_r2.py', ROOT / 'tools/electronics/w5_s1_source_layout_r1.py',
             ROOT / 'tools/electronics/w5_rounded_path.py', ROOT / 'tools/electronics/w5_source_grips_native_r1.py',
             ROOT / 'tools/electronics/w5_exact_separation.py', ROOT / 'tools/electronics/main_input_return_r4.py',
             ROOT / 'tools/electronics/main_input_return_r3.py', ROOT / 'tools/electronics/main_input_return_r1.py',
             ROOT / 'hardware/electronics/power-platform/wiring-p0.json',
             ROOT / 'hardware/electronics/power-platform/BATTERY-INLET-P0.md',
             ROOT / 'hardware/electronics/power-platform/POWER-WIRE-P0.md',
             ROOT / 'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json',
             ROOT / 'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json', RECEIVED]
    limits_ok = all(r.get('W001_existing150_limit_check') is not False and
                    r.get('BUS_existing300_check') is not False and
                    r.get('nominal_900_cable_check') is not False for r in lengths)
    save(OUT / 'checks.json', dict(status='GROUND_NETWORK_OPEN' if hits or errors or not limits_ok else
        'GROUND_NETWORK_STATIC_CLEAR_NATIVE_AND_MOVING_QUALIFICATION_OPEN',
        route_count=len(built), required_route_count=21, attached_end_count=26,
        hits=hits, errors=errors, pairs=pairs, limits_ok=limits_ok,
        lengths=lengths, superseded_complete_conductor_owners=sorted(superseded),
        native_supports_complete=False, other_D_and_V_qualification_complete=False,
        assembly_removal_complete=False, stock_selected=False, selected=False,
        W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in files},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish - begin).total_seconds()))
    print('GROUND_NETWORK_RESULT', len(built), pairs, len(hits), len(errors), limits_ok, flush=True)


if __name__ == '__main__': main()
