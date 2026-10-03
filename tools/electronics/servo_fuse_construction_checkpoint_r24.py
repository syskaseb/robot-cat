"""Pin completed twelve upper clamps, their actual fit, and open FR service.

Do not select the bank or award W5. Preserve rejected attempts explicitly.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r23/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    def read(rel):
        p=ROOT/rel;add(p);j=json.loads(p.read_text(encoding='utf-8'))
        for name,h in j.get('source_sha256',{}).items():assert sha(ROOT/name)==h,name;add(ROOT/name)
        return j
    add(prev)
    native=read('hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r3/checks.json')
    assert len(native['exports'])==2 and len(native['openings'])==12
    for r in native['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        assert r['parameter_mm']==[0,.2,0]
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    fit=read('hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1/checks.json')
    assert fit['checked_clamps']==12 and not fit['hits'] and not fit['errors']
    release=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r4/checks.json')
    assert release['early_rejection'] and len(release['hits'])==1 and not release['errors']
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r4/stock.json')
    assert stock['T18I']['local_installed_known']==49 and stock['T18I']['local_removal_replacement_allowance']==26
    for name in ('servo_fuse_output_rib_exits_native_r1.py','servo_fuse_output_rib_exits_native_r2.py',
                 'servo_fuse_output_rib_exits_native_r3.py','servo_fuse_output_clamps_fit_r1.py',
                 'servo_fuse_bank_fixed_rr_lift_r3.py','servo_fuse_bank_fixed_rr_lift_r4.py','servo_fuse_bank_stock_budget_r4.py'):
        add(ROOT/'tools/electronics'/name)
    for folder in ('servo-fuse-output-rib-exits-native-r1','servo-fuse-output-rib-exits-native-r2',
                   'servo-fuse-output-rib-exits-native-r3','servo-fuse-output-clamps-fit-r1',
                   'servo-fuse-bank-fixed-rr-lift-r3','servo-fuse-bank-fixed-rr-lift-r4'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    prior=read('hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r1/checks.json')
    for r in prior['exports']:
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='Twelve bottom-open upper insulation keepers replace old lower seats on both native bank sides. Same12T18I loops cinch upward, all planning insulation contact surfaces retained.62changed pairs/0contacts/0errors. Both parts1solid/BOP0/closedSTL/parameter roundtrip/relocated nested links; no new print/fastener/wire/tie.',
        remaining=['Shared module liftR4 rejected at2mm:old FRExtensionSeat binds stationary W042 extension,15.40007156mm3. Transfer BOTH source grips to fixed Deck with actual supports and open-edge bank passage; keep source routes.',
                   'P-WAGO restraints, whole bank mount/removal, one selection/stock/E3 contribution still OPEN.',
                   'R51 selected15/20=75%; local bank NOT SELECTED/W5 OPEN.'])
    m['output_clamps']=dict(source='hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r3/checks.json',
        exports=native['exports'],static_fit='hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1/checks.json',
        changed_pairs=fit['pairs'],contacts=0,clamps=12,replacement_output_loops=12,added_installed_ties=0)
    m['whole_bank_release']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r4/checks.json',
        status='REJECTED',first_contact=release['hits'][0],Guard_owner='MOVING_BANK_WITH_4_FASTENERS',continuous_withdrawal_qualified=False)
    m['local_bank_materials'].update(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r4/stock.json',
        local_installed_ties=49,conditional_removal_replacements=26,
        condition='If FR source grips become fixed on Deck, their2ties stay installed and allowance returns to24. No stock selection yet.')
    m['gates']['geometry']=dict(status='open',reason='Completed upper keepers/installed tie fit; whole source grip owner transfer still needed.')
    m['gates']['service']=dict(status='open',reason='Fixed source wire binds bank-mounted FR seat at2mm; shared complete module removal NOT qualified.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r24';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=2,phase1_percent=75,whole_release='REJECTED')))

if __name__=='__main__':main()
