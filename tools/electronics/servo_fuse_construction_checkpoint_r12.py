"""Recoverable construction checkpoint, not a selected or physically passed bank."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r11/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    folders=['servo-fuse-rolled-cradles-native-r1','servo-fuse-rolled-full-feeds-r1',
             'servo-fuse-rolled-output-wago-r2','servo-fuse-rolled-output-wago-r3',
             'servo-fuse-rolled-source-loop-r4','servo-fuse-feed-reliefs-native-r2',
             'servo-fuse-feed-reliefs-native-r3','servo-fuse-feed-reliefs-native-r4','servo-fuse-feed-reliefs-native-r5','servo-fuse-feed-reliefs-native-r6']
    reports={}
    for name in folders:
        folder=ROOT/'hardware/electronics/full-cat'/name
        if (folder/'checks.json').exists():
            report=json.loads((folder/'checks.json').read_text(encoding='utf-8'));reports[name]=report
            for p,h in report['source_sha256'].items():
                assert sha(ROOT/p)==h,p
                if p in files:assert files[p]==h,p
                files[p]=h
        else:assert name in ('servo-fuse-feed-reliefs-native-r2','servo-fuse-feed-reliefs-native-r3','servo-fuse-feed-reliefs-native-r4','servo-fuse-feed-reliefs-native-r5') and ((folder/'fault.json').exists() or (folder/'bridge-fit.json').exists())
        for q in folder.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for name in ('servo-fuse-rolled-cradles-native-r1','servo-fuse-feed-reliefs-native-r6'):
        for q in (ROOT/'hardware/cad/studies'/name).iterdir():
            if q.suffix in ('.FCStd','.brep','.stl'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    scripts=['servo_fuse_rolled_cradles_native_r1','servo_fuse_rolled_full_feeds_r1',
             'servo_fuse_rolled_output_wago_r2','servo_fuse_rolled_output_wago_r3',
             'servo_fuse_rolled_source_loop_r4','servo_fuse_feed_reliefs_native_r2',
             'servo_fuse_feed_reliefs_native_r3','servo_fuse_feed_reliefs_native_r4','servo_fuse_feed_reliefs_native_r5','servo_fuse_feed_reliefs_native_r6','servo_fuse_construction_checkpoint_r12']
    for name in scripts:
        q=ROOT/f'tools/electronics/{name}.py';files[q.relative_to(ROOT).as_posix()]=sha(q)
    cradle=reports['servo-fuse-rolled-cradles-native-r1']
    outputs=reports['servo-fuse-rolled-output-wago-r3']
    feeds=reports['servo-fuse-rolled-source-loop-r4']
    relief=reports['servo-fuse-feed-reliefs-native-r6']
    assert cradle['native']['single_solid'] and cradle['native']['strict_BOP_errors']==0
    assert len(cradle['hits'])==44 and not cradle['errors']
    assert not outputs['factory_failures'] and not feeds['factory_failures']
    assert not outputs['errors'] and not feeds['errors']
    assert len(feeds['routes'])==15 and len(feeds['joints'])==7
    assert all(p['single_solid'] and p['strict_BOP_errors']==0 and p['closed_STL'] and p['relocated_reopen']
               and p['changed_feed_contacts']==0 for p in relief['parts'])
    assert len(relief['parts'])==2
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,2,50,1,tzinfo=timezone.utc)).total_seconds(),
        completed='Native candidate cradles/Deck export saved but44 installed contacts REJECTED. Four distinct WAGO output joints remove output-wire intersections; all8factory feeds within100mm DESIGN ASSUMPTION with strip/rework reserves. W042 source high hairpin replaced by a west-side route. Actual editable cover/BankRight reliefs saved, exact changed-feed contacts0; parameter/reopen/strictBOP/closedSTL. Not a selected complete bank.',
        remaining=['One coherent supported layout correcting cradle44 contacts and remaining fixed-wire/source conflicts, with real joint/WAGO grips and strap insertion.',
                   'Shared removal with changed native cover/bank and all fixed feeds, selected export/stock/E3 contribution/commit. W5 and LOCAL remain OPEN.'],
        superseded='Full-feeds-r1 four output inline laps had same-direction wire approaches: rejected; commercial221412 cages replace them. Feed-reliefs-r2 conservative witness BBoxes overcut cover into3solids. Contact-sized R3 still disconnected lower lip. R4/R5 ribs contact existing bracket. Failed evidence retained; R6 adds a bracket-specific native rib notch with0.5mm nominal clearance, exact changed-feed/rib fit checks, without moving holder layout.')
    m['gates']['geometry']=dict(status='open',reason='Native cover and bank reliefs valid. Full installed cradle/feed fit and service remain OPEN; R1 supports44 contacts, source-loopR4 retains32 contacts against old cover/bank/remaining owners, not a shared updated assembly proof.')
    m['service_summary'].update(cradle_installed_contacts=44,all_factory_lead_assumptions_fit=True,
        complete_feeds_R4_contacts=len(feeds['hits']),native_feed_cover_bank_reliefs=True,
        new_relief_feed_contacts=0,cover_R2_disconnected_rejected=True,W5_complete=False,
        cradle_mount_check_note='R1 compares whole-foot common volume to bottom0.2mm overlap: excess contact is not absent bearing. Three excess-volume flags need bottom-slice interpretation on next changed supports; FRfoot1 actually has only0.09mm3 vs3.6mm3 expected.')
    for p,h in files.items():assert sha(ROOT/p)==h,p
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r12'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),phase1_percent=75,selected=False,native_reliefs=2,full_bank_complete=False)))


if __name__=='__main__':main()
