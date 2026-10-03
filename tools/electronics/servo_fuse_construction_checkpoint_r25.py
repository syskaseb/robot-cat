"""Preserve the complete fixed FR source interface and actual bank release.

Require all three native exports. Record a real rejected release rather than
selecting a partial bank or awarding W5. No new hardware or wire geometry.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r24/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'))
    files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    def read(rel):
        p=ROOT/rel;add(p);j=json.loads(p.read_text(encoding='utf-8'))
        for name,h in j.get('source_sha256',{}).items():
            assert sha(ROOT/name)==h,name;add(ROOT/name)
        return j
    add(prev)
    fit=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r3/checks.json')
    assert not fit['hits'] and not fit['errors'] and len(fit['embeds'])==2
    assert all(r['full'] for r in fit['embeds'])
    native=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')
    assert len(native['exports'])==3 and native['source_ties_owner']=='FIXED_DECK'
    assert native['unchanged_source_grips_and_wires'] and native['bank_mounts_preserved']==4
    for r in native['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        assert r['shared_parameter']['allowance_mm']==[.25,.35,.25]
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    release=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r6/checks.json')
    assert release['extra_FR_source_ties_cut']==0 and not release['errors']
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r5/stock.json')
    assert stock['T18I']['local_installed_known']==49
    assert stock['T18I']['local_removal_replacement_allowance']==24
    for p in (ROOT/'tools/electronics').glob('servo_fuse_fr_source_fixed_deck_*.py'):add(p)
    for name in ('servo_fuse_bank_fixed_rr_lift_r5.py','servo_fuse_bank_fixed_rr_lift_r6.py','servo_fuse_bank_stock_budget_r5.py'):add(ROOT/'tools/electronics'/name)
    for folder in ('servo-fuse-fr-source-fixed-deck-r1','servo-fuse-fr-source-fixed-deck-r2',
                   'servo-fuse-fr-source-fixed-deck-r3','servo-fuse-fr-source-fixed-deck-native-r1',
                   'servo-fuse-fr-source-fixed-deck-native-r2','servo-fuse-bank-fixed-rr-lift-r6',
                   'servo-fuse-bank-stock-budget-r5'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    failed=ROOT/'hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r1/FRSourceFixedDeck.FCStd'
    if failed.exists():add(failed)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='Both unchanged FR source saddles/slots/ties transferred to native fixed Deck; full support profiles and matched BankRight/Cover passages. Three native parts1solid/BOP0/closedSTL/parameter roundtrip/relocated nested links,29changed pairs/0contacts. No added print/fastener/wire/tie.',
        remaining=['Whole common module release outcome is explicitly recorded below; no continuous qualification from isolated clear samples.',
                   'P-WAGO restraints/access, complete bank assembly/removal and one selection/stock/E3 contribution still OPEN.',
                   'R51 selected15/20=75%; local bank NOT SELECTED/W5 OPEN.'])
    m['fixed_FR_source']=dict(source='hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json',
        exports=native['exports'],static_fit='hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r3/checks.json',
        changed_pairs=fit['pairs'],contacts=0,source_ties_owner='FIXED_DECK',added_parts=0)
    m['whole_bank_release']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r6/checks.json',
        status='REJECTED' if release['hits'] else 'SAMPLES_CLEAR_CONTINUOUS_OPEN',
        first_contact=release['hits'][0] if release['hits'] else None,
        completed_clear_lifts_mm=release['completed_clear_lifts_mm'],Guard_owner='MOVING_BANK_WITH_4_FASTENERS',continuous_withdrawal_qualified=False)
    m['local_bank_materials'].update(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r5/stock.json',
        local_installed_ties=49,conditional_removal_replacements=24,
        condition='FR source loops remain fixed. Replace only24released terminal insulation ties. Local candidate, not selected stock.')
    m['gates']['geometry']=dict(status='open',reason='Fixed FR source interface completed; remaining WAGO and common assembly interfaces not closed.')
    m['gates']['service']=dict(status='open',reason=m['whole_bank_release']['status']+'; common full removal/access still requires final qualification.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r25';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=3,phase1_percent=75,whole_release=m['whole_bank_release']['status'])))

if __name__=='__main__':main()
