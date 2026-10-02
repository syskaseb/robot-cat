"""Preserve completed changed interfaces and failed proposals, not selection."""
from pathlib import Path
from datetime import datetime, timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r4'


def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'manifest.json').exists()
    parent_path=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r3/manifest.json'
    parent=json.loads(parent_path.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in parent['files']}
    files[parent_path.relative_to(ROOT).as_posix()]=sha(parent_path)
    reports={}
    for folder,script in [('servo-fuse-wago-access-r2','servo_fuse_wago_access_r2.py'),
                          ('servo-fuse-bank-connected-release-r2','servo_fuse_bank_connected_release_r2.py'),
                          ('servo-fuse-parent-feeds-r1','servo_fuse_parent_feeds_r1.py'),
                          ('servo-fuse-parent-feed-grips-native-r1','servo_fuse_parent_feed_grips_native_r1.py'),
                          ('servo-fuse-parent-feed-grips-native-r2','servo_fuse_parent_feed_grips_native_r2.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/'checks.json';meta=json.loads(p.read_text(encoding='utf-8'));reports[folder]=meta
        code=ROOT/'tools/electronics'/script;assert sha(code)==meta['script_sha256'],code
        files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in meta['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for folder in ('hardware/reference/wago-221415-access-2026-10-02',
                   'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r1',
                   'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r1',
                   'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2'):
        for q in (ROOT/folder).iterdir():
            if q.suffix in ('.json','.pdf','.png','.brep','.FCStd','.stl'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    files['tools/electronics/servo_fuse_bank_connected_release_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_connected_release_r1.py')
    native=reports['servo-fuse-parent-feed-grips-native-r2'];feeds=reports['servo-fuse-parent-feeds-r1'];access=reports['servo-fuse-wago-access-r2']
    assert native['grips']==4 and native['through_slots']==8 and native['closed_STL'] and native['relocated_reopen']
    assert not native['hits'] and not native['errors']
    assert access['hits'] and len(access['ports'])==20 and not access['actual_lever_motion_qualified']
    assert feeds['hits'] and not feeds['errors']
    assert not any(h['part'].endswith(('_WIRE','_GRIP')) for h in feeds['hits'])
    assert reports['servo-fuse-bank-connected-release-r2']['hits']
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    now=datetime.now(timezone.utc);manifest=dict(parent)
    manifest.update(recorded_utc=now.isoformat(),started_utc='2026-10-02T20:34:11Z',
        elapsed_turn_seconds=(now-datetime(2026,10,2,20,34,11,tzinfo=timezone.utc)).total_seconds(),
        completed='Four provisional factory parent lead paths and four local grooves are clear inR1; holder carriers failed and are not selected. NativeDeckR1 added4editable feed grips/8through tie slots but2tie contacts remained. NativeR2 extends only the RL upper slot and moves the FR tie head; retained history, parameter/strictBOP/relocated reopen/closedSTL proof. ManufacturerWAGO family images preserved; all20 nominal lever sectors checked, actual hinge dimensions remain unknown.',
        remaining=['FourMTA holder carriers/body locations and BOTH factory lead exits must be settled; R1 outboard shelves hit cover/front brackets/source hardware and are rejected.',
                   'Installed P-WAGO lever sectors contactXB22/XL07/MAIN/XA04. Loose-connector prewiring is an assembly premise, not in-situ service qualification.',
                   'Connected input releaseR2 preserves length/radius but has20contacts; do not rerun that pose. R1 solver bracket interrupted and its midpoint checks were not persisted.',
                   'Resolve one assembly/removal order, choose coherent local export, stock3mLAPP/36newties/E3 assumptions and local completion commit. WholeW5 remainsOPEN.'],
        files=[dict(path=p,sha256=h) for p,h in sorted(files.items())])
    manifest['gates']=dict(parent['gates'])
    manifest['gates']['geometry']=dict(status='pass',reason='Limited nativeDeckR2 change only: four feed grooves and eight tie portals, including RL upper slot extension and movedFRhead; changed tie reserves clear. This does not pass failed holder carrier sites or installed lever access.',evidence=['hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2/checks.json'])
    manifest['gates']['service']=dict(status='open',reason='37nominal lever-sector contacts; connected equal-length input release failed20contacts. No in-situ service or continuous cable motion claimed.')
    manifest['service_summary']=dict(provisional_WAGO_sectors=20,WAGO_contacts=len(access['hits']),
         connected_release_contacts=len(reports['servo-fuse-bank-connected-release-r2']['hits']),
         native_feed_grips=4,feed_ties_clear=not native['hits'],physical_lever_verified=False)
    manifest['files'].append(dict(path=Path(__file__).relative_to(ROOT).as_posix(),sha256=sha(Path(__file__))))
    save(OUT/'manifest.json',manifest)
    print(json.dumps(dict(files=len(manifest['files']),selected=False,phase1_percent=75,elapsed_turn_seconds=manifest['elapsed_turn_seconds'])),flush=True)


if __name__=='__main__':main()
