"""One current bank material ledger, replacing the obsolete R1 feed totals.

Never sum revisions or mutate the selected R51. Source-wire920mm remains
unrouted; reserve it explicitly rather than claim a whole-robot census.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save


def main():
    start = datetime.now(timezone.utc)
    pins = {}

    def read(rel):
        p = ROOT / rel
        pins[rel] = sha(p)
        return json.loads(p.read_text(encoding='utf-8'))

    quantities = read('hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    order = {r['id']: r for r in quantities['lines']}
    feeds = read('hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json')
    inputs = read('hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1/materials.json')
    source = read('hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json')
    fixed = read('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1/checks.json')
    assert fixed['stock_delta'] == dict(additional_prints=0, fasteners=0, wires=0, straps=0, replacement='Deck')
    assert len(feeds['HELU23802']['extensions']) == 7
    assert sum(r['nominal_blank_mm'] for r in feeds['HELU23802']['extensions']) == 1190
    assert inputs['stock']['nominal_required_mm'] == 3020
    wires = {r['id']: r for r in source['conductors']}
    assert wires['W066']['nominal_selected_blank_mm'] == 330
    unresolved = [wires[k] for k in ('W064', 'W065', 'W067', 'W068')]
    assert all(not r['current_selected_route_checked'] for r in unresolved)
    assert sum(r['legacy_nominal_mm'] for r in unresolved) == 920
    roles = [dict(id=r['id'], blank_mm=r['nominal_blank_mm']) for r in feeds['HELU23802']['extensions']]
    roles.append(dict(id='W066', blank_mm=330))
    assert len({r['id'] for r in roles}) == 8
    # Each physical tie is counted once, never by its five BRep fragments.
    tie_groups = [
        dict(role='bank_TE_insulation', installed=24, removal_replacements=24),
        dict(role='fixed_lower_input_feeds', installed=20, removal_replacements=0),
        dict(role='main_MTA_FL_FR_RL_bodies', installed=6, removal_replacements=0),
        dict(role='FR_RL_RR_source_insulation', installed=6, removal_replacements=0),
        dict(role='FR_RL_RR_output_cage_and_two_insulated_ends', installed=9, removal_replacements=0),
    ]
    assert sum(r['installed'] for r in tie_groups) == 65
    out = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r2'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'stock.json').exists(), 'Preserve recorded evidence'
    end = datetime.now(timezone.utc)
    save(out / 'stock.json', dict(
        status='CURRENT_LOCAL_BANK_LEDGER_WHOLE_STOCK_OPEN', selected=False,
        physical_pass=False, K3_complete=False, E3_complete=False, W5_complete=False,
        replaces='servo-fuse-bank-stock-budget-r1; never add its1080mm/old splice count to this ledger.',
        HELU23802=dict(quantity_id='p0:WIRE-RED4-P0', unique_roles=roles,
            qualified_nominal_blank_subtotal_mm=1520,
            unchecked_source_roles=[dict(id=r['id'], legacy_reserve_mm=r['legacy_nominal_mm']) for r in unresolved],
            legacy_reserve_mm=920, provisional_stock_need_mm=2440,
            candidate_stock_m=3, selected_R51_stock_m=order['p0:WIRE-RED4-P0']['planning_quantity'],
            whole_robot_stock_qualified=False),
        LAPP0107001=dict(quantity_id='p0:WIRE-INLET-BLACK12-P0', input_blanks_mm=2880,
            W001_blank_mm=140, nominal_total_mm=3020, candidate_stock_m=4,
            selected_R51_stock_m=order['p0:WIRE-INLET-BLACK12-P0']['planning_quantity']),
        WAGO221412=dict(quantity_id='splice:WAGO221-412',
            installed_roles=['XB11', 'W026_output', 'W037_output', 'W045_output', 'W053_output'],
            installed=5, spare=1, candidate_quantity=6,
            selected_R51_quantity=order['splice:WAGO221-412']['planning_quantity'],
            exact_binding=order['splice:WAGO221-412']['product_binding']),
        TE_RNF100_3_8=dict(quantity_id='insulation:Pi:RNF-100-3/8-0-STK',
            new_source_joint_roles=['W042', 'W044', 'W052'], new_26mm_blanks=3,
            new_nominal_mm=78, trial_spare_mm=78,
            selected_stock_m=order['insulation:Pi:RNF-100-3/8-0-STK']['planning_quantity'],
            no_second_package=True, remaining_existing_sleeve_roles_retained=True),
        T18I=dict(quantity_id='tie:111-02370', local_groups=tie_groups,
            local_installed_known=65, local_removal_replacement_allowance=24,
            RR_MTA_body_ties=0, RR_MTA_integral_clips=4,
            fixed_RR_output_ties_cut_for_bank_removal=0,
            retained_R51_stock=order['tie:111-02370']['planning_quantity'],
            old_inline_holder_roles_must_be_replaced_not_added=True,
            missing_groups=['Final native P-WAGO wire restraints if changed.'],
            whole_robot_installed_census_qualified=False),
        fixed_RR_mount=fixed['stock_delta'],
        open=['Whole-source routes W064/W065/W067/W068 remain outside this local ledger.',
              'Select the final bank export only after assembly/removal and remaining WAGO grips.',
              'E3 current, temperature, fuse/source interruption assumptions remain their own gate.'],
        source_sha256=pins, script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(), finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(HELU_reserved_mm=1520, HELU_provisional_mm=2440,
        LAPP_mm=3020, WAGO_quantity_candidate=6, local_ties=65, selected=False)))


if __name__ == '__main__':
    main()
