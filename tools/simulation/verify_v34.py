"""Bind v34 native/fit/inheritance and fresh Gazebo evidence, not a release."""
import hashlib
import json
import zipfile
from cad_model import ROOT, OUT, REVISION, actuator_envelope


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert REVISION == 'v34', 'Set ROBOT_CAT_CAD_REVISION=v34'
    cad = ROOT / 'hardware/skorupa/v34'
    plan, native, fit, inherited = [read(cad / n) for n in
        ['assembly-plan.json', 'assembly-validation.json', 'fit-audit.json', 'inheritance-check.json']]
    digest, master = sha(cad / plan['cad_filename']), sha(cad / plan['master_filename'])
    assert all(r['source_sha256'] == digest for r in [plan, native, inherited])
    assert all(r['master_sha256'] == master for r in [plan, native, fit, inherited])
    # Fit is performed BEFORE integration, on the signed master plus signed v33.
    # Exact inheritance/snapshot comparisons bind those checked shapes to v34.
    source = ROOT / 'hardware/skorupa/v33'
    old = read(source / 'assembly-plan.json')
    assert sha(source / old['cad_filename']) == fit['source_checkpoint_sha256'] == inherited['inherited_from_sha256']
    assert inherited['verified'] and inherited['inherited_parts'] == 279
    assert inherited['max_absolute_delta'] < 1e-9
    assert len(inherited['master_snapshot_checks']) == 27
    assert len(plan['components']) == native['components'] == 306
    assert (native['fixed'], native['revolute'], native['temporary']) == (292, 13, 30)
    assert native['solver_result'] == 0 and native['restored']
    assert not native['head_actuation_tested'] and not native['physical_horn_verified']
    trial = native['tests'][0]
    assert len(trial['frames']) == 22 and len(trial['peak_angles_deg']) == 13
    for name, value in trial['peak_angles_deg'].items():
        assert abs(value - (30 if name == 'Rev_TailYaw29' else 3)) < 1e-5
    for row in trial['frames']:
        assert row['support_fixed_and_rotor_retained']
        assert max(row[k] for k in ['max_joint_gap_mm', 'max_fixed_error_rad', 'max_axis_error_rad']) < 1e-5
    assert fit['geometric_checks_passed'] and not fit['print_release']
    assert not fit['physical_bearing_fit_verified'] and not fit['horn_interface_verified']
    assert not fit['rest_interferences']
    assert len(fit['yaw_samples']) == 13 and not any(r['interferences'] for r in fit['yaw_samples'])
    assert all(r['fully_constrained'] for r in fit['sketches'])
    assert all(r['valid'] and r['solids'] == 1 and r['status'] == 'Valid' and not r['bop_errors'] for r in fit['native_parts'])
    assert all(not r['hits'] for r in fit['upper_housing_insertion_samples'])
    assert all(r['volume_mm3'] < .01 for r in fit['servo_insertion_samples'])
    assert any(r['volume_mm3'] > .01 for r in fit['rejected_straight_servo_insertion'])
    assert all(not r['hits'] for r in fit['tool_corridors'] if r['required_for_bench_assembly'])
    assert any(r['hits'] for r in fit['tool_corridors'] if not r['required_for_bench_assembly'])
    assert fit['assembly_requires_detached_tail_bridge'] and not fit['in_situ_foot_service_verified']
    archives = {}
    for stem in ['inputs', 'meshes', 'telemetry']:
        path = OUT / (stem + '.zip')
        archives[path.name] = sha(path)
        assert path.with_suffix('.sha256').read_text().split()[0] == archives[path.name]
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
    with zipfile.ZipFile(OUT / 'inputs.zip') as archive:
        geometry, model = [json.loads(archive.read(n)) for n in ['geometry.json', 'model.json']]
    assert geometry['source_sha256'] == model['source_sha256'] == digest
    assert len(geometry['components']) == 306 and all(r['valid'] for r in geometry['components'])
    assert len(model['links']) == 13 and len(model['joints']) == 12
    assert abs(sum(r['mass_kg'] for r in model['links']) - model['total']['mass_kg']) < 1e-10
    assert geometry['frozen_native_joints'] == ['Rev_TailYaw29']
    byname = {r['name']: r for r in model['components']}
    for name in ['BearingLower34', 'BearingUpper34']:
        assert abs(byname[name]['mass_kg'] - .013) < 1e-12 and 'allowance' in byname[name]['basis']
    assert read(OUT / 'auxiliary-budget.json')['source_sha256'] == digest
    suite = read(OUT / 'baseline-suite.json')
    assert suite['source_sha256'] == digest and suite['completed_cases'] == suite['planned_cases'] == 3
    trials = []
    with zipfile.ZipFile(OUT / 'telemetry.zip') as archive:
        for row in suite['trials']:
            name = 'trials/' + row['summary']
            summary = json.loads(archive.read(name))
            raw = json.loads(archive.read(name.replace('-summary.json', '.json')))
            assert summary['source_sha256'] == digest and not summary['hard_joint_velocity_limit']
            assert raw['summary'] == summary and len(raw['records']) == summary['samples'] > 0
            fresh = [r for r in raw['records'] if r['motor_fresh']]
            assert fresh and all(len(r['motor_joints']) == 12 for r in fresh)
            for record in fresh:
                assert all(abs(v[2]) <= actuator_envelope(speed=v[1])['moving_limit_nm'] + 1e-8
                           for v in record['motor_joints'].values())
            assert all(j['torque_speed_violations'] == 0 for j in summary.get('joints', {}).values())
            if summary['screening_completed']:
                assert summary.get('joints')
            trials.append(dict(file=name, mode=summary['mode'], mass_case=summary['configuration']['mass'],
                screening_completed=summary['screening_completed'], result=summary['result'], fresh_motor_samples=len(fresh)))
    assert {(r['mode'], r['mass_case']) for r in trials if r['screening_completed']} >= {
        ('stand', 'nominal'), ('crawl', 'nominal'), ('crawl', 'upper')}
    report = dict(source_sha256=digest, master_sha256=master, archives_sha256=archives,
        provenance_verified=True, mechanical_release=False, continuous_torque_certified=False,
        components=306, native_fixed=292, native_revolute=13, temporary_locks=30,
        native_frames=22, inherited_parts_checked=279, changed_rest_interferences=0,
        head_and_tail_frozen_in_Gazebo=True, physical_horn_verified=False,
        physical_bearing_fit_verified=False, in_situ_foot_service_verified=False,
        inherited_head_issues_open=True, trials=trials, scope=__doc__)
    (OUT / 'checkpoint-integrity.json').write_text(json.dumps(report, indent=2), encoding='utf8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
