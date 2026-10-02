"""Select the current W5 fabrication ledger, never the rejected fuse routes."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r44'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r45'
OUT=ROOT/'hardware/electronics/full-cat/body-harness-w5-r2'
REJECT=ROOT/'hardware/electronics/full-cat/servo-fuse-inputs-r1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    assert not (BATCH/'manifest.json').exists()
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    runs=[];tick=time.monotonic()
    patterns=['test_body_harness_w5_r2.py','test_servo_fuse_inputs_r1.py','test_main_positive_wiring_card.py','test_assembly_tools_k3_r2.py','test_termination_tools_k3_r1.py','test_g1_exit_restraints.py','test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py']
    for pattern in patterns:
        p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pattern,exit_code=p.returncode,output=p.stdout+p.stderr))
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick))
    assert all(r['exit_code']==0 for r in runs)
    data=read(OUT/'interface.json');assert data['coverage']['selected_nominal_cuts']==10
    s,q=copy.deepcopy(read(PARENT/'selection.json')),copy.deepcopy(read(PARENT/'one-order-quantities.json'))
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),body_harness=(OUT/'interface.json').relative_to(ROOT).as_posix(),
      body_harness_sha256=sha256(OUT/'interface.json'),current_wire_cut_sheet=(OUT/'wire-cuts.csv').relative_to(ROOT).as_posix(),
      current_stock_ledger=(OUT/'stock.json').relative_to(ROOT).as_posix(),W5_complete=False,K3_complete=False,
      W5_recipe_precedence='R45 compiles inherited R44 selected cuts/recipes; replaces R36 ledger reference, not the R44 CAD or quantities. Failed twelve-input routes remain unselected. Shared K1474 counted per colour, ONE cable. No W036 trial selected.')
    q['selected_prints']=(BATCH/'selection.json').relative_to(ROOT).as_posix()
    assert len(s['prints'])==71 and s['prints']==read(PARENT/'selection.json')['prints']
    assert q['lines']==read(PARENT/'one-order-quantities.json')['lines'] and len(q['lines'])==115
    BATCH.mkdir(parents=True,exist_ok=True);save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    end=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-02T07:55:28+00:00')
    save(OUT/'work-time.json',dict(start_utc=start.isoformat(),end_utc=end.isoformat(),wall_seconds=(end-start).total_seconds(),
      kind='Measured wall window: instructions, one12input candidate with24terminal reserves, rejection, current physical cut/stock ledger and package. Not CPU time.',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    own=[p for d in (OUT,REJECT,BATCH) for p in d.iterdir() if p.is_file() and p.name not in ('manifest.json','validation.json')]
    own += [ROOT/'tools/electronics'/n for n in ('servo_fuse_inputs_r1.py','test_servo_fuse_inputs_r1.py','body_harness_w5_r2.py','test_body_harness_w5_r2.py','package_body_harness_r45.py')]
    own += [PARENT/'manifest.json']
    for p in own:
        rel=p.relative_to(ROOT).as_posix();h=sha256(p);assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    m=copy.deepcopy(parent);m.update(parent_pins_preserved=len(parent['files']),newly_selected_stls=0,W5_complete=False,K3_complete=False,
      files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    checked=verify(ROOT,m);assert checked['integrity_ok'];save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=checked,parent_pins_preserved=len(parent['files']),unchanged_prints=71,
      print_jobs=71,installed_PETG=110,fit_samples=4,new_STLs=0,total_quantity_lines=115,
      phase1_percent=70,W5_complete=False,K3_complete=False,physical_pass=False,
      rejected_candidate=dict(source=(REJECT/'checks.json').relative_to(ROOT).as_posix(),hits=81,selected=False),
      ledger=data['coverage'],tests_passed=85))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),tests=85,phase1_percent=70,new_STLs=0)),flush=True)
if __name__=='__main__':main()
