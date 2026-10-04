"""Coupled 26 ground exits and ONE full W061 bridge in the received rail.

These are fixed internal end preparations, not supplier-qualified moving
servo leads. The other20 full wires, native seats and removal remain open.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, re
from w5_ground_joint_layout_r4 import ROOT, attached_ends
from servo_fuse_inputs_r1 import save, sha

OUT = ROOT / 'hardware/electronics/full-cat/w5-ground-entries-r1'
RECEIVED = ROOT / 'hardware/electronics/full-cat/w5-ground-joint-preflight-r4/checks.json'
THICK = {'W001', 'W025', 'W036', 'W061', 'W062', 'W063'}


def profile(wire):
    if wire in THICK:
        return dict(OD_mm=4.2, radius_mm=21, basis='received TKD2500125 fixed installation', supplier_radius=True)
    if wire == 'XA05':
        return dict(OD_mm=2.5, radius_mm=15, basis='received HELU23501 fixed installation', supplier_radius=True)
    if wire == 'W003':
        return dict(OD_mm=2, radius_mm=10, basis='R53 Waveshare34171 prototype envelope; supplier OD/radius unknown', supplier_radius=False)
    if wire == 'W060':
        return dict(OD_mm=3, radius_mm=10, basis='received R40 OD3 prototype; R10 >= earlier unqualified R6', supplier_radius=False)
    return dict(OD_mm=2.4, radius_mm=10, basis='leg loom prototype envelope; not delivered factory cable measurement', supplier_radius=False)


def entry_edges(A, Part, row):
    info = profile(row['wire']); radius = info['radius_mm']
    start = A.Vector(*row['point_mm']); u = A.Vector(*row['outward_axis']); up = A.Vector(0, 0, 1)
    first = start + u * 4
    mid = first + u * (radius / math.sqrt(2)) + up * (radius * (1 - 1 / math.sqrt(2)))
    bend_end = first + u * radius + up * radius
    top = bend_end + up * 20
    return [Part.makeLine(start, first), Part.Arc(first, mid, bend_end).toShape(), Part.makeLine(bend_end, top)]


def bridge_edges(A, Part, first, second):
    a = first[-1].valueAt(first[-1].LastParameter)
    b = second[-1].valueAt(second[-1].LastParameter)
    delta = b - a; assert abs(delta.z) < 1e-7
    distance = delta.Length; radius = 21; assert distance > 2 * radius
    u = delta / distance; up = A.Vector(0, 0, 1)
    p = a + u * radius + up * radius
    q = b - u * radius + up * radius
    middle = [Part.Arc(a, a + u * (radius * (1 - 1 / math.sqrt(2))) + up * (radius / math.sqrt(2)), p).toShape(),
              Part.makeLine(p, q),
              Part.Arc(q, q + u * (radius / math.sqrt(2)) - up * (radius * (1 - 1 / math.sqrt(2))), b).toShape()]
    reverse = []
    for edge in reversed(second):
        start = edge.valueAt(edge.LastParameter)
        end = edge.valueAt(edge.FirstParameter)
        if isinstance(edge.Curve, Part.Circle):
            reverse.append(Part.Arc(start, edge.valueAt((edge.FirstParameter + edge.LastParameter) / 2), end).toShape())
        else:
            reverse.append(Part.makeLine(start, end))
    return [*first, *middle, *reverse]


def owners(A, Part, receipt):
    from w5_source_grips_native_r1 import current_owners
    result, pins = current_owners(A, Part)
    for block in ('G1', 'G2', 'FL_G', 'FR_G', 'RL_G', 'RR_G'):
        result.pop(block + '_design')
        p = RECEIVED.parent / (block + '_WORLD.brep')
        result[block + '_NEW_BODY'] = Part.read(str(p)); pins.append(p)
    for label, rel in (
        ('W064', 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1/W064_WORLD.brep'),
        ('SourceCarrier', 'hardware/cad/studies/w5-joint-source-carrier-native-r1/Carrier_WORLD.brep'),
        ('SourceCover', 'hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep'),
        ('SourceWestHood', 'hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
        ('SourceEastHood', 'hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
        p = ROOT / rel; result[label] = Part.read(str(p)); pins.append(p)
    folder = ROOT / 'hardware/electronics/full-cat/w5-joint-source-carrier-native-r1'
    for wire in ('W064', 'W065', 'W067', 'W068'):
        p = folder / (wire + '_T18I_WORLD.brep')
        result[wire + '_band'] = Part.read(str(p)); pins.append(p)
    for p in (ROOT / 'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
        if p.name.startswith(('Bolt', 'Nut', 'Washers')):
            result['SourceHoodHardware/' + p.stem] = Part.read(str(p)); pins.append(p)
    folder = ROOT / 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    data = json.loads((folder / 'checks.json').read_text(encoding='utf-8'))
    shapes = Part.read(str(folder / 'FANOUTS_WORLD.brep')).childShapes()
    assert len(shapes) == len(data['routes']) == 36
    for row, shape in zip(data['routes'], shapes):
        if row['role'] == 'V': result['ReceivedV/' + row['wire']] = shape
    pins.extend((folder / 'checks.json', folder / 'FANOUTS_WORLD.brep'))
    return result, pins


def main():
    import FreeCAD as A, Part
    from w5_exact_separation import separated
    begin = datetime.now(timezone.utc); assert not (OUT / 'checks.json').exists()
    receipt = json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert not receipt['fixed_wire_or_bought_body_contacts'] and not receipt['errors']
    assert all(sha(ROOT / k) == v for k, v in {**receipt['source_sha256'], **receipt['files']}.items())
    graph_file = ROOT / 'hardware/electronics/power-platform/wiring-p0.json'
    rows = attached_ends(json.loads(graph_file.read_text(encoding='utf-8')))
    OUT.mkdir(parents=True, exist_ok=True)
    intent = OUT / 'intent.json'
    save(intent, dict(ends=[dict(row, **profile(row['wire'])) for row in rows],
        straight_insulated_preparation_mm=4, vertical_preparation_mm=20,
        W061_complete_geometry_planned=True, other_full_wires_complete=False,
        cage_datums_provisional=True, new_splices=0, selected=False, W5_complete=False, physical_pass=False))
    fixed, pins = owners(A, Part, receipt)
    affected = {r['wire'] for r in rows}; files = [intent]
    built = []; paths = {}; geometries = {}
    for row in rows:
        key = row['wire'] + '@' + row['end']
        edges = entry_edges(A, Part, row); paths[key] = edges
        built.append(dict(row, **profile(row['wire']), key=key))
    first, second = paths['W061@G1.5'], paths['W061@G2.1']
    paths['W061_COMPLETE'] = bridge_edges(A, Part, first, second)
    path_receipts = []
    for key, edges in paths.items():
        for previous, current in zip(edges, edges[1:]):
            assert (previous.valueAt(previous.LastParameter) - current.valueAt(current.FirstParameter)).Length < 1e-6
            assert (previous.tangentAt(previous.LastParameter) - current.tangentAt(current.FirstParameter)).Length < 1e-6
        wire = key.split('@')[0] if '@' in key else 'W061'
        pinfo = profile(wire); path = Part.Wire(edges); assert path.isValid()
        for edge in edges:
            if isinstance(edge.Curve, Part.Circle): assert abs(edge.Curve.Radius - pinfo['radius_mm']) < 1e-6
        pieces = [Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(pinfo['OD_mm'] / 2,
            e.valueAt(e.FirstParameter), e.tangentAt(e.FirstParameter))])], True, False) for e in edges]
        assert all(s.isValid() and len(s.Solids) == 1 and not s.check(True) for s in pieces)
        geometries[key] = Part.makeCompound(pieces)
        for suffix, shape in (('WORLD', geometries[key]), ('CENTERLINE_WORLD', path)):
            p = OUT / (key.replace('@', '_') + '_' + suffix + '.brep')
            shape.exportBrep(str(p)); files.append(p)
        path_receipts.append(dict(key=key, external_mm=path.Length, **pinfo))
    actual = [row['key'] for row in built if row['wire'] != 'W061'] + ['W061_COMPLETE']
    hits, errors, pairs = [], [], 0

    def category(owner):
        if owner in geometries or owner.endswith('_NEW_BODY'): return 'new_ground_interface'
        if owner in receipt['owner_dependencies']: return 'old_ground_restraint_requires_rebuild'
        if any(re.search(r'(?<![A-Za-z0-9])' + re.escape(w) + r'(?![A-Za-z0-9])', owner) for w in affected):
            return 'old_affected_wire_or_restraint_requires_rebuild'
        if owner in ('SourceDeck', 'SourceCover', 'SourceCarrier', 'SourceBankLeft', 'BankRight'):
            return 'printed_owner_requires_native_resolution'
        return 'other_fixed_obstacle'

    def check(key, shape, owner, obstacle):
        nonlocal pairs
        for a in shape.Solids:
            for b in obstacle.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs += 1
                if separated(a, b): continue
                try:
                    common = a.common(b)
                    if common.Volume > 1e-5:
                        bb = common.BoundBox
                        hits.append(dict(end=key, owner=owner, category=category(owner), mm3=common.Volume,
                            bounds_mm=[getattr(bb, k) for k in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]))
                except Exception as exc: errors.append(dict(end=key, owner=owner, error=str(exc)))
    for index, key in enumerate(actual):
        for owner, shape in fixed.items(): check(key, geometries[key], owner, shape)
        for other in actual[:index]: check(key, geometries[key], other, geometries[other])
        print('GROUND_END', key, pairs, len(hits), len(errors), flush=True)
        save(OUT / 'progress.json', dict(completed_checked_entries=index + 1, total_checked_entries=len(actual),
             paths=path_receipts, pairs=pairs, hits=hits, errors=errors))
    finish = datetime.now(timezone.utc)
    pins.extend((Path(__file__), ROOT / 'tools/electronics/w5_ground_joint_layout_r4.py',
        ROOT / 'tools/electronics/w5_ground_joint_layout_r2.py', ROOT / 'tools/electronics/w5_ground_joint_layout_r1.py',
        RECEIVED, ROOT / 'tools/electronics/w5_ground_joint_preflight_r4.py', graph_file,
        ROOT / 'hardware/electronics/full-cat/aux-power-r1/circuit.json',
        ROOT / 'hardware/electronics/power-platform/POWER-WIRE-P0.md',
        ROOT / 'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json',
        ROOT / 'hardware/electronics/full-cat/main-input-return-r4/checks.json',
        ROOT / 'tools/electronics/w5_source_grips_native_r1.py', ROOT / 'tools/electronics/w5_exact_separation.py'))
    length = next(p['external_mm'] for p in path_receipts if p['key'] == 'W061_COMPLETE')
    save(OUT / 'checks.json', dict(status='GROUND_ENDS_AND_W061_OPEN' if hits or errors else 'GROUND_ENDS_AND_W061_STATIC_CLEAR_NATIVE_AND_OTHER_FULL_WIRES_OPEN',
        paths=path_receipts, hits=hits, errors=errors, pairs=pairs, attached_end_count=26,
        full_route_count=1, other_full_route_count_open=20,
        W061_external_mm=length, W061_provisional_blank_mm=math.ceil((length + 14 + 11 + 30) / 10) * 10,
        nominal_strip_mm={'G1': [12, 14], 'G2': 11}, blank_is_not_strip_length=True,
        native_supports_complete=False, stock_selected=False, motion_qualified=False,
        source_family_unselected=True, selected=False, W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in files},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish - begin).total_seconds()))


if __name__ == '__main__': main()
