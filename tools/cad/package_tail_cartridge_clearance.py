"""R4 prototype checkpoint: preserve R3 and bind new geometry/assembly evidence."""
import json
import pilot
from release_check import sha256, verify
from tail_cartridge_clearance import OUT, TARGET


def main():
    parent_path = pilot.ROOT/'hardware/releases/tail-cartridge-integrated.json'
    parent = json.loads(parent_path.read_text())
    assert verify(pilot.ROOT, parent)['integrity_ok']
    paths = [pilot.ROOT/r['path'] for r in parent['files']] + [parent_path]
    paths += [OUT/n for n in ('TailCartridgeClearance.FCStd', 'TailBearingLidService.FCStd',
                             'README.md', 'audit.json', 'housing-installation.json', 'bearing-preassembly.json',
                             'underside-clearance.png', 'lid-service-ports.png')]
    paths += [OUT/'superseded-open-lid-sequence'/n for n in ('housing-installation.json',
              'tail_housing_installation.py', '.gitattributes')]
    paths += [pilot.ROOT/'tools/cad'/n for n in ('tail_cartridge_clearance.py',
              'tail_housing_installation.py', 'tail_bearing_preassembly.py', 'package_tail_cartridge_clearance.py',
              'test_tail_cartridge_clearance.py')]
    paths += [pilot.ROOT/'tools/freecad/skorupa/support34.py']
    reports = [json.loads((OUT/n).read_text()) for n in ('audit.json', 'housing-installation.json')]
    assert reports[0]['conditional_checks_passed']
    for r in reports:
        assert r['study_sha256'] == sha256(TARGET)
        for name, digest in r['unchanged_robot_files'].items(): assert sha256(pilot.ROOT/name) == digest
    bench = json.loads((OUT/'bearing-preassembly.json').read_text())
    assert reports[1]['lid_sha256'] == bench['lid_sha256'] == sha256(OUT/'TailBearingLidService.FCStd')
    for name, digest in (bench['source_sha256'] | bench['helper_sha256']).items():
        assert sha256(pilot.ROOT/name) == digest
    reasons = {
        'geometry': 'Two adapter solids plus revised lid: strict BOP, 25 constrained sketches, independent differences, relocation and parameter restoration.',
        'assembly': 'Native bench Fixed retention and sampled cartridge/block/preassembly paths only; no real spline, physical retention, threads or whole-tail solver.',
        'fit': 'Nominal 0.2 mm radial boss clearance; factory horn/screw, purchased part tolerances and PETG coupons unresolved.',
        'petg': 'Four web probes increased to 1.4 mm; smaller boss section, other local edges, supports and print profile remain unverified.',
        'loads': 'No allowable clamp torque, layer-direction strength or long-term PETG creep validation.',
        'electrical': 'Wiring and complete electrical/thermal integration unresolved.',
        'service': 'Sampled nominal paths do not prove tool/hand access, bearing preload or physical assembly.'}
    m = {'schema_version': 1, 'name': 'tail-cartridge-clearance-r4', 'readiness': 'concept',
         'installed_in_robot': False, 'freecad': '1.1.3', 'occt': '7.8.1', 'freecad_ai': '0.23.1-alpha',
         'files': [{'path': p.relative_to(pilot.ROOT).as_posix(), 'sha256': sha256(p)} for p in paths],
         'gates': {n: {'status': 'pass' if n == 'geometry' else 'open', 'reason': r} for n, r in reasons.items()}}
    if not all([reports[1]['all_sampled_stages_clear'], reports[1]['housing_driver_paths_clear'],
                bench['all_sampled_stages_clear'], bench['counterhold_envelopes_clear']]):
        m['gates']['assembly'] = {'status': 'fail', 'reason': 'Nominal staged housing assembly has collisions; later stages are conditional. See hashed report.'}
    m['gates']['geometry']['evidence'] = [(OUT/n).relative_to(pilot.ROOT).as_posix()
                                         for n in ('audit.json', 'housing-installation.json')]
    assert verify(pilot.ROOT, m)['integrity_ok']
    assert not verify(pilot.ROOT, m, True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/tail-cartridge-clearance.json').write_text(
        json.dumps(m, indent=2), encoding='utf-8', newline='\n')
    print(verify(pilot.ROOT, m))


if __name__ == '__main__': main()
