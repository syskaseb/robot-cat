"""Select the complete nominal MAIN positive interface, not all of W5."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
from main_positive_wiring_card_r1 import OUT,SCREEN,NATIVE,build_selection
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r43'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r44'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (BATCH/'manifest.json').exists()
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    card=read(OUT/'interface.json');native=read(NATIVE/'checks.json')
    for path,h in card['source_sha256'].items():assert sha256(ROOT/path)==h
    assert native['candidate_checks_sha256']==sha256(SCREEN/'checks.json')
    runs=[];tick=time.monotonic()
    for pattern in ['test_main_positive_wiring_card.py','test_assembly_tools_k3_r2.py','test_termination_tools_k3_r1.py','test_g1_exit_restraints.py','test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py']:
        p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pattern,exit_code=p.returncode,output=p.stdout+p.stderr))
    assert all(r['exit_code']==0 for r in runs)
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick))
    ps,pq=read(PARENT/'selection.json'),read(PARENT/'one-order-quantities.json')
    s,q=build_selection(card,ps,pq,native)
    changed=[r['identity'] for r,p in zip(s['prints'],ps['prints']) if r!=p]
    assert len(changed)==2,changed
    assert len(s['prints'])==71 and len(q['lines'])==115
    assert [r['id'] for r in q['lines']]==[r['id'] for r in pq['lines']]
    assert [r['planning_quantity'] for r in q['lines']]==[r['planning_quantity'] for r in pq['lines']]
    small=next(r for r in q['lines'] if r['id']=='tie:111-02370');assert small['installed']==95 and small['planning_quantity']==100
    large=next(r for r in q['lines'] if r['id']=='consumable:p0:1');assert large['existing_working_allowance']+large['unallocated_stock']==100 and large['existing_working_allowance']==21
    assert sum(r['quantity'] for r in s['prints'] if r['purpose']=='installed_candidate')==110
    assert sum(r['quantity'] for r in s['prints'] if r['purpose']!='installed_candidate')==4
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),main_positive_input_sha256=sha256(OUT/'interface.json'))
    q['selected_prints']=(BATCH/'selection.json').relative_to(ROOT).as_posix()
    BATCH.mkdir(parents=True,exist_ok=True);save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    (BATCH/'README.md').write_text((OUT/'README.md').read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    end=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-02T06:30:06+00:00')
    save(OUT/'work-time.json',dict(start_utc=start.isoformat(),end_utc=end.isoformat(),wall_seconds=(end-start).total_seconds(),
        kind='Measured wall window: required instructions, complete changed interface, rejected contact evidence, native construction/export, termination/stock and package; interrupted own validation retained. Not CPU time.',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    directories=[OUT,NATIVE,BATCH,ROOT/'hardware/cad/studies/main-positive-native-r1',ROOT/'hardware/cad/studies/main-positive-native-r2',SCREEN]
    own=[p for d in directories for p in d.iterdir() if p.is_file() and p.suffix not in ('.FCBak',) and p.name not in ('manifest.json','validation.json')]
    for number in range(3,8):own+=[ROOT/f'hardware/electronics/full-cat/main-positive-complete-r{number}/checks.json']
    scripts=['main_positive_complete_r'+str(i)+'.py' for i in range(3,9)]+['main_positive_native_r1.py','main_positive_native_r2.py','main_positive_native_r3.py','main_positive_mesh_probe.py','main_positive_native_interrupted_r1.py','main_positive_wiring_card_r1.py','test_main_positive_wiring_card.py','main_positive_preview.py','package_main_positive_r44.py']
    own+=[ROOT/'tools/electronics'/n for n in scripts]+[PARENT/'manifest.json']
    for p in own:
        rel=p.relative_to(ROOT).as_posix();h=sha256(p);assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    m=copy.deepcopy(parent);m.update(parent_pins_preserved=len(parent['files']),newly_selected_stls=2,
        W5_complete=False,K3_complete=False,files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    checked=verify(ROOT,m);assert checked['integrity_ok']
    save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=checked,parent_pins_preserved=len(parent['files']),changed_print_identities=changed,
        retained_prints=69,print_jobs=71,installed_PETG=110,fit_samples=4,replaced_STLs=2,total_quantity_lines=115,
        phase1_percent=70,W5_complete=False,K3_complete=False,physical_pass=False,collision_free=False,
        soft_contacts=card['soft_contacts'],tests_passed=72))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),tests=72,changed_prints=changed,phase1_percent=70)),flush=True)

if __name__=='__main__':main()
