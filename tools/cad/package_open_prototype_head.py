"""Select one nominal M2 package only after current native/mount receipts."""
from pathlib import Path
from datetime import datetime,timezone
import time,json
from package_open_prototype_tail import ROOT,BASE,sha,read,save,stl_size
from release_check import verify,REQUIRED_GATES
OUT=BASE/'head-mount-checkpoint'

def run():
    tick=time.monotonic()
    proofs=[read(OUT/n) for n in ('preflight.json','native-assembly-checks.json','head-neck-checks.json')]
    pre,native,fresh=proofs
    assert pre['status']=='CURRENT_HEAD_EXTERNAL_INTERFACES_CLEAR' and not pre['contacts'] and not pre['errors']
    assert native['status']=='CURRENT_HEAD_LOCAL_NATIVE_PREPARED_FRESH_REOPEN_REQUIRED'
    assert fresh['status']=='CURRENT_HEAD_NECK_FRESH_RELOCATED_NATIVE_PREPARED'
    assert fresh['external_links']==0 and fresh['all_52_rise_restore'] and fresh['MAIN_absolute_4_5_4']
    assert len(native['parts'])==52 and len(fresh['neck_hardware'])==32 and len(fresh['neck_supports'])==2
    assert fresh['head_washer_changed_interface']['washers']==8 and not fresh['head_washer_changed_interface']['contacts']
    for proof in proofs:
      for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(OUT/'HeadNeckCurrent.FCStd')==fresh['model_sha256']
    assert sha(OUT/'HeadAssemblyCurrent.FCStd')==native['model_sha256']
    inherited_paths=[ROOT/'hardware/cad/studies/head-p8/head-current-motion-r1/candidate-checks.json',
      ROOT/'hardware/cad/studies/head-p8/head-yaw-fit-jaws-r2/motion-screen/checks.json',
      ROOT/'hardware/cad/studies/head-p8/head-printed-horns-r2/checks.json',
      BASE.parent/'neck-support/mount-check-corrected.json']
    for p in inherited_paths[:2]:assert not read(p)['positive_hits'],str(p)
    selection=read(ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json');prints=[]
    for row in selection['prints']:
      if row['module']!='head/neck' and row['identity']!='drive:MG92BPrintedHorn20T-R2':continue
      q=dict(row)
      if row['identity']=='drive:MG92BPrintedHorn20T-R2':
        q['quantity']=2;q['allocation']='Two head horns only; third horn belongs to M3, not added again'
      q['sha256']=sha(ROOT/q['stl']);q['print_size_mm']=stl_size(ROOT/q['stl'])
      q['status']='nominal_current_M2_selected_delivery_and_PETG_fit_open';prints.append(q)
    assert len(prints)==20 and sum(p['quantity'] for p in prints)==21
    for name,rel in [('LeftRiser','neck-support/main-mount-sequence/LeftRiserWithMain_candidate.stl'),
                     ('RightRiser','neck-support/coupled/RightRiser_candidate.stl')]:
      p=BASE.parent/rel
      prints.append(dict(identity='CP2Head:'+name,quantity=1,stl=p.relative_to(ROOT).as_posix(),sha256=sha(p),
        source=(OUT/'HeadNeckCurrent.FCStd').relative_to(ROOT).as_posix(),source_object=name,material='PETG',
        print_size_mm=stl_size(p),brim_mm=5,orientation='Existing flat foot down; retain original orientation',
        supports='Phase2 slicer/fit trial; do not assume printed strength'))
    assert sum(p['quantity'] for p in prints)==23
    assert all(max(p['print_size_mm'])+10<256 for p in prints)
    kitpath=ROOT/'hardware/manufacturing/head-fastener-kit-r1/kit.json';kit=read(kitpath)
    assert len(kit['internal_groups'])==12
    package=dict(status='M2_CURRENT_NOMINAL_PROTOTYPE_MECHANICS_SELECTED',result_id='M2',selected=True,
      mechanical_M2_complete=True,physical_pass=False,print_ready=False,wiring_complete=False,
      current_assembly='HeadNeckCurrent.FCStd',prints=prints,printed_pieces=23,print_geometries=22,
      head_modeled_identities=52,model_does_not_claim_every_fastener_is_separate=True,
      pitch_nominal_deg=[-10,5],yaw_nominal_deg=[-15,15],continuous_sweep_qualified=False,
      internal_hardware_groups=kit['internal_groups'],internal_hardware_totals=kit['internal_nominal_totals'],
      bearings=kit['bearing_reference_only'],unknown_factory_retention_screws='Measure actual MG92B on delivery; no invented SKU',
      neck_hardware=dict(lower_M2x10=4,upper_M2x12=4,M2_nuts_AF4=8,M2_washers_OD5_ID2p2_t0p3=16,
        washer_allocation='8 existing lower P0 washers reused; 8 upper washers additional; two per bolt',
        replaces='Old four upper M2x14 omitted; lower four existing P0 bolts/nuts reused, not a second kit',
        MAIN_board_mount_separate=dict(M2x12=2,M2_nuts_AF4=2,M2_washers_OD5_ID2p2_t0p3=4)),
      assembly_recipe='README.md',inherited_mechanical_proofs=[p.relative_to(ROOT).as_posix() for p in inherited_paths],
      preserved=['P0','E6 contoured concave ears','15 drives','bank R47','MAIN worldZ46.52','torso325x200x160','replaceable provisional MG92B horns'],
      phase2_gates=['Actual MG92B spline/axial screw and horn clamp preload',
        'PETG bearing/tool/washer/fastener fit and torque, continuous safe motion and loads',
        'Slicer/supports/printed material trials; nominal native geometry is not physical PASS'],
      explicitly_open=['W2 local moving harness and CP2 body integration','W3 complete head feeds','W5 remaining full harness',
        'M4 covers','M5 electronics mounts','E3 data','K1/K2/K3 whole selected kit','A2/A3 whole build reconciliation'],
      work_timing=dict(started_utc='2026-10-09T23:33:37Z',prepared_utc=datetime.now(timezone.utc).isoformat(),
        native_workers_seconds=[p['worker_seconds'] for p in proofs],not_cpu_time_for_whole_task=True))
    save(OUT/'selection.json',package)
    pins={OUT/n for n in ('README.md','selection.json','preflight.json','native-assembly-checks.json','head-neck-checks.json','HeadAssemblyCurrent.FCStd','HeadNeckCurrent.FCStd')}
    pins.update(inherited_paths);pins.add(kitpath);pins.add(Path(__file__));pins.add(ROOT/'tests/test_open_prototype_head_package.py')
    for proof in proofs:pins.update(ROOT/n for n in proof['source_sha256'])
    for row in prints:pins.add(ROOT/row['stl'])
    for group in kit['internal_groups']:pins.add(ROOT/group['source'])
    manifest=dict(schema_version=1,readiness='prototype',result_id='M2',mechanical_preparation_complete=True,
      physical_pass=False,gates={g:dict(status='open',reason='Physical phase2 trial required; nominal M2 scope only') for g in REQUIRED_GATES},
      files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)])
    manifest['gates']['geometry']=dict(status='pass',reason='Current external head/neck interface, retained internal samples and independent relocated native parameter restore; no whole wiring claim',
      evidence=[(OUT/n).relative_to(ROOT).as_posix() for n in ('preflight.json','native-assembly-checks.json','head-neck-checks.json')])
    assert verify(ROOT,manifest)['integrity_ok'] and not verify(ROOT,manifest,True)['integrity_ok']
    save(OUT/'manifest.json',manifest)
    score=read(BASE/'current-phase1-score.json')
    assert score['fixed_total']==20 and score['confirmed_result_ids']==['M1','M3','E4','A1']
    prior={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
    score.update(confirmed_result_ids=['M1','M2','M3','E4','A1'],result_count=5,result_percent=25,change_pp=5,new_result='M2',
      previous_evidence=prior,evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),
      checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3))
    save(BASE/'current-phase1-score.json',score)
    print(json.dumps(dict(result_count=5,result_percent=25,pins=len(pins),printed_pieces=23)))

if __name__=='__main__':run()
