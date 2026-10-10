"""Select complete nominal W2 local head wiring, not the six body feeds W3."""
import json, math, time
from pathlib import Path
from datetime import datetime, timezone
from package_open_prototype_tail import ROOT, BASE, sha, read, save, stl_size
from release_check import verify, REQUIRED_GATES
OUT = BASE/'head-wiring-checkpoint'

def ready(q, native, anchor):
 return (q['status']=='CURRENT_W2_NOMINAL_COMPLETE' and not q['contacts']
  and len(q['motion_samples'])==9 and len(q['boundaries'])==9
  and native['status']=='CURRENT_W2_ANCHOR_RELEASE_PREPARED' and not native['contacts']
  and native['native_parameter_restore'] and native['fresh_relocated_reopen']
  and not anchor['contacts'] and not anchor['outside']
  and min(v['minimum_sampled_radius_mm'] for v in anchor['poses'])>=31.5
  and min(v['distance_mm'] for v in anchor['separation'])>=2.1-1e-4)

def run():
 tick=time.monotonic()
 q=read(OUT/'head-final-checks.json');n=read(OUT/'anchor-release-checks.json');a=read(OUT/'anchor-space-checks.json')
 assert ready(q,n,a)
 model=OUT/'HeadWiringCurrent.FCStd';assert sha(model)==q['model_sha256']==n['model_sha256']
 proofnames=['retained-space-checks.json','anchor-direct-arm-rejection.json','anchor-space-checks.json','anchor-native-checks.json','anchor-release-checks.json','head-final-checks.json']
 pins={OUT/x for x in proofnames+['HeadWiringCurrent.FCStd','selection.json','README.md','.gitattributes']}
 for name in proofnames:
  proof=read(OUT/name)
  for path,digest in proof.get('source_sha256',{}).items():
   if name=='anchor-direct-arm-rejection.json' and path=='tools/cad/plan_current_head_anchor.py':
    # Archived rejected straight arm: ONLY its exact saved nine loops and
    # unchanged scene are reused. Current dogleg source/receipt supersede
    # that old script revision; never silently refresh its historical hash.
    assert digest=='c4b3bb59f4cdefc9bc5ef12ff18a12ab3956e563432852af9660b2fc2a88f125'
    continue
   assert sha(ROOT/path)==digest,path
   pins.add(ROOT/path)
 for name,digest in a['unchanged_loop_geometry_sha256'].items():
  assert sha(OUT/name)==digest; pins.add(OUT/name)
 oldpath=ROOT/'hardware/manufacturing/one-batch-prototype-r28/head-local-interface.json';old=read(oldpath);pins.add(oldpath)
 pins.add(BASE/'head-mount-checkpoint/manifest.json')
 pins.add(BASE/'tail-wiring-checkpoint/manifest.json')
 rows=[]
 for name in ('XB12','XB13','XS13','XB22','XB23','XS23'):
  pitch=name in ('XB22','XB23','XS23');loop=max((v['length_mm'] for v in a['poses'] if v['wire']==name),default=0)
  local=old['local_routes'][name]['length_mm'];reserve=60
  # Local geometric span includes JR-side material: taking the entire span
  # as HELU is a labelled conservative stock allowance, not an exact cut.
  allowance=5*math.ceil((local+loop+(9 if pitch else 0)+reserve)/5)
  rows.append(dict(wire=name,local_mixed_JR_HELU_guide_mm=local,moving_HELU_mm=loop,fixed_HELU_anchor_tail_mm=9 if pitch else 0,
   conservative_local_HELU_fit_allowance_mm=allowance,local_procurement_contribution_mm=5*math.ceil(allowance*1.25/5),
   JR_stock_mm=300,cut_only_after_fit=True,body_feed_W3_not_included=True))
 for row in n['exports']:
  path=ROOT/row['path'];assert sha(path)==row['sha256'] and max(stl_size(path))+10<256;pins.add(path)
 selection=dict(status='CURRENT_W2_NOMINAL_PROTOTYPE_SELECTED',selected=True,W2_complete=True,physical_pass=False,print_ready=False,
  native=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),prints=n['exports'],
  scope='Two complete nominal local servo/JR/tail interfaces, six isolated joins, three constant-length moving conductors and independent fixed anchor. Six body feeds are W3, not W2; wholeW5 remainsOPEN.',
  retained_mechanics='Current selected M2 head/neck52identities and provisional interchangeableMG92B adapters; unchanged local support geometry retained from R28. One matched UpperCarrier replaces W4 carrier, not a second carrier.',
  frames=dict(head_root_translation_mm=[-42,0,25],applied_once=True),
  pins={'JR1':'GND provisional delivered-cavity gate','JR2':'AUX6V centre provisional','JR3':'PWM provisional'},
  boundaries=q['boundaries'],motion_samples=q['motion_samples'],moving_required_project_radius_mm=31.5,
  minimum_sampled_moving_radius_mm=min(v['minimum_sampled_radius_mm'] for v in a['poses']),
  fixed_project_radius_mm=12.6,wire_OD_mm=2.1,individual_sleeve_max_OD_mm=3.4,
  factory_leads=[dict(axis='yaw',nominal_uncut_mm=250,modeled_guide_mm=220,unallocated_delivery_fit_budget_mm=30),
   dict(axis='pitch',nominal_uncut_mm=250,modeled_guide_mm=224.886,unallocated_delivery_fit_budget_mm=25.114)],
  factory_limit='These retained R28 guides do NOT prove an exact installed250mm coil. Residual length is an explicit unpowered delivery fit budget, not invented routed geometry. Current body interference checked; retained internal flat-exit/support evidence conditional on the same delivery fit gates.',
  splice_recipe=old['splice_recipe'],length_stock_rows=rows,
  quantities=dict(MG92B_factory250_reused_uncut=2,JR_Kamami586761_300mm22AWG=2,RNF100_1_8_raw_mm=[11.5]*6,
   T18I_11102370_fixed_anchor_replacement=1,M3x10=2,M3_nut_AF5p5_h2p4=2,M3_washer_OD7_ID3p2_t0p5=2),
  stock_rule='Retain both original factory leads and two JR300extensions. Six individual11.5+/-0.2mm sleeves, final<=12mm, lap<=4mm, no common wrap. Existing local head ties retained; new fixed-anchor tie REPLACES oldY136cover tie. W3 must aggregate continuous HELU with these local allowances, not add another joint atY67.',
  load_path='Two M3x10/washer/captive-nut stacks on actual carrier floor -> single editable dogleg anchor -> intact9mm straight insulation tails. New receiver material checked against all retained body and head neighbours; no floating support or adhesive strain relief.',
  assembly=['All battery/USB/monitor sources removed. Fit two captive nuts/receiver and anchor screws on bare carrier before boards.',
   'Prepare factory/JR pairs and six labelled individual joins off PETG; preserve factory250uncut, cut extensions only after fit. Retain qualified head housing/factory/local insulation ties.',
   'Install head and complete moving conductors in assigned triangle, no common sleeve. Three equal-length-per-wire yaw routes; never put a tie on solder or moving bend.',
   'Lay nine-mm straight tails on independent anchor land; one replacementT18I on intact insulation. W3 continues each same wire fromY67 without a splice.',
   'Inspect polarity/cavity view, flat exit, sleeve packing, actual slack in all poses and support creep before energizing in phase2.'],
  service=q['service'],tool_assumption=n['tool_assumption'],
  supersedes='Historical outside-cover anchor and fixed pitch transition retired. 50mm straight tool rejection superseded by dimensioned18/40mm Lkey proof, not waived.',
  phase2_gates=['Delivered MG92B factory length/flat3.5x1.8 exit and flexibility, uncut residual30/25.114mm storage fit.',
   'JR/Futaba Kamami58676130cm22AWG actual mating/cavity/polarity and provisional30x12x10pair allowance.',
   'Individual RNF sleeve recovery/OD3.4 and actual lap coverage; insulation/strain pull, PETG creep and physical motion clearances.',
   'Sampled nominal motion/curve radii are not a physical sweep test; exports are not sliced or printed.'],
  open_outside_W2=['Six current body feeds/independent terminations/native roots W3','Full remaining body/leg/source harness W5, stock and E3 actual data'],
  checked_utc=datetime.now(timezone.utc).isoformat())
 save(OUT/'selection.json',selection)
 for name in ('plan_current_head_wiring.py','plan_current_head_anchor.py','build_current_head_anchor.py','finish_current_head_anchor.py','qualify_current_head_wiring.py','package_current_head_wiring.py'):
  pins.add(ROOT/'tools/cad'/name)
 pins.add(ROOT/'tests/test_current_head_wiring_package.py')
 manifest=dict(schema_version=1,readiness='prototype',result_id='W2',physical_pass=False,
  files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)],
  gates={g:dict(status='open',reason='Phase2 delivered/physical trial; nominal phase1 preparation only.') for g in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='Retained local guides, changed body context, complete constant-length head loop and native anchor/service qualified; explicit factory residual fit budgets, no whole W3/W5 claim.',evidence=[(OUT/'head-final-checks.json').relative_to(ROOT).as_posix(),(OUT/'anchor-release-checks.json').relative_to(ROOT).as_posix()])
 assert verify(ROOT,manifest)['integrity_ok'];assert not verify(ROOT,manifest,True)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
 if 'W2' not in score['confirmed_result_ids']:
  assert score['result_count']==8
  prev={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
  score.update(confirmed_result_ids=score['confirmed_result_ids']+['W2'],result_count=9,result_percent=45,change_pp=5,new_result='W2',previous_evidence=prev)
 score.update(evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3));save(BASE/'current-phase1-score.json',score)
 print(json.dumps(dict(percent=score['result_percent'],pins=len(pins),seconds=round(time.monotonic()-tick,3))))
if __name__=='__main__':run()
