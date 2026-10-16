"""Whole current neutral phase1 assembly, not a cropped wiring scene.

Actual manufacturing instances get explicit identities. Retained imported
geometry stays labelled snapshot;27 editable/current print links keep original
sources. No solver/dynamic/physical certification inferred from a saved view.
"""
import json,time,tempfile,shutil,re
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from current_work_guard import check
from build_phase1_source_mounts import dependencies,signature
from battery_p0_frame_fasteners import probes

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'phase1-whole-assembly'
PROTECTION=BASE/'functional-protection';P0=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
MODEL=OUT/'RobotCatPhase1Current.FCStd'
def run():
 check();tick=time.monotonic();OUT.mkdir(exist_ok=True);assert not MODEL.exists(),'Receive current assembly before rerun'
 planfile=PROTECTION/'full-composition-plan.json';plan=json.loads(planfile.read_text());assert not plan['missing']
 current=PROTECTION/'CurrentW5Protected.FCStd';reader=SavedShapes();objects=reader.doc(current);p0=reader.doc(P0)
 printset=BASE/'phase1-current-print-selection-r4.json';k=json.loads(printset.read_text());quant={r['identity']:r['quantity'] for r in k['prints']}
 receipt=json.loads((PROTECTION/'current-w5-protected-native.json').read_text());own={r['object']:r for r in receipt['native_print_links']}
 binding={i['object']:r['identity'] for r in plan['bindings'] for i in r['instances']}
 retired={'head/0/0/Foundation/0/0','P0_Part__Feature005/0/0','P0_Part__Feature038/0/0'};removed=[];snapshots=[];restored=[];links=[];instances=[];opened={}
 d=A.newDocument('RobotCatPhase1Current');d.saveAs(str(OUT/'RobotCatPhase1Current.building.FCStd'))
 def part(n,label,s,identity=None,scope='Pinned current neutral reference snapshot'):
  o=d.addObject('Part::Feature',n);o.Label=label;o.Shape=s;o.addProperty('App::PropertyString','GeometryScope');o.GeometryScope=scope
  if identity:o.addProperty('App::PropertyString','ManufacturingIdentity');o.ManufacturingIdentity=identity;instances.append(dict(identity=identity,object=o.Name,label=label,source='current W5 snapshot'))
  snapshots.append(dict(object=o.Name,label=label,scope=scope));return o
 def native(identity,file,name,placement=None):
  key=str(file.resolve())
  if key not in opened:opened[key]=A.openDocument(key)
  source=opened[key].getObject(name);assert source and not source.Shape.isNull(),(identity,name)
  o=d.addObject('App::Link','Print_'+identity);o.LinkedObject=source;o.Label=identity
  if placement is not None:o.LinkTransform=True;o.LinkPlacement=placement
  links.append(dict(identity=identity,object=o.Name,native=file.relative_to(ROOT).as_posix(),native_object=name,signature=signature(o.Shape)))
  instances.append(dict(identity=identity,object=o.Name,label=o.Label,source=file.relative_to(ROOT).as_posix()))
  return o
 # Only already-qualified cached native sources are read; no repeated giant
 # BOP check/rebuild of every unchanged Upper/receiver parent.
 for n,r in own.items():native(r['identity'],ROOT/r['native'],r['native_object'])
 print('Current17native links retained',flush=True)
 washfile=BASE/'commercial-hardware/washer-checks.json';wash=json.loads(washfile.read_text());washers={r['replaces']:r for r in wash['rows']}
 assert len(washers)==20 and sha(ROOT/wash['native'])==wash['native_sha256']
 for n,o in objects.items():
  if not n.startswith('Ref_'):continue
  label=prop(o,'Label')[0].get('value')
  if label in retired or label.startswith('wire/head/local/') and label.split('/')[-1] in ('+15','-15'):
   removed.append(dict(object=n,label=label,reason='Superseded physical Foundation/bottomplate or non-neutral wire pose reference'));continue
  s=reader.shape(current,n);scope='Pinned accepted current neutral material/wire reference'
  if label.startswith('P0_'):
   name=label.split('/')[0][3:]
   if name in p0 and 'Rigid_'+name in p0:
    full=reader.shape(P0,name);full.Placement=reader.placement(p0['Rigid_'+name])*full.Placement
    if abs(full.optimalBoundingBox().ZMin-s.optimalBoundingBox().ZMin)>1e-6:
     restored.append(dict(object=n,source_object=name,old_min_z_mm=s.optimalBoundingBox().ZMin,full_min_z_mm=full.optimalBoundingBox().ZMin,
      provenance='Authoritative unchanged E6/P0 world wrapper; not a redesigned leg or extra physical component'))
    s=full;scope='Full authoritative P0 saved world geometry, no Z-25 view clip; inherited source snapshot'
  if n in washers:s=reader.shape(ROOT/wash['native'],washers[n]['object']);scope='Current commercial DIN433 OD4.5 replacement, not an extra washer'
  part(n,label,s,binding.get(n),scope)
 print('Full P0/rest references composed; restored',len(restored),'retired',len(removed),flush=True)
 tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'
 for i in range(1,5):native('CP2:TailRiser',PROTECTION/'DirectFrameTailRisers.FCStd','TailRiser'+str(i))
 for i in range(1,5):
  for suffix in ('Bolt','LowerWasher','UpperWasher','Nut'):
   n='RearShared'+str(i)+suffix;s=reader.shape(tail,n);part(n,n,s,scope='Retained4rearM2x30joint stacks; original top/bolt/nut datums unchanged by direct-frame risers')
 carrier=ROOT/'hardware/cad/studies/battery-p0/r4/electronics/BatteryCarrierP0.FCStd';plate=ROOT/'hardware/cad/studies/battery-p0/r4/chassis/BottomPlateP0.FCStd';ret=ROOT/'hardware/cad/studies/battery-p0/r6/BatteryNutRetainerP0.FCStd'
 native('P0-BATTERY-CARRIER-R4',carrier,'Carrier');native('P0-BATTERY-PLATE-R4',plate,'Plate')
 for x in (-75,117):
  for y in (-22.5,22.5):native('P0-BATTERY-NUT-RETAINER-R6',ret,'Retainer',A.Placement(A.Vector(x,y,1.5),A.Rotation()))
 # Actual selected pack reservation, not the older90x43x19 Battery snapshot.
 packfile=ROOT/'hardware/cad/studies/battery-p0/SupplierPack.brep';pack=Part.Shape();pack.read(str(packfile));part('BatterySelectedNominal','GensAce GEA223S30X6GT nominal supplier envelope',pack,scope='Supplier nominal106.5x35x21.5; delivered/fault/electrical gates OPEN')
 part('BatteryPE1','Battery PE1 liner107x36x1',Part.makeBox(107,36,1,A.Vector(-26.5,-18,5.2)),scope='Selected nominal PE1 cut, not primary electrical insulation certification')
 # Two adjustable existing15x200 straps. Nominal1mm packing wall and20mm
 # engagement are project gates, not supplier guaranteed buckle dimensions.
 for i,x in enumerate((6.5,36.5),1):
  loop=Part.makeBox(15,54.5,27.5,A.Vector(x,-27.25,1.2)).cut(Part.makeBox(15.2,52.5,25.5,A.Vector(x-.1,-26.25,2.2)))
  part('BatteryStrapCurrent'+str(i),'Existing15x200 adjustable battery strap '+str(i),loop,scope='Nominal fitted loop160mm+project20engagement+6buckle=186<=200. Actual buckle/thickness/usable length, hand tension and retention must be checked unplugged; not a fixed rigid strap or new purchase')
 for i,(x,y) in enumerate(( (x,y) for x in (-80,-70,112,122) for y in (-22.5,22.5) )):
  hardware=probes(x,y)['installed_hardware'];hardware.rotate(A.Vector(x,y,0),A.Vector(0,0,1),30)
  part('BatteryFrameHardware'+str(i),'R4 frame M2x6 with2washers/nut '+str(i),hardware,scope='Retained source-backed R4 frame hardware8sets; hexnut clocked30degrees into actual R6trap, not thread or torque geometry certification')
 # Four existing tray-to-plate bolts/nuts use the original authoritative
 # hardware with the exact R3 translation retained by R4; no new allocation.
 for end,dx in [('Front',-5),('Rear',5)]:
  for side,dy in [('L',-1),('R',1)]:
   for kind in ('Screw','Nut'):
    n='Battery'+kind+end+side;s=reader.shape(P0,n);s.Placement=reader.placement(p0['Rigid_'+n])*s.Placement;s.translate(A.Vector(dx,dy,0));part(n,n,s,scope='Retained R3/R4 tray hardware and authoritative translated datums')
 counts={n:sum(i['identity']==n for i in instances) for n in quant};assert counts==quant,[(n,counts[n],quant[n]) for n in quant if counts[n]!=quant[n]]
 assert len(instances)==117 and len({i['object'] for i in instances})==117
 d.recompute();d.saveAs(str(MODEL));files=dependencies(MODEL)
 baseline={r['object']:signature(d.getObject(r['object']).Shape) for r in links}
 for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
 print('Whole117print instances saved; checking relocated27links',flush=True)
 with tempfile.TemporaryDirectory(prefix='cat-phase1-whole-') as td:
  root=Path(td)
  for f in files:dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
  moved=A.openDocument(str(root/MODEL.relative_to(ROOT)))
  for r in links:
   o=moved.getObject(r['object']);assert o.LinkedObject and Path(o.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
   assert max(abs(a-b) for a,b in zip(signature(o.Shape),baseline[r['object']]))<1e-5,r['identity']
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
 result=dict(status='WHOLE_PHASE1_CURRENT_NEUTRAL_ASSEMBLY_COMPOSED_A3_PACKAGE_PENDING',selected=False,A3_complete=False,physical_pass=False,
  native=MODEL.relative_to(ROOT).as_posix(),native_sha256=sha(MODEL),print_instances=instances,print_identities=84,installed_prints=117,
  current_native_links=links,native_link_count=len(links),retained_reference_snapshots=snapshots,restored_full_P0=restored,retired_references=removed,
  commercial_washers_replaced=20,battery_carrier_plate_R6_instances=6,tail_risers=4,drive_count=15,MG92B_replaceable_horns=3,
  relocated_reopen=True,links_within_relocated_package=True,cosmetic_torso_included=False,closed160mm_fit_claimed=False,
  native_editability='27 current print-instance links to original editable/inherited sources; other unchanged whole-robot geometry explicitly pinned snapshots, not falsely fully migrated native joints.',
  source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():sha(f) for f in files},printset.relative_to(ROOT).as_posix():sha(printset),planfile.relative_to(ROOT).as_posix():sha(planfile),
   packfile.relative_to(ROOT).as_posix():sha(packfile),washfile.relative_to(ROOT).as_posix():sha(washfile),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'native-composition.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],print_instances=117,links=len(links),seconds=result['worker_seconds'])),flush=True)
if __name__=='__main__':run()
