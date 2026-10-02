"""Save a scoped, explicitly incomplete construction checkpoint, not selection."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'manifest.json').exists()
    names=['servo-fuse-side-bank-r9','servo-fuse-bank-native-r5','servo-fuse-bank-outputs-r1',
           'servo-fuse-bank-restraints-r2','servo-fuse-bank-restraints-fit-r2','servo-fuse-cover-native-r3',
           'servo-fuse-cover-fit-r1']
    files={};reports={}
    for name in names:
        p=ROOT/'hardware/electronics/full-cat'/name/'checks.json'
        report=json.loads(p.read_text(encoding='utf-8'));reports[name]=report;files[p.relative_to(ROOT).as_posix()]=sha(p)
        for rel,h in report.get('source_sha256',{}).items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h
            files[rel]=h
        script=ROOT/'tools/electronics'/(name.replace('-','_')+'.py')
        if name=='servo-fuse-bank-restraints-fit-r2':script=ROOT/'tools/electronics/servo_fuse_bank_restraints_fit_r2.py'
        assert sha(script)==report['script_sha256'],script
        files[script.relative_to(ROOT).as_posix()]=sha(script)
    inputs=reports['servo-fuse-side-bank-r9'];outputs=reports['servo-fuse-bank-outputs-r1']
    assert inputs['input_routes']==12 and inputs['terminal_reserves']==24
    assert outputs['local_outputs']==12 and len({r['id'] for r in outputs['lengths']})==12
    assert all(any(re.fullmatch(r'F_(FL|FR|RL|RR)[123]\.out',p) for p in (r['a'],r['b'])) for r in outputs['lengths'])
    for n in names[:-1]:
        assert not reports[n].get('hits') and not reports[n].get('errors')
        assert not reports[n]['selected'] and not reports[n]['physical_pass']
    assert reports['servo-fuse-cover-fit-r1']['status']=='REJECTED' # No fabricated independent-cover removal PASS.
    assert all(b['missing_mm3']<1e-5 for b in reports['servo-fuse-bank-native-r5']['bearing_checks'])
    for folder in ['servo-fuse-bank-native-r5','servo-fuse-bank-restraints-r2','servo-fuse-cover-native-r3']:
        for p in (ROOT/'hardware/cad/studies'/folder).iterdir():
            if p.suffix in ('.FCStd','.brep','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in (ROOT/'tools/electronics').glob('servo_fuse_*.py'):
        if p.name in ('servo_fuse_inputs_r1.py','servo_fuse_inputs_r2.py','servo_fuse_flag_bank_r3.py'):continue
        # Own source chain, not unrelated inherited development scripts.
        if re.fullmatch(r'servo_fuse_(side_bank_r[6-9]|bank_native(?:_r[2-5])?|bank_outputs_r1|bank_restraints(?:_fit)?_r[12]|cover_native_r[123]|cover_fit_r1|cover_neighbors|construction_checkpoint)\.py',p.name):
            files[p.relative_to(ROOT).as_posix()]=sha(p)
    files['tools/electronics/servo_fuse_inputs_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_inputs_r1.py')
    gates={n:dict(status='open',reason='Local prototype construction only; phase1 interface not selected/complete.') for n in ('geometry','assembly','fit','petg','loads','electrical','service')}
    evidence='hardware/electronics/full-cat/servo-fuse-bank-restraints-r2/checks.json'
    gates['geometry']=dict(status='pass',reason='Limited native bank/output seats and cover: constrained features, valid single solids, strict BOP, parameter restore, relocated reopen and closed STL. Not whole-cat geometry.',evidence=[evidence,'hardware/electronics/full-cat/servo-fuse-cover-native-r3/checks.json'])
    gates['service']['reason']='Independent cover lift collided with bank panels. Modified bolt windows and connected skirt saved, but disconnected module removal not yet qualified.'
    now=datetime.now(timezone.utc)
    manifest=dict(schema_version=1,readiness='prototype',selected=False,physical_pass=False,W5_complete=False,
        phase1_completed=15,phase1_total=20,phase1_percent=75,parent_selected='one-batch-prototype-r51',
        completed='12 inputs/24 end reservations; actual four Deck bearing sites; two native bank parts with12local output spans and integral output seats; connected replacement-cover candidate; 127changed rest pairs clear.',
        remaining=['Input straight grip lengths and native strain relief.','All five physical cages of each rotated P-WAGO and other two feed roles.','Disconnected module assembly/removal and cover access.','Native selected Deck portals, one selected export/quantity/stock update.','Full leg moving spans remain W5; never count local output segments as whole leads.'],
        started_utc='2026-10-02T18:03:05Z',recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,2,18,3,5,tzinfo=timezone.utc)).total_seconds(),
        git_note='Only own source/current candidate geometry/evidence is committed. Inherited untracked caches stay unresolved for A3; this is not a clean-clone or print-ready claim.',
        gates=gates,files=[dict(path=p,sha256=h) for p,h in sorted(files.items())])
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),elapsed_turn_seconds=manifest['elapsed_turn_seconds'],phase1_percent=75,selected=False)))
if __name__=='__main__':main()
