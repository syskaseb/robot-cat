"""Close only the local bank milestone after its actual R52 reconciliation."""
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
    def read(rel):
        p=ROOT/rel;add(p);j=json.loads(p.read_text(encoding='utf-8'))
        for name,h in j.get('source_sha256',{}).items():assert sha(ROOT/name)==h,name;add(ROOT/name)
        return j
    add(prev)
    lift=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r12/checks.json')
    assert not lift['hits'] and not lift['errors'] and lift['completed_clear_lifts_mm']==[2,5,10,30,60,100]
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r8/stock.json')
    assembly=read('hardware/electronics/full-cat/servo-fuse-bank-assembly-r7/assembly.json')
    selected=read('hardware/manufacturing/one-batch-prototype-r52/selection.json')
    reconciliation=read('hardware/manufacturing/one-batch-prototype-r52/local-bank-reconciliation.json')
    assert reconciliation['local_bank_complete'] and not reconciliation['W5_complete'] and reconciliation['phase1_completed_count']==15
    assert selected['local_fuse_bank_complete'] and selected['jobs']==76 and selected['installed_petg_parts']==115
    assert assembly['assembly_complete'] and stock['T18I']['local_installed_known']==53 and stock['T18I']['local_removal_replacement_allowance']==49
    for p in selected['prints']:assert sha(ROOT/p['stl'])==p['sha256'];add(ROOT/p['stl'])
    for folder in ('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r12','servo-fuse-bank-stock-budget-r8','servo-fuse-bank-assembly-r7','servo-fuse-cover-fixed-guard-service-r1'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for p in (ROOT/'hardware/manufacturing/one-batch-prototype-r52').glob('*.json'):read(p.relative_to(ROOT).as_posix())
    for name in ('servo_fuse_bank_select_r2.py','servo_fuse_bank_select_r3.py','servo_fuse_bank_stock_budget_r8.py','servo_fuse_bank_assembly_r7.py','servo_fuse_bank_fixed_rr_lift_r12.py','servo_fuse_cover_fixed_guard_service_r1.py'):
        add(ROOT/'tools/electronics'/name)
    cover=read('hardware/electronics/full-cat/servo-fuse-cover-fixed-guard-service-r1/checks.json')
    for row in cover['exports']:
        gp=ROOT/row['file'];add(gp);add(gp.parent/'Cover_WORLD.brep');add(gp.parent/'Cover_UNSELECTED.stl')
    m['Cover_main_service']=dict(source='hardware/electronics/full-cat/servo-fuse-cover-fixed-guard-service-r1/checks.json',exports=cover['exports'],mounts=cover['mounts'])
    add(Path(__file__))
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
      status='LOCAL_12_FUSE_BANK_COMPLETE_PHASE1_INCOMPLETE',local_bank_complete=True,selected=True,whole_selected_package='hardware/manufacturing/one-batch-prototype-r52/selection.json',
      completed='12holders/24ends/8mainfeeds/nativegrips/fixedchannel/cages/currentCover, one nominal assembly and six clear shared release poses. Six local prints selected into one R52 set with exact stock/fastener offers; no duplicated variants.',
      remaining=['WholeE3/source coordination, remaining wholeW5, K3material census, wholeA2/A3 are OPEN.',
        'Slicer/prints/purchase/physical fit,latch,PETG,crimp,thermal and continuous practical movement trials are phase2. No physical PASS.',
        'Whole phase1 remains15/20=75%; this local milestone is not a counter point.'])
    m['whole_bank_release']=dict(status=lift['status'],source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r12/checks.json',
        sampled_clear_lifts_mm=lift['completed_clear_lifts_mm'],service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['current_local_stock']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r8/stock.json',installed_ties=53,service_ties=49)
    m['gates']['geometry']=dict(status='complete_local_nominal',reason='Six native parts/oneR52printset with preserved mounts and actual changed interface checks.')
    m['gates']['service']=dict(status='complete_local_nominal_sampled',reason='Explicit49tie recipe, fixedGuard/wires, clear shared2/5/10/30/60/100mm; physical/continuous trialsphase2.')
    m['gates']['assembly']=dict(status='complete_local_nominal',reason='One assemblyR6, inverse shared removal; optional rewiring outside the local service proof.')
    m['gates']['stock']=dict(status='complete_local_contribution',reason='R52updates existing exact offers, counted once; wholeK3 remains OPEN.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r31';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('LOCAL_BANK_R31_COMPLETE',len(files),'PHASE1_15_OF_20',flush=True)
if __name__=='__main__':main()
