"""Close explicitly revised nominal E3, never electrical/power qualification.

Preserve the strict95 result and selected CAD bytes. One manifest composes the
existing exact-byte payload with this small documentation overlay; no new CAD.
"""
import argparse, copy, json, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from plan_current_harness_interfaces import ROOT, BASE, SHA
from release_check import verify, REQUIRED_GATES
from current_work_guard import check

OUT = BASE / 'phase1-prototype-final'
REVISION = 'E3_NOMINAL_PROTOTYPE_20261017'


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')


def validate_basis(criteria, result):
    assert criteria['criterion_revision'] == result['criterion_revision'] == REVISION
    assert criteria['fixed_total'] == result['fixed_total'] == 20
    assert criteria['previous_score_under_strict_criterion'] == 95
    assert criteria['human_authorization']['latest_message'] and criteria['no_CAD_or_BOM_change']
    for q in (criteria, result):
        assert all(q[k] is False for k in ('physical_pass', 'power_authorized', 'electrical_qualification_complete'))
    assert result['E3_complete'] and result['completion_kind'] == 'NOMINAL_DOCUMENTATION_ONLY'
    rows = result['fuse_roles']
    assert len(rows) == len({r['ref'] for r in rows}) == 23
    assert Counter(r['rating_a'] for r in rows) == Counter({30:1, 10:4, 4:13, 3:1, 1:3, 0.1:1})
    assert all(r['qualification'] == 'OPEN_PHASE2' for r in rows)
    assert {r['id'] for r in result['phase2_holds']} == {'SOURCE','LEADS','CLEARING','TRANSIENTS'}
    assert all(r['status'] == 'open' and r['blocks_LiPo_trials'] for r in result['phase2_holds'])
    assert result['scenarios']['all_stall_permitted'] is False
    assert result['scenarios']['leg_stall_A'] > result['scenarios']['operating_budget_A']
    assert result['assumptions']['MG92B_0_85A']['kind'] == 'supplier_estimate_at4.8V_not_guarantee_at6V'
    assert result['assumptions']['cable_26AWG']['delivered_Waveshare_confirmed'] is False
    return True


def build():
    check(); tick = time.monotonic(); pins = {}
    def read(path):
        pins[path.relative_to(ROOT).as_posix()] = SHA(path)
        return json.loads(path.read_text(encoding='utf-8'))
    score_path = BASE/'current-phase1-score.json'
    score = json.loads(score_path.read_text())
    assert score['fixed_total'] == 20 and score['result_count'] == 19 and score['result_percent'] == 95
    assert 'E3' not in score['confirmed_result_ids']
    assert SHA(ROOT/score['evidence']) == score['evidence_sha256']
    for row in score['current_result_overrides'].values():
        assert SHA(ROOT/row['evidence']) == row['sha256']
    before = OUT/'score-before.json'; before.write_bytes(score_path.read_bytes())
    pins[before.relative_to(ROOT).as_posix()] = SHA(before)
    previous = read(BASE/'phase1-whole-assembly/manifest.json')
    checked = verify(ROOT, previous); assert checked['integrity_ok'], checked
    pins.update({r['path']:r['sha256'] for r in previous['files']})
    criteria = read(OUT/'criteria.json')
    k1 = read(BASE/'phase1-current-print-selection-r4.json')
    k2 = read(BASE/'phase1-current-purchased-selection-r4.json')
    assert len(k1['prints']) == 84 and sum(r['quantity'] for r in k1['prints']) == 117
    assert k2['drive_count'] == 15
    protection = read(ROOT/'hardware/electronics/full-cat/protection-selection-r2/branch-protection.json')
    read(ROOT/'hardware/electronics/full-cat/protection-selection-r2/sources.json')
    rows = copy.deepcopy(protection['rows'])
    expected = Counter(r['sku'] for r in rows)
    installed = {r['id'].removeprefix('Fuse '):r['installed'] for r in k2['components'] if r['id'].startswith('Fuse ')}
    assert dict(expected) == installed, (expected, installed)
    for row in rows:
        row.update(qualification='OPEN_PHASE2', nominal_selection_status='CONDITIONAL_NOMINAL_PROTOTYPE')
        if row['ref'] in ('F_HY','F_HP','F_TY'):
            row['prototype_reference_A_at4_8V'] = 0.85
            row['sensitivity_A_at6V_NOT_guarantee'] = 0.85*6/4.8
            row['scenario_basis'] = 'Adafruit supplier estimate at4.8V; delivered6V pulse/duration and1A fuse compatibility remain phase2 holds.'
    pi = 3*5.2/(0.8*9)+0.01; aux = 3*6.24/(0.8*9)+0.01
    result = dict(result_id='E3', E3_complete=True, selected=True, readiness='prototype', fixed_total=20,
        criterion_revision=REVISION, completion_kind='NOMINAL_DOCUMENTATION_ONLY',
        physical_pass=False, power_authorized=False, electrical_qualification_complete=False,
        strict_previous_E3_qualification_still_open=True, fuse_roles=rows,
        assumptions={
          'battery':dict(kind='manufacturer_catalogue',sku='GEA223S30X6GT',cells=3,nominal_V=11.1,full_V=12.6,capacity_Ah=2.2,C=30,fault_upper_A=None),
          'ST3215':dict(kind='manufacturer_catalogue_12V_variant',no_load_A=0.2,rated_A=0.9,stall_A=2.7,actual_gait_current_measured=False),
          'MG92B_0_85A':dict(kind='supplier_estimate_at4.8V_not_guarantee_at6V',source='https://forums.adafruit.com/viewtopic.php?t=104598',value_A=0.85),
          'cable_26AWG':dict(kind='analogue_vendor_description_NOT_actual_harness_rating',source='https://armdojo.com/products/feetech-servo-cable-set-3-pin-5264',delivered_Waveshare_confirmed=False),
          'converter_budget':dict(kind='project_assumption',MAIN_output_A=3,AUX_output_A=3,efficiency=0.8,VIN_calculation_V=9,extra_input_A=0.01,automatic_limiter=False),
          'fault_sensitivity':dict(kind='hypothetical_complete_loop_NOT_measured_pack_bounds',R_milliohm=[10,20,40],I_at12_6V_A=[1260,630,315],F0_interruption_A=1000,all_scenarios_within_F0_rating=False)},
        scenarios=dict(operating_budget_A=20, budget_is_enforced=False,pi_input_reference_A=pi,aux_input_reference_A=aux,
          leg_rated_reference_A=12*0.9,leg_stall_A=12*2.7,all_stall_with_converter_budgets_A=12*2.7+pi+aux,
          MG92B_three_voltage_scaled_sensitivity_A=3*0.85*6/4.8,all_stall_permitted=False,
          fuse4A_does_not_guarantee_trip_at_servo_stall2_7A=True,larger_fuse_not_automatic_fix=True),
        phase2_holds=[
          dict(id='SOURCE',status='open',blocks_LiPo_trials=True,acceptance='Defensible complete-loop prospective current within exact F0/holder interruption limits; revise before use if unknown or incompatible. No intentional LiPo short.'),
          dict(id='LEADS',status='open',blocks_LiPo_trials=True,acceptance='Identify delivered15lead/contact limits and inspect polarity/insulation/restraint; controlled competent qualification where data unavailable.'),
          dict(id='CLEARING',status='open',blocks_LiPo_trials=True,acceptance='Protection clearing/energy compatible with actual conductors, including thin pre-branch segments, and actual normal startup pulses. No blind fuse uprating.'),
          dict(id='TRANSIENTS',status='open',blocks_LiPo_trials=True,acceptance='Controlled voltage/current/thermal/start-stop/reverse-energy/S821 assessment within actual component limits and project budgets before LiPo trials.')],
        instructions=(OUT/'ELECTRICAL_PROTOTYPE.md').relative_to(ROOT).as_posix(),
        native_geometry_unchanged=True, no_new_parts=True,
        scope='Approved revised E3 nominal prototype documentation:23exact fuse roles, catalogue/estimated/analogous assumptions, budget/stall scenarios and4mandatoryphase2 holds. NOT completed electrical qualification, power authorization or physicalPASS.')
    validate_basis(criteria, result)
    assessment = OUT/'assessment.json'; save(assessment, result)
    for file in [assessment, OUT/'README.md',OUT/'ELECTRICAL_PROTOTYPE.md',OUT/'.gitattributes',Path(__file__),Path(__file__).with_name('test_phase1_nominal_completion.py'),ROOT/'hardware/cad/toolchain.json']:
        pins[file.relative_to(ROOT).as_posix()] = SHA(file)
    selection = dict(result, current_entry=(OUT/'README.md').relative_to(ROOT).as_posix(),
        current_CAD='hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/phase1-whole-assembly/RobotCatPhase1Current.FCStd',
        existing_exact_byte_payload='hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/phase1-whole-assembly/Phase1CurrentPayload.zip',
        print_identities=84,installed_prints=117,drive_count=15,cosmetic_body_included=False,
        previous_strict_score=before.relative_to(ROOT).as_posix(),small_overlay_no_duplicated_CAD_archive=True)
    sf=OUT/'selection.json'; save(sf,selection);pins[sf.relative_to(ROOT).as_posix()]=SHA(sf)
    gates={g:dict(status='open',reason='Physical/electrical/material/fit/loads/service qualification remainsphase2; no print/power approval.') for g in REQUIRED_GATES}
    for g in ('geometry','assembly'):
        gates[g]=dict(status='pass',reason='Unchanged selected whole117instance CAD and assembly evidence retained; documentation overlay only.',evidence=[(BASE/'phase1-whole-assembly/manifest.json').relative_to(ROOT).as_posix()])
    manifest=dict(schema_version=1,result_id='E3',E3_complete=True,selected=True,readiness='prototype',physical_pass=False,power_authorized=False,
        electrical_qualification_complete=False,criterion_revision=REVISION,selection=sf.relative_to(ROOT).as_posix(),scope=result['scope'],
        files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],gates=gates,toolchain='hardware/cad/toolchain.json')
    v=verify(ROOT,manifest);assert v['integrity_ok'],v
    assert not verify(ROOT,manifest,True)['integrity_ok']
    save(OUT/'manifest.json',manifest)
    print(json.dumps(dict(status='NOMINAL_E3_DOCUMENTATION_VERIFIED_NOT_YET_SCORED',files=v['files_checked'],seconds=round(time.monotonic()-tick,3))))


def confirm_existing():
    check();mf=OUT/'manifest.json';m=json.loads(mf.read_text());r=json.loads((OUT/'assessment.json').read_text());c=json.loads((OUT/'criteria.json').read_text())
    validate_basis(c,r);v=verify(ROOT,m);assert v['integrity_ok'],v
    sf=BASE/'current-phase1-score.json';old=json.loads((OUT/'score-before.json').read_text());score=json.loads(sf.read_text())
    assert score == old, 'Current score changed after review; do not overwrite it'
    assert len(set(score['confirmed_result_ids'])) == score['result_count'] == 19 and 'E3' not in score['confirmed_result_ids']
    assert score['fixed_total'] == 20 and score['result_percent'] == 95
    score['confirmed_result_ids'].append('E3')
    score.update(result_count=20,result_percent=100,change_pp=5,new_result='E3',phase1_prototype_design_complete=True,
      electrical_qualification_complete=False,power_authorized=False,physical_pass=False,
      previous_evidence={k:old[k] for k in ('new_result','evidence','evidence_sha256')},
      evidence=mf.relative_to(ROOT).as_posix(),evidence_sha256=SHA(mf),checked_utc=datetime.now(timezone.utc).isoformat(),
      verification_basis=r['scope'],criterion_revisions={'E3':dict(revision=REVISION,previous_strict_percent=95,
        authorization_file=(OUT/'criteria.json').relative_to(ROOT).as_posix(),strict_electrical_qualification_complete=False)},
      current_release_index=(OUT/'README.md').relative_to(ROOT).as_posix())
    score['current_result_overrides']['E3']=dict(evidence=score['evidence'],sha256=score['evidence_sha256'],new_points=5)
    save(sf,score)
    print(json.dumps(dict(score='20/20=100',basis='APPROVED_NOMINAL_PROTOTYPE_DESIGN',electrical_qualification_complete=False,power_authorized=False,physical_pass=False)))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--confirm-existing',action='store_true');a=p.parse_args()
    confirm_existing() if a.confirm_existing else build()
