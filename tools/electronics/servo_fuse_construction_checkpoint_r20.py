"""Pin completed coupled rear native stations; never select a partial bank."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r19/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    add(previous)
    for rev in (1,2,3):
        script=ROOT/f'tools/electronics/servo_fuse_rear_output_stations_native_r{rev}.py';add(script)
        folder=ROOT/f'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r{rev}'
        q=folder/'preflight.json';j=json.loads(q.read_text(encoding='utf-8'))
        assert j['script_sha256']==sha(script)
        for rel,h in j['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
        for p in folder.iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    native=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/checks.json'
    j=json.loads(native.read_text(encoding='utf-8'));assert not j['hits'] and not j['errors'] and not j['mount_failures'] and not j['strict_BOP']
    assert j['script_sha256']==sha(ROOT/'tools/electronics/servo_fuse_rear_output_stations_native_r3.py')
    assert {r['tag'] for r in j['exports']}=={'Deck','BankRight','Cover','BankLeft'}
    for row in j['exports']:
        assert row['single_solid'] and row['closed_STL'] and row['relocated_reopen'] and row['strict_BOP_errors']==0
        gp=ROOT/row['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(row['tag']+suffix))
    assert len(j['stations'])==2 and len(j['ties'])==6 and sum(r['installed'] for r in j['ties'])==6
    add(native)
    if 'recovery' in j:
        recovery=j['recovery'];writer=ROOT/recovery['writer']
        assert sha(writer)==recovery['writer_sha256'];add(writer)
    for rel,h in j['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    for p in (ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-native-r3').iterdir():
        if p.suffix in ('.json','.brep','.FCStd','.stl'):add(p)
    parameter=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json'
    final=json.loads(parameter.read_text(encoding='utf-8'));assert len(final['exports'])==4
    assert all(r['parameter_mm']==[.2,.3,.2] and r['relocated_reopen'] for r in final['exports'])
    add(parameter);add(ROOT/'tools/electronics/servo_fuse_rear_output_stations_parameter_r4.py')
    for rel,h in final['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    for p in (ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-parameter-r4').iterdir():
        if p.suffix in ('.json','.brep','.FCStd','.stl'):add(p)
    materials=ROOT/'hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json'
    data=json.loads(materials.read_text(encoding='utf-8'));assert data['HELU23802']['nominal_blank_mm']==1190 and data['factory'] and len(data['factory'])==8
    add(materials);add(ROOT/'tools/electronics/servo_fuse_main_feeds_materials_r1.py')
    for rel,h in data['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,10,34,12,tzinfo=timezone.utc)).total_seconds(),
        completed='Coupled RL/RR output cages with four independent insulation seats and six straps, actual native Deck/Bank/left-head/Cover passages and complete unchanged input paths. Four native parents exported with BOP0, closedSTL, parameter/restore and relocated reopen. Main feed roles merged once. Static scope only, shared release/lever/whole stock still OPEN.',
        remaining=['Genuine access/lever operation for current WAGO and four native RR clips.',
            'Whole bank/guard/cover assembly and release using current fixtures, selected export/stock/E3.',
            'Full W5 and phase1 count unchanged: R51selected15/20=75%.'])
    m['rear_output_stations']=dict(source=native.relative_to(ROOT).as_posix(),exports=final['exports'],
        static_pairs=j['pairs'],contacts=0,full_anchor_proofs=j['feet'],new_straps=6,additional_prints=0,
        main_feed_materials=materials.relative_to(ROOT).as_posix(),selected=False,W5_complete=False,physical_pass=False)
    m['gates']['geometry']=dict(status='open',reason='Rear native station static scope complete; lever/clip access and shared removal remain open.')
    add(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r20';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=4,phase1_percent=75,selected=False)))
if __name__=='__main__':main()
