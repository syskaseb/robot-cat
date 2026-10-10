"""Move the complete receiving U-turn, not individual wire nudges.

Retain the already received moving-loop pairs. Recheck the changed complete
three-wire approach against actual head poses and body/anchor geometry.
"""
import json,time,copy
from pathlib import Path
import plan_current_head_access as C
H,A,Part,P,ROOT,BASE,OUT=C.H,C.A,C.Part,C.P,C.ROOT,C.BASE,C.OUT
def run():
 tick=time.monotonic();original=H.read(OUT/'space-checks.json')
 assert original['status']=='REJECTED_HEAD_ACCESS_SPACE'
 assert len(original['contacts'])==1 and original['contacts'][0]['a']=='XS23_approach'
 archive=OUT/'rejected-west-turn.json'
 if not archive.exists():C.save(archive.name,original)
 prior=H.read(archive);reader=P.SavedShapes();targets,torso=C.F.physical_scene(reader)
 targets['UpperCarrier001']=reader.shape(C.K.OUT/'HeadWiringCurrent.FCStd','UpperCarrier001');targets.update(C.solids())
 incoming={};metadata=[]
 for n,c in C.approaches()[0].items():
  edges=[]
  for i,e in enumerate(c.Edges):
   if i<4:z=e.copy();z.translate(A.Vector(6,0,0))
   elif i==4:z=Part.makeLine(e.valueAt(e.FirstParameter)+A.Vector(6,0,0),e.valueAt(e.LastParameter))
   else:z=e
   edges.append(z)
  incoming[n]=Part.Wire(edges)
  metadata.append(dict(wire=n,start_mm=list(edges[0].valueAt(edges[0].FirstParameter)),end_mm=list(edges[-1].valueAt(edges[-1].LastParameter)),
   minimum_radius_mm=next(v['minimum_radius_mm'] for v in prior['receiving_approaches'] if v['wire']==n)))
 r=copy.deepcopy(prior);r.update(status='PENDING',contacts=[],pairs=0,receiving_approaches=metadata,
  reused_moving_loop_pairs=9,rejected_contact_witness_mm=[-141.7959231208,48.4596951171,137.2124355653],
  whole_U_turn_reallocated_east_mm=6)
 for n,c in incoming.items():
  c.exportBrep(str(OUT/(n+'_ReceivingApproach.brep')))
  for m,t in targets.items():
   if not t.Solids or not H.T.near(c,t,1.05):continue
   r['pairs']+=1;dist=min(c.distToShape(s)[0] for s in t.Solids)
   if dist<1.05-1e-5:r['contacts'].append(dict(a=n+'_approach',b=m,distance_mm=dist))
  for yaw in (-15,0,15):
   for pitch in (-10,0,5):
    for m,t in H.head(reader,yaw,pitch).items():
     if not H.T.near(c,t,1.05):continue
     r['pairs']+=1;dist=min(c.distToShape(s)[0] for s in t.Solids)
     if dist<1.05-1e-5:r['contacts'].append(dict(a=n+'_approach',b='head/'+m,pose=[yaw,pitch],distance_mm=dist))
  print('Received complete changed approach',n,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True);C.save('progress.json',r)
 for i,n in enumerate(incoming):
  for m in list(incoming)[i+1:]:
   r['pairs']+=1;dist=incoming[n].distToShape(incoming[m])[0]
   if dist<2.1-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist))
 r.update(status='CURRENT_HEAD_ACCESS_SPACE_CLEAR' if not r['contacts'] else 'REJECTED_HEAD_ACCESS_TURN',
  worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,
   archive.relative_to(ROOT).as_posix():P.sha(archive),
   Path(C.__file__).relative_to(ROOT).as_posix():P.sha(Path(C.__file__)),
   Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))})
 C.save('space-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
if __name__=='__main__':run()
