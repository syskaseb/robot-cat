"""Fail-closed complete current W4, fixed20-result score; no wholeW5 claim."""
import json,math,time
from pathlib import Path
from datetime import datetime,timezone
from package_open_prototype_tail import ROOT,BASE,sha,read,save,stl_size
from release_check import verify,REQUIRED_GATES
OUT=BASE/'tail-wiring-checkpoint'

def ready(q):
 return q['status']=='CURRENT_W4_RELEASE_PREPARED' and not q['contacts'] and q['native_parameter_restore'] and q['fresh_relocated_reopen'] and q['tail_motion_samples']==list(range(-30,31,5)) and q['bare_rail_continuous_lift_mm']==30

def run():
 tick=time.monotonic();q=read(OUT/'release-checks.json');assert ready(q)
 assert sha(OUT/'TailWiringRelease.FCStd')==q['model_sha256']
 proofs=[read(OUT/n) for n in ('native-checks.json','final-checks.json','complete-checks.json','release-checks.json')]
 for proof in proofs:
  for name,digest in proof['source_sha256'].items():assert sha(ROOT/name)==digest,name
 p=read(OUT/'elevated-final-plan.json');lengths=read(OUT/'elevated-received-space-checks.json')['lengths_mm']
 rows=[]
 # Boundary88 is accounting only; all three HELU wires continue to their
 # sleeve centre without a fourth joint. JR stock is counted separately.
 for name,sku,joint,strip,extra_bare in [('XB32','HELU23302 red0.5mm2',100,16,0),('XB33','HELU23301 black0.5mm2',98,19,0),('XS33','HELU23308 yellow0.5mm2',96,8,lengths['XS33_bare'])]:
  guided=lengths[name]+joint-88+extra_bare;nominal=5*math.ceil((guided+strip+60)/5)
  extension=q['local_lengths']['JR/'+name]['length_mm']+q['local_lengths']['local/'+name+'/0_CENTERLINE']['length_mm']+108-joint
  rows.append(dict(wire=name,sku=sku,body_guide_mm=lengths[name],local_HELU_mm=joint-88,bare_board_mm=extra_bare,
   guided_total_mm=guided,strip_lap_allowance_mm=strip,trim_service_reserve_mm=60,nominal_fit_blank_mm=nominal,
   procurement_contribution_mm=5*math.ceil(nominal*1.25/5),purchased_mm=0,
   JR_extension_guide_mm=extension,JR_extension_nominal_blank_mm=5*math.ceil((extension+8+30)/5),JR_stock_minimum_mm=300))
 assert all(v['JR_extension_nominal_blank_mm']<=300 for v in rows)
 assert q['factory']['external_with_JR_approach_mm']+q['factory']['exit_mm']<=250.0001
 assert lengths['F_TY_factory_out']<=84.5 and lengths['F_TY_input_prefix']<84.5
 p.update(status='CURRENT_W4_NOMINAL_PROTOTYPE_SELECTED',selected=True,W4_complete=True,physical_pass=False,print_ready=False,full_phase1_complete=False,
  current_native='TailWiringRelease.FCStd',tail_boundary_x_mm=88,local_translation_mm=[12,-3,35],factory=q['factory'],prints=q['exports'],length_stock_rows=rows,
  pin_map={'XB32':'F_TY.out to C_TY project pin2 AUX6V','XB33':'G_TAIL.5 to C_TY project pin1 GND; same bus rebind, port4XL09 retained','XS33':'Known B3/R3 output86.51/13.97 to C_TY project pin3 PWM; no externalU1 pin used','R9':'10k servo-side PWM to dedicated XB33 motor return'},
  connector_gate='JR/Futaba Kamami58676130cm22AWG,30x12x10 project pair allowance. Both8mm extension/10mm factory approaches included; delivered cavity view/polarity/exit/length/OD are unpowered fit gates, not measured manufacturer pinout.',
  load_paths=['Cradle2M3x10 into side-loaded nuts on two receiver bridges to ACTUAL carrier floor; no floating posts.',
   'Six central straps:2case,2factory,red andB3. PairedE2/W4 source-ground band replaces ONE existingE2 band, not an additional allocation.',
   'Rail:2bands118/138 through existing native tunnels,1JRcaseband145,2local insulation85/112,1factoryguard140. Six new rail bands; old five local bands retired.',
   'R9 sleeves preserve3mm overlaps; no band on solder, resistor or unknown pads. Adhesive does not carry wire loads.'],
  assembly=['All battery/USB/monitor energy sources physically absent. Fit upper carrier root bridges, captive2nuts and cradle2M3x10/2washers before PCBs/holder.',
   'Bench fit JR and three uncut factory conductors, cut only300mm extension. Form/solder three isolated joins and R9 away fromPETG; local three14mm raw sleeves plusR9 sleeves14/32/30mm.',
   'Prepare B3 formed-end insulation as documented. Seat board after lead has independent sound-insulation grip; solder only known assignedB3 pad. Keep hole/solder face clean.',
   'Place bare rail using2bands118/138; fitJRcase and independent local/guard bands. Lay complete factory250 including10mm final approach without cutting, inspect curvature/pressure unpowered.',
   'FitF_TY with6centralbands and output8mm lap inside final15mm factory tail;35mm raw output sleeve. Leave factoryINPUT uncut: its full source route belongs toW5.',
   'G_TAIL5 untinned11mm end, separate same-bus port3E2 black, one paired-ground band on intact insulation. Verify polarity/insulation/strain relief and all safety gates before energizing.'],
  service=[q['service_limits'],proofs[1]['service']],
  quantities=dict(M3x10=2,M3_nut_AF5p5_h2p4=2,M3_washer_OD7_ID3p2_t0p5=2,T18I_11102370_new=12,T18I_existing_E2_replacement=1,
   JR_Kamami586761=1,MG92B_factory250_reused_uncut=1,R9_MRS16000C1002FCT00_10k_reused=1,
   RNF100_1_8_9_raw_mm=[14,14,14,14,32,30],RNF100_3_16_raw_mm=[35],Temflex165_black15x50mm=1,FHAC16AWG_reused=1),
  body_insulation=q['insulation'],allocation='One replacement upper carrier andE2 fixture, two new printedparts cradle/rail. Replace historical tail-local bracket/5ties allocation; keep M3 selected mechanics/monitor/root/bankR47. K2/K3 whole-robot stock not claimed.',
  open_outside_W4=['FullF_TY input/source approach and920mm historical sourceW5','W1 AUX / W2 W3 head / wholeW5','E3 actual data and phase2 delivery/insulation/load/current checks'],
  phase2_gates=p['delivery_gates']+['New explicitR21=6x3.5mm factory assumption replaces historicalR22, does not inherit its validation. Actual cable length/OD/flexibility/exit must fit250mm full route unpowered; if not, adjust interchangeable rail before fabrication.',
   'Temflex165 two-layer nominal wrap and0.33mm material reserve are NOT proof of actual coverage. Inspect complete formed-lead insulation to board underside,>=3mm intact-jacket overlap, adhesion/deburr/pull and separation before power.',
   'Manual deliveredATO/JR/WAGO access, PETG creep/tie tension/printedfit and support removal; exports not slicer verified.'],
  checked_utc=datetime.now(timezone.utc).isoformat(),worker_seconds=q['worker_seconds'])
 p.pop('support_plan',None);p['support_plan']=p['load_paths'];p['local_shift_mm']=[12,-3,35]
 p['body_insulation']['product_reference']='https://imager.lapp.com/e/lapp/Dc8_lSkO5Unvw4TvlGpRNQ~~/DB61721030EN.pdf'
 save(OUT/'selection.json',p)
 pins={OUT/n for n in ('selection.json','README.md','.gitattributes','release-checks.json','complete-checks.json','final-checks.json','native-checks.json','elevated-final-space-checks.json','elevated-final-plan.json','elevated-received-space-checks.json','elevated-received-plan.json','TailWiringRelease.FCStd')}
 for proof in proofs:
  pins.update(ROOT/n for n in proof['source_sha256'])
 for n in ('plan_current_tail_wiring.py','plan_current_tail_inboard.py','plan_current_tail_lower_bus.py','plan_current_tail_complete.py','plan_current_tail_elevated.py','receive_current_tail_elevated.py','build_current_tail_wiring.py','finish_current_tail_wiring.py','receive_current_tail_final.py','qualify_current_tail_service.py','package_current_tail_wiring.py'):
  pins.add(ROOT/'tools/cad'/n)
 pins.add(ROOT/'tests/test_current_tail_wiring_package.py')
 pins.add(ROOT/'tests/.gitattributes')
 for row in q['exports']:
  assert sha(ROOT/row['path'])==row['sha256'] and max(stl_size(ROOT/row['path']))+10<256;pins.add(ROOT/row['path'])
 manifest=dict(schema_version=1,readiness='prototype',result_id='W4',physical_pass=False,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)],
  gates={g:dict(status='open',reason='Nominal phase1 preparation only; physical delivery/printedfit/electrical/attached cable tests remain phase2.') for g in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='Full3feed/factory250 approaches/R9/insulation/current4nativeprints/13tailposes and bare-rail continuous30mm removal qualified. Earlier failed receipts explicitly superseded, no physical pass.',evidence=[(OUT/'release-checks.json').relative_to(ROOT).as_posix()])
 assert verify(ROOT,manifest)['integrity_ok'] and not verify(ROOT,manifest,True)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
 if 'W4' not in score['confirmed_result_ids']:
  assert score['result_count']==7
  previous={k:score[k] for k in ('new_result','evidence','evidence_sha256')};ids=score['confirmed_result_ids']+['W4']
  score.update(confirmed_result_ids=ids,result_count=8,result_percent=40,change_pp=5,new_result='W4',previous_evidence=previous,
   evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3));save(BASE/'current-phase1-score.json',score)
 elif score['new_result']=='W4':
  score.update(evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat());save(BASE/'current-phase1-score.json',score)
 print(json.dumps(dict(result_percent=score['result_percent'],pins=len(pins),prints=4,stock=rows,seconds=round(time.monotonic()-tick,3))))
if __name__=='__main__':run()
