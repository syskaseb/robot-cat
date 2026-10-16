"""Complete the4link repair and retire a superseded factory tail horn.

Previous fix saved correct transforms before failing an over-strict BYTE
comparison. Verify full topology/parameters at1e-12; don't call kernel text
normalization a new physical layout or rerun all unchanged material pairs.
"""
import json,time,zipfile,tempfile,shutil,math
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from fix_whole_tail_link_transforms import OUT,MODEL,fingerprint
from geometry_text_equivalence import compare
from build_phase1_source_mounts import dependencies,signature
from current_work_guard import check

def run():
 check();tick=time.monotonic();oldfile=OUT/'native-composition.json';old=json.loads(oldfile.read_text());archive=OUT/'link-placement-rejected'/MODEL.name
 assert sha(archive)==old['native_sha256'];before=fingerprint(archive)
 changed={r['object'] for r in old['current_native_links'] if r['identity']=='CP2:TailRiser'};retired='Ref_Material_P0_MG92BOutput29_0_0'
 # Resume a successfully saved removal without another giant model rewrite.
 with zipfile.ZipFile(MODEL) as z:needs_removal=retired.encode() in z.read('Document.xml')
 if needs_removal:
  doc=A.openDocument(str(MODEL));doc.removeObject(retired);doc.save()
 for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
 after=fingerprint(MODEL);assert set(after)==set(before)-{retired};normalized=[];maxdelta=0
 r=SavedShapes();a=r.doc(archive);b=r.doc(MODEL)
 with zipfile.ZipFile(archive) as za,zipfile.ZipFile(MODEL) as zb:
  for n in after:
   if n in changed:continue
   if before[n]==after[n]:continue
   if 'shape_sha256' in before[n]:
    af=prop(a[n],'Shape')[0].get('file');bf=prop(b[n],'Shape')[0].get('file');q=compare(za.read(af),zb.read(bf));assert q['equal'],(n,q)
    maxdelta=max(maxdelta,q['max_float_delta']);normalized.append(dict(object=n,**q))
   else:
    x,y=before[n],after[n];assert all(x[k]==y[k] for k in ('link_file','link_object','transform')),n
    assert max(abs(u-v) for u,v in zip(x['placement'],y['placement']))<1e-12,n
 for row in old['current_native_links']:
  if row['object'] not in changed:continue
  s=r.shape(MODEL,row['object']);expected=r.shape(ROOT/row['native'],row['native_object']);actual=signature(s)
  assert max(abs(u-v) for u,v in zip(actual,signature(expected)))<1e-5 and abs(actual[-1]-57.52)<1e-5
  row['signature']=actual
 files=dependencies(MODEL)
 print('Full topology/parameters unchanged except4worldlinks and1retiredhorn; floatmax',maxdelta,flush=True)
 with tempfile.TemporaryDirectory(prefix='cat-owned-whole-') as td:
  root=Path(td)
  for f in files:dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
  d=A.openDocument(str(root/MODEL.relative_to(ROOT)));assert not d.getObject(retired)
  for row in old['current_native_links']:
   ob=d.getObject(row['object']);assert ob.LinkedObject and Path(ob.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
   if row['object'] in changed:assert max(abs(u-v) for u,v in zip(signature(ob.Shape),row['signature']))<1e-5
  for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
 pins={n:h for n,h in old['source_sha256'].items() if n!=MODEL.relative_to(ROOT).as_posix()};pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in files})
 pins[archive.relative_to(ROOT).as_posix()]=old['native_sha256'];pins[oldfile.relative_to(ROOT).as_posix()]=sha(oldfile)
 for f in (Path(__file__),Path(__file__).with_name('geometry_text_equivalence.py'),Path(__file__).with_name('test_geometry_text_equivalence.py')):pins[f.relative_to(ROOT).as_posix()]=sha(f)
 old.update(native_sha256=sha(MODEL),source_sha256=pins,link_transform_corrections=sorted(changed),
  retired_factory_tail_horn=retired,unchanged_component_fingerprints_verified=len(after)-4,
  restored_full_P0=[q for q in old['restored_full_P0'] if q['object']!=retired],
  retained_reference_snapshots=[q for q in old['retained_reference_snapshots'] if q['object']!=retired],
  historical_model_byte_copy=archive.relative_to(ROOT).as_posix(),relocated_reopen=True,
  topology_parameter_roundoff=dict(tolerance=1e-12,maximum_delta=maxdelta,normalized_shapes=len(normalized),checked_flag_changes=sum(q.get('checked_flag_changes',0) for q in normalized),flag_rule='OCCT Checked bit only; all other flags, topology/counts and parameters retained'),
  original_composition_seconds=old['worker_seconds'],worker_seconds=round(time.monotonic()-tick,3))
 old['retired_references'].append(dict(object=retired,label='P0_MG92BOutput29/0/0',reason='Already replaced by current tail/PrintedHornR2; not a second factory horn or original15mm-lower pose'))
 (OUT/'native-composition-r2.json').write_text(json.dumps(old,indent=2)+'\n')
 (OUT/'link-transform-fingerprints.json').write_text(json.dumps(dict(changed_links=sorted(changed),retired=[retired],before=before,after=after,normalized=normalized),indent=2)+'\n')
 print(json.dumps(dict(status='CURRENT_WHOLE_NATIVE_OWNERSHIP_TRANSFORMS_RELOCATED_COMPLETE',seconds=old['worker_seconds'],normalized_shapes=len(normalized),floatmax=maxdelta)),flush=True)
if __name__=='__main__':run()
