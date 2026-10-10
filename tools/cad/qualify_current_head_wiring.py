"""Current W2 boundaries, changed supports and nominal service sequence."""
import time,json
from pathlib import Path
import finish_current_head_anchor as F
H,K,B=F.H,F.B.K,F.B
A,Part,P,ROOT,BASE,OUT=H.A,H.Part,H.P,H.ROOT,H.BASE,H.OUT

def run():
 tick=time.monotonic();q=H.read(OUT/'anchor-release-checks.json');assert q['status']=='CURRENT_W2_ANCHOR_RELEASE_PREPARED' and not q['contacts']
 reader=P.SavedShapes();anchor=reader.shape(B.MODEL,'HeadFixedAnchor');carrier=reader.shape(B.MODEL,'UpperCarrier001')
 old=reader.shape(BASE/'tail-wiring-checkpoint/TailWiringRelease.FCStd','UpperCarrier001');delta=carrier.cut(old)
 r=dict(status='PENDING',contacts=[],pairs=0,boundaries=[],motion_samples=[],physical_pass=False,selected=False)
 for y in (-15,0,15):
  local=H.local(y)
  for n in K.PACK:
   loop=Part.read(str(OUT/f'{n}_yaw{y:+}_CurrentLoop.brep')).Edges[0]
   # Index8 is the12mm sleeve centreline, NOT the routed wire end.
   last=local[f'local/{n}/7'][0].Edges[0]
   a,b=last.valueAt(last.LastParameter),loop.valueAt(loop.FirstParameter)
   gap=(a-b).Length;dot=last.tangentAt(last.LastParameter).dot(loop.tangentAt(loop.FirstParameter))
   assert gap<1e-6 and dot>1-1e-5,(y,n,gap,dot)
   end=loop.valueAt(loop.LastParameter)
   assert loop.tangentAt(loop.LastParameter).dot(A.Vector(0,-1,0))>1-1e-5
   r['boundaries'].append(dict(yaw=y,wire=n,gap_mm=gap,tangent_dot=dot,fixed_tail_end_mm=list(end+A.Vector(0,-9,0))))
   for name,(c,rr,p) in local.items():
    if not name.startswith('local/') or '/'+n+'/' in name or not H.T.near(loop,c,rr+1.05):continue
    r['pairs']+=1;d=loop.distToShape(c)[0]
    if d<rr+1.05-1e-4:r['contacts'].append(dict(yaw=y,a='loop/'+n,b=name,distance_mm=d,required_mm=rr+1.05))
  for p in (-10,0,5):
   r['motion_samples'].append(dict(yaw=y,pitch=p))
   for name,t in H.head(reader,y,p).items():
    for n,s in [('Anchor',anchor),('CarrierAdded',delta)]:
     if not H.T.near(s,t,0):continue
     r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
     if v>1e-5:r['contacts'].append(dict(yaw=y,pitch=p,a=n,b=name,volume_mm3=v))
  print('Current W2 boundary/support yaw',y,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True)
  H.save('head-final-progress.json',r)
 r.update(status='CURRENT_W2_NOMINAL_COMPLETE' if not r['contacts'] else 'REJECTED_CURRENT_W2_BOUNDARIES',
  reused_body_pairs=98,reused_moving_loop_pairs=45,native_anchor_pairs=36,
  model_sha256=P.sha(B.MODEL),service=['Sources removed. Release both JR pairs and designated local insulation bands before extracting either servo by retainedM2 procedure.',
   'For body/head separation, disconnect three W3 supply/PWM/return ends on supported bench, then cut new anchor band before undoing two accessibleM3 screws. Do not lift a soldered or taut harness.',
   'The two independent bolted modules are removed AFTER their wires are free; no connected cable sweep or live service claimed. Current head shell/52-part mechanical assembly remains selectedM2.'],
  source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 for y in (-15,0,15):
  for n in K.PACK:
   path=OUT/f'{n}_yaw{y:+}_CurrentLoop.brep';r['source_sha256'][path.relative_to(ROOT).as_posix()]=P.sha(path)
 H.save('head-final-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
if __name__=='__main__':run()
