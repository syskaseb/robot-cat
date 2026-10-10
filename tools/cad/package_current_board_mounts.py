"""Select the current board mechanics only; wiring is not silently waived."""
from pathlib import Path
from datetime import datetime,timezone
import time,json
from package_open_prototype_tail import ROOT,BASE,sha,read,save,stl_size
from release_check import verify,REQUIRED_GATES
OUT=BASE/'mounting-checkpoint'

def run():
    tick=time.monotonic();proof=read(OUT/'current-M5-checks.json')
    assert proof['status']=='CURRENT_BOARD_MOUNT_NATIVE_PREPARED'
    assert not proof['contacts'] and proof['fresh_relocated_reopen'] and proof['native_U1_hole_parameter_restore']
    assert len(proof['supplier_axis_bearing_checks'])==17
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(OUT/'CurrentBoardMounts.FCStd')==proof['model_sha256']
    prior=read(OUT/'mount-current-set.json');prints=[]
    for row in prior['current_print_parts']:
      if row['part'] in ('SideDistributionRail','SideRailSpacer'):continue
      q=dict(row)
      if row['part']=='LowerCarrier':
        q.update(path=(BASE/'tail-mount-checkpoint/LowerCarrier_x1.stl').relative_to(ROOT).as_posix(),
          source=(OUT/'CurrentBoardMounts.FCStd').relative_to(ROOT).as_posix(),source_object=proof['copy_receipts'][0]['name'],
          shared_physical_identity='CP2:LowerCarrier already selected by M3; one plate, not two')
      if row['part']=='UpperCarrier':
        q.update(path=(BASE/'wiring-checkpoint/DataShelf_UpperCarrier.stl').relative_to(ROOT).as_posix(),
          source=(OUT/'CurrentBoardMounts.FCStd').relative_to(ROOT).as_posix(),source_object=proof['copy_receipts'][1]['name'])
      q['sha256']=sha(ROOT/q['path']);q['print_size_mm']=stl_size(ROOT/q['path'])
      q['bounds_with_5mm_brim_mm']=[q['print_size_mm'][0]+10,q['print_size_mm'][1]+10,q['print_size_mm'][2]]
      assert max(q['bounds_with_5mm_brim_mm'])<256
      prints.append(q)
    assert len(prints)==8 and sum(p['quantity'] for p in prints)==20
    quantities=dict(M3x14=4,M3x45=4,M3_washer_OD7_ID3p2_t0p5=16,M3_nut_AF5p5_h2p4=8,
      M2x12=8,M2x14=9,M2x10=2,M2_washer_OD4p3_ID2p2_t0p3=24,M2_nut_AF4_h1p6=19)
    selection=dict(status='M5_CURRENT_NOMINAL_BOARD_MECHANICS_SELECTED',result_id='M5',selected=True,M5_complete=True,
      physical_pass=False,print_ready=False,full_wiring_complete=False,current_native='CurrentBoardMounts.FCStd',
      scope='Current Pi/BUS/PWM/AUX/U1 plate attachment and clamp load path; not WAGO/S1/wire/service completion',
      fixed_criterion_basis='Original R31 M5 closed PiTray/clamps/Pi mounting and staged Bus removal, with Pi wires explicitly left W5. Requalify that full mechanical function at CP2, not redefine M5 as all W5 distribution routes.',
      original_M5_definition='hardware/manufacturing/one-batch-prototype-r31/README.md',
      print_parts=prints,print_quantity_total=20,unique_print_geometries=8,fastener_total=27,quantities=quantities,
      shared_allocations=['LowerCarrier is the M3 plate, not a duplicate','Monitor and its two ties already belong to M3',
        'MAIN and its two bolts belong to M2','Bank R47 retained, not rebuilt or duplicated'],
      excludes=['Old WAGO/source positions in historical document are hidden and not selected',
        'Side distribution rails/spacers belong to current wiring packaging, not this board-only kit',
        'No U1 pinout inferred; E1/E2/W1/W5 and global stock K2/K3 remain OPEN'],
      assembly_recipe='current-M5-README.md',
      inherited_proofs=['board-mount-checks.json','board-hardware-checks.json','board-rear-tool-checks.json',
        'pwm-flat-insulator-checks.json','shared-retention-mount-checks.json'],
      phase2_gates=[g for g in prior['delivery_gates'] if g['id'] in ('DELIVERED_U1','POPULATED_FIT')],
      provisional_U1_authorized=True,delivered_U1_map_required_before_local_print=True,
      prepared_utc=datetime.now(timezone.utc).isoformat(),worker_seconds=proof['worker_seconds'])
    save(OUT/'current-M5-selection.json',selection)
    pins={OUT/n for n in ('current-M5-checks.json','current-M5-selection.json','current-M5-plan.json','current-M5-README.md','CurrentBoardMounts.FCStd','mount-current-set.json','board-mount-plan.json')}
    pins.update(ROOT/n for n in proof['source_sha256']);pins.add(Path(__file__))
    pins.add(ROOT/'tests/test_current_board_mounts_package.py')
    pins.add(ROOT/'tools/cad/open_prototype_head_assembly.py');pins.add(ROOT/'tools/cad/check_main_p0_placement.py')
    pins.add(ROOT/selection['original_M5_definition'])
    for row in prints:pins.add(ROOT/row['path'])
    for name in selection['inherited_proofs']:
      pins.add(OUT/name)
      for n,h in read(OUT/name)['source_sha256'].items():assert sha(ROOT/n)==h,n;pins.add(ROOT/n)
    manifest=dict(schema_version=1,readiness='prototype',result_id='M5',physical_pass=False,
      files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)],
      gates={g:dict(status='open',reason='Delivered fit/PETG/load/electrical/service phase2 gates, not a physical PASS') for g in REQUIRED_GATES})
    manifest['gates']['geometry']=dict(status='pass',reason='Retained supplier hole/support/tool evidence plus only changed plate material and relocated fresh native restore',evidence=[(OUT/'current-M5-checks.json').relative_to(ROOT).as_posix()])
    assert verify(ROOT,manifest)['integrity_ok'] and not verify(ROOT,manifest,True)['integrity_ok']
    save(OUT/'current-M5-manifest.json',manifest)
    score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
    assert score['confirmed_result_ids'] in (['M1','M2','M3','E4','A1'],['M1','M2','M3','M5','E4','A1'])
    previous=score['previous_evidence'] if score['new_result']=='M5' else {k:score[k] for k in ('new_result','evidence','evidence_sha256')}
    score.update(confirmed_result_ids=['M1','M2','M3','M5','E4','A1'],result_count=6,result_percent=30,change_pp=5,new_result='M5',
      previous_evidence=previous,evidence=(OUT/'current-M5-manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'current-M5-manifest.json'),
      checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3))
    save(BASE/'current-phase1-score.json',score)
    print(json.dumps(dict(result_count=6,result_percent=30,prints=20,geometries=8,pins=len(pins))))

if __name__=='__main__':run()
