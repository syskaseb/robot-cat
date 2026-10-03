"""Recover current native Cover and whole-release rejection, never hide it."""
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
    add(prev)
    for folder in ('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-fixed-rr-lift-r16','servo-fuse-cover-deck-edge-service-r2'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for p in (ROOT/'hardware/cad/studies/servo-fuse-cover-deck-edge-service-r2').iterdir():
        if p.suffix in ('.FCStd','.brep','.stl'):add(p)
    for n in ('servo_fuse_cover_deck_edge_service_r1.py','servo_fuse_cover_deck_edge_service_r2.py',
        'servo_fuse_bank_fixed_rr_lift_r16.py','servo_fuse_bank_fixed_rr_lift_r17.py',
        'servo_fuse_bank_inner_feed_service_r1.py','servo_fuse_bank_stock_budget_r12.py',
        'servo_fuse_bank_assembly_r11.py','servo_fuse_bank_select_r7.py','servo_fuse_construction_checkpoint_r38.py'):
        add(ROOT/'tools/electronics'/n)
    nativepath='hardware/electronics/full-cat/servo-fuse-cover-deck-edge-service-r2/checks.json'
    cover=json.loads((ROOT/nativepath).read_text(encoding='utf-8'))
    assert cover['subtractive_by_native_construction'] and cover['exports'][0]['relocated_reopen']
    for p,h in cover['source_sha256'].items():assert sha(ROOT/p)==h,p;add(ROOT/p)
    # Include complete inner passage when it has actually finished, never
    # partially changing native outputs of a running worker.
    innerpath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-inner-feed-service-r1/checks.json'
    inner=None
    if innerpath.exists():
        inner=json.loads(innerpath.read_text(encoding='utf-8'))
        assert inner['exports'][0]['relocated_reopen']
        for folder in (innerpath.parent,ROOT/'hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1'):
            for p in folder.iterdir():
                if p.suffix in ('.json','.FCStd','.brep','.stl'):add(p)
        for p,h in inner['source_sha256'].items():assert sha(ROOT/p)==h,p;add(ROOT/p)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,21,3,47,tzinfo=timezone.utc)).total_seconds(),
        status='COVER_EDGE_NATIVE_COMPLETE_R16_REJECTED_BANK_PASSAGE_IN_PROGRESS',local_bank_complete=False,selected=False,
        completed='Native left foot/Deck pair committed; native Cover edge retains mounts; R16 whole2/5mm clear, rejected BankRight/W042 at10mm. One entire factory-loop passage replaces a local-position notch.',
        remaining=['Receive native inner passage then wholeR17; only clear actual result permits stockR12/assemblyR11/selectorR7/checkpointR38.',
          'R51 remains selected;15/20=75%, W5/E3/K3/A2/A3 OPEN.'])
    m['current_cover']=dict(source=nativepath,exports=cover['exports'])
    m['current_bank_inner_passage']=dict(complete=inner is not None,source=innerpath.relative_to(ROOT).as_posix())
    m['whole_bank_release']=dict(status='R16_REJECTED_AT10MM_BANKRIGHT_W042_R17_PENDING',
        source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r16/checks.json',continuous_withdrawal_qualified=False)
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r37';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('RECOVERABLE_R37',len(files),flush=True)
if __name__=='__main__':main()
