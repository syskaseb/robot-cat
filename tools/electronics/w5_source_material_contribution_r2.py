"""One reconciled source-family candidate, replacing rather than stacking parts.

Keep R53 selected until whole assembly gates close. This ledger pins seven
actual exports and six exact existing fastener allocations; no purchase.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, json
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-source-material-contribution-r2'

PRINTS = [
    ('electronics:DeckP10-cover-mount', 'replace', 'w5-source-platform-native-r4', 'Deck', 'SourceInletPlatform.FCStd', 'SourcePlatformDeckFinished'),
    ('electronics:Carrier service ports', 'replace', 'w5-source-grips-native-r2', 'Carrier', 'SourceCarrierInsulationGrips.FCStd', 'SourceGripsFinished'),
    ('electronics:servo-fuse-bank-left', 'replace', 'w5-source-bank-passage-native-r1', 'BankLeft', 'SourceBankEdgePassage.FCStd', 'SourceBankLeftFinished'),
    ('body:raised-upper-cover-mount', 'replace', 'w5-source-roof-native-r5', 'Cover', 'SourceProtectiveHoods.FCStd', 'SourceRoofCoverFinished'),
    ('electronics:source-inlet-platform', 'add', 'w5-source-platform-native-r4', 'Platform', 'SourceInletPlatform.FCStd', 'PlatformFinished'),
    ('body:source-hood-west', 'add', 'w5-source-roof-native-r5', 'WestHood', 'SourceProtectiveHoods.FCStd', 'WestHoodFinished'),
    ('body:source-hood-east', 'add', 'w5-source-roof-native-r5', 'EastHood', 'SourceProtectiveHoods.FCStd', 'EastHoodFinished'),
]


def reconcile(prior, selection, platform, roof):
    result = copy.deepcopy(prior)
    result.pop('source_sha256', None)
    for key in ('started_utc', 'finished_utc', 'worker_wall_seconds'):
        result.pop(key, None)
    old = {p['identity']: p for p in selection['prints']}
    assert len(old) == len(selection['prints'])
    rows = []
    for ident, action, folder, tag, native, final in PRINTS:
        if action == 'replace':
            assert ident in old and old[ident]['quantity'] == 1
        else:
            assert ident not in old
        rows.append(dict(identity=ident, action=action, quantity=1,
                         cad_folder='hardware/cad/studies/' + folder,
                         export=tag + '_UNSELECTED_x1.stl', native_file=native,
                         native_final=final, material='PETG'))
    result['prints'] = dict(roles=rows, replaced=4, additional=3,
                           source_family_installed_parts=7,
                           old_R53_jobs=len(old), candidate_jobs=len(old)+3,
                           right_bank_and_P0_E6_head_ears_unchanged=True,
                           no_old_and_new_Cover_or_Carrier_or_Deck_counted_together=True)
    allocations = [*platform['allocations'][:3], *roof['allocations']]
    assert len({r['role'] for r in allocations}) == len(allocations) == 6
    totals = {}
    for row in allocations:
        totals[row['supplier_id']] = totals.get(row['supplier_id'], 0) + row['quantity']
    assert sum(totals.values()) == 24  # 6bolts +6nuts +12washers
    return result, rows, allocations, totals


def main():
    begin = datetime.now(timezone.utc); assert not (OUT/'stock.json').exists()
    paths = [ROOT/'hardware/electronics/full-cat'/rel for rel in (
        'w5-source-material-contribution-r1/stock.json',
        'w5-source-platform-assembly-r1/assembly.json',
        'w5-source-roof-service-r2/assembly.json')]
    selection_path = ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    prior, platform, roof = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    for record in (prior, platform, roof):
        assert all(sha(ROOT/k) == v for k, v in
                   {**record.get('source_sha256', {}), **record.get('files', {})}.items())
    selection = json.loads(selection_path.read_text(encoding='utf-8'))
    result, rows, allocations, totals = reconcile(prior, selection, platform, roof)
    pins = [Path(__file__), *paths, selection_path]
    for row in rows:
        folder = ROOT/row['cad_folder']
        for name in (row['export'], row['native_file']):
            p = folder/name; assert p.is_file(), p; pins.append(p)
        row['stl_sha256'] = sha(folder/row['export'])
        row['native_sha256'] = sha(folder/row['native_file'])
    result['additional_fasteners'] = dict(allocations=allocations, consolidated_existing_supplier_ids=totals,
                                         installed_bolts=6, installed_nuts=6, installed_washers=12,
                                         obsolete_source_mounts_not_removed_or_double_counted=True)
    result['T18I145'] = dict(unique_roles=[
        dict(role='SourcePlatform_body_and_inlet', installed=2, service_replacements=2),
        dict(role='Carrier_four_S1_insulation_grips', installed=4, service_replacements=4)],
        installed=6, one_service_replacement_allowance=6,
        older_P_SYS_tie_retired=True, unchanged_W066_middle_tie_retained=True,
        shared_stock_quantity=300, final_robot_census_open=True,
        rule='Replace old inlet/S1 restraint roles at selection; do not add historic allowances to these12 loops.')
    result['whole_source_assembly_complete'] = False
    result['open_selection_gate'] = 'Receive whole source assembly/removal, including cage access and Carrier threading; keep R53 selected meanwhile.'
    result['supplier_model_note'] = dict(
        url='https://wago-embedded.customer-domain.wago.com/3d-cad-models/?info=wago/pg07/serie221/0221-0615_0999-0962.prj',
        observed_dimensions_mm=[36.5, 21.3, 9.8],
        older_local_datasheet_dimensions_mm=[36.7, 21.1, 10.1],
        open_lever_dimensions_available=False,
        rule='SameSKU but closed model metadata differ from saved datasheet. Neither gives dimensioned hinge movement; do not replace prototype body/port datums from this table alone.')
    end = datetime.now(timezone.utc)
    result.update(source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
                  started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds())
    OUT.mkdir(parents=True, exist_ok=True); save(OUT/'stock.json', result)
    print('SOURCE_FAMILY_STOCK', len(rows), totals, result['HELU23802']['candidate_stock_m'], flush=True)


if __name__ == '__main__':
    main()
