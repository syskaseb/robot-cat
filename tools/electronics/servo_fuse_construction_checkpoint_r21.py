"""Pin completed clip sequence and matched RR service Bank/Cover.

Keep R51 selected, count75%, bank/W5 OPEN. RR parking is the next coupled
interface, never silently treat its pending preflight as selected geometry.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r20/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    def receive(rel):
        p=ROOT/rel;add(p);j=json.loads(p.read_text(encoding='utf-8'))
        for name,h in j.get('source_sha256',{}).items():assert sha(ROOT/name)==h,name;add(ROOT/name)
        return j
    add(previous)
    clips=receive('hardware/electronics/full-cat/servo-fuse-rr-clip-approach-r2/checks.json')
    assert len(clips['probes'])==4 and not clips['hits'] and not clips['errors'] and clips['removed_module_before_tool_access']
    service=receive('hardware/electronics/full-cat/servo-fuse-rr-output-service-receive-r6/checks.json')
    assert len(service['exports'])==2 and not service['hits'] and not service['errors']
    assert service['assumptions']['opening_degrees']==90 and not service['actual_manufacturer_lever_motion_qualified']
    for row in service['exports']:
        assert row['single_solid'] and row['closed_STL'] and row['relocated_reopen'] and row['parameter_mm']==[.2,.3,.2]
        gp=ROOT/row['file'];add(gp)
        tag='BankRight' if row['final']=='RROutputServiceFinished' else 'Cover'
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(tag+suffix))
    for name in ('servo_fuse_rr_clip_approach_r1.py','servo_fuse_rr_clip_approach_r2.py',
                 'servo_fuse_rr_output_disconnect_r1.py','servo_fuse_rr_output_disconnect_r2.py',
                 *[f'servo_fuse_rr_output_service_native_r{k}.py' for k in range(1,6)],
                 'servo_fuse_rr_output_service_receive_r6.py','servo_fuse_rr_output_park_r1.py'):
        add(ROOT/'tools/electronics'/name)
    folders=['servo-fuse-rr-clip-approach-r1','servo-fuse-rr-clip-approach-r2',
        'servo-fuse-rr-output-disconnect-r1','servo-fuse-rr-output-disconnect-r2',
        *[f'servo-fuse-rr-output-service-native-r{k}' for k in range(1,6)],
        'servo-fuse-rr-output-service-receive-r6']
    for name in folders:
        for p in (ROOT/'hardware/electronics/full-cat'/name).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    add(ROOT/'tools/electronics/servo_fuse_bank_assembly_r5.py')
    add(ROOT/'hardware/electronics/full-cat/servo-fuse-bank-assembly-r5/assembly.json')
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,11,55,8,tzinfo=timezone.utc)).total_seconds(),
        completed='Four RR clip tools and separate outward envelopes clear AFTER bank+Cover removal; no PETG action claim. Current BankRight/Cover receive open outward RR cage corridor and supported frame. Two editable native parents, BOP0/closedSTL/numeric parameter restore/reopen. No added prints/fasteners/installed straps.',
        remaining=['RR housing withdrawal/parking with both wire routes stationary and matched support/casing, current joint module removal.',
            'Missing remaining restraint/quantity/source protection contributions, one selected local bank export/stock/E3/commit.',
            'R51 selected15/20=75%; bank NOT SELECTED/W5 OPEN.'])
    m['rr_output_service']=dict(source='hardware/electronics/full-cat/servo-fuse-rr-output-service-receive-r6/checks.json',exports=service['exports'],
        three_changed_access_pairs=0,bridge_pairs=service['bridge_pairs'],assumptions=service['assumptions'],selected=False,physical_pass=False)
    m['rr_clip_access']=dict(source='hardware/electronics/full-cat/servo-fuse-rr-clip-approach-r2/checks.json',conditional='AFTER bank+Cover removed, not a pre-lift operation',physical_deflection_qualified=False)
    m['gates']['geometry']=dict(status='open',reason='Matched RR service parts complete; housing parking/shared current module release and selected local bank still OPEN.')
    add(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r21';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=2,phase1_percent=75,selected=False)))
if __name__=='__main__':main()
