"""Recover the coupled rear routes and matched native passages, no selection."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r18/manifest.json'
    m=json.loads(previous.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[previous.relative_to(ROOT).as_posix()]=sha(previous)
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    for rev in (6,7,8):
        script=ROOT/f'tools/electronics/servo_fuse_output_returns_complete_r{rev}.py';add(script)
        folder=ROOT/f'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r{rev}'
        j=json.loads((folder/'checks.json').read_text(encoding='utf-8'));assert j['script_sha256']==sha(script)
        for rel,h in j['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
        for p in folder.iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    r=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8/checks.json').read_text(encoding='utf-8'))
    casing={'CandidateDeck','ModifiableCover','Bank/RightClipAccessFinished_WORLD',
        'hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.brep'}
    assert not r['errors'] and not r['factory_failures'] and all(h['owner'] in casing for h in r['hits'])
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-reliefs-native-r1'
    # Run only after receiving the worker: do not pin a changing CAD file.
    q=folder/'checks.json';j=json.loads(q.read_text(encoding='utf-8'))
    assert len(j['parts'])==4
    for row in j['parts']:
        assert all(row[k] for k in ('single_solid','closed_STL','relocated_reopen'))
        assert row['strict_BOP_errors']==0 and all(v<1e-5 for v in row['channel_contacts_mm3'].values())
    scripts=['servo_fuse_rear_output_reliefs_native_r1.py','servo_fuse_output_quantity_contribution_r1.py']
    for name in scripts:add(ROOT/'tools/electronics'/name)
    for root in (folder,ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1',
        ROOT/'hardware/electronics/full-cat/servo-fuse-output-quantity-contribution-r1'):
        for p in root.iterdir():
            if p.suffix in ('.json','.brep','.FCStd','.stl'):add(p)
        if root==folder:
            for rel,h in j['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,9,59,58,tzinfo=timezone.utc)).total_seconds(),
        completed='Coupled rear outputR8 preserves four main bodies/factory clear routes, valid same-face cages.113pairs,9PETG-only contacts; no wire/terminal/purchased-part contacts. Four native matched passages remove these contacts, retain source history and have closedSTL/parameter/reopen proofs. All3FR straps included. No whole-bank selection/grip/service or physicalPASS.',
        remaining=['Native output WAGO housing and independent insulation grips still OPEN, including RL/RR.',
            'Native support load paths, lever access, four RR clips and whole shared bank/cover/guard assembly-removal OPEN.',
            'Single selected export/stock/E3 and full W5 still OPEN. R51 selected15/20=75%.'])
    m['rear_output_construction']=dict(routes='servo-fuse-output-returns-complete-r8',
        static_pairs=r['pairs'],prior_PETG_contacts=len(r['hits']),actual_fixed_contacts=0,
        native_parts=j['parts'],rejected=dict(R6_contacts=12,R7_contacts=19,R7_factory_failure=True),
        quantity_contribution='servo-fuse-output-quantity-contribution-r1/checks.json',
        output_HELU_blank_mm=530,replaces_previous_mm=440,whole_stock_selected=False,
        chosen_bank=False,W5_complete=False,physical_pass=False)
    m['gates']['geometry']=dict(status='open',reason='Rear routes/passages complete in static scope; matched native grips/supports and shared removal still block selection.')
    add(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r19';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=4,phase1_percent=75,selected=False)))
if __name__=='__main__':main()
