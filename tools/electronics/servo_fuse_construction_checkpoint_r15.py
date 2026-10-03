"""Recover the complete candidate RR source station, retaining open RL/W5.

This is construction evidence, not a newly selected prototype or print
release. Pin only new changed sources/results plus the inherited snapshot.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r14/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    names=[f'servo-fuse-rear-source-pair-r{i}' for i in range(1,7)]+[
        'servo-fuse-rr-source-complete-r7','servo-fuse-rr-source-complete-r8',
        'servo-fuse-rr-source-station-native-r1','servo-fuse-rr-source-station-native-r2','servo-fuse-rr-source-station-native-r3','servo-fuse-rr-source-station-native-r4',
        'servo-fuse-rr-source-quantity-contribution-r1']
    reports={}
    for name in names:
        folder=ROOT/'hardware/electronics/full-cat'/name
        for check in ('checks.json','grips-fit.json','support-preflight.json'):
            p=folder/check
            if p.exists():
                r=json.loads(p.read_text(encoding='utf-8'));reports[name+'/'+check]=r
                for rel,h in r['source_sha256'].items():
                    assert sha(ROOT/rel)==h,rel
                    if rel in files:assert files[rel]==h,rel
                    files[rel]=h
        for parent in (folder,ROOT/'hardware/cad/studies'/name):
            if parent.exists():
                for p in parent.iterdir():
                    if p.suffix in ('.json','.brep','.FCStd','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
        script=ROOT/'tools/electronics'/(name.replace('-','_')+'.py')
        files[script.relative_to(ROOT).as_posix()]=sha(script)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    pending_rl=ROOT/'tools/electronics/servo_fuse_rl_source_complete_r1.py'
    files[pending_rl.relative_to(ROOT).as_posix()]=sha(pending_rl)
    station=reports['servo-fuse-rr-source-station-native-r4/checks.json']
    route=reports['servo-fuse-rr-source-complete-r8/checks.json']
    assert not station['hits'] and not station['errors'] and not route['errors'] and not route['factory_failures']
    assert all(h['owner']=='RetainedCover' for h in route['hits'])
    assert all(r['single_solid'] and r['closed_STL'] and r['relocated_reopen'] and r['strict_BOP_errors']==0 for r in station['exports'])
    assert m['phase1_completed']==15 and m['phase1_total']==20 and m['phase1_percent']==75 and not m['selected']
    rows={r['id']:r for r in route['routes']};rl_status=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8/RL-status.json'
    rl=json.loads(rl_status.read_text(encoding='utf-8'));assert not rl['accepted']
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,6,42,11,tzinfo=timezone.utc)).total_seconds(),
        completed='Candidate RR source W052: full factory route and HELU extension, opposed8mm bare lap/26mm RNF100 sleeve, two4mm straight insulation grips,2T18I, one native Deck/casing replacement. Changed static fit clear against retained owners/front and complete lower RL R3 candidate. RL R3 is still rejected. Factory99.906mm including strip8/reserve10 within100mm PROJECT assumption; HELU160mm blank. Native editable sources, strictBOP0/1solid/closedSTL/parameter restore/relocated reopen. Not whole-bank selection, service or physical PASS.',
        remaining=['RL source is OPEN: lower complete R3 candidate has known retained-owner contacts. RR was checked against it but this does not qualify RL or a whole rear pair.',
                   'Remaining output routes/nativeWAGO grips, RR body-clip release/tool access, whole bank/cover/guard assembly-removal.',
                   'One coherent selection/stock/E3 and local full-bank completion still OPEN. R51 remains selected15/20=75%.'],
        rear_source_construction=dict(selected=False,physical_pass=False,RR_static_complete=True,RL_static_complete=False,
            RR_route='servo-fuse-rr-source-complete-r8',RR_station='servo-fuse-rr-source-station-native-r4',
            RR_reference_RL='servo-fuse-rear-source-pair-r3 (REJECTED self-consistent construction candidate only)',
            RR_factory_nominal_need_mm=rows['W052_factory']['minimum_blank_mm'],RR_factory_assumption_mm=100,
            native_RR_grip_centres_mm={r['role']:r['grip_centre_mm'] for r in station['seats']},
            grip_metadata_rule='Native R4 station supersedes route R8 extension grip by1mm along existing straight insulation, not a route/end/length change. Extension4mm seat abuts the nominal sleeve end; real shrinking/end tolerance is phase2.',
            RR_HELU_blank_mm=rows['W052_extension']['stock_blank_mm'],additional_T18I=2,additional_prints=0,
            selector_rule='Replace candidate Deck with RRSourceStation and Cover with RRSourceStation; retain accepted front/FRGuard BankRight/Guard. Do not select intermediate Deck/Cover variants as additional prints.',
            quantity_rule='Two new installed T18I roles, replace existing RR extension cut length with160mm, retain existing one26mm sleeve/lap. Reconcile installed/spare/stock only when full bank selected; no free hardware or duplicated sleeve.',
            RL_known_contacts=len(rl['fixed_contacts'])))
    m['gates']['geometry']=dict(status='open',reason='Front preserved and native RR source station static clear in declared candidate scope. RL and remaining feeds/grips/whole removal block full bank selection.')
    m['service_summary'].update(RR_source_static_complete=True,RR_additional_ties=2,RL_source_static_complete=False,W5_complete=False)
    for p,h in files.items():assert sha(ROOT/p)==h,p
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r15';out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    save(out/'manifest.json',m);print(json.dumps(dict(pins=len(files),phase1_percent=75,selected=False,RR_complete=True,RL_complete=False)))
if __name__=='__main__':main()
