"""Current M3 repair and A3 exact-byte payload; never award electrical E3."""
import json,copy,time,zipfile,hashlib
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check
from release_check import verify,REQUIRED_GATES
OUT=BASE/'phase1-whole-assembly'
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',newline='\n')
def run():
 check();tick=time.monotonic();pins={}
 def read(p):pins[p.relative_to(ROOT).as_posix()]=SHA(p);return json.loads(p.read_text())
 native=read(OUT/'native-composition-r2.json');added=read(OUT/'added-interface-checks-r2.json')
 assert native['relocated_reopen'] and native['installed_prints']==117 and native['native_link_count']==27
 assert added['status']=='WHOLE_ADDED_BATTERY_TAIL_INTERFACES_CLEAR' and not added['contacts']
 for q in (native,added):
  for n,h in q['source_sha256'].items():assert SHA(ROOT/n)==h,n;pins[n]=h
 for name in ['phase1-current-print-manifest-r4.json','phase1-current-purchased-manifest-r4.json','phase1-material-manifest-r4.json',
  'phase1-assembly-manifest-r5.json','body-harness-checkpoint/w5-manifest-r2.json','functional-protection/manifest.json']:
  m=read(BASE/name);v=verify(ROOT,m);assert v['integrity_ok'],(name,v)
  for r in m['files']:pins[r['path']]=r['sha256']
 for n in ['direct-frame-tail-risers-plan.json','direct-frame-tail-risers-native.json']:
  q=read(BASE/'functional-protection'/n)
  assert not q.get('contacts') and not q.get('errors')
  for name,h in q['source_sha256'].items():assert SHA(ROOT/name)==h,name;pins[name]=h
 direct=read(BASE/'functional-protection/direct-frame-tail-risers-native.json')
 for n in ('native','path'):
  f=ROOT/(direct[n] if n=='native' else direct['part'][n]);pins[f.relative_to(ROOT).as_posix()]=SHA(f)
 def manifest(result,sf,scope):
  allpins=dict(pins);allpins[sf.relative_to(ROOT).as_posix()]=SHA(sf)
  m=dict(schema_version=1,result_id=result,selected=True,readiness='prototype',physical_pass=False,selection=sf.relative_to(ROOT).as_posix(),scope=scope,
   files=[dict(path=n,sha256=h) for n,h in sorted(allpins.items())],
   gates={n:dict(status='open',reason='Delivered fit/PETG/adhesion/loads/thermal/electrical qualification remains separate; no physicalPASS/power approval.') for n in REQUIRED_GATES})
  m[result+'_complete']=True
  for gate in ('geometry','assembly'):m['gates'][gate]=dict(status='pass',reason='Current full instance map, changed root/battery interfaces and relocated native links qualified; inherited unchanged module evidence explicitly retained.',evidence=[(OUT/'native-composition-r2.json').relative_to(ROOT).as_posix(),(OUT/'added-interface-checks-r2.json').relative_to(ROOT).as_posix()])
  v=verify(ROOT,m);assert v['integrity_ok'],v;return m
 # Retain the complete upper tail61identities and13motion samples, while
 # replacing the4static root members. No original tail native is overwritten.
 oldmf=read(BASE/'tail-mount-checkpoint/manifest.json');v=verify(ROOT,oldmf);assert v['integrity_ok'],v
 for r in oldmf['files']:pins[r['path']]=r['sha256']
 oldsel=read(BASE/'tail-mount-checkpoint/selection.json');m3=copy.deepcopy(oldsel)
 replacement=dict(direct['part'],stl=direct['part']['path'],source=direct['native'],source_object='DirectFrameRiser')
 m3['prints']=[replacement if r['identity']=='CP2:TailRiser' else r for r in m3['prints']]
 m3.update(status='M3_CURRENT_DIRECT_FRAME_TAIL_MECHANICS_SELECTED',M3_complete=True,selected=True,physical_pass=False,
  historical_upper_tail_assembly=m3['current_assembly'],current_assembly=native['native'],native=native['native'],native_sha256=native['native_sha256'],
  repaired_root=dict(instances=4,bottom_mm=37.02,top_mm=57.52,height_mm=20.5,no_new_hardware=True,
   source='functional-protection/direct-frame-tail-risers-plan.json',old19mm_and_TopPlate038_NOT_selected=True),
  inherited_motion_scope='Same61upper-tail identities/13sampled yaw poses and fixed top57.52/pivot. New static lower1.5mm root material is below retained moving tail and qualified with actual FrameRear/changed adjacent material; not a new whole motion sweep or physical load test.',
  scope='Complete nominal selected tail mechanics with direct-frame4root replacement, actual rearM2x30stacks and full current assembly. Original upper tail/provisional MG92B horn and movement evidence retained; physical fit/creep/continuous motion remain phase2.')
 sf=BASE/'tail-mount-checkpoint/selection-r2.json';save(sf,m3);mf=BASE/'tail-mount-checkpoint/manifest-r2.json';save(mf,manifest('M3',sf,m3['scope']));pins[mf.relative_to(ROOT).as_posix()]=SHA(mf);pins[sf.relative_to(ROOT).as_posix()]=SHA(sf)
 # One readable CURRENT instruction replaces obsolete selector/upper bolt
 # references, while the prior instruction and its old hashes remain history.
 olddoc=BASE/'PHASE1_ASSEMBLY.md';text=olddoc.read_text()
 text=text.replace('phase1-current-print-selection.json','phase1-current-print-selection-r4.json').replace('phase1-current-purchased-selection-r3.json','phase1-current-purchased-selection-r4.json').replace('body-harness-checkpoint/w5-selection.json','body-harness-checkpoint/w5-selection-r2.json')
 text=text.replace('Posadzić górny zestaw na czterech M3x45/postach.','Posadzić górny zestaw na trzech M3x45 i jednej DIN965M3x50 przy S1; jego górna podkładka usunięta. PH1 przed instalacją S1.')
 a2=read(BASE/'phase1-assembly-selection-r5.json')
 text+='\n## Aktualne zastąpienia, obowiązkowe\n\n'+'\n'.join('- '+s for s in a2['source_protection_sequence'])+'\n\nObecny spis:84typy/117sztuk. Nie instalować starychU1spacerów/izolatorów ani zastąpionych PWM1608topinsulators; nie wracają stare U1MountM2x10/nuts. Szczegóły izolacji i przymiarek: functional-protection/ASSEMBLY.md. E3 pozostajeOPEN, źródła odłączone.\n'
 instruction=BASE/'PHASE1_ASSEMBLY_CURRENT.md';instruction.write_text(text,encoding='utf-8',newline='\n');pins[instruction.relative_to(ROOT).as_posix()]=SHA(instruction)
 a2.update(instruction=instruction.relative_to(ROOT).as_posix(),current_full_assembly=native['native']);sf=BASE/'phase1-assembly-selection-r6.json';save(sf,a2);mf=BASE/'phase1-assembly-manifest-r6.json';save(mf,manifest('A2',sf,a2['scope']));pins[sf.relative_to(ROOT).as_posix()]=SHA(sf);pins[mf.relative_to(ROOT).as_posix()]=SHA(mf)
 for f in [OUT/'README.md',BASE/'phase1-electrical-open.json',Path(__file__)]:pins[f.relative_to(ROOT).as_posix()]=SHA(f)
 k1=read(BASE/'phase1-current-print-selection-r4.json');k2=read(BASE/'phase1-current-purchased-selection-r4.json');k3=read(BASE/'phase1-material-selection-r4.json')
 assert len(k1['prints'])==84 and sum(r['quantity'] for r in k1['prints'])==117 and k2['drive_count']==15
 counts={r['identity']:sum(i['identity']==r['identity'] for i in native['print_instances']) for r in k1['prints']}
 assert all(counts[r['identity']]==r['quantity'] for r in k1['prints'])
 # Archive contains required runtime/source/evidence bytes, not a cyclic
 # copy of its own A3manifest/score. A3manifest is delivered beside archive.
 archive=OUT/'Phase1CurrentPayload.zip';building=OUT/'Phase1CurrentPayload.building.zip';assert not archive.exists(),'Receive existing payload before rebuilding'
 index=dict(entry=native['native'],current_print_selection=(BASE/'phase1-current-print-selection-r4.json').relative_to(ROOT).as_posix(),
  print_identities=84,installed_prints=117,drive_count=15,physical_pass=False,E3_complete=False,
  files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],rule='Exact local bytes; historical evidence is not another current print choice. A3manifest/score external to avoid circular hashes.')
 for n,h in pins.items():assert SHA(ROOT/n)==h,n
 print('Writing one exact-byte current payload',len(pins),'files',flush=True)
 with zipfile.ZipFile(building,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
  z.writestr('PAYLOAD_INDEX.json',json.dumps(index,indent=2)+'\n')
  for n in sorted(pins):
   check();kind=zipfile.ZIP_STORED if Path(n).suffix.lower() in ('.fcstd','.zip','.pdf','.png','.jpg') else zipfile.ZIP_DEFLATED
   z.write(ROOT/n,n,compress_type=kind,compresslevel=1)
 print('Payload saved, verifying every archived byte stream',flush=True)
 with zipfile.ZipFile(building) as z:
  assert len(z.namelist())==len(pins)+1
  for n,h in pins.items():
   check();digest=hashlib.sha256()
   with z.open(n) as f:
    for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
   assert digest.hexdigest()==h,n
 building.replace(archive);ar=dict(status='CURRENT_EXACT_BYTE_PAYLOAD_ALL_FILES_VERIFIED',path=archive.relative_to(ROOT).as_posix(),sha256=SHA(archive),bytes=archive.stat().st_size,files=len(pins),physical_pass=False)
 af=OUT/'payload-receipt.json';save(af,ar);pins[af.relative_to(ROOT).as_posix()]=SHA(af);pins[ar['path']]=ar['sha256']
 selection=dict(status='A3_ONE_CURRENT_WHOLE_PHASE1_PACKAGE_SELECTED',result_id='A3',selected=True,A3_complete=True,readiness='prototype',physical_pass=False,
  native=native['native'],native_sha256=native['native_sha256'],archive=ar,print_identities=84,installed_prints=117,drive_count=15,MG92B_provisional_horns=3,
  print_instance_map=native['print_instances'],purchased_components=k2['components'],purchased_reference_semantics='K2 counts physical purchased identities; many CAD reference solids are subparts or nominal envelopes, not additional purchases or drives.',
  source_selections=dict(K1='phase1-current-print-selection-r4.json',K2='phase1-current-purchased-selection-r4.json',K3='phase1-material-selection-r4.json',A2='phase1-assembly-selection-r6.json',M3='tail-mount-checkpoint/selection-r2.json',M4='functional-protection/selection.json',W5='body-harness-checkpoint/w5-selection-r2.json'),
  E3_complete=False,cosmetic_torso_included=False,closed160mm_torso_fit_claimed=False,
  native_editability=native['native_editability'],relocated_reopen=True,
  scope='One whole current neutral robot, all117print instances/84identities, actual current frame/root/battery/head/tail/material/wiring context, selected resources and verified exact-byte payload. E3 remains OPEN; no physicalPASS, power/slicer/ROS/cosmeticbody approval.',
  source_sha256=dict(pins),worker_seconds=round(time.monotonic()-tick,3))
 sf=OUT/'selection.json';save(sf,selection);mf=OUT/'manifest.json';save(mf,manifest('A3',sf,selection['scope']))
 print(json.dumps(dict(status=selection['status'],payload_bytes=ar['bytes'],files=ar['files'],seconds=selection['worker_seconds'])),flush=True)
if __name__=='__main__':run()
