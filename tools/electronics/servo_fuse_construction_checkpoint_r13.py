"""Recover the shared-mount repair without treating native export as fit.

R2 failed attachment; R3 has twelve installed conflicts/two incomplete feet.
Include R4 actual evidence if received, otherwise record its source as pending.
Source-loop R5 is prepared and not a result unless checks.json exists.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r12/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    folders=['servo-fuse-rolled-cradles-native-r2','servo-fuse-rolled-cradles-native-r3',
             'servo-fuse-rolled-cradles-native-r4','servo-fuse-rolled-cradles-native-r5',
             'servo-fuse-rolled-cradles-native-r7','servo-fuse-rolled-source-loop-r5']
    reports={}
    for name in folders:
        folder=ROOT/'hardware/electronics/full-cat'/name
        report_path=folder/'checks.json'
        if report_path.exists():
            report=json.loads(report_path.read_text(encoding='utf-8'));reports[name]=report
            for p,h in report['source_sha256'].items():
                assert sha(ROOT/p)==h,p
                if p in files:assert files[p]==h,p
                files[p]=h
        if folder.exists():
            for q in folder.iterdir():
                if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for name in folders:
        cad=ROOT/'hardware/cad/studies'/name
        if cad.exists():
            for q in cad.iterdir():
                if q.suffix in ('.FCStd','.brep','.stl'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for name in ('servo_fuse_rolled_cradles_native_r2','servo_fuse_rolled_cradles_native_r3',
                 'servo_fuse_rolled_cradles_native_r4','servo_fuse_rolled_cradles_native_r5',
                 'servo_fuse_rolled_cradles_native_r6','servo_fuse_rolled_cradles_native_r7',
                 'servo_fuse_rolled_source_loop_r5','servo_fuse_construction_checkpoint_r13'):
        q=ROOT/f'tools/electronics/{name}.py';files[q.relative_to(ROOT).as_posix()]=sha(q)
    r3=reports['servo-fuse-rolled-cradles-native-r3']
    assert r3['native']['single_solid'] and r3['native']['strict_BOP_errors']==0
    assert len(r3['hits'])==12 and not r3['errors']
    assert sum(not row['full_bearing'] for row in r3['mounts'])==2
    r4=reports.get('servo-fuse-rolled-cradles-native-r4');r5=reports.get('servo-fuse-rolled-source-loop-r5')
    r7=reports['servo-fuse-rolled-cradles-native-r7']
    assert not r7['hits'] and not r7['errors'] and all(r['full_bearing'] for r in r7['mounts'])
    assert len(r7['mounts'])==6 and len(r7['straps'])==6
    assert all(r7['native'][p] for p in ('single_solid','closed_STL','relocated_reopen')) and r7['native']['strict_BOP_errors']==0
    cover_r7=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7/cover-checks.json').read_text(encoding='utf-8'))
    assert all(cover_r7[p] for p in ('single_solid','closed_STL','relocated_reopen')) and cover_r7['strict_BOP_errors']==0
    mount_r4_fault=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r4/fault.json').read_text(encoding='utf-8'))
    assert len(mount_r4_fault['hits'])==8 and not mount_r4_fault['errors']
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,3,56,58,tzinfo=timezone.utc)).total_seconds(),
        completed='R7 coherent mount/cover construction saved: all changed supports, six body ties and four native RR manual clips have0 exact static contacts/errors; all6 pedestal bearing slices complete on the actual augmented Deck. Valid editable Deck/Cover, strict BOP/one solid/closed STL/parameter restore/relocated reopen. Front single pedestal and RR PETG clip flex/creep remain prototype physical trials, not strength or physical PASS. R2 attachment/R3 twelve contacts/R4 eight contacts/R5 fourteen contacts retained as rejected evidence. Source-loop R5 is prepared, not a routing result unless its checks exist.',
        remaining=['RR clip release corridor/actual W042 and other fixed-wire conflicts, WAGO/native joint grips and strap insertion.',
                   'Shared mount/removal, one selected export/stock/E3 contribution/commit. LOCAL and W5 remain OPEN.'],
        current_reports={name:dict(status=r['status'],selected=r.get('selected',False),physical_pass=False) for name,r in reports.items()},
        rejected_mount_R4=dict(installed_contacts=8,mount_failures=4,native_export=False),
        prepared_sources=dict(shared_mount_R7='received static/native construction, not full bank selection/service or physical fit',
                              shared_mount_R6='definition only, superseded by R7; do not run rejected RR Y-loop concept',
                              W042_R5='result received' if r5 else 'definition validated only; now uses native R7 Deck/Cover'))
    m['gates']['geometry']=dict(status='open',reason='R7 shared support/clip static fit0 and valid native exports. Full source/fixed-wire fit, joint grips and shared service remain OPEN; no bank selection.')
    m['service_summary'].update(cradle_R3_installed_contacts=12,cradle_R3_mount_failures=2,
                               cradle_R4_complete=bool(r4),cradle_installed_contacts=0,
                               cradle_R7_complete=True,cradle_R7_mounts=6,cradle_R7_mount_failures=0,
                               RR_native_manual_clips=4,body_ties=6,W042_R5_complete=bool(r5),W5_complete=False)
    m['mount_construction_R7']=dict(selected=False,physical_pass=False,
        bench_sequence=['Use bare unpowered Deck before wiring/other modules obstruct its underside. Pre-thread6 T18I145mm ties under FL/FR/RL roofs.',
                        'Seat FL/FR/RL bodies at retained R3 datums; close two transverse ties per body. Check actual cable exits before final tightening.',
                        'Manually hold four RR clips outward, lower RR body onto its roof, release clips. Nominal0.4mm body/lip clearance is not a flex/strength qualification.',
                        'Prepare factory source/output ends and actual joint grips only after their remaining routing/assembly gates close. No bank selection from this local mount proof.'],
        remaining='Verify RR manual-release access, full bank-plus-cover removal and remaining real wire ends/grips. Do not independently lift the cover or reuse rejected parking geometry.',
        prototype_trials='Front cantilever stiffness, RR clip flex/creep/pull retention, actual MTA envelope/leads and tie insertion checked with delivered parts in phase2.')
    for p,h in files.items():assert sha(ROOT/p)==h,p
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r13';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),phase1_percent=75,selected=False,R4_received=bool(r4),R5_received=bool(r5))))


if __name__=='__main__':main()
