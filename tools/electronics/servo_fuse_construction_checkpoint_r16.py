"""Recover the matched rear source routes; RL native station remains open."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r15/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    for rev in (1,2):
        folder=ROOT/f'hardware/electronics/full-cat/servo-fuse-rl-source-complete-r{rev}'
        r=json.loads((folder/'checks.json').read_text(encoding='utf-8'))
        for rel,h in r['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for p in folder.iterdir():
            if p.suffix in ('.json','.brep'):files[p.relative_to(ROOT).as_posix()]=sha(p)
        script=ROOT/f'tools/electronics/servo_fuse_rl_source_complete_r{rev}.py'
        files[script.relative_to(ROOT).as_posix()]=sha(script)
    assert not r['hits'] and not r['errors'] and not r['factory_failures']
    assert r['pairs']==40
    rows={x['id']:x for x in r['routes']}
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,6,42,11,tzinfo=timezone.utc)).total_seconds(),
        completed='R15 native RR station preserved. Full RL sourceR2 factory/lap/sleeve/extension against actual RR sourceR8/nativeR4/front/retained owners:40pairs,0contacts,0errors,within nominal100mm factory PROJECT assumption. This replaces the rejected lower RL_R3 reference for the shared rear source routes, not a native RL station, full bank selection or physical PASS.',
        remaining=['RL native insulation grips, ties and any casing clearance are still OPEN; preserve complete RL_R2/RR_R8 source routes and native RR_R4.',
            'Remaining output routes/nativeWAGO grips, RR body-clip release/tool access, whole bank/cover/guard assembly-removal.',
            'One coherent selection/stock/E3 and local full-bank completion OPEN. R51 remains selected15/20=75%.'])
    m['rear_source_construction'].update(RR_reference_RL='servo-fuse-rl-source-complete-r2 (matched source route40pairs/0hits against current RR R4)',
        rear_routes_static_complete=True,RL_route='servo-fuse-rl-source-complete-r2',RL_native_station_complete=False,
        RL_known_contacts=0,RL_native_grips='PENDING',RL_factory_nominal_need_mm=rows['W044_factory']['minimum_blank_mm'],
        RL_HELU_blank_mm=rows['W044_extension']['stock_blank_mm'],RL_quantity_status='Contribution must be reconciled after native RL station; no selected stock mutation.')
    m['gates']['geometry']=dict(status='open',reason='Rear source routes statically clear together; RR native station exported. Native RL station, remaining feeds/grips and whole removal block full-bank selection.')
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r16';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),phase1_percent=75,rear_routes_static_complete=True,RL_native_complete=False)))
if __name__=='__main__':main()
