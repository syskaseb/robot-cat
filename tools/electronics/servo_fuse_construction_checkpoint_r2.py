"""Recoverable local input-grip/port checkpoint; bank still not selected."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r2'
def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'manifest.json').exists()
    parent_path=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r1/manifest.json'
    parent=json.loads(parent_path.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in parent['files']}
    files[parent_path.relative_to(ROOT).as_posix()]=sha(parent_path)
    reports={}
    pairs=[('servo-fuse-side-bank-r10','checks.json','servo_fuse_side_bank_r10.py'),
           ('servo-fuse-side-bank-r11','checks.json','servo_fuse_side_bank_r11.py'),
           ('servo-fuse-bank-restraints-r3','checks.json','servo_fuse_bank_restraints_r3.py'),
           ('servo-fuse-bank-input-fit-r1','checks.json','servo_fuse_bank_input_fit_r1.py'),
           ('servo-fuse-wago-map-r1','interface.json','servo_fuse_wago_map_r1.py'),
           ('servo-fuse-holder-release-r1','checks.json','servo_fuse_holder_release_r1.py'),
           ('servo-fuse-ato-access-r1','checks.json','servo_fuse_ato_access_r1.py')]
    for folder,filename,scriptname in pairs:
        p=ROOT/'hardware/electronics/full-cat'/folder/filename;meta=json.loads(p.read_text(encoding='utf-8'));reports[folder]=meta
        script=ROOT/'tools/electronics'/scriptname;assert sha(script)==meta['script_sha256'],script
        files[script.relative_to(ROOT).as_posix()]=sha(script)
        for rel,h in meta['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for folder in ('servo-fuse-bank-restraints-r3',):
        for p in (ROOT/'hardware/cad/studies'/folder).iterdir():
            if p.suffix in ('.FCStd','.brep','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    assert len(reports['servo-fuse-side-bank-r10']['hits'])==1
    assert len(reports['servo-fuse-bank-restraints-r3']['hits'])==1
    for name in ('servo-fuse-side-bank-r11','servo-fuse-bank-input-fit-r1','servo-fuse-holder-release-r1','servo-fuse-ato-access-r1'):
        assert not reports[name]['hits'] and not reports[name]['errors'],name
    assert reports['servo-fuse-wago-map-r1']['all_ports']==20
    now=datetime.now(timezone.utc);manifest=dict(parent)
    manifest.update(recorded_utc=now.isoformat(),started_utc='2026-10-02T19:15:06Z',
        elapsed_turn_seconds=(now-datetime(2026,10,2,19,15,6,tzinfo=timezone.utc)).total_seconds(),
        completed='Twelve input straight grips8/10mm and integral native seats; two bank STL with no extra print count; corrected one XT60 witness and one tie-head witness. All20 P-WAGO cages mapped,16 connections/four NC. Necessary holder lift and continuous ATO20mm cover clearance saved.',
        remaining=['Four parent factory feeds W026/W037/W045/W053 and WAGO lever/end restraints.',
                   'Native Deck worker may still be running; do not duplicate. Export only after actual receipt.',
                   'Real latch/tool access and end parking, disconnected bank+cover removal, final mounting order.',
                   'Stock/E3 length update and one selected export/quantities. Local bank is not complete W5.'],
        files=[dict(path=p,sha256=h) for p,h in sorted(files.items())])
    manifest['gates']['geometry']=dict(status='pass',reason='Limited native bank/input/output seats and cover, strict BOP, parameter restore, relocated reopen, closed STL. Corrected route/head contacts have explicit separate evidence. Not whole-cat/complete service.',
        evidence=['hardware/electronics/full-cat/servo-fuse-bank-restraints-r3/checks.json','hardware/electronics/full-cat/servo-fuse-bank-input-fit-r1/checks.json','hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json'])
    manifest['gates']['service']=dict(status='open',reason='Necessary holder/ATO lift clearance is not full latch/tool access or module withdrawal. Old independent-cover lift remains rejected; do not assume TE input can pull downward past an insulation backer.')
    manifest['stock_candidate']=reports['servo-fuse-wago-map-r1']['stock']
    filescript=Path(__file__).relative_to(ROOT).as_posix();manifest['files'].append(dict(path=filescript,sha256=sha(Path(__file__))))
    save(OUT/'manifest.json',manifest)
    print(json.dumps(dict(files=len(manifest['files']),selected=False,phase1_percent=75,elapsed_turn_seconds=manifest['elapsed_turn_seconds'])),flush=True)
if __name__=='__main__':main()
