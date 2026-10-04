"""Staged access for the received five-lead source and bank/Cover family.

Remove the hoods first. Do not infer bank withdrawal from installed static
clearance: test it after explicitly disconnecting/removing the five source
leads. Wire fishing and delivered S1 screw pockets remain physical gates.
No old whole-robot geometry is rebuilt and no old service builder runs.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-source-family-service-r1'
SOURCE_LEADS = ('W064', 'W065', 'W067', 'W068', 'XA01')
AXES = ((117, 70), (129, 70), (117, 82), (129, 82))


def main():
    import FreeCAD as A, Part
    from w5_source_grips_native_r1 import current_owners
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'assembly.json').exists(), 'Preserve received result'
    OUT.mkdir(parents=True, exist_ok=True)
    owners, pins = current_owners(A, Part)

    def read(rel):
        p = ROOT / rel; pins.append(p)
        return json.loads(p.read_text(encoding='utf-8'))

    def load(rel):
        p = ROOT / rel; pins.append(p)
        return Part.read(str(p))

    for rel in ('w5-source-roof-service-r2/assembly.json',
                'w5-source-grips-native-r2/checks.json',
                'w5-source-roof-native-r5/checks.json'):
        r = read('hardware/electronics/full-cat/' + rel)
        assert not r['hits'] and not r['errors']
        assert all(sha(ROOT / k) == v for k, v in
                   {**r['source_sha256'], **r.get('files', {})}.items())
    owners['SourceCover'] = load('hardware/cad/studies/w5-source-roof-native-r5/Cover_WORLD.brep')
    owners['SourceCarrier'] = load('hardware/cad/studies/w5-source-grips-native-r2/Carrier_WORLD.brep')
    for wire in SOURCE_LEADS[:4]:
        owners[wire + '_band'] = load('hardware/electronics/full-cat/w5-source-grips-native-r2/' + wire + '_T18I_WORLD.brep')
    # Exact received service geometry; hoods and their four screws are absent.
    # Old P_SYS seat/tie roles are replaced, not a second installed support.
    retired = []
    for key in ('source-switch-restraints-r2/P_SYS_seat_DESIGN',
                'source-switch-restraints-r2/P_SYS_tie_DESIGN'):
        assert key in owners
        owners.pop(key); retired.append(key)
    hits, errors, pairs = [], [], 0

    def check(phase, label, shape, obstacles):
        nonlocal pairs
        for key, target in obstacles.items():
            for a in shape.Solids:
                for b in target.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):
                        continue
                    pairs += 1
                    try:
                        common = a.common(b)
                        if common.Volume > 1e-5:
                            hits.append(dict(phase=phase, part=label, owner=key,
                                             mm3=common.Volume))
                            common.exportBrep(str(OUT / ('HIT_' + str(len(hits)) + '.brep')))
                    except Exception as exc:
                        errors.append(dict(phase=phase, part=label, owner=key, error=str(exc)))

    # A project screwdriver-space allowance, NOT a received screw-head size.
    # Ring metal is intentionally excluded ONLY at its own contact axis.
    for i, (x, y) in enumerate(AXES):
        tool = Part.makeCylinder(4, 30, A.Vector(x, y, 31.5))
        tool.exportBrep(str(OUT / ('S1_driver_' + str(i) + '_ALLOWANCE.brep')))
        check('S1_bottom_driver', str(i), tool,
              {k: v for k, v in owners.items() if k != 'TE130171/' + str(i)})
    tool_hits = len(hits)
    print('SOURCE_S1_ACCESS', pairs, tool_hits, len(errors), flush=True)

    # The current bank recipe already specifies holder/end/tie release.
    census = read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r22/owner-census.json')
    oldproof = read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r22/checks.json')
    assert not oldproof['hits'] and not oldproof['errors']
    released = []
    for key in census['removed']:
        if key in owners:
            owners.pop(key); released.append(key)
    for key in census['parked']:
        assert key in owners, key
        ident = key.rsplit('/', 1)[-1]
        owners[key] = load('hardware/electronics/full-cat/servo-fuse-bank-service-r3/' + ident + '_PARKED.brep')
    for key in census['released_inputs']:
        assert key in owners, key
        filename = key.rsplit('/', 1)[-1].replace('release_0.0_', 'release_1.0_') + '.brep'
        rel = next(q for q in oldproof['source_sha256'] if q.endswith('/' + filename))
        owners[key] = load(rel)
    assert len(census['parked']) == 24 and len(census['released_inputs']) == 12
    for key in (*SOURCE_LEADS, *(w + '_band' for w in SOURCE_LEADS[:4]),
                *(('TE130171/' + str(i)) for i in range(4))):
        assert key in owners
        owners.pop(key); released.append(key)
    module = {k: owners.pop(k) for k in ('SourceBankLeft', 'BankRight', 'SourceCover')}
    completed = []
    for dz in (2, 5, 10, 30, 60, 100):
        before = len(hits) + len(errors)
        for label, shape in module.items():
            moved = shape.copy(); moved.translate(A.Vector(0, 0, dz))
            check('bank_Cover_lift_' + str(dz), label, moved, owners)
        print('SOURCE_BANK_COVER_LIFT', dz, pairs, len(hits), len(errors), flush=True)
        if len(hits) + len(errors) != before:
            break
        completed.append(dz)
    end = datetime.now(timezone.utc)
    save(OUT / 'assembly.json', dict(
        status='SOURCE_STAGED_SERVICE_GEOMETRY_CLEAR_FLEX_AND_CAGES_OPEN' if not hits and not errors else 'SOURCE_STAGED_SERVICE_REJECTED',
        pairs=pairs, hits=hits, errors=errors, S1_tool_hits=tool_hits,
        S1_driver_allowance=dict(diameter_mm=8, bottom_Z_mm=31.5, top_Z_mm=61.5,
                                actual_screwdriver_and_terminal_pocket_verified=False),
        obsolete_replaced_roles=retired, released_before_bank_lift=released,
        parked_TE_ends=census['parked'], completed_clear_bank_Cover_poses_mm=completed,
        samples_not_continuous=True, Carrier_kept_fixed=True,
        assembly=['Install source platform and existing S0 mounts on the removed bare Deck before wiring.',
                  'With bank/Cover absent prewire loose P_SYS/P_FRONT/P_REAR cages; preserve labels and exchanged same-net P_REAR ports.',
                  'Fit Carrier; feed bare WAGO ends through its four full-depth apertures before final source routing/ring crimping.',
                  'Fit bank and Cover using the reverse staged path BEFORE dressing the elevated source loops and four Carrier straps.',
                  'Crimp four TE130171 rings with qualified TE58433-3/die58423-1; fit delivered S1 screws from below, maintaining metal-to-metal bearing.',
                  'Dress received five-lead source and four insulation straps; fit both removable hoods last.'],
        removal=['Disconnect physical battery before any work; remove both hoods by the received service-r2 sequence.',
                 'Release the four S1 screws/rings from below and cut the four Carrier insulation straps.',
                 'Release the five source cage ends and remove XA01 and all four long S1 leads before lifting bank/Cover. Pass only bare cage ends through Carrier, NEVER the wide TE rings.',
                 'Execute existing bank release recipe: holders,24parkedTEends,49cut loops and4bank+4Cover screws; lower fixed station remains unchanged.',
                 'Lift bank+Cover together through the recorded poses; Carrier remains fixed. Reassemble in reverse with replacement cut straps.'],
        open_gates=['Source cage lever/withdrawal access not qualified by this receipt.',
                    'Flexible threading/removal of released source tails has not been modelled as a swept cable motion.',
                    'Delivered S1 pocket/screw-head location and actual workshop tool must be fitted in phase2.'],
        whole_source_assembly_complete=False, selected=False, W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in dict.fromkeys([*pins, Path(__file__)])},
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in OUT.glob('*.brep')},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds()))


if __name__ == '__main__':
    main()
