"""Recover complete fixed-Deck Guard native parts; shared lift is pending."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r28/manifest.json'
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
    native=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json')
    assert native['Guard_owner']=='FIXED_DECK' and native['bank_unchanged'] and native['contacts']==0
    assert len(native['exports'])==2
    for r in native['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    for folder in ('servo-fuse-guard-fixed-deck-r1','servo-fuse-guard-fixed-deck-r2','servo-fuse-guard-fixed-deck-r3','servo-fuse-guard-fixed-deck-native-r1'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_guard_fixed_deck_r1.py','servo_fuse_guard_fixed_deck_r2.py','servo_fuse_guard_fixed_deck_r3.py','servo_fuse_guard_fixed_deck_native_r1.py',
                 'servo_fuse_bank_fixed_rr_lift_r11.py','servo_fuse_bank_stock_budget_r7.py','servo_fuse_bank_assembly_r6.py','servo_fuse_bank_select_r1.py'):add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
      completed='FixedDeck owns Guard/channel/FR output cage; exact2M3horizontal mounts with full rings, actual integral foot24mm3. NativeDeck/Guard1solid/BOP0/closedSTL/parameter/reopen; no added parts/wires/fasteners. NewDeck249.5mm with3mm/side brim.',
      remaining=['Shared liftR11 is PENDING; native parts are not yet selected, not fullW5.',
        'Prepared stockR7/assemblyR6/R52selector only run after full clear shared result. R51selected15/20=75%.'])
    m['fixed_Guard']=dict(source='hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json',exports=native['exports'],owner='Deck')
    m['whole_bank_release']=dict(status='PENDING_R11',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json',service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['gates']['geometry']=dict(status='open',reason='Completed fixedGuard interface; new complete shared lift pending.')
    m['gates']['service']=dict(status='open',reason='R11pending, not infer clearance from native exports or static test.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r29';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('CONSTRUCTION_R29_FIXED_GUARD_COMPLETE_SHARED_PENDING',len(files),flush=True)
if __name__=='__main__':main()
