"""Reuse unchanged checked geometry, then check corrected4world tail roots."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from current_work_guard import check
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'phase1-whole-assembly'
def run():
 check();tick=time.monotonic();receipt=OUT/'native-composition-r2.json';native=json.loads(receipt.read_text());model=ROOT/native['native'];assert sha(model)==native['native_sha256']
 previousfile=OUT/'added-interface-checks.json';previous=json.loads(previousfile.read_text());changed=set(native['link_transform_corrections'])
 assert len(changed)==4 and previous['status']=='WHOLE_ADDED_INTERFACES_REJECTED'
 assert len(previous['contacts'])==12 and all(c['b'] in changed for c in previous['contacts'])
 assert native['topology_parameter_roundoff']['maximum_delta']<=1e-12 and native['unchanged_component_fingerprints_verified']>1000
 historical=ROOT/native['historical_model_byte_copy'];oldnative=json.loads((OUT/'native-composition.json').read_text());assert sha(historical)==oldnative['native_sha256']
 for n,h in previous['source_sha256'].items():
  target=historical if n==native['native'] else ROOT/n
  assert sha(target)==h,n
 reader=SavedShapes();objects=reader.doc(model);targets={}
 names=set(previous['checked_new_components'])|{n for n in objects if n.startswith('RearShared')}
 for n in names:targets[n]=reader.shape(model,n)
 planfile=BASE/'functional-protection/direct-frame-tail-risers-plan.json';plan=json.loads(planfile.read_text());assert not plan['contacts'] and len(plan['bearings'])==4
 result=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],pairs=0,
  inherited_pairs_checked=previous['pairs'],inherited_failure_contacts_replaced=12,
  reused_scope='All26addedbattery/R4/R6/straps/hardware versus unchanged geometry retain earlier exact171pair check, whose12failures exclusively involved4incorrect-at-origin tail links. Full serialized topology/parameters and native link inputs verified at1e-12; no real layout change of these26parts. Removed old factoryhorn cannot add a contact.',
  corrected_scope='Fourworld-tail roots exactly match already-qualified4planBReps/33currentW5pairs/bearings, then tested against26newbattery parts and16RearShared hardware pieces.')
 for row in native['current_native_links']:
  if row['object'] not in changed:continue
  s=reader.shape(model,row['object']);p=Part.Shape();p.read(str(BASE/'functional-protection'/('DirectTailRiser'+row['native_object'][-1]+'.brep')))
  assert s.copy().cut(p.copy()).Volume+p.copy().cut(s.copy()).Volume<1e-5
  for n,t in targets.items():
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid()
   if q.Volume>1e-5:result['contacts'].append(dict(a=row['object'],b=n,volume_mm3=q.Volume))
 result.update(status='WHOLE_ADDED_BATTERY_TAIL_INTERFACES_CLEAR' if not result['contacts'] else 'CORRECTED_TAIL_INTERFACES_REJECTED',
  source_sha256={**reader.hashes,receipt.relative_to(ROOT).as_posix():sha(receipt),previousfile.relative_to(ROOT).as_posix():sha(previousfile),
   historical.relative_to(ROOT).as_posix():sha(historical),planfile.relative_to(ROOT).as_posix():sha(planfile),
   (OUT/'link-transform-fingerprints.json').relative_to(ROOT).as_posix():sha(OUT/'link-transform-fingerprints.json'),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'added-interface-checks-r2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)
if __name__=='__main__':run()
