"""Verify saved v30 CAD, mounting tests and physics provenance; not print approval."""
import hashlib
import json
import zipfile
from cad_model import ROOT, OUT, REVISION


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert REVISION == 'v30', 'Set ROBOT_CAT_CAD_REVISION=v30'
    cad = ROOT/'hardware/skorupa/v30'
    digest = sha(cad/'Kot_v30_ELEKTRONIKA.FCStd')
    master = sha(cad/'ElectronicsDesign30.FCStd')
    plan, native, fit, inheritance = [read(cad/n) for n in [
        'assembly-plan.json', 'assembly-validation.json', 'fit-audit.json', 'inheritance-check.json']]
    assert all(r['source_sha256'] == digest for r in [plan, native, fit, inheritance])
    assert all(r['master_sha256'] == master for r in [plan, native, fit])
    assert len(plan['components']) == 264
    assert (native['fixed'], native['revolute'], native['temporary']) == (250, 13, 35)
    assert native['solver_result'] == 0 and native['restored']
    test = native['tests'][0]
    assert len(test['frames']) == 22 and len(test['peak_angles_deg']) == 13
    for name, value in test['peak_angles_deg'].items():
        assert abs(value-(30 if name == 'Rev_TailYaw29' else 3)) < 1e-5
    for frame in test['frames']:
        assert frame['imu_fixed_to_chassis']
        assert max(frame[k] for k in ['max_joint_gap_mm', 'max_fixed_error_rad', 'max_axis_error_rad']) < 1e-5
    assert fit['new_components'] == 12 and fit['rest_pairs'] == 48 and not fit['rest_interferences']
    assert len(fit['native_sketches']) == 6 and all(r['fully_constrained'] for r in fit['native_sketches'])
    assert all(r['valid'] and r['solids'] == 1 and r['fits_256_cube'] for r in fit['printable_master_parts'])
    assert len(fit['contacts']) == 4
    assert all(min(r['post_to_deck_contact_mm2'], r['post_to_PCB_contact_mm2']) > 15
               and r['screw_clearance_interference_mm3'] < 1e-6 for r in fit['contacts'])
    assert len(fit['cable_keepouts']) == 2 and all(not r['hits'] for r in fit['cable_keepouts'])
    assert inheritance['verified'] and inheritance['inherited_parts'] == 249
    assert inheritance['inherited_from_sha256'] == sha(ROOT/'hardware/skorupa/v29/Kot_v29_OGON_PROTOTYP.FCStd')
    assert inheritance['max_absolute_delta'] < 1e-9
    archives = {}
    for stem in ['inputs', 'meshes', 'telemetry']:
        p = OUT/(stem+'.zip')
        archives[p.name] = sha(p)
        assert p.with_suffix('.sha256').read_text().split()[0] == archives[p.name]
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
    with zipfile.ZipFile(OUT/'inputs.zip') as z:
        geometry, model = [json.loads(z.read(n)) for n in ['geometry.json', 'model.json']]
    assert geometry['source_sha256'] == model['source_sha256'] == digest
    assert len(geometry['components']) == 264 and all(r['valid'] for r in geometry['components'])
    assert len(model['links']) == 13 and len(model['joints']) == 12
    assert abs(sum(r['mass_kg'] for r in model['links'])-model['total']['mass_kg']) < 1e-10
    assert geometry['frozen_native_joints'] == ['Rev_TailYaw29']
    tail = read(ROOT/'hardware/skorupa/v29/tail-budget.json')
    aux = read(OUT/'auxiliary-budget.json')['tail_yaw_actual_cad_axis']
    assert abs(aux['mass_kg']-tail['moving_mass_kg']) < 1e-12
    assert abs(aux['inertia_about_axis_kg_m2']-tail['yaw_inertia_kg_m2']) < 1e-12
    trials = []
    with zipfile.ZipFile(OUT/'telemetry.zip') as z:
        for n in z.namelist():
            if not n.endswith('-summary.json'):
                continue
            r = json.loads(z.read(n))
            assert r['source_sha256'] == digest and r['screening_completed']
            assert not r['hard_joint_velocity_limit']
            assert all(j['torque_speed_violations'] == 0 for j in r['joints'].values())
            trials.append(dict(file=n, mode=r['mode'], mass_case=r['configuration']['mass']))
    assert {(r['mode'], r['mass_case']) for r in trials} >= {('stand', 'nominal'), ('crawl', 'nominal'), ('crawl', 'upper')}
    report = dict(provenance_verified=True, mechanical_release=False,
                  continuous_torque_certified=False, full_gait_collision_test=False,
                  tail_support_verified=False, IMU_magnetic_calibration=False,
                  source_sha256=digest, master_sha256=master, archives_sha256=archives,
                  components=264, native_revolute=13, native_fixed=250, temporary_locks=35,
                  native_frames=22, new_part_rest_interferences=0, inherited_parts_checked=249,
                  dynamic_links=13, dynamic_leg_axes=12, tail_frozen_in_Gazebo=True,
                  trials=trials, scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
