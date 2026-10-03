"""Recover the completed front-pair construction, not whole bank selection."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r13/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    names=[f'servo-fuse-rolled-source-loop-r{i}' for i in range(6,14)]+['servo-fuse-fr-source-corridor-solver-r1',
           'servo-fuse-front-source-ports-r1','servo-fuse-front-source-ports-r2','servo-fuse-fr-joint-station-native-r1',
           'servo-fuse-front-station-shared-fit-r1','servo-fuse-fr-return-guard-native-r1',
           'servo-fuse-fr-return-guard-native-r2','servo-fuse-fr-return-guard-native-r3']
    reports={}
    for name in names:
        folder=ROOT/'hardware/electronics/full-cat'/name
        check=folder/'checks.json'
        if check.exists():
            r=json.loads(check.read_text(encoding='utf-8'));reports[name]=r
            for p,h in r['source_sha256'].items():
                assert sha(ROOT/p)==h,p
                if p in files:assert files[p]==h,p
                files[p]=h
        for parent in (folder,ROOT/'hardware/cad/studies'/name):
            if parent.exists():
                for p in parent.iterdir():
                    if p.suffix in ('.json','.brep','.FCStd','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
    scripts=[f'servo_fuse_rolled_source_loop_r{i}' for i in range(6,14)]+['servo_fuse_fr_source_corridor_solver_r1',
             'servo_fuse_front_source_ports_r1','servo_fuse_front_source_ports_r2','servo_fuse_fr_joint_station_native_r1',
             'servo_fuse_front_station_shared_fit_r1','servo_fuse_fr_return_guard_native_r1',
             'servo_fuse_fr_return_guard_native_r2','servo_fuse_fr_return_guard_native_r3','servo_fuse_construction_checkpoint_r14']
    for name in scripts:
        p=ROOT/f'tools/electronics/{name}.py';files[p.relative_to(ROOT).as_posix()]=sha(p)
    station=reports['servo-fuse-fr-joint-station-native-r1'];shared=reports['servo-fuse-front-station-shared-fit-r1']
    guard=reports['servo-fuse-fr-return-guard-native-r3'];routes=reports['servo-fuse-front-source-ports-r2']
    assert not station['hits'] and not station['errors'] and not shared['hits'] and not shared['errors']
    assert not guard['hits'] and not guard['errors'] and guard['external_source_outside_guard_cavity_mm3']<1e-5
    assert not routes['errors'] and not routes['factory_failures']
    assert len(shared['inherited_other_feed_contacts'])==12
    assert all(x['single_solid'] and x['closed_STL'] and x['relocated_reopen'] and x['strict_BOP_errors']==0 for x in station['exports']+guard['exports'])
    assert m['phase1_completed']==15 and m['phase1_total']==20 and m['phase1_percent']==75 and not m['selected']
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,5,29,44,tzinfo=timezone.utc)).total_seconds(),
        completed='Front FL/FR source pair routed on the same retained block/body layout: project cages2/3 permuted within P_FRONT221-615, no topology/extra connector. Factory totals92.935/96.832mm within100mm project assumption, radii/strip/reserve retained. FR integral two-sided seats/native cover shared static fit0; removable side guard captures all source volume outsideX-98 with0 fixed-owner/hardware contacts. Editable bank/cover/guard,1solid/BOP0/closedSTL/parameter restore/reopen. Not whole-bank selection/service/physical PASS.',
        remaining=['Twelve known contacts of unchanged rear source/output feeds remain, other joint/WAGO grips and RR release/tool access.',
                   'Shared bank/cover/guard assembly-disconnection/removal, candidate quantity/stock/E3 contribution and one selected export. LOCAL and W5 remain OPEN.'],
        front_source_construction=dict(selected=False,physical_pass=False,
            routing='servo-fuse-front-source-ports-r2',joint_station='servo-fuse-fr-joint-station-native-r1',
            shared_fit='servo-fuse-front-station-shared-fit-r1',return_guard='servo-fuse-fr-return-guard-native-r3',
            same_net_cage_swap=True,additional_T18I=2,additional_prints=1,installed_M3x8=2,installed_M3nuts=2,
            selector_rule='When selecting whole bank, swap both P_FRONT.2/.3 ledger ends; replace BankRight with FRGuard native export, Cover with FRJointStation export, add Guard x1. Never select intermediate right-bank variants as extra prints.',
            quantities_rule='New roles reuse existing exact fastener SKUs, not free stock; reconcile installed/spare/purchase counts once at final selection.'),
        rejected_source_corridors=dict(R6='length/fixed contacts',R7_13='static contacts; preserve evidence, do not rerun',
            scalar_dx_solver='No clear offset at old137.5mm plane; same-net port permutation removes forced crossing.'),
        current_front_reports={name:dict(status=reports[name]['status'],selected=False,physical_pass=False) for name in names if name in reports})
    m['gates']['geometry']=dict(status='open',reason='Front source pair/native joint/guard static construction complete;12 remaining contacts of unchanged feeds and their grips/service prevent bank selection.')
    m['service_summary'].update(front_pair_static_complete=True,FR_native_two_sided_grips=2,FR_guard_static_complete=True,
                               retained_other_feed_contacts=12,FR_additional_ties=2,W5_complete=False)
    for p,h in files.items():assert sha(ROOT/p)==h,p
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r14';out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    save(out/'manifest.json',m);print(json.dumps(dict(pins=len(files),phase1_percent=75,selected=False,other_feed_contacts=12)))
if __name__=='__main__':main()
