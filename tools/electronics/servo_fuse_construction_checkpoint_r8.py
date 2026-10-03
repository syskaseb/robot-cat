"""Preserve complete routes/materials and R6's REJECTED native export.

R6 raised strict BOP before writing checks.json. Witness identities were
lost, so this checkpoint pins them as diagnostics, NOT shared-fit proof.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r8'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r7/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent)
    reports=[]
    for folder,name,script in [('servo-fuse-parent-extension-materials-r2','materials.json','servo_fuse_parent_extension_materials_r2.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/name;r=json.loads(p.read_text(encoding='utf-8'))
        code=ROOT/'tools/electronics'/script;assert sha(code)==r['script_sha256']
        files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in r['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
        reports.append(r)
    materials=reports[0]
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r6'
    failure=json.loads((folder/'native-failure.json').read_text(encoding='utf-8'))
    intent=json.loads((folder/'intent.json').read_text(encoding='utf-8'))
    assert failure['status']=='REJECTED_NATIVE_BOP' and len(intent['routes'])==12
    assert not (folder/'checks.json').exists()
    for q in folder.iterdir():
        if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    witnesses=len(list(folder.glob('HIT_*.brep')));assert witnesses==98
    assert materials['red_4mm2_additional_rough_blank_mm']==1080
    for q in (ROOT/'hardware/cad/studies/servo-fuse-parent-complete-layout-r6').iterdir():
        if q.suffix in ('.FCStd','.stl','.brep','.json'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for folder in ('servo-fuse-parent-complete-layout-r5','servo-fuse-parent-extension-materials-r1'):
        for q in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    fact=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json';files[fact.relative_to(ROOT).as_posix()]=sha(fact)
    for name in ('servo_fuse_parent_complete_layout_r5.py','servo_fuse_parent_complete_layout_r6.py','servo_fuse_parent_extension_materials_r1.py'):
        code=ROOT/'tools/electronics'/name;files[code.relative_to(ROOT).as_posix()]=sha(code)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,2,23,39,31,tzinfo=timezone.utc)).total_seconds(),
        completed='One coherent4MTA layout with both exits and all8feeds/12wire sections; local1080mm extension blanks and exact selected TE3/8 sleeve contribution. R6 native Deck export REJECTED by strict BOP;98 contact witness files preserved without missing pair identities. No complete shared-fit report or native PASS. R51 unchanged.',
        remaining=['R7 active repair: union overlapping tie tools instead of Compound; no automatic refinement in new operations. Save strict validation before shared-fit and contact identities incrementally. R6 export must not be selected.',
                   'Rear output uses9mm explicit trim reserve/rough100; factory100/side still provisional, not supplied-length proof.',
                   'Separate rear bareCu/core and actual selected TE3/8 sleeve are modelled; add complete native joint/WAGO restraints and service access.',
                   'Then full module mount/disconnect/removal and one selected export/stock/E3/commit. WholeW5 not complete.'])
    m['gates']['geometry']=dict(status='open',reason='R6 strict BOP REJECTED;98 diagnostic witness files, identities/count not recoverable from absent checks.json. Joints/grips/service and selection unfinished.')
    m['service_summary'].update(parent_complete_R6_contacts=None,parent_complete_R6_native_status='REJECTED_NATIVE_BOP',
        parent_complete_R6_witness_files=witnesses,complete_feed_count=8,wire_section_count=12,additional_4mm2_blanks_mm=1080)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())];save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),native_status=failure['status'],diagnostic_witnesses=witnesses,phase1_percent=75,selected=False)))


if __name__=='__main__':main()
