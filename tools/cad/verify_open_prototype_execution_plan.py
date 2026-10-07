"""Cheap frozen planning checkpoint gate; no CAD rebuild and no fit claim."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'


def sha(path, mode='bytes'):
    data = path.read_bytes()
    if mode == 'utf8_lf':
        data = data.decode('utf-8').replace('\r\n','\n').encode('utf-8')
    else:
        assert mode == 'bytes'
    return hashlib.sha256(data).hexdigest()


def main():
    plan = json.loads((PACKAGE / 'execution-plan.json').read_text(encoding='utf-8'))
    old = json.loads((PACKAGE / 'layout.json').read_text(encoding='utf-8'))
    proof = json.loads((PACKAGE / 'reference-frame-correction.json').read_text(encoding='utf-8'))
    assert plan['status'] == 'STAGE1_PLAN_FROZEN_NOT_FULL_PHASE_RELEASE'
    modes = plan.get('source_digest_modes',{})
    assert set(modes) <= set(plan['source_sha256'])
    assert all(sha(ROOT / path,modes.get(path,'bytes')) == value
               for path,value in plan['source_sha256'].items())
    assert plan['result_count'] == 3 and plan['result_denominator'] == 20 and plan['result_percent'] == 15
    assert plan['confirmed_result_ids'] == ['M1', 'E4', 'A1']
    assert len({r['id'] for r in plan['result_dispositions']}) == len(plan['result_dispositions']) == 20
    assert {r['id'] for r in plan['result_dispositions'] if r['status'] == 'retained'} == set(plan['confirmed_result_ids'])
    assert not any(plan[k] for k in ['selected','physical_pass','W1_complete','W5_complete','E3_complete'])
    ids = [w for group in plan['wire_groups'].values() for w in group]
    assert len(ids) == len(set(ids)) == 80
    assert set(ids) == {r['id'] for r in old['body_conductors']}
    assert plan['bound_body_end_count'] == 122 and plan['body_end_count'] == 160
    assert set(plan['missing_body_endpoint_roles']) == set(old['missing_body_endpoint_roles'])
    assert len(plan['missing_body_endpoint_roles']) == 38
    assert plan['distribution_boundary_pair_count'] == len(old['distribution_boundary']) == 80
    assert all(plan['stage1_gates'].values())
    assert proof['source_unchanged'] and proof['save_reopen_verified']
    assert sha(ROOT / proof['target']) == proof['target_sha256']
    assert proof['translation_mm'] == [0,0,46.52] and proof['four_nominal_pads_inside_reference']
    assert proof['unchanged_shape_and_placement_count'] == 362
    assert proof['unaffected_BRep_structure_and_placements_preserved']
    assert proof['maximum_BRep_numeric_roundtrip_error'] <= 1e-10
    assert proof['no_mount_or_wire_geometry_changed'] and proof['no_full_assembly_collision_claim']
    main_row = next(r for r in plan['measured_current_inventory'] if r['name'] == 'MainSupplierFamily')
    assert main_row['bounds_mm'] == proof['corrected_bounds_mm']
    assert main_row['origin_mm'][2] == 46.52
    assert not plan['electrical_data_check']['E3_complete']
    assert {b['id'] for b in plan['electrical_data_check']['blockers']} == {'SOURCE','SERVO_LEADS','PREFUSE','SWITCH_CONVERTERS'}
    assert plan['remaining_phase1_estimate_hours'] == [12,24]
    assert not plan['hook']['enabled_at_record']
    assert plan['hook']['next_stage_requires_user_approval']
    print('Frozen stage1 PASS: source pins, 80 wire IDs, 38 open roles, corrected MAIN/reopen, fixed 3/20, E3 still open')


if __name__ == '__main__':
    main()
