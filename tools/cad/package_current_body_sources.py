"""Preserve six qualified source guides, NOT complete W5 or native selection."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    tick=time.monotonic();own={Path(__file__)}
    for tag in ('main-source','s1-output'):
        own.update(OUT/(tag+s+'.json') for s in ('-plan','-checks'))
    own.update(ROOT/'tools/cad'/n for n in ('plan_current_main_sources.py','check_current_main_sources.py','plan_current_s1_outputs.py','check_current_s1_outputs.py'))
    own.update(ROOT/'tests'/n for n in ('test_current_main_sources.py','test_current_s1_outputs.py'))
    pins={f.relative_to(ROOT).as_posix():SHA(f) for f in own};receipts={}
    for tag in ('main-source','s1-output'):
        p=json.loads((OUT/(tag+'-plan.json')).read_text());q=json.loads((OUT/(tag+'-checks.json')).read_text())
        assert not q['contacts'] and not q['errors'];assert not p['selected'] and not p['W5_complete']
        assert q['source_sha256'][(OUT/(tag+'-plan.json')).relative_to(ROOT).as_posix()]==SHA(OUT/(tag+'-plan.json'))
        for data in (p,q):
            for n,h in data.get('source_sha256',{}).items():
                assert SHA(ROOT/n)==h,n
                assert n not in pins or pins[n]==h,n
                pins[n]=h
        receipts[tag]=dict(routes=len(p['routes']),pairs=q['pairs'],worker_seconds=q['worker_seconds'],contacts=0,errors=0,
          head_poses=9,scope='Source guide clearance only; no connected service/mount/whole wiring acceptance')
    for f in (OUT/'mta-interface-manifest.json',OUT/'retained-mta-inputs.zip',BASE/'aux-wiring-checkpoint/retained-inputs.json',BASE/'aux-wiring-checkpoint/retained-inputs.zip'):
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    m=dict(status='SIX_SOURCE_GUIDES_SPACE_ONLY_NOT_W5_SELECTION',selected=False,W5_complete=False,physical_pass=False,
      result_count=11,fixed_total=20,percent=55,receipts=receipts,
      changed_purchased_poses=json.loads((OUT/'s1-output-plan.json').read_text())['changed_e2_heads'],
      changed_pose_scope='Two E2 locking heads static neighbours qualified; retain full bands. Current native pose/removal and swept-motion binding OPEN.',
      native_parts_created=0,STL_created=0,
      archive_recovery='Foreign historical inputs preserved by exact AUX48 and MTA1 archives; originals not committed.',
      open=['Two S1 input feeds, P_SYS/F_PI and S0/F0/battery/MAIN/Pi/ground source group',
            'Four MTA output continuations, remaining body/local and12leglooms',
            'Current12holder retention and all native independent grips/service/whole stock'],
      source_sha256=dict(sorted(pins.items())),verification_seconds=time.monotonic()-tick)
    (OUT/'source-guides-manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=m['status'],pins=len(pins),percent=55,verification_seconds=m['verification_seconds'])))
if __name__=='__main__':run()
