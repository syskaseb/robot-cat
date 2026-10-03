"""Recoverable real new Guard interface; shared release R14 remains pending."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r30/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    add(prev)
    for folder in ('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r13','hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1','hardware/cad/studies/servo-fuse-guard-fixed-service-r1'):
        for p in (ROOT/folder).iterdir():
            if p.suffix in ('.json','.brep','.FCStd','.stl'):add(p)
    for n in ('servo_fuse_guard_fixed_service_r1.py','servo_fuse_bank_fixed_rr_lift_r13.py','servo_fuse_bank_fixed_rr_lift_r14.py','servo_fuse_bank_stock_budget_r9.py','servo_fuse_bank_stock_budget_r10.py','servo_fuse_bank_assembly_r8.py','servo_fuse_bank_assembly_r9.py','servo_fuse_bank_select_r4.py','servo_fuse_bank_select_r5.py','servo_fuse_construction_checkpoint_r32.py','servo_fuse_construction_checkpoint_r34.py'):add(ROOT/'tools/electronics'/n)
    guard=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1/checks.json').read_text(encoding='utf-8'))
    assert guard['exports'][0]['relocated_reopen'] and guard['exports'][0]['single_solid']
    for rel,h in guard['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        status='NATIVE_GUARD_LOCATOR_SERVICE_COMPLETE_SHARED_R14_PENDING',local_bank_complete=False,selected=False,
        completed='Existing stationary Guard receives native upward locator passage; output restraint below140mm and front M3 zone unchanged. Seven localBank/Guard poses clear; native1solid/BOP0/closedSTL/parameter/reopen. R13 failure at5mm retained.',
        remaining=['Receive soleR14 whole module release; no selection before all six poses clear. Then stockR10/assemblyR9/selectorR5/R52/checkpointR34/integrity/commit.',
          'R51 remains selected; phase1 remains15/20=75%, wholeW5/E3/K3/A2/A3 OPEN.'])
    m['Fixed_guard_service']=dict(source='hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1/checks.json',exports=guard['exports'],notch_mm=guard['notch_mm'],preserved=guard['preserved_zones'])
    m['whole_bank_release']=dict(status='R13_REJECTED_AT5MM_R14_PENDING',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r13/checks.json',continuous_withdrawal_qualified=False)
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r33';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m);print('RECOVERABLE_R33',len(files),flush=True)
if __name__=='__main__':main()
