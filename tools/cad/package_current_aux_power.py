"""Fail-closed selection of the complete W1 interface, not a partial score."""
import copy,json,math,time,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
from package_current_head_wiring import ROOT,BASE,sha,read,save,verify,REQUIRED_GATES
OUT=BASE/'aux-wiring-checkpoint'
FEEDS=('XA02','XA03','XA04','XA05','XA06','XB11')

def save(path,value):
 path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')

def archive_retained_inputs(pins):
 tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
 old=sorted(f for f in pins if f.relative_to(ROOT).as_posix() not in tracked and not f.is_relative_to(OUT)
            and f.suffix=='.brep')
 archive=OUT/'retained-inputs.zip';rows=[]
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for f in old:
   name=f.relative_to(ROOT).as_posix();info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
   rows.append(dict(path=name,sha256=sha(f)))
 save(OUT/'retained-inputs.json',dict(status='EXACT_RETAINED_INPUT_ARCHIVE_NOT_NEW_GEOMETRY',
  files=rows,zip_sha256=sha(archive),
  reason='Necessary existing BRep inputs were untracked before this milestone. Preserve their original paths untouched and commit exact byte snapshots, not foreign workspace changes.',
  replay='tools/cad/restore_current_aux_inputs.py --verify-only; omit flag only in a checkout missing these inputs. Existing differing files are never overwritten.'))
 pins.update((archive,OUT/'retained-inputs.json',ROOT/'tools/cad/restore_current_aux_inputs.py'))
 return {r['path'] for r in rows}

def inherited_tail_metadata():
 original=BASE/'tail-wiring-checkpoint/manifest.json';m=read(original)
 report=verify(ROOT,m)
 if report['integrity_ok']:return original
 assert report['errors']==['Hash mismatch: tests/.gitattributes'],report
 archive=OUT/'inherited-tail-test-attributes.txt'
 row=next(r for r in m['files'] if r['path']=='tests/.gitattributes')
 assert sha(archive)==row['sha256']=='adc42694124efa6f61e7d67378bc060c9458581b2ded4421d37039cb716eaf2a'
 current=ROOT/'tests/.gitattributes'
 lines=current.read_text().splitlines();old=archive.read_text().splitlines()
 assert lines[:len(old)]==old
 assert all(v.startswith('test_current_head_') and v.endswith('.py text eol=lf') for v in lines[len(old):])
 reconciled=copy.deepcopy(m)
 entry=next(r for r in reconciled['files'] if r['path']=='tests/.gitattributes')
 entry['sha256']=sha(current)
 reconciled['files'] += [dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f)) for f in (original,archive)]
 reconciled['metadata_reconciliation']=dict(original_manifest_sha256=sha(original),
  original_attributes_sha256=row['sha256'],current_attributes_sha256=sha(current),
  reason='Append-only LF rules for unrelated later head tests. Original W4 rule is byte-identical, archived and hashed. Every original engineering/test file retains its exact hash; no geometry verdict refreshed.')
 assert verify(ROOT,reconciled)['integrity_ok']
 dest=OUT/'inherited-tail-manifest.json';save(dest,reconciled);return dest

def ready(q,s,n):
 return (q.get('status')=='SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN'
  and s.get('status')=='SOLID_CLEARANCE_ONLY_MOUNTS_OPEN'
  and n.get('status')=='CURRENT_NATIVE_W1_PREPARED'
  and q.get('insulation_included') is True
  and all(not r.get('contacts') and not r.get('errors') for r in (q,s,n))
  and not s.get('reservation_conflicts') and len(n.get('exports',[]))==3
  and n.get('native_parameter_restore') and n.get('fresh_relocated_reopen')
  and all(v<1e-5 for v in n.get('removed_retained_material_mm3',{'missing':1}).values()))

def joint_coverage(p):
 result={}
 for name,factory,custom_start in [('XA02','F_AUX_factory_out',True),('XB11','F_HY_factory_in',False)]:
  spec=p['factory_custom_joints'][name];f=p['routes'][factory]['parts'][-1]
  c=p['routes'][name]['parts'][0 if custom_start else -1]
  ft=f['end'];ct=c['start' if custom_start else 'end']
  assert ft==spec['factory_tip_mm'] and ct==spec['custom_tip_mm'],name
  axis=next(i for i in range(3) if abs(ft[i]-ct[i])>1e-8)
  assert all(abs(ft[i]-ct[i])<1e-8 for i in range(3) if i!=axis),name
  lap=spec['strip_each_mm'];assert abs(abs(ft[axis]-ct[axis])-lap)<1e-7,name
  # Both bare intervals must end at the OTHER tip, not overlap somewhere
  # in the middle of the jacketed routes.
  inner_f=f['start'];inner_c=c['end' if custom_start else 'start']
  def endpoint(tip,inside):
   length=math.dist(tip,inside);assert length>=lap
   return [tip[i]+(inside[i]-tip[i])*lap/length for i in range(3)]
  assert math.dist(endpoint(ft,inner_f),ct)<1e-7,name
  assert math.dist(endpoint(ct,inner_c),ft)<1e-7,name
  sleeve=p['routes'][name+'_sleeve']['parts'];lo,hi=sorted([sleeve[0]['start'][axis],sleeve[-1]['end'][axis]])
  cover=[min(ft[axis],ct[axis])-lo,hi-max(ft[axis],ct[axis])]
  assert min(cover)>=3 and hi-lo<=spec['sleeve_raw_mm'],name
  result[name]={'opposed_end_lap_mm':lap,'nominal_jacket_coverage_mm':cover,'raw_sleeve_mm':spec['sleeve_raw_mm']}
 return result

def run():
 tick=time.monotonic();q=read(OUT/'grip-checks.json');s=read(OUT/'whole-layout-solid-checks.json');n=read(OUT/'native-checks.json')
 b=read(OUT/'bank-boundary-checks.json')
 disposition=read(OUT/'bank-owner-disposition.json')
 assert disposition['status']=='HISTORICAL_BANK_REFERENCE_NOT_CURRENT_FIT_PROOF'
 assert ready(q,s,n),'Whole W1 not qualified; do not select or award a point'
 p=read(OUT/'whole-layout-plan.json');g=read(OUT/'grip-plan.json');c=read(OUT/'whole-layout-preflight.json')
 terminals=read(OUT/'terminal-data.json')
 source_strip=terminals['221-615']['nominal_stock_strip_mm']
 source_blank=c['lengths_mm']['XA01_factory']+source_strip
 assert 12<=source_strip<=14 and source_blank<=50,'Actual221-615 strip exceeds source-length gate'
 coverage=joint_coverage(p)
 assert not c['contacts'] and not c['errors'] and set(FEEDS)<=set(p['routes'])
 model=OUT/'AUXPowerCurrent.FCStd';assert sha(model)==n['model_sha256']
 ends={'XA02':['F_AUX.OUT supported8mm factory/custom lap','Pololu4092 VIN component-side solder'],
  'XA03':['Pololu4092 VOUT component-side solder','P_AUX.2 untinned11mm strip'],
  'XA04':['Pololu4092 GND component-side solder','G_AUX.2 untinned11mm strip'],
  'XA05':['G2.5 untinned11mm strip','G_AUX.1 untinned11mm strip'],
  'XA06':['G_AUX.5 untinned11mm strip','G_TAIL.1 untinned11mm strip'],
  'XB11':['P_AUX.1 untinned11mm strip','F_HY.INPUT supported8mm factory/custom lap']}
 rows=[]
 for name in FEEDS:
  guided=c['lengths_mm'][name];formed=max(0,c['lengths_mm'].get(name+'_bare',3)-3)
  strip=0 if name=='XA02' else 22 if name in ('XA05','XA06') else 11
  blank=5*math.ceil((guided+formed+strip+60)/5)
  rows.append(dict(wire=name,sku='HELU23501' if name in ('XA04','XA05','XA06') else 'HELU23502',section_mm2=1,
   guided_mm=guided,extra_formed_bare_mm=formed,additional_WAGO_strip_mm=strip,trim_allowance_mm=60,
   nominal_fit_blank_mm=blank,procurement_contribution_mm=5*math.ceil(blank*1.25/5),
   accounting='Replaces historical R19/R20 contribution; no additional wire at layer/owner boundaries. Factory/custom8mm overlap already included in guide. Formed bare and jacket overlap3mm counted once. Cut only after delivered unpowered dry fit.'))
 selection=dict(status='CURRENT_W1_NOMINAL_PROTOTYPE_SELECTED',result_id='W1',physical_pass=False,native=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),prints=n['exports'],
  feed_ends=[dict(wire=k,ends=v) for k,v in ends.items()],length_stock_rows=rows,
  additional_source_prefix=dict(wire='XA01',source='P_REAR.1 same BAT_SW rail',factory_route_mm=c['lengths_mm']['XA01_factory'],source_strip_mm=source_strip,complete_unfused_blank_mm=source_blank,maximum_unfused_mm=50,not_additional_custom_HELU=True,delivered_length_measurement_required=True,supersedes_historical_11mm_accounting=True),
  factory_budget=c['factory_budgets'],joint_coverage=coverage,grips=g['grips'],new_hardware={'T18I_11102370':g['T18I_new'],'M3':0,'FHAC_new':0,'WAGO_new':0,'SJ4570_reused_matched_pairs':2,'SJ4570_pair_trim_mm':[18,10],'RNF100_3_16_9_raw_mm':[18,20]},
  board_end_insulation={'material':'3M Temflex165','layers':2,'nominal_added_radius_mm':.33,'jacket_overlap_mm':3,'nominal_material_contribution_mm':60,'supplier_revision_and_solder_land_fit_gate':True},
  sleeves={'joints':p['factory_custom_joints'],'finished_OD_max_mm':4.8,'lap_mm':8,'rule':'Individual insulated opposed END strips soldered off PETG, >=3mm intact insulation each side. XA02 raw18mm must finish16..18mm; XB11 raw20mm must finish14..20mm. Coverage and delivered shrink are phase2 gates. No shared bare junction.'},
  circuit_rules='BAT_SW before AUX4092, AUX6 after it; separate AUX/platform power returns. No MAIN/AUX positive bridge or invented externalU1 pinout.',
  replaces=['W3 Foundation print only: retained geometry/material and head functions unchanged','W3 UpperCarrier001 print only','W4 E2Fixture print only','P_AUX/G2 case poses and case adhesion','W4 paired-source-ground tie locking head envelope, same existing band/wires'],
  preserves=['P0','E6','15 drives','replaceable provisionalMG92B','bankR47','W2/W3/W4 conductors and all retained material','existing E2 board/connector and both factory module leads','325x200x160 torso sides'],
  assembly=p['assembly']+['Install three matched native replacements, reusing all retained screws/nuts. Thread all band side/return channels before cases/boards. Case retention is not wire relief.',
   'Prepare two individual8mm factory/custom laps and three formed board ends on supported bench; heat shrink off PETG. No full1mm2 conductor through1.02mm drill.',
   'Retain16new wire/case ties, two reused SJ4570 pairs trimmed18x10; W4 common band uses its locking head on TOP. Inspect and replace a damaged old tie, do not count it as a new mandatory tie.'],
  service=[g['service'],'F_AUX routine service: cut two dedicated body straps only; use qualified nominal SOUTH22x35x10mm lid/tool space, not through either factory output. Delivered hinge/ATO/puller check remains open.',
   'Other ATO service under an overhead free arch: remove all sources, label and free only the crossing W1 conductor at its assigned supported WAGO or bench joint, release its dedicated ties, then move that disconnected wire aside. No connected sweep or routine74WAGO disconnects claimed.',
   'For board replacement, support and desolder the three known component-side joints on the bench; no fictitious plug or pulling on solder pads. Release case adhesion and wire ties separately before floor removal.'],
  open_prototype_limit='Upper cosmetic shell omitted. Free wire arches reach185mm; no closed160mm shell fit claim, no side widening. Delivery fit/creep/insulation/manual motion and global E3/K3 remain open.',
  phase2_gates=['Delivered supplier PCB registration and component-side solder lands; no bridges/loose strands','Actual FHAC factory OD/length/R/lid travel;100mm per side is not catalogL140','Actual WAGO levers/entry11mm, tie pressure, PETG edge deburr/creep and adhesive retention','Individual sleeves/tape coverage and unplugged continuity/polarity/pull inspection','Global source/fault/thermal E3 approval before any power'],
  bank_ownership=disposition,
  measured_worker_seconds={'joint_support':q['worker_seconds'],'changed_routes_cases':s['worker_seconds'],'native':n['worker_seconds'],'bank_boundary':b['worker_seconds']},checked_utc=datetime.now(timezone.utc).isoformat())
 save(OUT/'selection.json',selection)
 pins={OUT/name for name in ('selection.json','README.md','.gitattributes','whole-layout-plan.json','whole-layout-preflight.json','whole-layout-solid-checks.json','grip-plan.json','grip-checks.json','native-checks.json','AUXPowerCurrent.FCStd')}
 pins.add(OUT/'terminal-data.json');pins.add(OUT/'bank-owner-disposition.json');pins.add(OUT/'bank-boundary-checks.json');pins.add(ROOT/'tools/cad/check_current_aux_bank_boundary.py')
 pins.add(ROOT/'tools/cad/whole_cat_interior.py')
 for receipt in (q,s,n,b):
  for path,digest in receipt['source_sha256'].items():
   assert sha(ROOT/path)==digest,path;pins.add(ROOT/path)
 for row in n['exports']:pins.add(ROOT/row['path'])
 for name in ('plan_current_aux_wiring.py','plan_current_aux_grips.py','build_current_aux_power.py','package_current_aux_power.py'):pins.add(ROOT/'tools/cad'/name)
 pins.add(ROOT/'tests/test_current_aux_power.py')
 pins.add(ROOT/'.gitattributes')
 for folder in ('head-supply-checkpoint','tail-wiring-checkpoint','pwm-branch-checkpoint'):
  path=inherited_tail_metadata() if folder=='tail-wiring-checkpoint' else BASE/folder/'manifest.json'
  manifest=read(path);assert verify(ROOT,manifest)['integrity_ok'],folder
  pins.add(path)
  if folder=='tail-wiring-checkpoint':
   pins.add(BASE/folder/'manifest.json');pins.add(OUT/'inherited-tail-test-attributes.txt');pins.add(ROOT/'tests/.gitattributes')
 archived=archive_retained_inputs(pins)
 manifest=dict(schema_version=1,readiness='prototype',result_id='W1',physical_pass=False,
  files=[dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f)) for f in sorted(pins)],
  retained_input_archive_paths=sorted(archived),
  tool_versions={'native':'FreeCAD1.1.3 Windows py311','compatibility':'Self-contained editable constrained PartDesign bodies; no external links required by changed bodies.'},
  gates={gate:dict(status='open',reason='Delivered phase2 prototype gate, no physical approval') for gate in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='Local W1 scope: six-current-conductor routing, factory inputs/output/lap budgets, independent grips, complete native material/slots/bands, side-service space, head poses,3closedSTLs, parameter/relocated reopen; inherited receiving material retained. Current W5 bank retention is open; historical raw bank poses are NOT a current fit proof.',evidence=[(OUT/name).relative_to(ROOT).as_posix() for name in ('whole-layout-solid-checks.json','grip-checks.json','native-checks.json','bank-owner-disposition.json')])
 assert verify(ROOT,manifest)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
 if 'W1' not in score['confirmed_result_ids']:
  assert score['result_count']==10
  score['confirmed_result_ids'].append('W1');score['previous_evidence']={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
 else:assert score['result_count']==11 and score['new_result']=='W1'
 score.update(result_count=11,result_percent=55,change_pp=5,new_result='W1',evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat())
 save(BASE/'current-phase1-score.json',score);print(json.dumps(dict(percent=55,pins=len(pins),seconds=time.monotonic()-tick)))

if __name__=='__main__':run()
