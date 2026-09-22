"""Verify saved v31 CAD, mounting tests and physics provenance; not print approval."""
import hashlib
import json
import zipfile
from cad_model import ROOT, OUT, REVISION


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert REVISION == 'v31', 'Set ROBOT_CAT_CAD_REVISION=v31'
    cad = ROOT/'hardware/skorupa/v31'
    digest = sha(cad/'Kot_v31_ZASILANIE.FCStd')
    master = sha(cad/'PowerDesign31.FCStd')
    plan, native, fit, inheritance = [read(cad/n) for n in [
        'assembly-plan.json', 'assembly-validation.json', 'fit-audit.json', 'inheritance-check.json']]
    assert all(r['source_sha256'] == digest for r in [plan, native, fit, inheritance])
    assert all(r['master_sha256'] == master for r in [plan, native, fit])
    assert len(plan['components']) == 280
    assert (native['fixed'], native['revolute'], native['temporary']) == (266, 13, 34)
    assert native['solver_result'] == 0 and native['restored']
    test = native['tests'][0]
    assert len(test['frames']) == 22 and len(test['peak_angles_deg']) == 13
    for name, value in test['peak_angles_deg'].items():
        assert abs(value-(30 if name == 'Rev_TailYaw29' else 3)) < 1e-5
    for frame in test['frames']:
        assert frame['imu_fixed_to_chassis'] and frame['power_fixed_to_chassis']
        assert max(frame[k] for k in ['max_joint_gap_mm', 'max_fixed_error_rad', 'max_axis_error_rad']) < 1e-5
    assert fit['new_components'] == 16 and fit['rest_pairs'] > 0 and not fit['rest_interferences']
    assert len(fit['native_sketches']) == 9 and all(r['fully_constrained'] for r in fit['native_sketches'])
    assert all(r['valid'] and r['solids'] == 1 and r['fits_256_cube'] for r in fit['printable_master_parts'])
    assert len(fit['contacts']) == 4
    assert all(min(r['post_to_support_mm2'], r['post_to_PCB_mm2']) > 15
               and r['shaft_clearance_interference_mm3'] < 1e-6 for r in fit['contacts'])
    assert len(fit['terminal_pins']) == 4 and all(r['PCB_interference_mm3'] < 1e-6 for r in fit['terminal_pins'])
    assert all(min(r.get('gap_spacer_to_deck_mm2',20), r.get('gap_spacer_to_bridge_mm2',20)) > 15 for r in fit['contacts'])
    assert len(fit['cable_keepouts']) == 2 and all(not r['hits'] for r in fit['cable_keepouts'])
    assert inheritance['verified'] and inheritance['inherited_parts'] == 260
    assert inheritance['inherited_from_sha256'] == sha(ROOT/'hardware/skorupa/v30/Kot_v30_ELEKTRONIKA.FCStd')
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
    assert len(geometry['components']) == 280 and all(r['valid'] for r in geometry['components'])
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
                  tail_support_verified=False, IMU_magnetic_calibration=False, power_thermal_approval=False,
                  complete_terminal_tool_access=not any(r['blockers'] for r in fit['terminal_tool_access']),
                  source_sha256=digest, master_sha256=master, archives_sha256=archives,
                  components=280, native_revolute=13, native_fixed=266, temporary_locks=34,
                  native_frames=22, new_part_rest_interferences=0, inherited_parts_checked=260,
                  dynamic_links=13, dynamic_leg_axes=12, tail_frozen_in_Gazebo=True,
                  trials=trials, scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
