"""Checkpoint the installed R4 whole robot, without promoting print readiness."""
import json
from pathlib import Path
import pilot
import integrate_tail_cartridge as task
from release_check import verify, sha256


def main():
    geometry = json.loads((task.OUT/'geometry.json').read_text())
    native = json.loads((task.OUT/'relocation-native.json').read_text())
    migration = json.loads((task.OUT/'migration.json').read_text())
    plan = json.loads((task.OUT/'assembly-plan.json').read_text())
    assert migration['assembly_sha256'] == plan['source_sha256'] == sha256(task.TARGET)
    assert migration['module_sha256'] == sha256(task.MODULE)
    paths = []
    for filename in ['modular-pilot.json', 'tail-cartridge-clearance.json']:
        path = pilot.ROOT/'hardware/releases'/filename
        m = json.loads(path.read_text())
        assert verify(pilot.ROOT, m)['integrity_ok']
        paths.extend([path] + [pilot.ROOT/r['path'] for r in m['files']])
    for r in [geometry,native]:
        for path,digest in r['file_sha256'].items():
            assert sha256(pilot.ROOT/path) == digest
            paths.append(pilot.ROOT/path)
        assert r['tool_sha256'] == sha256(pilot.ROOT/'tools/cad/validate_tail_integration.py')
    assert geometry['components'] == 329 and geometry['unchanged_components'] == 318
    assert not geometry['static_intersections']
    assert all(not r['intersections'] for r in geometry['tail_collision_samples'])
    assert native['documents'] == 10 and len(native['links']) == 54
    assert len(native['native']['frames']) == 22 and native['native']['restored']
    assert all(p['restored'] for p in native['parameters'])
    assert native['native']['temporary'] == 29
    for p,h in migration['unchanged_predecessor_files'].items(): assert sha256(pilot.ROOT/p) == h
    paths += [task.OUT/n for n in ['README.md', '.gitattributes', 'migration.json', 'geometry.json', 'relocation-native.json', 'assembly-plan.json', 'whole-cat.png', 'tail-installed.png', 'tests.json']]
    paths += [pilot.ROOT/'tools/cad'/n for n in ['integrate_tail_cartridge.py', 'validate_tail_integration.py',
                                             'package_tail_installation.py', 'test_tail_installation.py']]
    paths += [pilot.CAD/'current-assembly.json', pilot.ROOT/'hardware/bom/tail-cartridge-installation.json']
    paths = list(dict.fromkeys(paths))
    reasons = {
        'geometry': 'Inherited shell strict BOP errors remain. Incremental R4 equivalence, strict new-part BOP and sampled clearances pass separately.',
        'assembly': '329 parts / 315 Fixed / 13 Revolute retained in native motion; 29 TEMP and unconfirmed real servo horn remain.',
        'fit': 'No physical horn, spline, center screw or PETG/bearing fit confirmation.',
        'petg': 'Three R4 prints fit 256 cubed nominally; profile/supports and printed coupons not approved.',
        'loads': 'No clamp load, layer strength or creep approval. Existing v35 Gazebo does not validate this modified assembly.',
        'electrical': 'Harness and electrical/thermal integration remain incomplete.',
        'service': 'Nominal R4 geometry matches sampled bench/cartridge installation studies; physical assembly and battery service remain open.'}
    m = {'schema_version': 1, 'name': 'robot-cat-tail-cartridge-installed-r4', 'readiness': 'prototype',
         'installed_in_robot': True, 'entry': task.TARGET.relative_to(pilot.ROOT).as_posix(),
         'freecad': '1.1.3', 'occt': '7.8.1', 'freecad_ai': '0.23.1-alpha',
         'checks': {'components':329, 'linked_parts':54, 'documents':10, 'native_frames':22,
                    'fixed':315, 'revolute':13, 'temporary':29, 'tail_collision_samples':13},
         'files': [{'path': p.relative_to(pilot.ROOT).as_posix(), 'sha256':sha256(p)} for p in paths],
         'gates': {n:{'status':'fail' if n == 'geometry' else 'open', 'reason':r} for n,r in reasons.items()}}
    assert verify(pilot.ROOT,m)['integrity_ok']
    assert not verify(pilot.ROOT,m,True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/tail-cartridge-installation.json').write_text(json.dumps(m,indent=2),encoding='utf-8',newline='\n')
    print(verify(pilot.ROOT,m))


if __name__ == '__main__': main()
