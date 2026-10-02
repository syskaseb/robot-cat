"""Keep rejected R3 and completed R4 lower-loop/tie evidence recoverable."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import sha,save


def main():
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r5'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    parent_path=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r4/manifest.json'
    manifest=json.loads(parent_path.read_text(encoding='utf-8'))
    files={r['path']:r['sha256'] for r in manifest['files']}
    files[parent_path.relative_to(ROOT).as_posix()]=sha(parent_path);reports={}
    for folder,script in [('servo-fuse-bank-connected-release-r3','servo_fuse_bank_connected_release_r3.py'),
                          ('servo-fuse-bank-connected-release-r4','servo_fuse_bank_connected_release_r4.py'),
                          ('servo-fuse-bank-lower-loop-ties-r1','servo_fuse_bank_lower_loop_ties_r1.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/'checks.json';report=json.loads(p.read_text(encoding='utf-8'));reports[folder]=report
        code=ROOT/'tools/electronics'/script;assert sha(code)==report['script_sha256'];files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in report['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    rejected=reports['servo-fuse-bank-connected-release-r3'];loops=reports['servo-fuse-bank-connected-release-r4'];ties=reports['servo-fuse-bank-lower-loop-ties-r1']
    assert len(rejected['hits'])==71 and not rejected['errors']
    assert not loops['hits'] and not loops['errors'] and not ties['hits'] and not ties['errors']
    assert len(loops['paths'])==60 and loops['sampled_fractions']==[0,.25,.5,.75,1]
    now=datetime.now(timezone.utc)
    manifest.update(recorded_utc=now.isoformat(),started_utc='2026-10-02T21:54:42Z',
        elapsed_turn_seconds=(now-datetime(2026,10,2,21,54,42,tzinfo=timezone.utc)).total_seconds(),
        completed='Native feed-grip Deck R2 retained. R3 lower vertical loops failed71 contacts and are preserved. R4 diagonal lower U: installed plus4release samples, equal length/R12.4,1390pairs/0hits/0errors. Shared fit of60wire shapes against20parent tie reserves:60intersecting pairs/0hits/0errors. No continuous deformation or whole-bank selection.',
        remaining=['Four independent parent holder carriers and both factory lead exits, exact source-side routes and lengths.',
                   'Complete bank/cover removal with all newly installed carriers/leads, native changed Deck/cover and one selected local export.',
                   'Bank inputs2880mm + W001140mm =3020mm, so4mLAPP candidate; previous3m not enough. Update stock/E3 and assembly with actual new lengths.',
                   'All20P-WAGO ports need one feasible assembly/removal order; loose prewiring is not in-situ lever access. WholeW5 remainsOPEN.'])
    manifest['gates']['service']=dict(status='open',reason='Five R4 lower-wire release poses clear with fixed upper fans and R12.4; changed ties clear. Complete bank/cover/parent carrier removal and source-side routes still open. Not continuous or physical qualification.')
    manifest['service_summary'].update(lower_loop_rejected_R3_contacts=71,lower_loop_R4_sampled_poses=5,
        lower_loop_R4_contacts=0,parent_tie_shared_contacts=0,continuous_wire_motion_qualified=False)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    manifest['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    save(out/'manifest.json',manifest);print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False)),flush=True)


if __name__=='__main__':main()
