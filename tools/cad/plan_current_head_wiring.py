"""Current W2/W3 shared interface receipt, before any native changes.

Rigidly translated historical local wiring is reused; no historical source
is overwritten. Head world placement is applied exactly once, including its
parent assembly placement. Bounding boxes only choose exact distance pairs.
"""
import sys,json,time,math
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A,Part
import plan_current_tail_wiring as T
from check_main_p0_placement import prop
from open_prototype_head_assembly import FIXED,PITCH
ROOT,BASE,P=T.ROOT,T.BASE,T.P
OUT=BASE/'head-wiring-checkpoint'
HEAD=BASE/'head-mount-checkpoint/HeadNeckCurrent.FCStd'
SHIFT=A.Vector(-42,0,25)

def read(p):return json.loads(p.read_text())
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def bb(s):
 b=s.BoundBox
 return [getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
def moved(s,yaw=0,pitch=0):
 c=s.copy()
 if pitch:c.rotate(A.Vector(-194,0,161),A.Vector(0,1,0),pitch)
 if yaw:c.rotate(A.Vector(-152,-5.25,25),A.Vector(0,0,1),yaw)
 return c
def head(reader,yaw=0,pitch=0):
 receipt=read(BASE/'head-mount-checkpoint/native-assembly-checks.json')
 root=reader.placement(reader.doc(HEAD)['CP2Head'])
 assert (root.Base-SHIFT).Length<1e-7,(root.Base,SHIFT)
 result={}
 for row in receipt['parts']:
  n=row['name'];s=reader.shape(HEAD,'Head_'+n)
  s.Placement=root*s.Placement
  result[n]=moved(s,yaw if n not in FIXED else 0,pitch if n in PITCH else 0)
 return result
def scene(reader):
 result,torso=T.scene(reader)
 # W4 is the current selected replacement set, not the E2 predecessor.
 model=BASE/'tail-wiring-checkpoint/TailWiringRelease.FCStd'
 for n,o in reader.doc(model).items():
  if n in ('UpperCarrier001','E2Fixture','FTYCradle','TailLocalRail') or n.startswith(('W4_','W4Reference_')):
   if prop(o,'Shape') is not None:
    s=reader.shape(model,n)
    if s.Solids:result[n]=s
 for n in ('Band_SourceBlack','TieHead_SourceBlack'):result.pop(n,None)
 # Explicitly retain current native neck supports, absent from old body scene.
 for n in ('LeftRiser','RightRiser'):
  result['neck/'+n]=reader.shape(HEAD,n)
 for n in reader.doc(HEAD):
  if n.startswith('Neck') and prop(reader.doc(HEAD)[n],'Shape') is not None:
   result['neck/'+n]=reader.shape(HEAD,n)
 return result,torso
def local(yaw=0):
 f=ROOT/'hardware/electronics/full-cat';out={}
 for n in ('XB12','XB13','XS13','XB22','XB23','XS23'):
  pitch=n in ('XB22','XB23','XS23');count=9 if pitch else 3
  for i in range(count):
   p=f/f'head-local-rigid-conductors-r1/{n}_{i}_CENTERLINE.brep'
   s=Part.read(str(p));s.translate(SHIFT)
   out[f'local/{n}/{i}']=(moved(s,yaw if pitch else 0),1.7 if i==count-1 else 1.05,p)
 for n in ('XB22','XB23','XS23'):
  p=f/f'head-transport-flex-r7/{n}_yaw{yaw:+}_CENTERLINE.brep'
  s=Part.read(str(p));s.translate(SHIFT);out['flex/'+n]=(s,1.05,p)
  for i in range(5):
   p=f/f'head-fixed-pitch-conductors-r1/{n}_{i}.brep'
   # Fixed transition is supplied as actual tube solids, handled separately.
 return out
def run():
 OUT.mkdir(exist_ok=True);assert not (OUT/'retained-space-checks.json').exists()
 tick=time.monotonic();reader=P.SavedShapes();targets,torso=scene(reader)
 plan=dict(status='CURRENT_SHARED_HEAD_PLAN_BEFORE_NATIVE',selected=False,physical_pass=False,
  baseline_result_count=8,fixed_total=20,target_count=10,
  retain=['Selected M2 translated52-part head and neck; no internal mechanical rerun','Selected W4/E2 current carrier and independent restraints','Six R28 individual tails/sleeves, both uncut250 factory leads and JR pairs'],
  boundaries={'yaw_mm':[-112,-56.8,85.2],'pitch_fixed_mm':[-52,76,149],'historical_fixed_loop_anchor_mm':[-52,136,166]},
  remaining=['One ACTUAL fixed loop-anchor load path, not historicalCover','All six W3 current receiving endpoints/independent grips/holder input reservations','Shared current assembly/service and fitted stock; no wholeW5 claim'],
  sequence=['Unpowered bench head factory/JR preparation before shell closure','Head fixed base remains bolted to native risers; moving tail follows yaw only','Do not lift a soldered/taut harness: unplug JR and release designated insulation bands first'],
  counter_rule='A shared-space receipt alone earns zero complete results; W2/W3 only after whole current interfaces/selected native package.',
  geometry_note='Loop and head-local wires are external head/neck paths, not all constrained to torso reservation. Any fixed body support still needs justified root and full clearance.')
 save('plan.json',plan)
 prior=read(OUT/'progress.json') if (OUT/'progress.json').exists() else None
 result=prior or dict(status='PENDING',pairs=0,contacts=[],errors=[],physical_pass=False,selected=False)
 changed={}
 for yaw in (-15,0,15):
  paths=local(yaw)
  for s,r,p in paths.values():reader.hashes[p.relative_to(ROOT).as_posix()]=P.sha(p)
  if prior and yaw in prior.get('completed_yaws',[-15,0,15] if prior['pairs']==70 else []):continue
  for n,(s,r,p) in paths.items():
   reader.hashes[p.relative_to(ROOT).as_posix()]=P.sha(p)
   for m,t in targets.items():
    if not T.near(s,t,r):continue
    assert t.isValid() and t.Solids,(m,'invalid current scene')
    d=min(s.distToShape(c)[0] for c in t.Solids);result['pairs']+=1
    if d<r-1e-5:result['contacts'].append(dict(yaw=yaw,a=n,b=m,distance_mm=d,required_mm=r))
  # Head internals share rigid translation with historical qualified local
  # paths. Check the unchanged local geometry ONLY against changed neck/body.
  print('Received current head local/body yaw',yaw,'pairs',result['pairs'],'contacts',len(result['contacts']),flush=True)
  result.setdefault('completed_yaws',[]).append(yaw)
  result['source_sha256']=dict(reader.hashes)
  save('progress.json',result)
 for folder,prefix in [('head-factory-lead-storage-r3','pitch'),('head-fixed-yaw-feed-r3','yaw')]:
  directory=ROOT/('hardware/electronics/full-cat' if prefix=='pitch' else 'hardware/cad/studies')/folder
  files=list(directory.glob('LeadEnvelope[0-9]*.brep' if prefix=='pitch' else 'factory_*.brep'))
  assert files,(folder,'missing retained whole factory envelopes')
  for p in files:
   s=Part.read(str(p));s.translate(SHIFT);assert s.isValid() and s.Solids
   reader.hashes[p.relative_to(ROOT).as_posix()]=P.sha(p)
   for yaw in ((-15,0,15) if prefix=='pitch' else (0,)):
    q=moved(s,yaw)
    for n,t in targets.items():
     if not T.near(q,t,0):continue
     result['pairs']+=1;v=sum(a.common(b).Volume for a in q.Solids for b in t.Solids)
     if v>1e-5:result['contacts'].append(dict(yaw=yaw,a=prefix+'/'+p.name,b=n,volume_mm3=v))
 current=head(reader)
 changed.update({n:bb(s) for n,s in current.items() if n in ('Fork','Foundation','Bridge','YawCarrier','Carrier')})
 # Six fixed tubes are retained only up to the old W3 boundary, not W3 credit.
 for n in ('XB22','XB23','XS23'):
  for i in range(5):
   p=ROOT/f'hardware/electronics/full-cat/head-fixed-pitch-conductors-r1/{n}_{i}.brep';s=Part.read(str(p));s.translate(SHIFT)
   reader.hashes[p.relative_to(ROOT).as_posix()]=P.sha(p)
   for m,t in targets.items():
    if not T.near(s,t,0):continue
    result['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
    if v>1e-5:result['contacts'].append(dict(a='fixed/'+n+'/'+str(i),b=m,volume_mm3=v))
 result.update(status='RETAINED_HEAD_NEW_BODY_SPACE_CLEAR_ONLY' if not result['contacts'] else 'REJECTED_RETAINED_HEAD_BODY_INTERFACES',
  changed_scene_head_datums=changed,source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
 save('retained-space-checks.json',result)
 print(json.dumps({k:result[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
if __name__=='__main__':run()
