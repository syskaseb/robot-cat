"""Receive only changed PWM loop and the split ground-support load path.

All completed unchanged wire/body/head pairs are retained by hash. The west
return is outside the complete wing, not another cut through its edge.
"""
import json,time,copy
from pathlib import Path
import plan_current_head_supply as S
A,Part,H,P,ROOT,BASE,OUT=S.A,S.Part,S.H,S.P,S.ROOT,S.BASE,S.OUT
original_layout=S.layout

def layout():
 p=original_layout();p.pop('GroundPost')
 p['GroundFoot']=H.T.box([-103,-34,71.52,-95,-21.2,74.52])
 p['GroundSouthRib']=H.T.box([-103,-34,74.52,-95,-30.5,113.40378221735])
 p['GroundNorthRib']=H.T.box([-103,-24.7,74.52,-95,-21.2,113.40378221735])
 return p

def build():
 p=S.build();q=p['routes']['XS13']['parts'];tail=q[-1];y,z=tail['start'][1:]
 idx=next(i for i,v in enumerate(q) if v.get('end')==[-142.6,-98,64.2])
 q=q[:idx];S.straight(q,[-168.4,-98,64.2]);S.turn(q,[-168.4,-98,76.8],[-181,-98,76.8])
 S.straight(q,[-181,-98,z-12.6]);S.turn(q,[-168.4,-98,z-12.6],[-168.4,-98,z]);S.move(q,[1,0,0],[0,y+98,0]);S.straight(q,tail['start']);q.append(tail)
 p['routes']['XS13']['parts']=q
 p['changed_topology']+=' Entire lower PWM west return outside wing atX-181, separated from groundX-175.2; ground support replaced by two full ribs straddling the other PWM route.'
 return p

def run():
 tick=time.monotonic();old=json.loads((OUT/'space-checks.json').read_text())
 assert old['status']=='REJECTED_WHOLE_HEAD_SUPPLY_SPACE'
 assert {(v['a'],v['b']) for v in old['contacts']}=={('XS13','FoundationSouthWing'),('XS13','FHYFoot'),('XS13','FHYFloor'),('XS23','GroundPost')}
 S.save('rejected-support-crossings.json',old);S.save('rejected-support-plan.json',json.loads((OUT/'plan.json').read_text()))
 p=build();S.save('received-plan.json',p);paths={n:S.Q.makewire(v['parts']) for n,v in p['routes'].items()}
 changed=paths['XS13'];changed.exportBrep(str(OUT/'XS13.brep'))
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,
  reused_receipt_sha256=P.sha(OUT/'rejected-support-crossings.json'),reused_unmodified_paths=[n for n in paths if n!='XS13'],
  lengths_mm={n:w.Length for n,w in paths.items()})
 for e,f in zip(changed.Edges,changed.Edges[1:]):
  assert (e.valueAt(e.LastParameter)-f.valueAt(f.FirstParameter)).Length<1e-5
  assert e.tangentAt(e.LastParameter).dot(f.tangentAt(f.FirstParameter))>1-1e-5
 def curve(n,c,rr,m,t,required=None,pose=None):
  req=rr if required is None else required
  if not H.T.near(c,t,req):return
  r['pairs']+=1;d=min(c.distToShape(z)[0] for z in t.Solids) if t.Solids else c.distToShape(t)[0]
  if d<req-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=req,pose=pose))
 def solid(n,s,m,t,pose=None):
  if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,pose=pose))
 for n,c in paths.items():
  if n not in ('XS13','XS13_bare'):curve('XS13',changed,1.05,n,c,1.05+p['routes'][n]['radius'])
 reader=P.SavedShapes();targets,torso=S.C.F.physical_scene(reader)
 targets.update({n:reader.shape(S.C.OUT/'HeadWiringAccess.FCStd',n) for n in ('UpperCarrier001','HeadFixedAnchor')})
 parts=layout();heads={(y,pitch):H.head(reader,y,pitch) for y in (-15,0,15) for pitch in (-10,0,5)}
 for m,t in {**targets,**parts}.items():
  if t.Solids:curve('XS13',changed,1.05,m,t)
 for pose,group in heads.items():
  for m,t in group.items():curve('XS13',changed,1.05,'head/'+m,t,pose=pose)
 # Changed support ribs and the COMPLETE relocated pitch case/load path.
 module_names=['F_HP_case','FoundationNorthWing','FHPFoot','FHPPost','FHPFloor','GroundFoot','GroundSouthRib','GroundNorthRib','GroundFloor']
 for n in module_names:
  s=parts[n]
  for m,t in targets.items():solid(n,s,m,t)
  for pose,group in heads.items():
   for m,t in group.items():
    if m=='Foundation' and n!='F_HP_case':continue # intentional native union
    solid(n,s,'head/'+m,t,pose)
  for m,c in paths.items():
   cc=c
   if n=='F_HP_case' and m.startswith('F_HP'):
    cc=Part.Wire(c.Edges[1:]) if len(c.Edges)>1 else None
   if cc is not None:curve(m,cc,p['routes'][m]['radius'],n,s)
  print('Received whole load path',n,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True);S.save('received-progress.json',r)
 # Other CURRENT local head wires, not obsolete historical flex curves.
 for y in (-15,0,15):
  local={n:(c,rr) for n,(c,rr,_) in H.local(y).items() if n.startswith('local/')}
  for n,c in paths.items():
   rr=p['routes'][n]['radius'];owner=n.split('_')[0]
   for m,(other,rad) in local.items():
    if '/'+owner+'/' in m:continue
    curve(n,c,rr,m,other,rr+rad,pose=[y,0])
   for name in S.C.K.PACK:
    if owner==name:continue
    other=Part.read(str(S.C.OUT/f'{name}_yaw{y:+}_Loop.brep'))
    curve(n,c,rr,name+'_current_loop',other,rr+1.05,pose=[y,0])
 for n,w in paths.items():
  if n.startswith('F_') and n.endswith('_out'):assert w.Length<=84.5,(n,w.Length)
 r.update(status='CURRENT_HEAD_SUPPLY_RECEIVED_SPACE_ONLY' if not r['contacts'] else 'REJECTED_HEAD_SUPPLY_RECEIVED',
  worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,
   Path(S.__file__).relative_to(ROOT).as_posix():P.sha(Path(S.__file__)),Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),
   (OUT/'rejected-support-crossings.json').relative_to(ROOT).as_posix():P.sha(OUT/'rejected-support-crossings.json')})
 S.save('received-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
if __name__=='__main__':run()
