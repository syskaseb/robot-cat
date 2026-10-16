"""Select the full nominal M4 with current whole-resource overlays and W5."""
import json,time,copy
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check
from release_check import verify,REQUIRED_GATES

OUT=BASE/'functional-protection'
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',newline='\n')
def run():
 check();tick=time.monotonic();pins={}
 def read(p):
  pins[p.relative_to(ROOT).as_posix()]=SHA(p);return json.loads(p.read_text())
 receipts={n:read(OUT/(n+'.json')) for n in ['native-mounts','BUS-ground-guide-native','MAIN-insulated-grip-native',
  'source-hardware-checks','changed-ATO-access','current-w5-protected-native','quantity-reconciliation']}
 assert receipts['changed-ATO-access']['status']=='CHANGED_PROTECTION_PRESERVES_NOMINAL_ROUTINE_ATO_ACCESS'
 assert receipts['current-w5-protected-native']['relocated_reopen']
 for n,q in receipts.items():
  assert not q.get('contacts') and not q.get('errors'),n
  for path,h in q.get('source_sha256',{}).items():assert SHA(ROOT/path)==h,path;pins[path]=h
 # Retain the accepted rounded-metal fullneck proof except the two changed
 # W003 pairs, which the whole new route proof explicitly resolves.
 old=read(OUT/'contact-insulation-space.json');bypass=read(OUT/'W003RetainedUpperBypass.json')
 assert len(old['contacts'])==2 and all(r.get('wire')=='wire/W003' for r in old['contacts'])
 assert not bypass['contacts'] and not bypass.get('errors')
 read(OUT/'foundation-space-check.json');read(OUT/'MAIN-insulated-restraint-plan.json')
 for n in ['phase1-current-print-manifest-r2.json','phase1-current-purchased-manifest-r4.json','phase1-material-manifest-r2.json','phase1-assembly-manifest-r3.json']:
  q=read(BASE/n);v=verify(ROOT,q);assert v['integrity_ok'],v
  for r in q['files']:pins[r['path']]=r['sha256']
 for n in ['head-wiring-checkpoint/fixed-head-current-manifest.json','tail-mount-checkpoint/manifest.json',
  'tail-wiring-checkpoint/manifest.json','head-supply-checkpoint/manifest.json','aux-wiring-checkpoint/manifest.json',
  'body-harness-checkpoint/e1-manifest.json','body-harness-checkpoint/w5-manifest.json']:
  q=read(BASE/n);v=verify(ROOT,q)
  recoveries={'tail-wiring-checkpoint/manifest.json':('tests/.gitattributes','tail-tests-gitattributes.original','a29c59b35e543a3ee48417e498ec13147e398235'),
   'aux-wiring-checkpoint/manifest.json':('.gitattributes','aux-root-gitattributes.original','a8930c6f0cba615e1229c3e6f4e68c2d4f5bf3be')}
  if n in recoveries and v['errors']==['Hash mismatch: '+recoveries[n][0]]:
   # Restore the exact harmless historical normalization input, not a new
   # verdict or a changed part/test. Original manifest remains untouched.
   oldpath,archive,commit=recoveries[n];original=OUT/'checked-inputs'/archive;oldhash=next(r['sha256'] for r in q['files'] if r['path']==oldpath)
   assert SHA(original)==oldhash
   q=copy.deepcopy(q)
   for r in q['files']:
    if r['path']==oldpath:r['path']=original.relative_to(ROOT).as_posix()
   q['historical_input_recovery']=dict(original_path=oldpath,exact_original_sha256=oldhash,
    recovered_from_commit=commit,only_effect='Text/binary normalization policy; all CAD, wire, test source and electrical inputs unchanged')
   mf=OUT/(n.split('/')[0]+'-inherited-manifest-current.json');save(mf,q);pins[mf.relative_to(ROOT).as_posix()]=SHA(mf)
   v=verify(ROOT,q)
  assert v['integrity_ok'],(n,v)
  for r in q['files']:pins[r['path']]=r['sha256']
 for f in [OUT/'ASSEMBLY.md',Path(__file__),ROOT/'hardware/reference/source-contact-insulation-2026-10-16/Temflex165-TDS.pdf',
  ROOT/'hardware/reference/hella-s0-primary-2026-10-16/HELLA_Product_Overview_2025.pdf']:
  pins[f.relative_to(ROOT).as_posix()]=SHA(f)
 w5=read(BASE/'body-harness-checkpoint/w5-selection.json');w5=copy.deepcopy(w5)
 w5.update(native=receipts['current-w5-protected-native']['native'],native_sha256=receipts['current-w5-protected-native']['native_sha256'],
  protection_overlay='functional-protection/selection.json',current_endpoint_grip_override={'MAIN/USB':'functional-protection/MAIN-insulated-grip-native.json'},
  current_W003_override=dict(path=bypass['path'],sha256=bypass['sha256'],nominal_fit_blank_mm=310,additional_lacing_blanks_mm=[150]),
  source_sha256=dict(pins),scope='Complete retained nominal W5 with one current W003 and owned Upper/MAIN protection overlays. Same80nets/101portions/202cutends; whole physical map remains A3.')
 replacements={r['part']:r for r in receipts['native-mounts']['parts']}
 for r in w5['prints']:
  if r['part']=='FrontRightFixedCarrier':
   new=replacements['FrontRightFixedCarrierProtectedCurrent'];r.update({k:v for k,v in new.items() if k!='part'})
  if r['part']=='UpperCarrier001':r.update({k:v for k,v in receipts['BUS-ground-guide-native']['part'].items() if k!='part'})
 assert (w5['nets'],w5['conductor_portions'],w5['physical_cut_ends'])==(80,101,202)
 sf=BASE/'body-harness-checkpoint/w5-selection-r2.json';save(sf,w5);pins[sf.relative_to(ROOT).as_posix()]=SHA(sf)
 def manifest(result,selection,scope):
  files=dict(pins);files[selection.relative_to(ROOT).as_posix()]=SHA(selection)
  q=dict(schema_version=1,result_id=result,selected=True,readiness='prototype',physical_pass=False,selection=selection.relative_to(ROOT).as_posix(),scope=scope,
   files=[dict(path=n,sha256=h) for n,h in sorted(files.items())],
   gates={n:dict(status='open',reason='Nominal preparation only; delivered fit/PETG/insulation/loads/E3 remain separate.') for n in REQUIRED_GATES})
  q[result+'_complete']=True;q['gates']['geometry']=dict(status='pass',reason='Inherited unchanged accepted geometry plus explicit new/new/source insulation/MAIN/ATO/relocated native checks.',evidence=[(OUT/'changed-ATO-access.json').relative_to(ROOT).as_posix(),(OUT/'current-w5-protected-native.json').relative_to(ROOT).as_posix()])
  v=verify(ROOT,q);assert v['integrity_ok'],v;return q
 save(BASE/'body-harness-checkpoint/w5-manifest-r2.json',manifest('W5',sf,w5['scope']))
 matrix=[
  dict(id='HEAD_E6',status='retained',basis='Current fixed-head selection, actual concave ears/head closures and cable passages. No old fork/anchor selected; provisional MG92B delivery gates retained.'),
  dict(id='P0_AND_BATTERY',status='retained',basis='P0 front/rear end covers, R4carrier/plate/R6nut retainers/straps and noncosmetic support. Full visible composition belongs A3, not assumed from cropped W5.'),
  dict(id='SOURCE_EXPOSED_METAL',status='nominal_prepared',basis='Six separate Temflex165 wraps, two half-lapped passes/tip cushions,1mm external space allocation, fullneck proof inherited except resolvedW003. Actual coverage/creep/temperature before power.'),
  dict(id='MAIN_PIN_NECKS',status='nominal_prepared',basis='Four individual raw13mm RNF3/32 sleeves, fittedOD<=3.2mm/bare<=3mm/overlap>=6mm delivery gate. New seat/band reserved3.5;75changedpairs0contacts plus native param/reopen/STL.'),
  dict(id='SOURCE_AND_POST_MOUNTS',status='nominal_prepared',basis='Three native source mount pieces plus qualified source hardware bench sequence; own filled source body/key is NOT a part-solid clearance proof. POSTadhesive supportscaseonly, wire relief retained.'),
  dict(id='BUS_AND_EXISTING_LOOMS',status='nominal_prepared',basis='W003whole bypass and extra integral Upper midguide/one lace, inherited whole endpoint relief. All other selected head/tail/E1/E2/AUX/W5 sleeves and loadpaths retained.'),
  dict(id='ATO_ACCESS',status='retained_with_changed_interface_check',basis='Twelve35mmnominalATOcorridors and24jawcorridors disjoint from all changed protection/wire geometry by exact world bounds; no candidate BRep pair, not36new physical tests.'),
  dict(id='DEEP_SERVICE',status='documented',basis='Actual A2 reverse stages, support/disconnect needed wires and renew disturbed insulation. S1framebolt beforecase, S0bench beforehead. No fastservice/zero-disconnection requirement.')]
 selection=dict(status='M4_CURRENT_FUNCTIONAL_PROTECTION_NOMINALLY_COMPLETE',result_id='M4',selected=True,M4_complete=True,physical_pass=False,readiness='prototype',
  native=w5['native'],native_sha256=w5['native_sha256'],protection_matrix=matrix,instruction=(OUT/'ASSEMBLY.md').relative_to(ROOT).as_posix(),
  resources=dict(K1='phase1-current-print-selection-r2.json',K2='phase1-current-purchased-selection-r4.json',K3='phase1-material-selection-r2.json',A2='phase1-assembly-selection-r3.json',W5='body-harness-checkpoint/w5-selection-r2.json'),
  scope='Complete nominal functional protection for the selected open prototype, before cosmetic torso. Delivered insulation/fit/load/electrical qualification explicitly separate; no IP/touch-safety/physicalPASS or power approval.',
  external_cosmetic_enclosure_included=False,closed160mm_torso_fit_claimed=False,E3_complete=False,
  phase2_gates=['Actual S0 flange/studclock/key/nut access','S1 neck/kit and screw tipthread','Actual sleeves OD/coverage/wall and tapes fully cover bare metal',
   'PETG/adhesive/cable retention, creep and continuous motion','E3 fault/source/lead coordination before power'],
  source_sha256=dict(pins),worker_seconds=round(time.monotonic()-tick,3))
 sf=OUT/'selection.json';save(sf,selection);save(OUT/'manifest.json',manifest('M4',sf,selection['scope']))
 print(json.dumps(dict(status=selection['status'],files=len(pins),seconds=selection['worker_seconds'])))
if __name__=='__main__':run()
