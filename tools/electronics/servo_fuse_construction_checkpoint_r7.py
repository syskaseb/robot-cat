"""Preserve R4 carrier failure and completed local material accounting."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r7'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r6/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent)
    for folder,name,script in [('servo-fuse-parent-carriers-r4','checks.json','servo_fuse_parent_carriers_r4.py'),
                               ('servo-fuse-lower-loop-materials-r1','materials.json','servo_fuse_lower_loop_materials_r1.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/name;r=json.loads(p.read_text(encoding='utf-8'))
        code=ROOT/'tools/electronics'/script;assert sha(code)==r['script_sha256'];files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in r['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
        if name=='checks.json':
            assert len(r['hits'])==34 and not r['errors'] and not r['access_hits']
            assert sum(v['missing_mm3']>1e-5 for v in r['bearing_checks'])==2
        else:assert r['stock']['nominal_required_mm']==3020 and r['stock']['candidate_metres']==4
    for q in (ROOT/'hardware/cad/studies/servo-fuse-parent-carriers-r4').iterdir():
        if q.suffix in ('.FCStd','.stl','.brep','.json'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,2,21,54,42,tzinfo=timezone.utc)).total_seconds(),
        completed='CoverR4/input liftR2 retained and committed: continuous100mm rigid lift clear. CandidateR4 parent carriers retain34contacts and2incomplete bearings as FAILED, although native4links/reopen/STL valid. Material report accounts for12longer blanks plusW001,3020mm and candidate4m; copper length sensitivity only, not E3 acceptance.',
        remaining=['Replace the partial parent layout with ONE coherent layout of four holders, both opposite exits and actual source/output mouths. R4 foot-only relocation failed: rearP_AUX/G_TAIL, ground shelf, own wires, W066/XS23 and cover; do not repeat.',
                   'Factory100mm/side remains provisional; catalogueL140 does not prove it. Any necessary extension must have its own identified component/wire/restraint and stock, not an invented long factory lead.',
                   'Then finish native shared Deck/cover, module removal/assembly, one selected export and stock/E3 contribution. R51 still selected; wholeW5 not complete.'])
    m['gates']['geometry']=dict(status='open',reason='R4 carriers34contacts/2missing bearings; not chosen. Completed CoverR4/input lift proof retained.')
    m['service_summary'].update(parent_carrier_R4_contacts=34,parent_carrier_R4_missing_bearings=2)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())];save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False)))


if __name__=='__main__':main()
