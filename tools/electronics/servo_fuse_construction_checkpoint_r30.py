"""Recover matched intact Cover before the sole current shared lift finishes."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r29/manifest.json'
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
    cover=read('hardware/electronics/full-cat/servo-fuse-cover-fixed-guard-service-r1/checks.json')
    assert len(cover['exports'])==1
    assert all(r['original_zone_removed_mm3']<1e-5 and r['bearing_removed_mm3']<1e-5 for r in cover['mounts'])
    for row in cover['exports']:
        assert row['single_solid'] and row['strict_BOP_errors']==0 and row['closed_STL'] and row['relocated_reopen']
        gp=ROOT/row['file'];add(gp);add(gp.parent/'Cover_WORLD.brep');add(gp.parent/'Cover_UNSELECTED.stl')
    bad=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json')
    assert bad['hits'][0]['owner']=='FixedGuard' and not bad['errors']
    for folder in ('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-cover-fixed-guard-service-r1'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_bank_select_r2.py','servo_fuse_bank_select_r3.py','servo_fuse_bank_stock_budget_r8.py','servo_fuse_bank_assembly_r7.py',
                 'servo_fuse_bank_fixed_rr_lift_r12.py','servo_fuse_cover_fixed_guard_service_r1.py','servo_fuse_construction_checkpoint_r31.py'):
        add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='Matched Cover bottom-open side for entire fixedGuard:1solid/BOP0/closedSTL/parameter/reopen; all4original mounting zones and bearing rings unchanged. R11previous103.245mm3contact preserved, NOT an accepted service.',
        remaining=['R12shared exact-gap/common check is the ONLY active worker; receive first, do not duplicate.',
                   'Only after full clear6poses run stockR8/assemblyR7/selectorR3/R52/finalcheckpointR31/integrity/commit.',
                   'R51current15/20=75%,bank NOT SELECTED/W5OPEN.'])
    m['Cover_main_service']=dict(source='hardware/electronics/full-cat/servo-fuse-cover-fixed-guard-service-r1/checks.json',exports=cover['exports'],mounts=cover['mounts'])
    m['whole_bank_release']=dict(status='PENDING_R12',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r12/checks.json',service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['gates']['geometry']=dict(status='open',reason='Finished matched Cover/fixedGuard, whole sharedR12pending.')
    m['gates']['service']=dict(status='open',reason='Do not infer qualification from complete native exports.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r30';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('R30_MATCHED_NATIVE_COVER_RECOVERED_SHARED_PENDING',len(files),flush=True)
if __name__=='__main__':main()
