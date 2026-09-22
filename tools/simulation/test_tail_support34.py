"""Offline evidence/stack regression; does not replace physical PETG tests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('support34', ROOT / 'tools/freecad/skorupa/support34.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def read(name):
    return json.loads((support.OUT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_instance_map_has_integral_base_and_removable_housing():
    assert len(support.ADDITIONS) == 17 and len(support.REPLACEMENTS) == 10
    assert support.REPLACEMENTS['MG92BMount29'] == ('ServoSupport34', None)
    assert 'BearingSupport34' not in support.ADDITIONS
    assert support.ADDITIONS['UpperHousing34'][1] == 'MG92BMount29'
    assert support.ADDITIONS['BearingLower34'][1] == 'UpperHousing34'
    assert support.PIVOT[:2] == [171, -6]  # old shaft line, not a new yaw axis


@pytest.mark.parametrize('length,head,nut,height,protrusion', [
    (16, 41, 50.6, 2.4, 4),     # upward foot screw
    (12, 128.2, 119.2, 1.6, 1.4),
    (12, 105, 97, 2.4, 1.6),
    (30, 125, 98.4, 2.4, 1),
])
def test_fastener_stack(length, head, nut, height, protrusion):
    assert length - abs(head - nut) - height == pytest.approx(protrusion)


def test_signed_native_and_snapshot_evidence():
    plan, native, fit, inherited = [read(n) for n in (
        'assembly-plan.json', 'assembly-validation.json', 'fit-audit.json', 'inheritance-check.json')]
    digest, master = sha(support.TARGET), sha(support.MASTER)
    assert all(r['source_sha256'] == digest for r in [plan, native, inherited])
    assert all(r['master_sha256'] == master for r in [plan, native, fit, inherited])
    assert fit['source_checkpoint_sha256'] == inherited['inherited_from_sha256'] == support.SOURCE_SHA
    assert len(plan['components']) == 306
    assert (native['fixed'], native['revolute'], native['temporary']) == (292, 13, 30)
    assert inherited['verified'] and inherited['inherited_parts'] == 279
    assert len(inherited['master_snapshot_checks']) == 27
    assert inherited['max_absolute_delta'] < 1e-9
    assert not native['physical_horn_verified'] and not native['head_actuation_tested']
    assert native['restored'] and native['solver_result'] == 0
    trial = native['tests'][0]
    assert len(trial['frames']) == 22 and len(trial['peak_angles_deg']) == 13
    for n, a in trial['peak_angles_deg'].items():
        assert a == pytest.approx(30 if n == 'Rev_TailYaw29' else 3, abs=1e-5)
    for frame in trial['frames']:
        assert frame['support_fixed_and_rotor_retained']
        assert max(frame[k] for k in ('max_joint_gap_mm', 'max_fixed_error_rad', 'max_axis_error_rad')) < 1e-5


def test_geometry_and_assembly_limits_remain_explicit():
    fit = read('fit-audit.json')
    assert fit['geometric_checks_passed'] and not fit['print_release']
    assert not fit['horn_interface_verified'] and not fit['physical_bearing_fit_verified']
    assert fit['assembly_requires_detached_tail_bridge'] and not fit['in_situ_foot_service_verified']
    assert not fit['rest_interferences']
    assert [r['yaw_deg'] for r in fit['yaw_samples']] == list(range(-30, 31, 5))
    assert all(not r['interferences'] for r in fit['yaw_samples'])
    assert all(s['fully_constrained'] for s in fit['sketches'])
    assert all(p['valid'] and p['solids'] == 1 and p['status'] == 'Valid' and not p['bop_errors'] and p['fits_256'] for p in fit['native_parts'])
    assert all(not r['hits'] for r in fit['tool_corridors'] if r['required_for_bench_assembly'])
    # The obstructed in-situ approach is retained, not disguised as serviceable.
    assert any(r['hits'] for r in fit['tool_corridors'] if not r['required_for_bench_assembly'])
    assert all(not r['hits'] for r in fit['upper_housing_insertion_samples'])
    assert all(r['volume_mm3'] < .01 for r in fit['servo_insertion_samples'])


def test_every_component_has_one_joint_parent_and_root_is_supported():
    plan = read('assembly-plan.json')
    names = {r['name'] for r in plan['components']}
    parents = {j['child']: j['parent'] for j in plan['joints']}
    assert len(parents) == len(plan['joints']) == len(names) - 1
    roots = names - set(parents)
    assert len(roots) == 1
    for start in names:
        seen = set()
        node = start
        while node in parents:
            assert node not in seen
            seen.add(node)
            node = parents[node]
        assert node in roots
    assert parents['TailRoot29'] == 'UpperHousing34'
    assert parents['MG92BOutput29'] == 'TailRoot29'
    assert parents['UpperHousing34'] == 'MG92BMount29'


def test_bearings_have_purchased_mass_not_petg_density():
    from cad_model import REVISION, BOUGHT_G
    if REVISION not in ('v34', 'v35'):
        pytest.skip('v34 mass budget only')
    assert BOUGHT_G['BearingLower34'] == BOUGHT_G['BearingUpper34'] == 13


def test_fit_coupon_files_match_checked_closed_meshes():
    folder = support.OUT / 'coupons'
    report = json.loads((folder / 'verification.json').read_text())
    assert report['master_sha256'] == sha(folder / 'PETGFit34.FCStd')
    assert len(report['coupons']) == 6
    assert report['export_linear_deflection_mm'] == .005
    for row in report['coupons']:
        assert row['closed'] and row['components'] == 1 and not row['nonmanifold']
        assert row['stl_sha256'] == sha(folder / (row['name'] + '.stl'))
        assert abs(row['mesh_volume_mm3'] / row['native_volume_mm3'] - 1) < .0002
    assert not report['physical_fit_verified'] and not report['robot_print_release']
