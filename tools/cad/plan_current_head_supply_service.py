"""Whole service-first source plan, including three grade-separated fanouts.

North pitch fuse was rejected: S0 blocked its wing and the fixed W2 arm
blocked ATO withdrawal. Allocate the COMPLETE fuse on the south free wing,
not another wire or screw offset. Existing receipts remain immutable.
"""
import json,time
from pathlib import Path
import receive_current_head_supply as R
S=R.S
A,Part,H,P,ROOT,BASE,OUT=S.A,S.Part,S.H,S.P,S.ROOT,S.BASE,S.OUT

def layout():
 p=R.layout()
 for n,b in {
  'F_HP_case':[-65,-74,89.99,-14,-53.75,111.99],
  'FoundationNorthWing':[-168,26,68.52,-108,60,71.52],
  'FoundationPitchSouthWing':[-168,-98,68.52,-12,-53.75,71.52],
  'FHPFoot':[-67,-74,71.52,-12,-53.75,74.52],
  'FHPPost':[-44,-68,74.52,-36,-60,85.99],
  'FHPFloor':[-67,-75.5,85.99,-12,-52,89.99]}.items():p[n]=H.T.box(b)
 return p

def build():
 p=S.build();routes=p['routes'];tails={n:routes[n]['parts'][-1] for n in ('XB12','XB13','XS13')}
 # Ground upper return stays above both other fanouts until its final
 # source straight. No independent packed triangle columns cross.
 q=routes['XB13']['parts'];idx=next(i for i,v in enumerate(q) if v.get('end')==[-175.2,-98,72.6]);q=q[:idx+1]
 g=tails['XB13']['start'];S.straight(q,[-175.2,-98,132.4]);S.turn(q,[-162.6,-98,132.4],[-162.6,-98,145])
 S.move(q,[1,0,0],[0,g[1]+98,0]);S.move(q,[1,0,0],[0,0,g[2]-145]);S.straight(q,g);q.append(tails['XB13']);routes['XB13']['parts']=q
 # PWM is BELOW the ground underpass, WEST of its complete wing, and
 # has a distinct upper returnY-94 before crossing the ground riser.
 x=81.43;q=[S.arc([68.83,14.97,79.2],[x,14.97,79.2],[68.83,27.57,79.2])]
 S.straight(q,[45,27.57,79.2]);S.move(q,[-1,0,0],[0,0,40.8]);S.move(q,[-1,0,0],[0,19.43,0])
 S.straight(q,[-90,47,120]);S.turn(q,[-90,34.4,120],[-102.6,34.4,120]);S.straight(q,[-102.6,-72.8,120])
 S.turn(q,[-102.6,-72.8,107.4],[-102.6,-85.4,107.4]);S.straight(q,[-102.6,-85.4,68.4]);S.turn(q,[-115.2,-85.4,68.4],[-115.2,-85.4,55.8])
 S.move(q,[-1,0,0],[0,-12.6,0]);S.straight(q,[-168.4,-98,55.8]);S.turn(q,[-168.4,-98,68.4],[-181,-98,68.4])
 S.straight(q,[-181,-98,100]);S.move(q,[0,0,1],[0,4,0]);S.straight(q,[-181,-94,124.4]);S.turn(q,[-168.4,-94,124.4],[-168.4,-94,137])
 s=tails['XS13']['start'];S.move(q,[1,0,0],[0,4,0]);S.move(q,[1,0,0],[0,0,s[2]-137]);S.move(q,[1,0,0],[0,s[1]+90,0]);S.straight(q,s);q.append(tails['XS13']);routes['XS13']['parts']=q
 zr=S.ZR;y=-63.875
 q=[S.line([-14,y,99.99],[-5,y,99.99])];S.turn(q,[-5,y,105.99],[1,y,105.99]);S.straight(q,[1,y,zr-6]);S.turn(q,[-5,y,zr-6],[-5,y,zr]);S.straight(q,[-25,y,zr]);routes['F_HP_out']['parts']=q
 routes['F_HP_input_prefix']['parts']=[S.line([-65,y,99.99],[-74,y,99.99])]
 q=[S.line([-17,y,zr],[-88.4,y,zr])];S.turn(q,[-88.4,-51.275,zr],[-101,-51.275,zr]);S.straight(q,[-101,59.1,zr]);S.turn(q,[-88.05,59.1,zr],[-88.05,72.05,zr]);S.straight(q,[-66,72.05,zr]);S.turn(q,[-66,85,zr],[-53.05,85,zr]);routes['XB22']['parts']=q
 routes['XB22_sleeve']['parts']=[S.line([-31,y,zr],[-11,y,zr])]
 p['factory_splices']['XB22']['centre_mm']=[-21,y,zr]
 p['changed_topology']='Service-first complete pitch case on south wing, EAST factory output/WEST input. Entire yaw source fanout has grade-separated underpasses and upper convergence, no wing/ATO collision patch. Both fuse outputs real, both inputs9mm reservations only.'
 return p

def run():
 tick=time.monotonic();prior=json.loads((OUT/'received-checks.json').read_text());assert prior['status']=='REJECTED_HEAD_SUPPLY_RECEIVED'
 p=build();S.save('service-plan.json',p);paths={n:S.Q.makewire(v['parts']) for n,v in p['routes'].items()}
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,lengths_mm={n:w.Length for n,w in paths.items()},reused_body_receipts=['space-checks.json','received-checks.json'])
 assigned=[('XB12','F_HY_out'),('XB22','F_HP_out'),('XS13','XS13_bare'),('XS23','XS23_bare')]+[(name+'_sleeve',part) for name,factory in [('XB12','F_HY_out'),('XB22','F_HP_out')] for part in (name,factory)]
 def curve(n,c,rr,m,t,required=None,pose=None):
  req=rr if required is None else required
  if not H.T.near(c,t,req):return
  r['pairs']+=1;distance,witness,_=c.distToShape(t)
  if distance<req-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=distance,required_mm=req,pose=pose,witness=[[list(v) for v in z] for z in witness[:1]]))
 def solid(n,s,m,t,pose=None):
  if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,pose=pose))
 for n,w in paths.items():
  for e,f in zip(w.Edges,w.Edges[1:]):
   assert (e.valueAt(e.LastParameter)-f.valueAt(f.FirstParameter)).Length<1e-5
   assert e.tangentAt(e.LastParameter).dot(f.tangentAt(f.FirstParameter))>1-1e-5,(n,e,f)
  w.exportBrep(str(OUT/(n+'_Service.brep')))
 for i,n in enumerate(paths):
  for m in list(paths)[i+1:]:
   if frozenset((n,m)) in [frozenset(v) for v in assigned]:continue
   curve(n,paths[n],p['routes'][n]['radius'],m,paths[m],p['routes'][n]['radius']+p['routes'][m]['radius'])
 if r['contacts']:
  r.update(status='REJECTED_SERVICE_PLAN_MUTUAL',worker_seconds=time.monotonic()-tick);S.save('service-checks.json',r);print(json.dumps(r),flush=True);return
 reader=P.SavedShapes();targets,torso=S.C.F.physical_scene(reader)
 targets.update({n:reader.shape(S.C.OUT/'HeadWiringAccess.FCStd',n) for n in ('UpperCarrier001','HeadFixedAnchor')})
 parts=layout();heads={(y,pitch):H.head(reader,y,pitch) for y in (-15,0,15) for pitch in (-10,0,5)}
 changed=['XB13','XS13','XB22','F_HP_out','F_HP_input_prefix','XB22_sleeve']
 for n in changed:
  c=paths[n];rr=p['routes'][n]['radius']
  for m,t in {**targets,**parts}.items():
   if not t.Solids:continue
   cc=c
   if n.startswith('F_HP') and m=='F_HP_case':cc=Part.Wire(c.Edges[1:]) if len(c.Edges)>1 else None
   if n=='XB13' and m=='G_AUX_case':cc=Part.Wire(c.Edges[1:])
   if cc is not None:curve(n,cc,rr,m,t)
  for pose,group in heads.items():
   for m,t in group.items():curve(n,c,rr,'head/'+m,t,pose=pose)
  print('Whole service wire',n,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True);S.save('service-progress.json',r)
 changedparts=['F_HP_case','FoundationPitchSouthWing','FHPFoot','FHPPost','FHPFloor']
 for n in changedparts:
  for m,t in targets.items():solid(n,parts[n],m,t)
  for pose,group in heads.items():
   for m,t in group.items():
    if m=='Foundation' and n!='F_HP_case':continue
    solid(n,parts[n],'head/'+m,t,pose)
  for m,c in paths.items():
   if m.startswith('F_HP') and n=='F_HP_case':continue
   curve(m,c,p['routes'][m]['radius'],n,parts[n])
 # Both ATOs have a dimensioned nominal35mm upward tool space after
 # cutting their case bands. It is a delivery fit gate, not a hand PASS.
 for label,x,y,z in [('HY',-140.5,-85.125,132),('HP',-39.5,-63.875,111.99)]:
  tool=H.T.box([x-11,y-5,z,x+11,y+5,z+35])
  for m,t in {**targets,**parts}.items():
   if m in ('F_HY_case' if label=='HY' else 'F_HP_case',):continue
   solid('ATO_'+label,tool,m,t)
  for pose,group in heads.items():
   for m,t in group.items():solid('ATO_'+label,tool,'head/'+m,t,pose)
 r.update(status='CURRENT_SERVICE_HEAD_SUPPLY_SPACE_ONLY' if not r['contacts'] else 'REJECTED_SERVICE_HEAD_SUPPLY_SPACE',worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,
  Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),Path(S.__file__).relative_to(ROOT).as_posix():P.sha(Path(S.__file__)),Path(R.__file__).relative_to(ROOT).as_posix():P.sha(Path(R.__file__)),
  (OUT/'space-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'space-checks.json'),(OUT/'received-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'received-checks.json')})
 S.save('service-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds')}),flush=True)
if __name__=='__main__':run()
