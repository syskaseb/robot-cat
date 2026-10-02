"""Select concrete tool requirements, not rejected F_PI routes or prints."""
from pathlib import Path
from datetime import datetime,timezone
import json,copy,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r41'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r42'
OUT=ROOT/'hardware/electronics/full-cat/termination-tools-k3-r1'
START=datetime.fromisoformat('2026-10-02T05:19:01+00:00')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert not (BATCH/'manifest.json').exists()
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    tools=read(OUT/'tools.json');assert len(tools['tools'])==4 and not tools['K3_complete']
    for p,h in tools['source_sha256'].items():assert sha256(ROOT/p)==h
    blocker=read(ROOT/'hardware/electronics/full-cat/main-positive-source-review-r1/validation.json')
    assert not blocker['selected'] and blocker['new_STLs']==0
    runs=[];tick=time.monotonic()
    for pat in ['test_termination_tools_k3_r1.py','test_g1_exit_restraints.py','test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py']:
        p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pat,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pat,exit_code=p.returncode,output=p.stdout+p.stderr))
    assert all(r['exit_code']==0 for r in runs)
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick))
    s=read(PARENT/'selection.json');q=read(PARENT/'one-order-quantities.json')
    q['selected_prints']=(BATCH/'selection.json').relative_to(ROOT).as_posix()
    for row in q['required_tools_buy_or_borrow']:
        if 'TE130171/130207/520448/520184' in row.get('tool',''):
            row.update(tool='TE69710-1+224027-2; TE58628-1; współdzielonyTE58433-3 z58423-1',
                status='Konkretny dostęp lub zgodna usługa przed montażem; nie zakładać posiadania. Dokładne role i warunki w termination-tools-k3-r1/tools.json.',
                required_for='30 zakończeń mocy. Przewód fabryczny OUT i F0 wymaga sprawdzenia; żadnego fizycznego PASS ani zalecenia zakupu wszystkich drogich narzędzi.')
    q['exact_crimp_tool_requirements']=tools['tools']
    q['crimp_process_recipe']=(OUT/'tools.json').relative_to(ROOT).as_posix()
    q['tools_quantity_rule']='Four exact crimp tool SKUs are access requirements, not presumed owned, not component purchase rows.58433-3 includes58423-1; no duplicate die. Other general tools and fullK3 remainOPEN.'
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),crimp_tooling=(OUT/'tools.json').relative_to(ROOT).as_posix(),
        crimp_tooling_sha256=sha256(OUT/'tools.json'),phase1_percent=70,W5_complete=False)
    s['unselected_MAIN_positive_work']='Source-review-r1 records impossible original W043 distance and rejected P0-support strap. No F_PI relocation, P_SYS cage remap, red-length increase, W043/W077/W078 route or new STL selected.'
    assert s['prints']==read(PARENT/'selection.json')['prints'] and q['lines']==read(PARENT/'one-order-quantities.json')['lines']
    BATCH.mkdir(exist_ok=True);save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    text=(OUT/'README.md').read_text(encoding='utf-8')+'\nR42 zachowuje wszystkie71wydruków/110PETG/4próbki i114wierszy komponentów R41.\nF_PI/W078 odrzucone, nie zmieniono ilości opasek; W5 pozostajeOPEN.\n'
    (BATCH/'README.md').write_text(text,encoding='utf-8',newline='\n')
    end=datetime.now(timezone.utc);save(OUT/'work-time.json',dict(start_utc=START.isoformat(),end_utc=end.isoformat(),wall_seconds=(end-START).total_seconds(),
        kind='Actual FHAC source/drawing review, unselected positive-input candidates, P0-strap blocker, independent exact termination tooling matrix and selection',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    folders=[OUT,BATCH,ROOT/'hardware/reference/fhac0001zxj-2026-10-02']+[ROOT/'hardware/electronics/full-cat'/n for n in ['main-positive-input-r1','main-positive-input-route-r1','main-positive-input-route-r2','main-positive-source-finish-r1','main-positive-source-review-r1']]
    files=[p for d in folders for p in d.iterdir() if p.is_file() and p.name not in ['manifest.json','validation.json']]
    # Validation for the recovered blocker is evidence, unlike batch manifest verification.
    files.append(ROOT/'hardware/electronics/full-cat/main-positive-source-review-r1/validation.json')
    names=['main_positive_input_r1.py','main_positive_input_route_r1.py','main_positive_input_route_common_r2.py','main_positive_input_route_r2.py','main_positive_input_finish_r1.py','verify_main_positive_input_evidence.py','termination_tools_k3_r1.py','test_termination_tools_k3_r1.py','package_termination_tools_r42.py']
    files += [ROOT/'tools/electronics'/n for n in names]+[PARENT/'manifest.json']+[ROOT/p for p in tools['source_sha256']]
    for p in files:
        rel=p.relative_to(ROOT).as_posix();h=sha256(p);assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    m=copy.deepcopy(parent);m.update(parent_pins_preserved=len(parent['files']),newly_selected_stls=0,phase1_percent=70,W5_complete=False,
        files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    m['gates']['geometry']['status']='open'
    m['gates']['geometry']['reason']='All R41 prints retained. MAIN positive work is rejected/unselected, not a new mounted branch; source restraint conflicts P0. R40 sleeve condition and wholeW5 remainOPEN.'
    integrity=verify(ROOT,m);assert integrity['integrity_ok']
    save(BATCH/'manifest.json',m);save(BATCH/'validation.json',dict(integrity=integrity,parent_pins_preserved=len(parent['files']),
        print_jobs_unchanged=71,installed_petg=110,fit_samples=4,quantity_lines_unchanged=114,new_STLs=0,purchase_lines_unchanged=True,
        exact_crimp_tool_SKUs=4,conditional_crimp_ends=30,phase1_percent=70,W5_complete=False,K3_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),phase1_percent=70,wall_seconds=(end-START).total_seconds())))

if __name__=='__main__':main()
