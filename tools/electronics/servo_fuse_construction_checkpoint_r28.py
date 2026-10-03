"""Preserve intact Cover and the actual rejected shared Guard motion."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r27/manifest.json'
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
    cover=read('hardware/electronics/full-cat/servo-fuse-cover-main-service-r6/checks.json')
    for r in cover['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    assert all(r['original_zone_removed_mm3']<1e-5 and r['bearing_removed_mm3']<1e-5 for r in cover['mounts'])
    lift=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r10/checks.json')
    assert len(lift['hits'])==1 and not lift['errors'] and lift['hits'][0]['part']=='FRReturnGuard'
    assert lift['hits'][0]['owner']=='RetainedFeed/W042_extension_DESIGN'
    for folder in ('servo-fuse-cover-main-service-r3','servo-fuse-cover-main-service-r5','servo-fuse-bank-fixed-rr-lift-r9','servo-fuse-bank-fixed-rr-lift-r10'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for name in ('servo_fuse_cover_main_service_r3.py','servo_fuse_cover_main_service_r4.py','servo_fuse_cover_main_service_r5.py','servo_fuse_cover_main_service_r6.py','servo_fuse_bank_fixed_rr_lift_r10.py'):add(ROOT/'tools/electronics'/name)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
      completed='Native intact CoverR6:1solid/BOP0/closedSTL/parameter/reopen, all original mount zones and bearing rings retained. Shared2mm Cover clear; moving Guard has an actual source-wire collision.',
      remaining=['Resolve Guard ownership/support as a complete interface; no more Cover changes needed for current2mm result.', 'One local export/assembly/stock/E3 contribution remains OPEN; R51selected15/20=75%, bank NOT SELECTED/W5OPEN.'])
    m['Cover_main_service']=dict(source='hardware/electronics/full-cat/servo-fuse-cover-main-service-r6/checks.json',exports=cover['exports'],mounts=cover['mounts'])
    m['whole_bank_release']=dict(status=lift['status'],source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r10/checks.json',hits=lift['hits'],service_ties_cut=49,continuous_withdrawal_qualified=False)
    m['gates']['geometry']=dict(status='open',reason='Intact Cover2mm clear; moving Guard collides with fixed FR source.')
    m['gates']['service']=dict(status='open',reason='Actual Guard/source collision88.258mm3 at2mm; no selected service sequence.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r28';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('CONSTRUCTION_R28_PRESERVED_GUARD_OPEN',len(files),flush=True)
if __name__=='__main__':main()
