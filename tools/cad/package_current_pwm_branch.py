"""Select only complete nominal current E2; retain failed receipts honestly."""
from datetime import datetime,timezone
from pathlib import Path
import json,time,shutil
from package_open_prototype_tail import ROOT,BASE,sha,read,save,stl_size
from release_check import verify,REQUIRED_GATES
OUT=BASE/'pwm-branch-checkpoint'

def ready(proof):
 return proof['status']=='E2_CURRENT_COMPLETE_NATIVE_PREPARED' and not proof['contacts'] and proof['native_parameter_restore'] and proof['fresh_relocated_reopen']

def run():
 tick=time.monotonic();q=read(OUT/'complete-checks.json');assert ready(q)
 assert sha(OUT/'PWMBranchCurrentFinal.FCStd')==q['model_sha256']
 first=read(OUT/'final-checks.json');middle=read(OUT/'received-checks.json');last=read(OUT/'current-checks.json')
 assert middle['status']=='E2_RECEIPT_STATIC_PREPARED' and not middle['contacts']
 assert not last['outside_torso'] and last['native_parameter_restore'] and last['fresh_relocated_reopen']
 assert len(last['contacts'])==3 and len(first['contacts'])==5
 for p in (q,first,last):
  for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
 assert sha(OUT/'final-checks.json')==middle['prior_receipt_sha256']
 p=read(OUT/'final-plan.json')
 p.update(status='CURRENT_E2_NOMINAL_BRANCH_SELECTED',selected=True,E2_complete=True,
  current_native='PWMBranchCurrentFinal.FCStd',P_REAR_centre_mm=[18,0,138],
  assumptions=['Mated MicroFit26x12x12 project allowance; catalogue24.77mm overall, delivered exit/latch/cavities must fit.',
   'All four exact factory leads225+/-5mm, minimum220mm. ModelOD1.85/R11.1 are project assumptions, not delivered measurement.',
   'Fuse final sleeveOD<=6.4, board sleevesOD<=2.8, ten band fits/tension are phase2 gates.',
   'No unknown externalU1 pinout, E3/fullW5 unchangedOPEN.'],
  load_path_plan=['One three-post fixture rooted26/Y+-20 and120/Y-20 in matched upper carrier.',
   'P_REAR18/0/138 andG_TAIL28/-35/141 both east; source pair and both module exits restrained independently.',
   'Two fuse seats, intactXP01/ground grips, pairedsource grip, housing2/module2/board1 bands:tenT18I.',
   'FullM3thread end bore and complete band-channel silhouette; source/module paired bands use complete two-wire envelope.'],
  service_plan=['README.md staged installation beforePi/BUS; free both source ends and ties before unplugging; bench fallback with supportedPCB.',
   'No connected-cable swept-volume claim; preserve nominal body/finger space in futureW5.'])
 assert p['fuse']['XP01_nominal_fit_blank_mm']==34 and p['fuse']['conservative_unfused_mm']<=50
 assert all(b['margin_mm']>=0 and b['minimum_factory_mm']==220 for b in p['budgets'].values())
 p['prints']=q['exports'];p['print_ready']=False;p['full_phase1_complete']=False
 p['quantities']=dict(M3x12_DIN912=3,M3_nut_AF5p5_h2p4=3,M3_washer_OD7_ID3p2_t0p5=3,T18I_11102370=10,
  F_PWM_0242p100UAT1=1,HELU23302_nominal_blank_mm=34,RNF100_3_32_blank_mm=[20,20],RNF100_3_16_blank_mm=[50],RNF100_1_8_9_blank_mm=[15,15],
  Molex2147612113=1,Molex2147611113=1,Molex2147632113=1,Molex2147631113=1,Molex430250200=1,Molex430200201=1,
  tesa4965_patch_mm=[[18,33],[15,26]])
 p['allocation']='One replacement UpperCarrier, one new fixture; existingP_REAR/G_TAIL/fuse/housings reused. TenT18I replace old4T18R+6T18I allocation. Local consumption only, K2/K3 global stock remainsOPEN.'
 p['checked_utc']=datetime.now(timezone.utc).isoformat();p['worker_seconds']=q['worker_seconds'];save(OUT/'selection.json',p)
 pins={OUT/n for n in ('selection.json','README.md','.gitattributes','complete-checks.json','current-checks.json','received-checks.json','final-checks.json','final-plan.json','PWMBranchCurrentFinal.FCStd')}
 for proof in (q,first,last):pins.update(ROOT/n for n in proof['source_sha256'])
 for row in q['exports']:
  assert sha(ROOT/row['path'])==row['sha256'];assert max(stl_size(ROOT/row['path']))+10<256;pins.add(ROOT/row['path'])
 for n in ('plan_current_pwm_branch.py','plan_current_pwm_east.py','plan_current_pwm_south_bypass.py','plan_current_pwm_inline_platform.py','plan_current_pwm_core_corridor.py','build_current_pwm_fixture.py','receive_current_pwm_fixture.py','finish_current_pwm_fixture.py','finish_current_pwm_bands.py','qualify_current_pwm_branch.py','package_current_pwm_branch.py','check_main_p0_placement.py','open_deck_p0_supports.py','open_deck_p0_plate.py','open_prototype_shared_distribution_carriers.py'):
  pins.add(ROOT/'tools/cad'/n)
 for rel in ('hardware/electronics/full-cat/pwm-complete-e2-r1/electrical-design.json','hardware/electronics/full-cat/pwm-complete-e2-r1/interface.json',
  'hardware/electronics/full-cat/pwm-fused-pigtail-r2/plan.json','hardware/electronics/full-cat/pwm-carrier-r3/population.json',
  'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json','hardware/manufacturing/one-batch-prototype-r32/README.md','tests/test_current_pwm_branch_package.py'):
  pins.add(ROOT/rel)
 manifest=dict(schema_version=1,readiness='prototype',result_id='E2',physical_pass=False,
  files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)],
  gates={g:dict(status='open',reason='Nominal phase1 preparation only; delivered fit/PETG/load/electrical/connected service phase2 gates remain.') for g in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='Three failed native receipts explicitly superseded by measured changed-interface corrections; current bodies/exports/parameter/reopen verified.',evidence=[(OUT/'complete-checks.json').relative_to(ROOT).as_posix()])
 assert verify(ROOT,manifest)['integrity_ok'];assert not verify(ROOT,manifest,True)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');ids=score['confirmed_result_ids'];assert score['fixed_total']==20
 if 'E2' not in ids:
  assert len(ids)==6;previous={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
  score.update(confirmed_result_ids=['M1','M2','M3','M5','E2','E4','A1'],result_count=7,result_percent=35,change_pp=5,new_result='E2',
   previous_evidence=previous,evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),
   checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3));save(BASE/'current-phase1-score.json',score)
 print(json.dumps(dict(result_count=score['result_count'],result_percent=score['result_percent'],pins=len(pins),prints=2,worker_seconds=q['worker_seconds'])))
if __name__=='__main__':run()
