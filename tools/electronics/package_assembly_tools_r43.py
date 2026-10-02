"""Select one tool-access set and shared solder spool; retain all R42 interfaces."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
from assembly_tools_k3_r2 import build_payload,OUT,REF,START,save
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r42'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r43'


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def main():
    assert not (BATCH/'manifest.json').exists()
    parent=read(PARENT/'manifest.json')
    assert verify(ROOT,parent)['integrity_ok']
    v=read(OUT/'tools.json')
    for path,h in v['source_sha256'].items():assert sha256(ROOT/path)==h
    runs=[];tick=time.monotonic()
    for pattern in ['test_assembly_tools_k3_r2.py','test_termination_tools_k3_r1.py','test_g1_exit_restraints.py','test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py']:
        p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pattern,exit_code=p.returncode,output=p.stdout+p.stderr))
    assert all(r['exit_code']==0 for r in runs)
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick))
    ps,pq=read(PARENT/'selection.json'),read(PARENT/'one-order-quantities.json')
    s,q=build_payload(v,ps,pq)
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),assembly_tooling_sha256=sha256(OUT/'tools.json'))
    q['selected_prints']=(BATCH/'selection.json').relative_to(ROOT).as_posix()
    assert s['prints']==ps['prints'] and len(q['lines'])==115 and len(pq['lines'])==114
    BATCH.mkdir(parents=True,exist_ok=True)
    save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    text=(OUT/'README.md').read_text(encoding='utf-8')+'\nR43:71zadań/110PETG/4próbki bez zmian;114stare wiersze zachowane,115łącznie po jednej wspólnej rolce spoiwa.0nowychSTL.\n'
    (BATCH/'README.md').write_text(text,encoding='utf-8',newline='\n')
    end=datetime.now(timezone.utc);begin=datetime.fromisoformat(START)
    save(OUT/'work-time.json',dict(start_utc=begin.isoformat(),end_utc=end.isoformat(),wall_seconds=(end-begin).total_seconds(),
        kind='Actual source/tool coverage review, drawing inspection, workshop set, package and regressions; includes R42 preservation/commit',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    own=[p for d in [OUT,REF,BATCH] for p in d.iterdir() if p.is_file() and p.name not in ['manifest.json','validation.json']]
    own+=[PARENT/'manifest.json']+[ROOT/'tools/electronics'/n for n in ['assembly_tools_k3_r2.py','test_assembly_tools_k3_r2.py','package_assembly_tools_r43.py']]
    for p in own:
        rel=p.relative_to(ROOT).as_posix();h=sha256(p);assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    m=copy.deepcopy(parent);m.update(parent_pins_preserved=len(parent['files']),newly_selected_stls=0,
        K3_complete=False,files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    check=verify(ROOT,m);assert check['integrity_ok']
    save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=check,parent_pins_preserved=len(parent['files']),print_jobs_unchanged=71,
        installed_PETG=110,fit_samples=4,new_STLs=0,retained_quantity_lines=114,total_quantity_lines=115,
        new_tool_access_SKUs=len(v['tools']),shared_solder_spools=1,phase1_percent=70,K3_complete=False,W5_complete=False,
        physical_pass=False,tool_ownership_confirmed=False,tests_passed=65))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),tests=65,wall_seconds=(end-begin).total_seconds(),phase1_percent=70)))


if __name__=='__main__':main()
