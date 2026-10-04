"""Replace legacy source reserve, never add source revisions together."""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import save, sha
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-source-material-contribution-r1'


def contribution(source, bank, grips):
    assert source['route_wires'] == ['W064', 'W065', 'W067', 'W068', 'XA01']
    assert source['S1_trial_total_mm'] == 2390 and source['legacy_S1_mm'] == 920
    assert grips['status'] == 'FOUR_SOURCE_INSULATION_GRIPS_LOCAL_COMPLETE_UNSELECTED'
    assert not grips['hits'] and not grips['errors']
    existing = bank['HELU23802']['unique_roles']
    roles = {r['id']: r['blank_mm'] for r in existing}
    assert len(roles) == len(existing) and sum(roles.values()) == 1520
    assert not set(source['route_wires'][:4]).intersection(roles)
    roles.update({k: source['route_trial_mm'][k] for k in source['route_wires'][:4]})
    total = sum(roles.values()); assert total == 3910
    # Deliberate prototype cutting budget: one100mm retermination per S1 wire
    # plus10% route fitting allowance. No supplier/manufacturing accuracy claim.
    allowance = 400 + 391
    return dict(status='SOURCE_MATERIAL_CONTRIBUTION_CANDIDATE_WHOLE_SELECTION_OPEN',
        HELU23802=dict(unique_roles=roles, legacy920mm_removed_not_added=True,
            nominal_total_mm=total, prototype_retermination_allowance_mm=400,
            prototype_fitting_allowance_mm=391, total_with_allowance_mm=total+allowance,
            candidate_stock_m=5, remaining_candidate_mm=5000-total-allowance,
            stock_reason='4m leaves only90mm over nominal3910mm;5m accommodates declared prototype fitting/retermination budget.',
            selected=False, supplier_cut_length_or_price_not_refreshed=True),
        HELU23502_XA01=dict(unique_role='XA01', nominal_trial_blank_mm=40,
            charge_existing_shared_stock_only=True, prefuse_internal_holder_length_unknown=True,
            must_not_claim_complete_prefuse_50mm_until_internal_path_received=True),
        T18I145=dict(unique_role='four_Carrier_source_insulation_seats',
            installed=4, one_service_replacement_allowance=4, contribution=8,
            replace_any_historical_S1_grip_roles_not_add_them=True,
            whole_robot_census_open=True),
        prints=dict(Carrier_replacement_quantity=1, additional_quantity=0,
            BankLeft_replacement_quantity=1, Cover_replacement_quantity=1,
            upper_guard_not_designed_or_counted=True),
        E3_changed_length_inputs=dict(
            FRONT_red_source_pair_roles=['W067','W064'], FRONT_nominal_mm=1320,
            FRONT_legacy_mm=480, FRONT_delta_mm=840,
            REAR_red_source_pair_roles=['W068','W065'], REAR_nominal_mm=1070,
            REAR_legacy_mm=440, REAR_delta_mm=630,
            need_actual_wire_resistance_and_branch_current_for_drop=True,
            source_or_fuse_electrical_qualification_claimed=False),
        additional_fasteners=0, selection_changed=False, K3_complete=False, E3_complete=False,
        W5_complete=False, physical_pass=False)


def main():
    begin = datetime.now(timezone.utc)
    paths = [ROOT / 'hardware/electronics/full-cat' / rel for rel in (
        'w5-source-received-interface-r1/checks.json',
        'servo-fuse-bank-stock-budget-r13/stock.json',
        'w5-source-grips-native-r2/checks.json')]
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    for row in rows:
        assert all(sha(ROOT/k) == v for k, v in {**row.get('source_sha256',{}), **row.get('files',{})}.items())
    result = contribution(*rows); end = datetime.now(timezone.utc)
    result.update(source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__), *paths]},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds())
    assert not (OUT / 'stock.json').exists(); OUT.mkdir(parents=True, exist_ok=True)
    save(OUT/'stock.json', result); print('SOURCE_STOCK_CANDIDATE', result['HELU23802'], flush=True)


if __name__ == '__main__': main()
