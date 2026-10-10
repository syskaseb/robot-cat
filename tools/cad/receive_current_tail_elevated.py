"""Receive changed W4 support registers; reuse unchanged233-pair receipt.

Flat-ended sleeves do not have spherical endcaps. A radial screen reporting
their end faces is resolved by valid actual finite cylinders, never a waiver.
"""
import json,time,math
from pathlib import Path
import plan_current_tail_elevated as E
Q,C,B,A,Part,P,OUT,ROOT=E.Q,E.C,E.B,E.A,E.Part,E.P,E.OUT,E.ROOT

def run():
 tick=time.monotonic();old=B.read(OUT/'elevated-received-plan.json');p=E.build()
 assert p['routes']==old['routes'],'Only support/factory receipt, not another body-route rerun'
 prior=B.read(OUT/'elevated-received-space-checks.json');assert prior['pairs']==233
 reader=P.SavedShapes();targets,torso=E.scene(reader);local=E.local(targets,reader);added=E.layout()
 for b in p['carrier_reliefs_mm']:targets['UpperCarrier001']=targets['UpperCarrier001'].cut(Q.box(b))
 targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(Part.makeCylinder(.6,3,A.Vector(86.51,13.97,82.5)))
 targets['F_TY_case']=Q.box(p['F_TY']['body_bounds_mm'])
 tubes={n:C.tube(v['parts'],v['radius']) for n,v in p['routes'].items()}
 changed={n:s for n,s in added.items() if n in ('TailLocalRail','E2W4Addition') or n.startswith(('Band_Rail','TieHead_Rail','Band_Local','TieHead_Local','Band_JR','TieHead_JR','Band_FactoryGuard','TieHead_FactoryGuard'))}
 r=dict(status='PENDING',contacts=[],pairs=0,finite_sleeve_receipts=[],physical_pass=False,selected=False,unchanged_prior_pairs=233)
 done=set()
 def solid(n,s,m,t):
  key=tuple(sorted((n,m)))
  if n==m or key in done or not C.near(s,t,0):return
  done.add(key);assert s.isValid() and t.isValid() and s.Solids and t.Solids,(n,m)
  v=s.common(t).Volume;r['pairs']+=1
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 for n,s in changed.items():
  for m,t in {**targets,**added,**tubes}.items():solid(n,s,m,t)
  for m,(c,rr) in local.items():
   if not C.near(s,c,rr):continue
   d=s.distToShape(c)[0];r['pairs']+=1
   if d<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr))
 # Paired ground band changed only its support side channel, not dimensions.
 solid('E2W4Addition',added['E2W4Addition'],'Band_PairedSourceGround',added['Band_PairedSourceGround'])
 n='XS33';c=local['local/XS33/SLEEVE_CENTERLINE'][0];e=c.Edges[0]
 assert isinstance(e.Curve,Part.Line)
 sleeve=Part.makeCylinder(1.7,c.Length,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))
 v=tubes[n].common(sleeve).Volume;assert sleeve.isValid();r['pairs']+=1
 r['finite_sleeve_receipts'].append(dict(wire=n,conservative_finite_cylinder_mm3=v,basis='Full valid flat-capped outer sleeve, no rounded cap assumption'))
 if v>1e-5:r['contacts'].append(dict(a=n,b='local sleeve',volume_mm3=v))
 factory,meta=E.factory();rr=math.hypot(1.75,.9)
 for n,s in {**targets,**added,**tubes}.items():
  if not C.near(factory,s,rr):continue
  assert s.isValid() and s.Solids,n
  d=factory.distToShape(s)[0];r['pairs']+=1
  if d<rr-1e-5:r['contacts'].append(dict(a='factory',b=n,distance_mm=d,required_mm=rr))
 for n,(c,cr) in local.items():
  if 'factory' in n or not C.near(factory,c,rr+cr):continue
  d=factory.distToShape(c)[0];r['pairs']+=1
  if d<rr+cr-1e-5:r['contacts'].append(dict(a='factory',b=n,distance_mm=d,required_mm=rr+cr))
 approach=Part.Wire(factory.Edges[:-1]);end=approach.Vertexes[-1].Point;ball=Part.makeSphere(6,end)
 d=approach.cut(ball).distToShape(factory.Edges[-1].cut(ball))[0];r['factory_nonlocal_distance_mm']=d
 assert d>=2*rr and meta['radius_mm']>=22 and abs(meta['uncut_total_mm']-250)<1e-6
 path=OUT/'FactoryCurrentFinalCentreline.brep';factory.exportBrep(str(path));B.save('elevated-final-plan.json',p)
 r.update(status='CURRENT_W4_SHARED_SPACE_PREPARED' if not r['contacts'] else 'CURRENT_W4_SHARED_SPACE_REJECTED',worker_seconds=round(time.monotonic()-tick,3),
  factory=meta,curve_sha256=P.sha(path),source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),
   Path(E.__file__).relative_to(ROOT).as_posix():P.sha(Path(E.__file__)),(OUT/'elevated-final-plan.json').relative_to(ROOT).as_posix():P.sha(OUT/'elevated-final-plan.json'),
   (OUT/'elevated-received-space-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'elevated-received-space-checks.json')},
  scope='Only changed supports, all new factory247 curve, flat-ended sleeve receipt. Original M3/E2 immutable; final current native qualification still required.')
 B.save('elevated-final-space-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','factory_nonlocal_distance_mm','worker_seconds')}),flush=True)
if __name__=='__main__':run()
