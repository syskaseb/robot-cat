"""Recoverable linked fixed-RR Deck and one material ledger; removal OPEN."""
from pathlib import Path
from datetime import datetime, timezone
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save


def main():
    previous = ROOT / 'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r21/manifest.json'
    m = json.loads(previous.read_text(encoding='utf-8'))
    files = {r['path']: r['sha256'] for r in m['files']}

    def add(p):
        rel = p.relative_to(ROOT).as_posix()
        h = sha(p)
        if rel in files:
            assert files[rel] == h, rel
        files[rel] = h

    def receive(rel):
        p = ROOT / rel
        add(p)
        j = json.loads(p.read_text(encoding='utf-8'))
        for name, h in j.get('source_sha256', {}).items():
            assert sha(ROOT / name) == h, name
            add(ROOT / name)
        return j

    add(previous)
    fixed = receive('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1/checks.json')
    preflight = receive('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r2/checks.json')
    assert not preflight['hits'] and not preflight['errors'] and preflight['bank_mounts_preserved'] == 4
    row = fixed['exports'][0]
    assert row['single_solid'] and row['strict_BOP_errors'] == 0 and row['closed_STL'] and row['relocated_reopen']
    assert row['local_mating_parameter']['parameter_mm'] == [.2, .3, .2]
    assert row['local_mating_parameter']['preflight_symmetric_difference_mm3'] < 1e-5
    gp = ROOT / row['file']
    for p in (gp, gp.parent / 'Deck_WORLD.brep', gp.parent / 'Deck_UNSELECTED.stl'):
        add(p)
    stock = receive('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r2/stock.json')
    assert stock['HELU23802']['qualified_nominal_blank_subtotal_mm'] == 1520
    assert stock['WAGO221412']['candidate_quantity'] == 6 and not stock['selected']
    for name in ('servo_fuse_rr_fixed_station_r2.py', 'servo_fuse_rr_fixed_station_native_r1.py',
                 'servo_fuse_bank_fixed_rr_lift_r1.py', 'servo_fuse_bank_stock_budget_r2.py'):
        add(ROOT / 'tools/electronics' / name)
    # Preserve the failed bank-foot split as failure, never select its geometry.
    for folder in ('servo-fuse-rr-fixed-station-r1', 'servo-fuse-rr-fixed-station-r2',
                   'servo-fuse-rr-fixed-station-native-r1'):
        for p in (ROOT / 'hardware/electronics/full-cat' / folder).iterdir():
            if p.suffix in ('.json', '.brep'):
                add(p)
    add(Path(__file__))
    now = datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),
        elapsed_turn_seconds=(now-datetime(2026, 10, 3, 13, 22, 51, tzinfo=timezone.utc)).total_seconds(),
        completed='Editable linked fixed RR output Deck:1solid/BOP0/closedSTL/local parameter restore/relocated external links. No additional print/fastener/wire/tie; original four bank mounts retained. Current material roles merged once, legacy source920mm explicitly unchecked.',
        remaining=['Receive current whole bank+Cover withdrawal with RR fixed on Deck; samples/continuous removal not yet qualified.',
                   'Remaining P-WAGO grips/access, complete local mounting/removal, stock/E3 contribution, one selected export.',
                   'R51 selected15/20=75%; local bank NOT SELECTED/W5 OPEN.'])
    m['fixed_RR_output'] = dict(source='hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1/checks.json',
        export=row, original_four_bank_mounts_preserved=True, entire_module_removal_qualified=False,
        rejected='Fixed-station-r1 severed the fourth bank foot; do not select/remove it blindly.')
    m['local_bank_materials'] = dict(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r2/stock.json',
        HELU_known_mm=1520, HELU_with_unchecked_legacy_reserve_mm=2440, LAPP_mm=3020,
        WAGO_candidate_quantity=6, selected=False, whole_stock_qualified=False)
    m['gates']['geometry'] = dict(status='open', reason='Fixed Deck export complete; shared bank removal/remaining grips not qualified.')
    m['gates']['service'] = dict(status='open', reason='Original bank restored with4mounts; earlier R21 removal/cage sequence is superseded, current shared lift PENDING.')
    for rel, h in files.items():
        assert sha(ROOT / rel) == h, rel
    m['files'] = [dict(path=p, sha256=h) for p, h in sorted(files.items())]
    out = ROOT / 'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r22'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'manifest.json').exists()
    save(out / 'manifest.json', m)
    print(json.dumps(dict(pins=len(files), phase1_percent=75, native_Deck_complete=True, removal_qualified=False)))


if __name__ == '__main__':
    main()
