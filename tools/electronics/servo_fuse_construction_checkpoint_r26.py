"""Pin completed body straps/Cover and the rejected alternative, not a bank.

Whole release R8 remains pending and is intentionally not pinned mid-write.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r25/manifest.json'
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
    cover=read('hardware/electronics/full-cat/servo-fuse-cover-rr-fixed-service-r1/checks.json')
    assert len(cover['exports'])==1
    for r in cover['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    wago=read('hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3/checks.json')
    assert len(wago['blocks'])==4 and wago['static_contacts']==0 and not wago['errors']
    for r in wago['blocks']:
        for rel in r['geometry']:add(ROOT/rel)
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r6/stock.json')
    assert stock['T18I']['local_installed_known']==53 and stock['T18I']['local_removal_replacement_allowance']==33
    prior=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r7/checks.json')
    assert prior['early_rejection'] and not prior['errors'] and prior['output_cage_and_insulation_ties_cut']==9
    rejected=read('hardware/electronics/full-cat/servo-fuse-bank-stationary-strap-corridors-r1/checks.json')
    assert rejected['part_counts']['Cover']['solids']==3 and not rejected['mounts_preserved']
    for folder in ('servo-fuse-p-wago-retention-r1','servo-fuse-p-wago-retention-r2','servo-fuse-p-wago-retention-r3',
                   'servo-fuse-bank-fixed-rr-lift-r7','servo-fuse-cover-rr-fixed-service-r1',
                   'servo-fuse-bank-stationary-strap-corridors-r1','servo-fuse-bank-stock-budget-r6'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_bank_current_owner_receive.py','servo_fuse_bank_stationary_strap_corridors_r1.py',
                 'servo_fuse_p_wago_retention_r1.py','servo_fuse_p_wago_retention_r2.py','servo_fuse_p_wago_retention_r3.py',
                 'servo_fuse_bank_fixed_rr_lift_r7.py','servo_fuse_bank_fixed_rr_lift_r8.py',
                 'servo_fuse_cover_rr_fixed_service_r1.py','servo_fuse_bank_stock_budget_r6.py'):
        add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='Four P-WAGO body ties use8existing native slots. Retain3clearR1 straps and clear changedRL_R2; all20ports/16conductors bench-first, strap cut before lever action. Conservative lever conflicts explicitly retained. Cover RR existing station opening extends to lower edge;1solid/BOP0/closedSTL/parameter/reopen;0newprints.',
        remaining=['WholeLiftR8 pending: fixed new Cover/WAGO straps and33explicit service-tie cuts. Do not select the bank before its actual result.',
                   'One complete local assembly/removal, selection/stock/E3 contribution/commit still OPEN.',
                   'R51 selected15/20=75%; bank NOT SELECTED/W5 OPEN.'])
    m['P_WAGO_retention']=dict(source='hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3/checks.json',
        body_ties=4,existing_native_slots=8,static_contacts=0,ports=20,connected=16,NC=4,lever_access='BENCH_FIRST_REMOVE_STRAP_BEFORE_OPENING_NOT_IN_SITU_QUALIFIED')
    m['Cover_RR_bottom_service']=dict(source='hardware/electronics/full-cat/servo-fuse-cover-rr-fixed-service-r1/checks.json',exports=cover['exports'])
    m['whole_bank_release']=dict(status='PENDING_R8',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r8/checks.json',
        previous_rejected='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r7/checks.json',service_ties_cut=33,continuous_withdrawal_qualified=False)
    m['local_bank_materials'].update(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r6/stock.json',
        local_installed_ties=53,conditional_removal_replacements=33,condition='Service33candidateuntilsharedR8accepted; replace existing4P-WAGO global roles, never add them twice.')
    m['gates']['geometry']=dict(status='open',reason='Completed four current body straps and native Cover replacement; sharedR8pending.')
    m['gates']['service']=dict(status='open',reason='Changed Cover lower opening and33tie release not yet jointly qualified.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r26';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('CONSTRUCTION_R26_SAVED_PENDING_SHARED_RELEASE',len(files),flush=True)

if __name__=='__main__':main()
