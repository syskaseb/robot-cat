"""Recover complete Cover/24end contribution and reject failed service paths.

The current shared R9 worker is pending, so no bank selection or service
qualification is inferred. Read only completed receipts and exact sources.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r26/manifest.json'
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
    cover=read('hardware/electronics/full-cat/servo-fuse-cover-main-service-r2/checks.json')
    assert len(cover['exports'])==1 and all(r['removed_mm3']<1e-5 for r in cover['mounts'])
    for r in cover['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    electrical=read('hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json')
    assert electrical['input_ends']==electrical['output_ends']==12 and len(electrical['ends'])==24
    prior=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r8/checks.json')
    assert prior['early_rejection'] and not prior['errors'] and prior['hits'][0]['owner']=='W045/extension'
    rejected=read('hardware/electronics/full-cat/servo-fuse-cover-main-service-r1/checks.json')
    assert rejected['state']['solids']==3
    for folder in ('servo-fuse-bank-fixed-rr-lift-r8','servo-fuse-cover-main-service-r1','servo-fuse-cover-main-service-r2','servo-fuse-bank-electrical-r2'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_cover_main_service_r1.py','servo_fuse_cover_main_service_r2.py','servo_fuse_bank_fixed_rr_lift_r9.py','servo_fuse_bank_electrical_r2.py'):
        add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='One segmented native Cover:1solid/BOP0/closedSTL/parameter/reopen,4mount zones retained; changed24end electrical receipt uses current2880mm inputs/3020mmLAPPtotal. Whole-wire/strap rectangle Cover3solids rejected, no fragment selected.',
        remaining=['WholeLiftR9 pending,49explicit service-tie cuts and actual stationary bodies/wires. Guard owns movingFR output cage; hand support required, not a fixedDeck cage.',
                   'One local choice/assembly/removal/stock/E3 contribution/commit still OPEN; fullE3 source/wholeW5 remain separate.',
                   'R51selected15/20=75%,bank NOT SELECTED.'])
    m['Cover_main_service']=dict(source='hardware/electronics/full-cat/servo-fuse-cover-main-service-r2/checks.json',exports=cover['exports'],mounts=cover['mounts'])
    m['electrical_current']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json',ends=24,E3_complete=False)
    m['whole_bank_release']=dict(status='PENDING_R9',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r9/checks.json',
        previous_rejected='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r8/checks.json',service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['gates']['geometry']=dict(status='open',reason='Complete segmentedCover and24ends; sharedR9pending.')
    m['gates']['service']=dict(status='open',reason='49tie release still requires actual joint result; no continuous path qualification.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r27';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('CONSTRUCTION_R27_SAVED_PENDING_SHARED_RELEASE',len(files),flush=True)

if __name__=='__main__':main()
