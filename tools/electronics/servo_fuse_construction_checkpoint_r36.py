"""Close only local bank after actual pair, R15 service and one R52 selection.

Whole phase1 remains fifteen of twenty. Physical gates remain open.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r35/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    def read(rel):
        add(ROOT/rel);j=json.loads((ROOT/rel).read_text(encoding='utf-8'))
        for p,h in j.get('source_sha256',{}).items():assert sha(ROOT/p)==h,p;add(ROOT/p)
        return j
    add(prev)
    liftpath='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r15/checks.json'
    lift=read(liftpath)
    assert not lift['hits'] and not lift['errors'] and lift['completed_clear_lifts_mm']==[2,5,10,30,60,100]
    stockpath='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r11/stock.json'
    stock=read(stockpath)
    assemblypath='hardware/electronics/full-cat/servo-fuse-bank-assembly-r10/assembly.json'
    assembly=read(assemblypath)
    selected=read('hardware/manufacturing/one-batch-prototype-r52/selection.json')
    reconciliation=read('hardware/manufacturing/one-batch-prototype-r52/local-bank-reconciliation.json')
    assert reconciliation['local_bank_complete'] and not reconciliation['W5_complete'] and reconciliation['phase1_completed_count']==15
    assert selected['local_fuse_bank_complete'] and selected['jobs']==76 and selected['installed_petg_parts']==115
    assert assembly['assembly_complete'] and stock['T18I']['local_installed_known']==53 and stock['T18I']['local_removal_replacement_allowance']==49
    assert next(q for q in reconciliation['added_fastener_roles'] if q['sku']=='00125202')['installed']==8
    for p in selected['prints']:assert sha(ROOT/p['stl'])==p['sha256'];add(ROOT/p['stl'])
    for p in (ROOT/'hardware/manufacturing/one-batch-prototype-r52').glob('*.json'):read(p.relative_to(ROOT).as_posix())
    for folder in ('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-stock-budget-r11','servo-fuse-bank-assembly-r10'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_bank_stock_budget_r11.py','servo_fuse_bank_assembly_r10.py','servo_fuse_bank_select_r6.py','servo_fuse_bank_fixed_rr_lift_r15.py'):add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),status='LOCAL_12_FUSE_BANK_COMPLETE_PHASE1_INCOMPLETE',
        local_bank_complete=True,selected=True,whole_selected_package='hardware/manufacturing/one-batch-prototype-r52/selection.json',
        completed='One local bank:12holders/24ends/8feeds/nativegrips/fixedchannel/currentCover/matched left foot and Deck; nominal assembly, six clear release poses and one reconciled print/stock selection.',
        remaining=['Whole W5/E3/K3/A2/A3 remain OPEN; local bank is not a counter point.',
          'Phase2: slicer/print/purchase/fit/latch/PETG/crimp/thermal and practical continuous movement. No physical PASS.'])
    m['whole_bank_release']=dict(source=liftpath,status=lift['status'],sampled_clear_lifts_mm=lift['completed_clear_lifts_mm'],service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['current_local_stock']=dict(source=stockpath,installed_ties=53,service_ties=49,bank_washers=8)
    m['local_assembly']=dict(source=assemblypath,complete=True,physical_pass=False)
    for gate in m['gates'].values():
        gate.update(status='open',reason='Local nominal bank complete; whole phase1 and applicable physical/continuous qualification are not complete.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r36';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('LOCAL_BANK_R36_COMPLETE',len(files),'PHASE1_15_OF_20',flush=True)
if __name__=='__main__':main()
