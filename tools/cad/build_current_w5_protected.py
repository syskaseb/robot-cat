"""One current W5 snapshot with explicit accepted protection replacements.

Retained references are saved geometry, not new native print sources. Current
print parents remain external native links; no historical document is saved.
Full P0/battery/head/tail ownership composition remains A3, not this snapshot.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,sha,check
from check_main_p0_placement import SavedShapes,prop
from build_phase1_source_mounts import dependencies,signature

MODEL=OUT/'CurrentW5Protected.FCStd'
def run():
 check();tick=time.monotonic();assert not MODEL.exists(),'Receive existing composition first'
 selected_file=BASE/'phase1-current-print-selection-r2.json';selected=json.loads(selected_file.read_text());rows={r['identity']:r for r in selected['prints']}
 old=json.loads((BODY/'current-w5-assembly/neutral-manifest.json').read_text());reader=SavedShapes();objects=reader.doc(SCENE)
 d=A.newDocument('CurrentW5Protected');d.saveAs(str(OUT/'CurrentW5Protected.building.FCStd'));opened={};links=[];refs=[];retired=[]
 def native(identity):
  r=rows[identity];file=ROOT/r['native'];key=str(file.resolve())
  if key not in opened:opened[key]=A.openDocument(key)
  obj=opened[key].getObject(r['native_object']);assert obj and obj.Shape.isValid(),identity
  o=d.addObject('App::Link','Print_'+identity);o.LinkedObject=obj;o.Label=identity
  links.append(dict(identity=identity,object=o.Name,native=r['native'],native_object=r['native_object'],signature=signature(obj.Shape)))
 for r in old['printed_body_support_links']:native(r['part'])
 for n in ('Foundation','MAINGrip','S1MountCurrent'):native(n)
 print('17 current native print links prepared',flush=True)
 changes={'wire/W003':'W003RetainedUpperBypass.brep','Power/MAINBand/0/0':'MAINBandInsulated.brep'}
 remove={'FoundationStationSupports/0/0','MAINGrip/0/0','UpperFrame8Screw/0/0','UpperFrame8TopWasher/0/0'}
 for n,o in objects.items():
  if not n.startswith('Ref_'):continue
  label=prop(o,'Label')[0].get('value')
  if label in remove:retired.append(label);continue
  s=reader.shape(SCENE,n)
  if label in changes:s=Part.Shape();s.read(str(OUT/changes[label]));retired.append(label+' OLD')
  q=d.addObject('Part::Feature',n);q.Label=label;q.Shape=s;refs.append(dict(object=q.Name,label=label))
 for name in ['S1SharedFrameScrew',*['S0'+part+'_'+x+suffix for x in ('96','58') for part,suffix in [('M6',''),('Washer','top'),('Washer','lower'),('Nut','')]],
  'Sleeve_W079','Sleeve_W080','Sleeve_W060','Sleeve_W078','BUSMidGuideLacingWest']:
  s=Part.Shape();s.read(str(OUT/(name+'.brep')));q=d.addObject('Part::Feature','Ref_Current_'+name);q.Label=name;q.Shape=s
  refs.append(dict(object=q.Name,label=name))
 # Adhesive holds only the POST_F0 casing:18mm X by8mm Y, not18mm across
 # the9mm-wide case. Independent existing wire restraints remain present.
 q=d.addObject('Part::Feature','Ref_POST_F0_Pad4905');q.Shape=Part.makeBox(18,8,.5,A.Vector(50.5,-62.8,21));refs.append(dict(object=q.Name,label='POST_F0 Pad4905 18x8x0.5'))
 d.recompute();assert len(links)==17 and len(set(r['label'] for r in refs))==len(refs)
 for r in links:assert max(abs(a-b) for a,b in zip(signature(d.getObject(r['object']).Shape),r['signature']))<1e-5,r['identity']
 d.saveAs(str(MODEL));files=dependencies(MODEL)
 for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
 print('Current W5 protection snapshot saved; relocated links next',flush=True)
 with tempfile.TemporaryDirectory(prefix='cat-protected-w5-') as td:
  root=Path(td)
  for f in files:dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
  moved=A.openDocument(str(root/MODEL.relative_to(ROOT)))
  for r in links:
   o=moved.getObject(r['object']);assert o.LinkedObject and Path(o.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve()),r['identity']
   assert max(abs(a-b) for a,b in zip(signature(o.Shape),r['signature']))<1e-5,r['identity']
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
 for n,h in reader.hashes.items():assert sha(ROOT/n)==h,n
 result=dict(status='CURRENT_W5_PROTECTION_COMPOSITION_RELOCATED_LINKS_COMPLETE',selected=False,W5_complete=False,M4_complete=False,A3_complete=False,
  native=MODEL.relative_to(ROOT).as_posix(),native_sha256=sha(MODEL),physical_pass=False,native_print_links=links,
  reference_objects=refs,retired_references=retired,relocated_reopen=True,all_links_within_package=True,
  unchanged_reference_geometry_pinned=True,not_whole_A3=True,
  source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():sha(f) for f in files},selected_file.relative_to(ROOT).as_posix():sha(selected_file),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'current-w5-protected-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],native_links=len(links),references=len(refs),seconds=result['worker_seconds'])),flush=True)
if __name__=='__main__':run()
