"""Select W3 only from whole geometry, native, ends, stock and service proof."""
import json,math,time,zipfile,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from package_current_head_wiring import ROOT,BASE,sha,read,save,verify,REQUIRED_GATES
OUT=BASE/'head-supply-checkpoint';W2=BASE/'head-wiring-access-checkpoint'
FEEDS=('XB12','XB13','XS13','XB22','XB23','XS23')

def ready(q,n,b):
 return (q['status']=='CURRENT_COUPLED_HEAD_SUPPLY_SPACE' and not q['contacts']
  and n['status']=='CURRENT_NATIVE_HEAD_SUPPLY_PREPARED' and not n['contacts']
  and n['native_parameter_restore'] and n['fresh_relocated_reopen'] and len(n['exports'])==2
  and b['status']=='CURRENT_W3_BOUNDARIES_CLEAR' and {v['wire'] for v in b['boundaries']}==set(FEEDS))

def run():
 tick=time.monotonic();q=read(OUT/'coupled-checks.json');n=read(OUT/'native-checks.json');b=read(OUT/'boundary-checks.json')
 assert ready(q,n,b),'Whole W3 incomplete, no partial result'
 model=OUT/'HeadSupplyCurrent.FCStd';assert sha(model)==n['model_sha256']
 with zipfile.ZipFile(model) as archive:
  program=ET.fromstring(archive.read('Document.xml')).attrib.get('ProgramVersion','unknown')
 assert program!='unknown','Record actual native producer version'
 p=read(OUT/'coupled-plan.json');g=read(OUT/'received-grips.json');w2=read(W2/'selection.json')
 lengths=q['lengths_mm'];local={v['wire']:v for v in w2['length_stock_rows']};rows=[]
 for name in FEEDS:
  guided=lengths[name]+local[name]['local_mixed_JR_HELU_guide_mm']
  if name in ('XB22','XB23','XS23'):guided+=local[name]['moving_HELU_mm']+9
  bare=lengths.get(name+'_bare',0);strip=8 if name in ('XS13','XS23','XB12','XB22') else 11
  blank=5*math.ceil((guided+bare+strip+60)/5)
  rows.append(dict(wire=name,sku='HELU'+('23302 red' if name.startswith('XB') and name.endswith('2') else '23301 black' if name.startswith('XB') else '23308 yellow')+'0.5mm2',
   W3_guide_mm=lengths[name],W2_mixed_JR_HELU_upper_bound_mm=local[name]['local_mixed_JR_HELU_guide_mm'],
   W2_moving_and_tail_mm=(local[name]['moving_HELU_mm']+9 if name in ('XB22','XB23','XS23') else 0),
   extra_bare_board_mm=bare,source_strip_or_lap_allowance_mm=strip,trim_allowance_mm=60,
   conservative_continuous_fit_blank_mm=blank,procurement_contribution_mm=5*math.ceil(blank*1.25/5),
   accounting='One continuous HELU per feed. W2 mixed-JR guide is an upper bound, not duplicate JR purchase or a splice at the W2/W3 boundary. Replaces, never adds, W2 local HELU stock contribution. Final cut after unpowered delivered fit.'))
 selection=dict(status='CURRENT_W3_NOMINAL_PROTOTYPE_SELECTED',physical_pass=False,result_id='W3',native=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),prints=n['exports'],
  replaces_prints=['M2 Foundation','W2 UpperCarrier001'],preserves=['M2/W2 YawCarrier unchanged','W2 HeadFixedAnchor/current local paths/moving paths/JR joints','M2 all moving head bodies and provisionalMG92B adapters','W4 boardB3/native fixture','bankR47','P0/E6/15drives/torso325x200x160'],
  feed_ends=[dict(wire=name,source=('F_HY WEST factory output/8mm lap' if name=='XB12' else 'F_HP WEST factory output/8mm lap' if name=='XB22' else 'G_AUX221 port4/11mm untinned strip' if name=='XB13' else 'G_AUX221 port3/11mm untinned strip' if name=='XB23' else 'PWM1608 assigned B1 pad' if name=='XS13' else 'PWM1608 assigned B2 pad'),
   receiving=('W2 fixed yaw local conductor' if name in ('XB12','XB13','XS13') else 'W2 Y85 current fixed tail and constant-length moving loop'),new_joint_at_boundary=False) for name in FEEDS],
  length_stock_rows=rows,grips=g['grips'],new_hardware={'T18I_11102370':g['T18I_new'],'M3':0,'FHAC_new':0,'G_AUX_new':0,'JR_new':0,'SJ4570_reused_matched_pairs':1,'SJ4570_trim_blank_mm':[20,10],'SJ4570_final_pair_mm':[18,10],'RNF100_3_16_9_raw_mm':[20,20]},
  factory_budget=[dict(wire=name,guide_mm=lengths[name],minimum_delivered_usable_mm=84.5,nominal_per_side_mm=100,manufacturer_verified=False) for name in ('F_HY_out','F_HP_out')],
  splices={'lap_mm':8,'individual_raw_sleeve_mm':20,'finished_length_gate_mm':[14,20],'finished_OD_max_mm':4.8,'rule':'Heat off PETG on supported bench. >=3mm intact insulation either side. No common sleeve. Delivered OD/length/heat recovery and solder fit gate.'},
  insulation={'product':'3M Temflex165 retained W4 material','layers':2,'nominal_added_radius_mm':.33,'intact_jacket_overlap_mm':3,'nominal_material_contribution_mm':40,'rule':'Separate formed B1/B2 leads to PCB underside only. Hole/solder face clean. Actual coverage/adhesion/edge separation gate before power.'},
  source_scope='Both FHAC opposite INPUTS retain9mm straight approaches and independent grips; full upstream supply belongs toW5. Three unused G_AUXports reserved, not W1. No invented externalU1 pinout.',
  assembly=['Unpowered bench: prepare both known PCB formed leads and their individual insulation before board seating; retain assigned solder hole access.',
   'Fit the two replacement native bodies using their unchanged mechanical fasteners. Retain W2 yaw carrier. Thread designated band return/side channels before installing cases/boards. No new body screws.',
   'Fit deliveredFHACs on floors, two case bands each; independently grip each intact factory exit/input. Trim reusedSJ4570 pair18x10 for G_AUXcase only.',
   'Prepare both8mm factory/HELU laps off PETG; individual20mm raw sleeves, verify final14..20/OD<=4.8. Do not cut factoryINPUT untilW5 is planned.',
   'Route six continuous nominal feeds in the coupled plan. Source yaw group uses its high bridge, not a post through its previous downleg. Retain qualified W2 joints without an extra jaw on staggered sleeves/taper.',
   'Seat B1/B2 insulation-only clamps on native board carrier. SourceG_AUX ports3/4 share independent intact-insulation grip, not the adhesivecase retention.',
   'Join continuous W2 lengths without a splice at accounting boundaries; keep W2 existing three9mm tails and moving loops unchanged. Final lengths and tension set after delivery.'],
  service=['No power. Routine head ATO: support holder, cut ONLY its two dedicated case bands; nominal22x10x35mm upward tool spaces are qualified. Inspect delivered lid/ATO fit before using in-place access.',
   'If delivered lid motion differs, free the supported holder and its source/output restraints for bench service; do not force a taut wire or claim a connected sweep.',
   'Whole head removal: label/unplug two localJR pairs and free the fixed HELU/source joints. ReleaseG_AUX3/4 on the supported loose case after its insulation band/SJ4570 retention is freed. Known soldered B1/B2 are desoldered on the bench if removal requires it, not pretended plug connections.',
   'Only after all six wires are free, undo retained root/arm fasteners. No routine74WAGO disconnects or attached-wire head lift claimed. Replace cut disposable bands on reassembly.'],
  functional_neck='No upper cosmetic torso installed; functional red return reachesZ160.594, like external neck hardware, no side widening or closed-shell claim.',
  phase2_gates=g['phase2_gates']+['84.5mm usable factory tails/OD4/R6 are delivery assumptions, not catalogL140','Actual JR cavity/polarity, all six end labels, bare/taped pad inspection and manual full travel before power','Global K3/E3 electrical/stock/load approval remainsOPEN; this is a nominal local contribution, not energizing authority'],
  checked_utc=datetime.now(timezone.utc).isoformat(),tool_versions={'native_document_program_version':program,'compatibility':'Self-contained FreeCAD FCStd, native constrained pads/pockets; no external links/addon runtime required by the changed bodies.'},
  measured_worker_seconds={'coupled_space_reused':q['worker_seconds'],'changed_native':n['worker_seconds'],'W2_boundary':b['worker_seconds']})
 save(OUT/'selection.json',selection)
 pins={OUT/name for name in ('selection.json','README.md','.gitattributes','coupled-plan.json','coupled-grips.json','received-grips.json','grip-plan-before-native.py','coupled-checks.json','native-checks.json','boundary-checks.json','HeadSupplyCurrent.FCStd')}
 for receipt in (q,n,b):
  for path,digest in receipt.get('source_sha256',{}).items():
   if receipt is q and path=='tools/cad/plan_current_head_supply_grips.py':
    assert sha(OUT/'grip-plan-before-native.py')==digest
    # Historical whole route/case proof retained byte-for-byte. Current
    # native receipt supersedes all changed grip/material/band interfaces.
    continue
   assert sha(ROOT/path)==digest,path;pins.add(ROOT/path)
 # Reuse only actually unchanged earlier wire/body pairs. The four old
 # failures involved the retired PWM downleg/support or removed GroundPost;
 # the current whole native check qualifies ALL paths against their replacements.
 previous=read(OUT/'plan.json');old=read(OUT/'space-checks.json')
 for name in ('XB12','XB23','XS23'):assert p['routes'][name]==previous['routes'][name],name
 assert {(v['a'],v['b']) for v in old['contacts']}=={('XS13','FoundationSouthWing'),('XS13','FHYFoot'),('XS13','FHYFloor'),('XS23','GroundPost')}
 for name in ('plan.json','space-checks.json','received-checks.json','received-plan.json','service-checks.json','service-plan.json'):
  pins.add(OUT/name)
 for row in read(W2/'manifest.json')['files']:
  path=ROOT/row['path'];assert sha(path)==row['sha256'],path;pins.add(path)
 pins.add(W2/'manifest.json')
 for row in n['exports']:pins.add(ROOT/row['path'])
 for name in ('plan_current_head_supply.py','receive_current_head_supply.py','plan_current_head_supply_service.py','plan_current_head_supply_coupled.py','plan_current_head_supply_grips.py','build_current_head_supply.py','qualify_current_head_supply_boundary.py','package_current_head_supply.py'):pins.add(ROOT/'tools/cad'/name)
 pins.add(ROOT/'tests/test_current_head_supply.py')
 for path in OUT.glob('*_Coupled.brep'):pins.add(path)
 manifest=dict(schema_version=1,readiness='prototype',result_id='W3',physical_pass=False,files=[dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)) for path in sorted(pins)],
  tool_versions=selection['tool_versions'],
  gates={gate:dict(status='open',reason='Delivered unpowered fit/phase2, not physical approval') for gate in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='Whole six-feed paths,8independent cut native grips,4case bands, individual formed-end insulation, ATO tool spaces, current boundaries,2editable/closed replacement prints and parameter/relocated reopen. Unchanged route/case proof retains exact archived allocation source; current native receipt supersedes every changed grip/material/band interface.',evidence=[(OUT/name).relative_to(ROOT).as_posix() for name in ('coupled-checks.json','native-checks.json','boundary-checks.json')])
 assert verify(ROOT,manifest)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
 if 'W3' not in score['confirmed_result_ids']:
  assert score['result_count']==9;score['confirmed_result_ids'].append('W3')
  score['previous_evidence']={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
 else:assert score['result_count']==10 and score['new_result']=='W3'
 score.update(result_count=10,result_percent=50,change_pp=5,new_result='W3',evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat())
 save(BASE/'current-phase1-score.json',score);print(json.dumps(dict(percent=50,pins=len(pins),seconds=time.monotonic()-tick)))
if __name__=='__main__':run()
