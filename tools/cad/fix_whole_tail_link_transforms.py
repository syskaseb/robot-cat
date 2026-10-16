"""Fix link-to-link placement semantics, not a new physical offset campaign.

Four installed source links already have the qualified world pose. Outer links
must retain it with LinkTransform=true. Preserve original bytes for the failed
interface proof; verify all other snapshot/link inputs unchanged.
"""
import json,time,shutil,tempfile,zipfile,hashlib
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from build_phase1_source_mounts import dependencies,signature
from current_work_guard import check
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'phase1-whole-assembly';MODEL=OUT/'RobotCatPhase1Current.FCStd'

def fingerprint(file):
 r=SavedShapes();x=r.doc(file);rows={}
 with zipfile.ZipFile(file) as z:
  for n,o in x.items():
   if not n.startswith(('Ref_','Print_','Battery','RearShared')):continue
   link=prop(o,'LinkedObject')
   if link is not None:
    rows[n]=dict(link_file=link[0].get('file'),link_object=link[0].get('name'),transform=prop(o,'LinkTransform')[0].get('value'),placement=list(r.placement(o,'LinkPlacement').toMatrix().A))
   else:
    p=prop(o,'Shape');rows[n]=dict(shape_sha256=hashlib.sha256(z.read(p[0].get('file'))).hexdigest())
 return rows
def run():
 check();tick=time.monotonic();oldfile=OUT/'native-composition.json';old=json.loads(oldfile.read_text());assert sha(MODEL)==old['native_sha256']
 rejected=OUT/'link-placement-rejected';rejected.mkdir(exist_ok=True);copy=rejected/MODEL.name;assert not copy.exists();shutil.copy2(MODEL,copy)
 before=fingerprint(MODEL);tail=[r for r in old['current_native_links'] if r['identity']=='CP2:TailRiser'];assert len(tail)==4
 doc=A.openDocument(str(MODEL))
 for r in tail:
  o=doc.getObject(r['object']);assert o.LinkedObject.Name==r['native_object']
  expected=signature(o.LinkedObject.Shape);assert abs(expected[-1]-57.52)<1e-5,expected
  o.LinkTransform=True;o.LinkPlacement=A.Placement();doc.recompute()
  actual=signature(o.Shape);assert max(abs(a-b) for a,b in zip(actual,expected))<1e-5,(r['object'],actual,expected)
  r['signature']=actual
 doc.save();files=dependencies(MODEL)
 for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
 after=fingerprint(MODEL);changed={r['object'] for r in tail};assert set(before)==set(after)
 assert all(before[n]==after[n] for n in before if n not in changed),'Unchanged material or native link fingerprint changed'
 print('Only4outer link transforms changed; all other saved geometry byte-identical',flush=True)
 with tempfile.TemporaryDirectory(prefix='cat-fixed-tail-links-') as td:
  root=Path(td)
  for f in files:dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
  moved=A.openDocument(str(root/MODEL.relative_to(ROOT)))
  for r in old['current_native_links']:
   o=moved.getObject(r['object']);assert o.LinkedObject and Path(o.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
   if r['object'] in changed:assert max(abs(a-b) for a,b in zip(signature(o.Shape),r['signature']))<1e-5
  for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
 pins={n:h for n,h in old['source_sha256'].items() if n!=MODEL.relative_to(ROOT).as_posix()};pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in files})
 pins[copy.relative_to(ROOT).as_posix()]=old['native_sha256'];pins[oldfile.relative_to(ROOT).as_posix()]=sha(oldfile);pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 old.update(native_sha256=sha(MODEL),current_native_links=old['current_native_links'],source_sha256=pins,
  link_transform_corrections=sorted(changed),unchanged_component_fingerprints_verified=len(before)-4,
  historical_model_byte_copy=copy.relative_to(ROOT).as_posix(),physical_pass=False,relocated_reopen=True,
  original_composition_seconds=old['worker_seconds'],worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'native-composition-r2.json').write_text(json.dumps(old,indent=2)+'\n')
 (OUT/'link-transform-fingerprints.json').write_text(json.dumps(dict(changed_links=sorted(changed),before=before,after=after),indent=2)+'\n')
 print(json.dumps(dict(status='FOUR_WORLD_LINK_TRANSFORMS_CORRECTED_OTHERS_IDENTICAL',seconds=old['worker_seconds'],unchanged=len(before)-4)),flush=True)
if __name__=='__main__':run()
