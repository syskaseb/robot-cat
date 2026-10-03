"""Preserve valid native R8 Deck separately from its rejected installed layout."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r9/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent)
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r8'
    r=json.loads((folder/'checks.json').read_text(encoding='utf-8'))
    code=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r8.py'
    assert sha(code)==r['script_sha256']
    assert not r['native']['strict_BOP_report'] and r['native']['single_solid']
    assert r['native']['closed_STL'] and r['native']['relocated_reopen']
    assert len(r['hits'])==99 and not r['errors'] and r['pairs']==814
    for rel,h in r['source_sha256'].items():
        assert sha(ROOT/rel)==h,rel
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    for path in (folder,ROOT/'hardware/cad/studies/servo-fuse-parent-complete-layout-r8'):
        for q in path.iterdir():
            if q.suffix in ('.json','.brep','.FCStd','.stl'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    plan=ROOT/'tools/electronics/servo_fuse_main_space_plan_r1.py'
    files[plan.relative_to(ROOT).as_posix()]=sha(plan)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),
        elapsed_turn_seconds=(now-datetime(2026,10,3,2,6,44,tzinfo=timezone.utc)).total_seconds(),
        completed='R8 native Deck: strict BOP, restored parameter, closed one-component STL and relocated reopen verified. Installed shared layout REJECTED:99 contacts/814 checked pairs,0 calculation errors. No selected new bank.',
        remaining=['Receive sole whole-layout space planning worker; do not duplicate.',
            'One coherent four-main-holder layout with both factory exits, full source/output routes, native insulation/joint grips and modified cover where necessary.',
            'Complete bank removal with all fixed feeds, select one export, reconcile stock/E3 contribution and commit. HELU3m/LAPP4m still candidates;920mm legacy source not routed.'])
    m['gates']['geometry']=dict(status='open',reason='R8 native Deck valid but installed complete layout has99 actual contacts. It is not selected and does not close W5.')
    m['service_summary'].update(native_R8_topology_valid=True,
        R8_installed_layout_contacts=99,R8_installed_layout_pairs=814,
        native_parameter_restored=True,R8_worker_wall_seconds=r['worker_wall_seconds'])
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r10'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False,native_R8_valid=True,installed_contacts=99)))


if __name__=='__main__':main()
