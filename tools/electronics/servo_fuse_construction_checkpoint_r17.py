"""Recover both native rear source stations, without full-bank selection."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r16/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    for rev in range(1,6):
        script=ROOT/f'tools/electronics/servo_fuse_rl_source_station_native_r{rev}.py'
        files[script.relative_to(ROOT).as_posix()]=sha(script)
        folder=ROOT/f'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r{rev}'
        if not folder.exists():continue
        for p in folder.iterdir():
            if p.suffix not in ('.json','.brep'):continue
            if p.suffix=='.json':
                for rel,h in json.loads(p.read_text(encoding='utf-8')).get('source_sha256',{}).items():
                    assert sha(ROOT/rel)==h,rel
                    if rel in files:assert files[rel]==h,rel
                    files[rel]=h
            files[p.relative_to(ROOT).as_posix()]=sha(p)
    station=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r5/checks.json'
    s=json.loads(station.read_text(encoding='utf-8'))
    assert not s['hits'] and not s['errors'] and s['additional_T18I']==2
    assert s['script_sha256']==sha(ROOT/'tools/electronics/servo_fuse_rl_source_station_native_r5.py')
    assert all(r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen'] for r in s['exports'])
    assert all(abs(r['foot_shared_bearing_mm2']-22)<1e-5 for r in s['seats'])
    for p in (ROOT/'hardware/cad/studies/servo-fuse-rl-source-station-native-r5').iterdir():
        if p.suffix in ('.FCStd','.brep','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
    quantity=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-quantity-contribution-r1/checks.json'
    q=json.loads(quantity.read_text(encoding='utf-8'))
    assert not q['selected'] and q['HELU23802']['replacement_blank_mm']==120
    for rel,h in q['source_sha256'].items():
        assert sha(ROOT/rel)==h,rel
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    files[quantity.relative_to(ROOT).as_posix()]=sha(quantity)
    tool=ROOT/'tools/electronics/servo_fuse_rl_source_quantity_contribution_r1.py'
    assert q['script_sha256']==sha(tool);files[tool.relative_to(ROOT).as_posix()]=sha(tool)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,6,42,11,tzinfo=timezone.utc)).total_seconds(),
        completed='Matched RL_R2/RR_R8 rear source routes retained. Native RL_R5 insulation seats with22mm2 full Deck foot/XA05 passage and2T18I, parameter change/restore, single-solid strictBOP0/closedSTL/relocated reopen. RR_R4 remains inherited. This is a conditional prototype construction, not full bank selection or physical PASS.',
        remaining=['Output routes W037/W045/W053 and native WAGO grips/lever qualification remain OPEN.',
            'Four RR body clips/tool access and whole bank/cover/guard assembly-removal remain OPEN.',
            'One coherent selection/stock/E3/local full-bank completion OPEN. R51 remains selected15/20=75%.'])
    m['rear_source_construction'].update(RL_native_station_complete=True,RL_native_grips='servo-fuse-rl-source-station-native-r5',
        RL_quantity_status='One additive candidate; HELU110->120mm,+2ties,+0prints/fasteners, retained lap/sleeve. Not selected stock.',
        RL_native_exports=s['exports'],rear_native_stations_complete=True)
    m['gates']['geometry']=dict(status='open',reason='Rear source routes and native stations clear in declared static scope. Remaining feeds/grips and whole removal block full-bank selection.')
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r17';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),phase1_percent=75,rear_native_stations_complete=True,selected=False)))
if __name__=='__main__':main()
