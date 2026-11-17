"""Receipt for this folder only. No shared plan/runtime/assembly writes."""
from pathlib import Path
import json,hashlib,zipfile,csv
from datetime import datetime,timezone
P=Path(__file__).parent;BASE=P.parent/'day17-night-common-body-mounts';MECH=P.parents[7]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def pin(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
native=P/'body-closure-interface.FCStd';baseline=BASE/'common-body-mounts.FCStd'
assert sha(baseline)=='4a4cb1fd1534e594bece855a8ff49aa8f29b2a532df518e14d52878cc7531361', 'Frozen source native changed'
gate=json.loads((P/'independent-MIC-export-gate.json').read_text(encoding='utf-8'))
mass=json.loads((P/'actual-candidate-print-material.json').read_text(encoding='utf-8'))
raw=json.loads((P/'raw-before-functional-cowl-clearances.json').read_text(encoding='utf-8'))
final=json.loads((P/'actual-native-final-save.json').read_text(encoding='utf-8'))
equiv=json.loads((P/'four-source-serialization-vs-geometry.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(native) as a,zipfile.ZipFile(baseline) as b:
 names=[n for n in b.namelist() if n.endswith(('.brp','.brep'))]
 changed=[n for n in names if n not in a.namelist() or a.read(n)!=b.read(n)]
 integrity={'native':pin(native),'zip_entries':len(a.infolist()),'zip_bad_member':a.testzip(),'baseline':pin(baseline),'baseline_geometry_members':len(names),'byte_identical_geometry_members':len(names)-len(changed),'changed_geometry_serializations':changed,'four_source_geometric_equivalence':equiv,'intentional_source_geometry_change':'CB_REMOVABLE_BUS_E1_BRIDGE, MIC extension only; four other serializations have actual bidirectional material comparison. NOT claimed all byte-identical.'}
put('native-integrity.json',integrity)
refs=[baseline,BASE/'manifest.json',BASE/'sourcepins.json',BASE/'N1_common_front_PCB_frame.brep',BASE/'N2_BUS_E1_liftoff_bridge.stl',BASE/'N3_PSYS_open_keeper.stl',BASE/'N4_MTA_lower_access_frame.stl',BASE/'N5_rear_POST_receiver.stl',BASE/'N6_POST_open_keeper.stl']
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical')
refs += [root/'hardware/reference/head-electronics-2026-09-22/measurements.json',root/'hardware/reference/appearance/ola-cat-reference.jpg',root/'hardware/reference/manual-stop-p0-2026-09-24/S821-A120.png',root/'hardware/reference/manual-stop-p0-2026-09-24/toggle_S.pdf']
put('sourcepins.json',{'baseline_commit':'ebd214b6de7013a3500f89a777fd7d12758c7cec','pins':[pin(p) for p in refs if p.exists()],'geometry_copytrace_not_serial_identity':True,'unchanged_sources_not_rehydrated_or_reaudited':True})
rows=[]
for p in mass['parts']:
 row={'source_object':p['name'],'qty':1,'status':p['status'],'file':None,'dimensions_mm':[p['bounds'][i+3]-p['bounds'][i] for i in range(3)],'full_PETG_equivalent_g':p['full_PETG_equivalent_g']}
 if p['name']=='CB_REMOVABLE_BUS_E1_BRIDGE' and gate['conditional_nominal_dryfit_release']:row.update(file='N2_BUS_E1_MIC_common_bridge.stl',orientation=gate['mesh']['orientation'],brim_support_allowance_mm=8,under256=True,stage='Independent unpowered primary-hole FIT3 before any body closure')
 rows.append(row)
put('current-print-index.json',{'new_parts':rows,'N1':'NO_STL_SOURCE_TECHNICAL_OPEN_MESH','unchanged_prints_reference_sourcepins_only':True,'wholekit':False,'physicalPASS':False})
with (P/'needed-hardware.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['role','qty','standard_demand','status','note'])
 w.writerow(['MIC diagonal mounts',2,'M2x12 socket head; D3.8/k2 nominal','NEEDED_UNCONFIRMED','Full shaft12; underheadZ140.5; tip152.5'])
 w.writerow(['MIC washers',4,'M2 OD5 ID2.2 t0.5','NEEDED_UNCONFIRMED','Two per bolt; no second standoff'])
 w.writerow(['MIC nuts',2,'M2 full AF4 h1.6','NEEDED_UNCONFIRMED','Z149.595..151.195; tip1.305'])
 w.writerow(['BUS/E1 bridge existing roots',2,'Existing full M3x16 sets from sourceebd','SOURCE_NOMINAL_REUSED','No extra joint/purchase; all washers/fullnuts remain'])
 w.writerow(['Body base joints',6,'Existing complete M3x10 hex sets from source82/ebd','SOURCE_RETAINED_NEW_BODY_NOT_QUALIFIED','No new crown fastener demand; crown slip keys only'])
body=[r for r in mass['parts'] if r['name'].startswith('HB_')];lo=[min(r['bounds'][i] for r in body) for i in range(3)];hi=[max(r['bounds'][i+3] for r in body) for i in range(3)]
put('current-disposition.json',{'input':'01a1e7c7-40f3-78b1-b2ee-d279af180781','result':'INDEPENDENT_MIC_BRIDGE_CONDITIONAL_DRYFIT; WHOLE_BODY_CLOSURE_HOLD','body_cad_hollow_material_real':True,'body_outer_bounds':lo+hi,'body_dimensions':[hi[i]-lo[i] for i in range(3)],'body_all_fragments_full_PETG_g':sum(r['full_PETG_equivalent_g'] for r in body),'MIC_conditional_dryfit':gate['conditional_nominal_dryfit_release'],'raw_finite_body_checks':len(raw['rows']),'raw_failed_relations':len(raw['failures']),'raw_checks_NOT_claimed_current_after_partial_reliefs':True,'three_causal_interfaces':['new belly vs actual source chassis','new belly/keys vs current decks/common receivers','Pi whole port/cooling layer and integrated fairing'],'failed_guard_offsets_NOT_clearance':True,'new_body_STL_release':False,'next_whole_decision':'Use actual continuous P02/P03 floor as the electronics bottom and allocate ONE real side/end cowl mating interface around CURRENT receivers + Pi endregions. Do not preserve the new ellipse underside or treat an unbuilt root as physical FIT.','operator_audio_realized':['MIC two diagonal primary-hole posts+complete M2sets on real BUS/E1 bridge'],'operator_audio_NOT_realized':['speaker basket retention','TTP safe adjustable support','S1 actual panel datum/capture','monitor case capture'],'headloom_MTA4_and_other_stock':'OPEN same source contracts; no new cut/slack credit','visual_assessment':'NEGATIVE/NOT_ACCEPTED: actual front neck remains a large opening, body still reads long/heavy relative to head, tail mostly buried. Curved surfaces do not qualify Ola appearance.','new_body_not_claimed_smaller_than_source_provisional_envelope':True,'wholekit':False,'appearance_accepted':False,'physicalPASS':False,'actual_fit_cut_slack':None})
put('own-progress.json',{'input':'01a1e7c7-40f3-78b1-b2ee-d279af180781','utc':datetime.now(timezone.utc).isoformat(),'status':'COMPLETED_BOUNDED_PARTIAL_WITH_BODY_HOLD','last_actual_usage_read':'2026-11-17T05:37:17Z','ordinary_allowed':True,'weekly_used_percent_observed':36,'no_percent_guard_or_reset':True,'owned_compute':'IDLE','pending':None,'unsaved':False,'shared_files_written':False})
put('own-receipt.json',{'input':'01a1e7c7-40f3-78b1-b2ee-d279af180781','result':'Conditional MIC/BUS/E1 common print; body+N1 not released','native':final,'source_commit':'ebd214b6de7013a3500f89a777fd7d12758c7cec','sourcepins':'sourcepins.json','printindex':'current-print-index.json','material':'actual-candidate-print-material.json','geometry_source_equivalence':'four-source-serialization-vs-geometry.json','wholekit':False,'appearance_accepted':False,'physicalPASS':False,'actual_fit_cut_slack':None,'shared_plan_runtime_currentassembly_untouched_by_owner':True,'git_commit':'actual verified narrow commit reported at bounded return; no self-referential hash'})
# UTF8/LF for OWN authored text only. Never rewrite BRep, mesh, native, or source binaries.
for p in P.iterdir():
 if p.suffix.lower() in ['.py','.json','.md','.csv']:p.write_bytes(p.read_text(encoding='utf-8').replace('\r\n','\n').encode('utf-8'))
files=[]
for p in sorted(P.iterdir()):
 if p.is_file() and (p.suffix.lower() in ['.py','.json','.md','.csv','.png','.stl','.brep'] or p.name=='body-closure-interface.FCStd') and p.name!='manifest.json':files.append({'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
put('manifest.json',{'input':'01a1e7c7-40f3-78b1-b2ee-d279af180781','utc':datetime.now(timezone.utc).isoformat(),'files':files,'release':'ONE independent nominal MIC/BUS/E1 bridge conditional; body and N1 HOLD; NOTwholekit','backups':'All FCStd backups preserved locally, excluded from this receipt'})
print(json.dumps({'files':len(files),'manifest_sha256':sha(P/'manifest.json'),'native_sha256':sha(native),'zip_entries':integrity['zip_entries'],'body_g':sum(r['full_PETG_equivalent_g'] for r in body),'new_print_release':gate['conditional_nominal_dryfit_release'],'changed_source_serializations':changed}))
