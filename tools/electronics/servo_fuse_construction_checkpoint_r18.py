"""Recover actual complete FR approaches and all rejected output variants."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r17/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    for rev in range(1,6):
        add(ROOT/f'tools/electronics/servo_fuse_output_returns_complete_r{rev}.py')
        folder=ROOT/f'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r{rev}'
        j=json.loads((folder/'checks.json').read_text(encoding='utf-8'))
        assert j['script_sha256']==sha(ROOT/f'tools/electronics/servo_fuse_output_returns_complete_r{rev}.py')
        for rel,h in j['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
        for p in folder.iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    fr=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r3/checks.json').read_text(encoding='utf-8'))
    assert fr['pairs']==28 and not fr['hits'] and not fr['errors'] and not fr['factory_failures']
    assert fr['joints'][0]['same_face_and_tangents_asserted']
    for rev in range(1,5):
        add(ROOT/f'tools/electronics/servo_fuse_fr_output_station_native_r{rev}.py')
        old_station=ROOT/f'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r{rev}'
        for p in old_station.iterdir():
            if p.suffix in ('.json','.brep'):add(p)
        for p in (ROOT/f'hardware/cad/studies/servo-fuse-fr-output-station-native-r{rev}').iterdir():
            if p.suffix in ('.FCStd','.brep','.stl'):add(p)
    station=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r5'
    pre=json.loads((station/'checks.json').read_text(encoding='utf-8'))
    add(ROOT/'tools/electronics/servo_fuse_fr_output_station_native_r5.py')
    assert pre['script_sha256']==sha(ROOT/'tools/electronics/servo_fuse_fr_output_station_native_r5.py')
    for rel,h in pre['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    for p in station.iterdir():
        if p.suffix in ('.json','.brep'):add(p)
    native=None
    if (station/'checks.json').exists():
        result=json.loads((station/'checks.json').read_text(encoding='utf-8'))
        assert not result['hits'] and not result['errors']
        native=result['native']
        assert all(native[k] for k in ('single_solid','closed_STL','relocated_reopen')) and native['strict_BOP_errors']==0
        for p in (ROOT/'hardware/cad/studies/servo-fuse-fr-output-station-native-r5').iterdir():
            if p.suffix in ('.FCStd','.brep','.stl'):add(p)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,8,59,24,tzinfo=timezone.utc)).total_seconds(),
        completed='R17 rear native source stations retained. FR R3 full factory/extension approaches and same-face connector normals qualified in declared static scope,28pairs/0contacts. FR housing/independent grips native status is explicit below, not an assumption. Rejected R1/R2/R4 evidence retained. No full bank selection or physical PASS.',
        remaining=['RL/RR outputs cross actual retained fuse holders and feeds, not only modifiable casing. R1/R2/R4 rejected, do not repeat.',
            'Matched WAGO restraint/lever access, four RR clips and whole bank/cover/guard assembly-removal remain OPEN.',
            'One selected export/stock/E3/whole bank completion OPEN; R51 selected15/20=75%.'])
    m['output_construction']=dict(FR_routes='servo-fuse-output-returns-complete-r3',FR_static_pairs=28,
        FR_same_face_cage_tangents=True,FR_native=native,
        FR_native_preflight_contacts=len(pre['hits']),FR_native_preflight_errors=len(pre['errors']),
        rejected=dict(R1_contacts=17,R2_contacts=19,R2_wrong_connector_approach=True,R4_contacts=21),
        chosen_bank=False,W5_complete=False)
    m['gates']['geometry']=dict(status='open',reason='FR routes are clear; rear outputs/remaining native grips and whole removal block full selection. Known contacts are not waived.')
    add(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r18';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),phase1_percent=75,FR_native_complete=native is not None,selected=False)))
if __name__=='__main__':main()
