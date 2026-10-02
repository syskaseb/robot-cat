"""Preserve completed native carrier attempts and changed lower cover/lift."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import sha,save


def main():
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r6'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r5/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent);reports={}
    for folder,script in [('servo-fuse-parent-carriers-r2','servo_fuse_parent_carriers_r2.py'),
                          ('servo-fuse-parent-carriers-r3','servo_fuse_parent_carriers_r3.py'),
                          ('servo-fuse-bank-lower-loop-lift-r1','servo_fuse_bank_lower_loop_lift_r1.py'),
                          ('servo-fuse-cover-native-r4','servo_fuse_cover_lower_wire_reliefs_r4.py'),
                          ('servo-fuse-bank-lower-loop-lift-r2','servo_fuse_cover_lower_wire_reliefs_r4.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/'checks.json';r=json.loads(p.read_text(encoding='utf-8'));reports[folder]=r
        code=ROOT/'tools/electronics'/script;assert sha(code)==r['script_sha256'];files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in r['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for folder in ('servo-fuse-parent-carriers-r2','servo-fuse-parent-carriers-r3','servo-fuse-cover-native-r4'):
        for q in (ROOT/'hardware/cad/studies'/folder).iterdir():
            if q.suffix in ('.FCStd','.stl','.brep','.json'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    native=reports['servo-fuse-cover-native-r4'];lift=reports['servo-fuse-bank-lower-loop-lift-r2']
    assert native['closed_STL'] and native['relocated_reopen'] and native['single_solid'] and len(native['cuts_mm'])==12
    assert not lift['hits'] and not lift['errors']
    failed=reports['servo-fuse-parent-carriers-r3'];assert len(failed['hits'])==20 and not failed['errors']
    now=datetime.now(timezone.utc);m.update(recorded_utc=now.isoformat(),started_utc='2026-10-02T21:54:42Z',
        elapsed_turn_seconds=(now-datetime(2026,10,2,21,54,42,tzinfo=timezone.utc)).total_seconds(),
        completed='R4 lower wire loops/ties retained. Two native independent parent-carrier constructions saved with4links/parameter/reopen/closedSTL, but failed fit and bearing retained as failures. CoverR4 adds12lower-lip reliefs, retained editable parent; conservative continuous100mm bank/cover lift over released input wires clear. This is not continuous flexible deformation, parent carrier acceptance or wholeW5.',
        remaining=['Parent carrierR3 still20contacts/4missing-bearing sites; earlierS contacts4feed tie tops, FR W066 and RR XS23. Do not repeat identical geometry.',
                   'All four source-side factory leads must reach actual P_FRONT/P_REAR mouths. Two opposite exits are visible in catalogue2016 page75, but L140 does not prove100mm per side.',
                   'Complete local assembly/removal with accepted parent mounts/leads; choose coherent Deck/bank/cover exports,4mLAPP/stock/E3 contribution and local completion commit. R51 still selected,75%.'])
    m['gates']['geometry']=dict(status='open',reason='CoverR4 native/lower-wire lift proof complete, but independent parent carriers have recorded20contacts and4incomplete bearings; not chosen.')
    m['gates']['service']=dict(status='open',reason='Changed cover clears conservative continuous100mm lift over stationary released R4 inputs; complete fixed parent mount/feed/module removal remains open.')
    m['service_summary'].update(lower_lip_reliefs=12,rigid_input_module_lift_mm=100,rigid_input_module_lift_contacts=0,parent_carrier_R3_contacts=20,parent_carrier_R3_missing_bearings=4)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())];save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False)),flush=True)


if __name__=='__main__':main()
