"""Only new full-composition battery/tail-root interfaces; not another microaudit."""
import json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from current_work_guard import check
from check_source_contact_insulation import bounded_distance

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'phase1-whole-assembly'
def run():
 check();tick=time.monotonic();proof=OUT/'native-composition.json';native=json.loads(proof.read_text());model=ROOT/native['native'];assert sha(model)==native['native_sha256']
 reader=SavedShapes();objects=reader.doc(model);shapes={};wires={};labels={}
 with zipfile.ZipFile(BASE/'body-harness-checkpoint/remaining25-space-context.zip') as z:ix=json.loads(z.read('index.json'))
 radii={r['name']:r['radius_mm'] for r in ix['entries'] if r['kind']=='wire'}
 for n,o in objects.items():
  if not n.startswith(('Ref_','Print_','Battery','RearShared')):continue
  label=prop(o,'Label')[0].get('value');labels[n]=label;s=reader.shape(model,n)
  if n.startswith('Ref_Wire'):assert label in radii,label;wires[n]=(s,radii[label])
  else:shapes[n]=s
 new={n:s for n,s in shapes.items() if n.startswith('Battery')}
 tailroots=[]
 for r in native['current_native_links']:
  if r['identity'].startswith('P0-BATTERY'):new[r['object']]=shapes[r['object']]
  elif r['identity']=='CP2:TailRiser':tailroots.append(r['object'])
 result=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],pairs=0,checked_new_components=sorted(new),
  scope='Added actual R4/R6/battery/adjustable straps/PE1/plate and tray/framehardware versus all current material/true-radius curves, all new/new pairs. Four repairedTailRisers versus previously absent16RearShared hardware pieces only; earlier33pairs/bearings inherited. Full lowerP0 source restored; no repeated settled routing or global motion claim.')
 for n,s in new.items():
  assert s.isValid(),n
  for m,t in shapes.items():
   if m==n or m in new and m<n or not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),(n,m)
   if q.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=q.Volume))
  for m,(c,r) in wires.items():
   b=s.BoundBox;b.enlarge(r)
   if not b.intersect(c.BoundBox):continue
   check();result['pairs']+=1;gap=bounded_distance(s,c,r)
   if gap<r-1e-6:result['contacts'].append(dict(a=n,b=m,wire=labels[m],distance_mm=gap,required_mm=r))
  (OUT/'added-interface-progress.json').write_text(json.dumps(result,indent=2)+'\n');print(n,'checked',len(result['contacts']),'contacts',flush=True)
 for n in tailroots:
  s=shapes[n]
  for m,t in shapes.items():
   if not m.startswith('RearShared') or not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid()
   if q.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=q.Volume))
 result.update(status='WHOLE_ADDED_BATTERY_TAIL_INTERFACES_CLEAR' if not result['contacts'] else 'WHOLE_ADDED_INTERFACES_REJECTED',
  source_sha256={**reader.hashes,proof.relative_to(ROOT).as_posix():sha(proof),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'added-interface-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)
if __name__=='__main__':run()
