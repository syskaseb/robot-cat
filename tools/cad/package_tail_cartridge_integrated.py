"""Package R3 with immutable R2 dependencies and explicit open readiness gates."""
import json
import pilot
from release_check import sha256, verify
from tail_cartridge_integrated import OUT, TARGET


def main():
    parent_path = pilot.ROOT/'hardware/releases/tail-cartridge-service.json'
    parent = json.loads(parent_path.read_text())
    assert verify(pilot.ROOT, parent)['integrity_ok']
    paths = [pilot.ROOT/r['path'] for r in parent['files']] + [parent_path]
    paths += [OUT/n for n in ('TailCartridgeIntegrated.FCStd', 'README.md', 'audit.json', 'integrated-cartridge.png', 'horn-fastener-research.md', '.gitattributes')]
    paths += [OUT/'rejected-short-channel'/n for n in ('TailCartridgeIntegrated.FCStd',
               'audit.json', 'tail_cartridge_integrated.py', '.gitattributes')]
    paths += [pilot.ROOT/'tools/cad'/n for n in ('tail_cartridge_integrated.py',
               'package_tail_cartridge_integrated.py', 'test_tail_cartridge_integrated.py')]
    audit = json.loads((OUT/'audit.json').read_text())
    assert audit['study_sha256'] == sha256(TARGET)
    assert audit['conditional_checks_passed']
    for name, digest in audit['unchanged_robot_files'].items():
        assert sha256(pilot.ROOT/name) == digest
    reasons = {
        'geometry': 'Two study PETG solids only: strict BOP, 22 constrained sketches, independent intended delta, relocation and parameter restoration.',
        'assembly': 'Nine native Fixed tested on bench; sampled rotation/insertion only. Whole drive, upper housing sequence and real spline/screw unresolved.',
        'fit': 'Community envelope and nominal fasteners; actual horn, screw, spline, threads and PETG coupon unverified.',
        'petg': 'Thicker local roof and removed thin head collar, but 0.9 mm divider remains; supports and printer profile unverified.',
        'loads': 'No physical clamp/creep, channel section or layer-direction strength validation.',
        'electrical': 'Servo wiring and complete integration unresolved.',
        'service': 'Conditional sampled nut and insertion paths; blade only, not hands, screw seating or final bearing housing installation.'}
    m = {'schema_version': 1, 'name': 'tail-cartridge-integrated-r3', 'readiness': 'concept',
         'installed_in_robot': False, 'freecad': '1.1.3', 'occt': '7.8.1',
         'freecad_ai': '0.23.1-alpha',
         'files': [{'path': p.relative_to(pilot.ROOT).as_posix(), 'sha256': sha256(p)} for p in paths],
         'gates': {n: {'status': 'pass' if n == 'geometry' else 'open', 'reason': r} for n, r in reasons.items()}}
    m['gates']['geometry']['evidence'] = [(OUT/'audit.json').relative_to(pilot.ROOT).as_posix()]
    assert verify(pilot.ROOT, m)['integrity_ok']
    assert not verify(pilot.ROOT, m, True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/tail-cartridge-integrated.json').write_text(
        json.dumps(m, indent=2), encoding='utf-8', newline='\n')
    print(verify(pilot.ROOT, m))


if __name__ == '__main__': main()
