"""Recoverable candidate package, not another selected robot release."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/head-jr-support-r2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    checks=json.loads((OUT/'checks.json').read_text())
    assert checks['status']=='JR_HOLDER_CANDIDATE' and not checks['hits'] and len(checks['slot_checks'])==8
    files=[p for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json' and p.suffix!='.FCBak']
    files += [Path(__file__),ROOT/'tools/cad/head_jr_support_r1.py',ROOT/'tools/electronics/head_jr_support_preview.py']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    pins.update(json.loads((OUT/'plan.json').read_text())['parent_files_sha256'])
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    result=dict(files_sha256=pins,new_stls=2,quantities={'ForkJRHolder_candidate_x1.stl':1,'PitchCarrierThroughLeadExit_candidate_x1.stl':1},
      replacements_only=True,additional_screws=0,additional_ties_from_existing_bag100=4,
      selected_robot_release=False,whole_head_wiring_complete=False,phase1_complete=False,physical_pass=False)
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(pins=len(pins),new_stls=2,selected=False)))
if __name__=='__main__':main()
