"""Check six actual body reservations BEFORE another expensive loom build.

All contacts are saved, including affected wires and supports. Such contacts
are dependencies, not permission to quietly omit geometry or select W5.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import save, sha
from w5_ground_joint_layout_r1 import ROOT, BLOCKS, attached_ends, ports, placement

OUT = ROOT / 'hardware/electronics/full-cat/w5-ground-joint-preflight-r1'


def main():
    import FreeCAD as A, Part
    from w5_source_grips_native_r1 import current_owners
    from w5_exact_separation import separated
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    graph_path = ROOT / 'hardware/electronics/power-platform/wiring-p0.json'
    ends = attached_ends(json.loads(graph_path.read_text(encoding='utf-8')))
    owners, pins = current_owners(A, Part)
    for label, rel in (
        ('W064', 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1/W064_WORLD.brep'),
        ('SourceCarrier', 'hardware/cad/studies/w5-joint-source-carrier-native-r1/Carrier_WORLD.brep'),
        ('SourceCover', 'hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep'),
        ('SourceWestHood', 'hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
        ('SourceEastHood', 'hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
        p = ROOT / rel; owners[label] = Part.read(str(p)); pins.append(p)
    native = ROOT / 'hardware/electronics/full-cat/w5-joint-source-carrier-native-r1/checks.json'
    received = json.loads(native.read_text(encoding='utf-8'))
    assert not received['hits'] and not received['errors']
    assert all(sha(ROOT / k) == v for k, v in {**received['source_sha256'], **received['files']}.items())
    for wire in ('W064', 'W065', 'W067', 'W068'):
        p = native.parent / (wire + '_T18I_WORLD.brep')
        owners[wire + '_band'] = Part.read(str(p)); pins.append(p)
    for p in (ROOT / 'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
        if p.name.startswith(('Bolt', 'Nut', 'Washers')):
            owners['SourceHoodHardware/' + p.stem] = Part.read(str(p)); pins.append(p)
    # Unchanged 12 individually fused V routes are actual obstacles. D/G
    # routes from the rejected joint family are NOT silently accepted here.
    received_fanouts = ROOT / 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    fanout = json.loads((received_fanouts / 'checks.json').read_text(encoding='utf-8'))
    shapes = Part.read(str(received_fanouts / 'FANOUTS_WORLD.brep')).childShapes()
    assert len(shapes) == len(fanout['routes']) == 36
    for row, shape in zip(fanout['routes'], shapes):
        if row['role'] == 'V': owners['ProvisionalV/' + row['wire']] = shape
    pins.extend((received_fanouts / 'checks.json', received_fanouts / 'FANOUTS_WORLD.brep'))
    moved, files = {}, []
    for block, row in BLOCKS.items():
        old = owners.pop(block + '_design')
        body = old.copy(); body.Placement = placement(A, row) * body.Placement
        assert body.isValid() and len(body.Solids) == 1
        moved[block] = body
        p = OUT / (block + '_WORLD.brep'); body.exportBrep(str(p)); files.append(p)
    affected = {r['wire'] for r in ends}
    intent = OUT / 'intent.json'
    save(intent, dict(blocks=BLOCKS, ports=ports(), attached_ends=ends,
        affected_unique_wires=sorted(affected), attached_end_count=26,
        isolated_NC_ports=[leg + '_G.5' for leg in ('FL', 'FR', 'RL', 'RR')],
        preserved_neighbour_XA06='G_AUX.5 -> G_TAIL.1, not attached to moved blocks',
        classification_note='Every contact retained. Affected-wire/support contacts remain OPEN, not ignored.',
        leg_pitch_mm=6, leg_pitch_basis='New editable prototype grid within inherited 30mm envelope; not manufacturer measurement. Replaces former mixed6/6.75 grids in this unselected family only.',
        source_pitch_basis='G1/G2 received body-ground-bridge-finish-r5 registration',
        new_splices=0, block_native_supports_complete=False,
        routes_complete=False, selected=False, W5_complete=False, physical_pass=False))
    files.append(intent)
    hits, errors, pairs = [], [], 0

    def category(owner):
        if owner in moved: return 'purchased_body'
        tokens = owner.replace('/', '_').split('_')
        if any(w in tokens for w in affected) or any(w in owner for w in ('XA05', 'W061')):
            return 'affected_wire_or_restraint_requires_rebuild'
        if owner in ('SourceDeck', 'SourceCover', 'SourceCarrier', 'BankRight', 'SourceBankLeft'):
            return 'printed_owner_requires_native_resolution'
        if any(t in owner.lower() for t in ('tie', 'seat', 'restraint', 'grip', 'support')):
            return 'support_contact_requires_identification'
        return 'fixed_obstacle'

    def check(block, body, owner, obstacle):
        nonlocal pairs
        for a in body.Solids:
            for b in obstacle.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs += 1
                if separated(a, b): continue
                try:
                    common = a.common(b)
                    if common.Volume > 1e-5:
                        bb = common.BoundBox
                        hits.append(dict(block=block, owner=owner, category=category(owner),
                            mm3=common.Volume, bounds_mm=[getattr(bb, k) for k in
                            ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]))
                except Exception as exc: errors.append(dict(block=block, owner=owner, error=str(exc)))
    for index, (block, body) in enumerate(moved.items()):
        for owner, obstacle in owners.items(): check(block, body, owner, obstacle)
        for other in list(moved)[:index]: check(block, body, other, moved[other])
        print('GROUND_BODY', block, pairs, len(hits), len(errors), flush=True)
        save(OUT / 'progress.json', dict(completed_blocks=index + 1, pairs=pairs, hits=hits, errors=errors))
    finish = datetime.now(timezone.utc)
    pins.extend((Path(__file__), ROOT / 'tools/electronics/w5_ground_joint_layout_r1.py',
        graph_path, native, ROOT / 'hardware/electronics/full-cat/aux-power-r1/circuit.json',
        ROOT / 'hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json',
        ROOT / 'tools/electronics/w5_source_grips_native_r1.py',
        ROOT / 'tools/electronics/w5_exact_separation.py'))
    save(OUT / 'checks.json', dict(status='GROUND_LAYOUT_BODY_PREFLIGHT_OPEN' if hits or errors else 'GROUND_BODIES_CLEAR_NATIVE_SUPPORTS_AND_ALL_ENDS_OPEN',
        hits=hits, errors=errors, pairs=pairs, candidate_count=6,
        datums_provisional=True, fixed_D_fanouts_still_open=True,
        received_body_envelopes_conservative=True, attached_end_count=26,
        affected_unique_wire_count=21, native_supports_complete=False,
        source_family_unselected=True, selected=False, W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in files},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish - begin).total_seconds()))


if __name__ == '__main__': main()
