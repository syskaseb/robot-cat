"""Pin one shared nominal receiving/input allocation, without W5 credit."""
import json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SHA=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()

def main():
    tick=time.monotonic();pins={}
    pfile=OUT/'bank-input-plan.json';gfile=OUT/'bank-input-checks.json'
    p=json.loads(pfile.read_text());g=json.loads(gfile.read_text())
    assert g['status']=='TWELVE_BANK_INPUT_GUIDES_CANDIDATE_FRAME_CHANGES_ONLY_NATIVE_OPEN'
    assert not g['contacts'] and not g['errors'] and len(p['routes'])==12
    lfile=OUT/'leg-stations-manifest.json';leg=json.loads(lfile.read_text())
    assert leg['status']=='TWELVE_RECEIVING_CASES_FOUR_MAIN_OUTPUT_GUIDES_SPACE_ONLY_NOT_W5'
    for v in (p,g,leg):
        for n,h in v['source_sha256'].items():
            assert SHA(ROOT/n)==h,n
            assert n not in pins or pins[n]==h,n
            pins[n]=h
    score=BASE/'current-phase1-score.json';s=json.loads(score.read_text())
    for f in (pfile,gfile,lfile,score,Path(__file__),ROOT/'tests/test_current_bank_inputs.py',
              ROOT/'tools/cad/capture_current_leg_static_evidence.py'):
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    v=dict(status='SHARED_LOWER_GALLERY_AND_TWELVE_ATO_INPUTS_SPACE_ONLY_NOT_W5',
      selected=False,W5_complete=False,physical_pass=False,
      result_count=s['result_count'],fixed_total=20,percent=s['result_percent'],change_pp=0,
      receiving_cases=12,main_outputs=4,bank_inputs=12,
      input_guide_mm={n:r['guide_mm'] for n,r in p['routes'].items()},
      candidate_foundation_passages=p['required_foundation_passages'],
      candidate_removed_foundation_mm3=g['candidate_removed_foundation_mm3'],
      obsolete_side_attachment_removal=p['obsolete_side_attachment_removal'],
      candidate_removed_obsolete_attachments_mm3=g['candidate_removed_obsolete_attachments_mm3'],
      board_carrier_core_unchanged=g['board_carrier_core_unchanged'],
      new_native_parts=0,new_STL=0,head_poses=9,
      input_gate_seconds=g['worker_seconds'],input_pairs=g['pairs'],
      output_gate_seconds=leg['gate_seconds'],output_changed_pairs=leg['pairs'],
      open=['Registered bank/native receiving mount and independent grip/load path/protection',
        'Remaining ground/data/source/Pi body routes and12complete moving factory looms',
        'Whole assembly/service, current cuts/electrical reconciliation/stock and selected export',
        'Delivered conductor OD/area/pin order/dynamic radius/usable lengths and physical phase2 fit gates'],
      source_sha256=dict(sorted(pins.items())),verification_seconds=time.monotonic()-tick)
    (OUT/'bank-input-manifest.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=v['status'],pins=len(pins),seconds=v['verification_seconds'],percent=v['percent'])))

if __name__=='__main__':main()
