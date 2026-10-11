"""Preserve the BUS candidate and native evidence; do not select whole W5."""
import hashlib
import json
import time
from pathlib import Path

from release_check import verify

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    started = time.monotonic()
    names = ('BUS-port-binding.json', 'BUS-routes-plan.json',
             'BUS-routes-checks.json', 'BUS-native-checks.json')
    reports = [json.loads((OUT / name).read_text()) for name in names]
    binding, plan, material, native = reports
    assert plan['status'] == 'BUS_SHARED_NOMINAL_CHANNELS_ONLY'
    assert not plan['rejected'] and not material['contacts'] and not material['errors']
    assert material['pairs'] == 350 and not material['sampled_leg_motion_checked']
    assert native['status'] == 'BUS_NATIVE_CARRIER_PREPARED_W5_OPEN'
    assert native['parameter_1p6_1p7_1p6_restore'] and native['fresh_relocated_reopen']
    assert native['volume_added_outside_qualified_material_mm3'] < 1e-5
    assert native['retained_removal_outside_two_plate_passages_mm3'] == 0
    assert native['extra_slot_corner_removal_mm3'] < 1
    assert max(native['export']['size_mm']) + 10 < 256
    pins = {}
    for report in reports:
        assert not report['selected'] and not report['W5_complete'] and not report['physical_pass']
        for name, digest in report['source_sha256'].items():
            assert sha(ROOT / name) == digest, name
            assert name not in pins or pins[name] == digest, name
            pins[name] = digest
    for name, digest in ((native['model'], native['model_sha256']),
                         (native['export']['path'], native['export']['sha256'])):
        assert sha(ROOT / name) == digest, name
        pins[name] = digest
    for path in [OUT / n for n in names] + [Path(__file__), ROOT / 'tests/test_current_bus_routes.py',
                                           ROOT / 'tools/cad/release_check.py', ROOT / 'hardware/cad/toolchain.json']:
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
    reason = 'Whole W5, movement, common assembly/service and delivered fit/data remain OPEN.'
    manifest = dict(
        schema_version=1, readiness='prototype', status='BUS_NATIVE_CANDIDATE_PRESERVED_W5_OPEN',
        selected=False, W5_complete=False, physical_pass=False, result_count=11, fixed_total=20,
        result_percent=55, score_change_pp=0,
        files=[dict(path=n, sha256=h) for n, h in sorted(pins.items())],
        gates={g: dict(status='open', reason=reason) for g in
               ('geometry', 'assembly', 'fit', 'petg', 'loads', 'electrical', 'service')},
        scoped_evidence=dict(material_pairs=350, material_contacts=0,
                             native_parameter_restore=True, fresh_relocated_reopen=True,
                             inherited_upper_bearings_preserved=9,
                             extra_slot_corner_removal_mm3=native['extra_slot_corner_removal_mm3']),
        replacement='UpperCarrier001 from selected W1, NOT an additional physical plate',
        local_consumption=dict(T18I_installed=1, T18I_service_spares=1, new_screws=0,
                               factory_cables_installed=1, factory_cores_installed=2,
                               entire_V_contact_and_wire_removed=True),
        stock='Existing300mm recipe is insufficient.900mm candidate is not selected or purchased; reconcile with leg packs.',
        portability='Local source integrity only. Historical extracted BRep/cache dependencies are not silently adopted into this commit; whole clean-checkout source/export reconciliation remains K1/A3 OPEN.',
        assembly=['Unpowered: bind actual H5 D/V/G and depin V including its whole wire.',
                  'Prepare paired D/G cores, pass allocated carrier passages before closing the independent insulation band.',
                  'Connect labelled D_FL/G2 receivers; cable clamp must not load PCB header or WAGO levers.',
                  'Common assembled access and removal remain a W5 gate, not a claimed completed sequence.'],
        delivery_gates=plan['delivery_gates'],
        worker_seconds=dict(material=material['worker_seconds'], native=native['worker_seconds']),
        verification_seconds=time.monotonic() - started)
    assert verify(ROOT, manifest)['integrity_ok']
    assert not verify(ROOT, manifest, require_print_ready=True)['integrity_ok']
    (OUT / 'BUS-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=manifest['status'], pins=len(pins), seconds=manifest['verification_seconds'])))


if __name__ == '__main__':
    run()
