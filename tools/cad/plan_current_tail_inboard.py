"""Whole W4 architecture: inboard F_TY, port5 return, perimeter B3.

Preserve r1 as rejected evidence. Route, support and factory/JR space are
considered together, with actual solids after broad-phase filtering.
"""
import json,math,time
from datetime import datetime,timezone
from pathlib import Path
import plan_current_tail_wiring as B
from build_current_pwm_fixture import tube
A,Part,P,ROOT,BASE,OUT=B.A,B.Part,B.P,B.ROOT,B.BASE,B.OUT
line,arc,wire,box,near,shift=B.line,B.arc,B.wire,B.box,B.near,B.shift

def build():
 p=B.build();n=1.05/math.sqrt(3);zr=92-2*n;zg=92+n;y=-41.875
 factory=[line([-10,y,99.99],[-1,y,99.99]),arc([-1,y,105.99],[-1,y,99.99],[5,y,105.99]),
  line([5,y,105.99],[5,y,145.49]),arc([-1,y,145.49],[5,y,145.49],[-1,y,151.49]),line([-1,y,151.49],[-16,y,151.49])]
 red=[line([-16,y,151.49],[-65,y,151.49]),arc([-65,y,138.89],[-65,y,151.49],[-77.6,y,138.89]),
  line([-77.6,y,138.89],[-77.6,y,100.6]),arc([-65,y,100.6],[-77.6,y,100.6],[-65,y,88])]
 red+=shift(red[-1]['end'],[1,0,0],[0,-1,0],3.125)
 red+=shift(red[-1]['end'],[1,0,0],[0,0,1],zr-88)
 red+=[line(red[-1]['end'],[68,-45,zr])]
 sy=2*12.6*math.sin(math.acos(1-.55/25.2))
 ground=[line([37.5,-44.5,141],[42.5,-44.5,141]),arc([42.5,-44.5,128.4],[42.5,-44.5,141],[55.1,-44.5,128.4]),
  line([55.1,-44.5,128.4],[55.1,-44.5,zg+12.6+sy])]
 ground+=shift(ground[-1]['end'],[0,0,-1],[0,1,0],.55)
 ground+=[arc([67.7,-43.95,zg+12.6],[55.1,-43.95,zg+12.6],[67.7,-43.95,zg]),line([67.7,-43.95,zg],[68,-43.95,zg])]
 signal=[line([86.51,14.97,79.2],[86.51,37.4,79.2]),arc([73.91,37.4,79.2],[86.51,37.4,79.2],[73.91,50,79.2]),
  line([73.91,50,79.2],[-31.9,50,79.2]),arc([-31.9,37.4,79.2],[-31.9,50,79.2],[-44.5,37.4,79.2]),
  line([-44.5,37.4,79.2],[-44.5,-33.45,79.2]),arc([-31.9,-33.45,79.2],[-44.5,-33.45,79.2],[-31.9,-46.05,79.2])]
 signal+=shift(signal[-1]['end'],[1,0,0],[0,0,1],zg-79.2)
 signal+=[line(signal[-1]['end'],[68,-46.05,zg])]
 for k,q in [('XB32',red),('XB33',ground),('XS33',signal),('F_TY_factory_out',factory)]:p['routes'][k]['parts']=q
 p.pop('G_TAIL2');p['G_TAIL5']=dict(point_mm=[37.5,-44.5,141],entry_axis=[1,0,0],strip_mm=11,
  basis='Previously unused same-bus port5; E4 XB33 port2->5 rebind only. Port4 occupied XL09, NOT available.',delivered_datum=False)
 p['F_TY'].update(body_bounds_mm=[-61,-52,89.99,-10,-31.75,111.99],centre_mm=[-35.5,-41.875,100.99],rotation_z_deg=0)
 p['carrier_reliefs_mm']=[[83.51,36,77.9,89.51,45,81.5],[-47.5,36,77.9,-41.5,45,81.5]]
 p['support_plan']=['Replaceable F_TY cradle on upper carrier south rim; casing below seam, ATO tool X-46.5..-24.5/Y-46.875..-36.875 above112.',
  'Casing bands X-39/-30: south heads between actual bank TE output stems, not across lid.',
  'Ground port5: 5mm immediate stub then R12.6 down; independent 9mm vertical insulation grip atX55.1/Y-44.5/Z119..128.4 rooted in E2 west tab.',
  'B3: two explicit north rim portals, floor retained>=1.68mm; independent outside-PCB insulation band X55/Y50 on carrier-rooted outrigger.',
  'Retain all local sleeves/JR/R9 and uncut factory250; artificial X68 boundary is NOT an added joint or detachable end.']
 p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
 return p

def retained_local(targets,reader):
 curves={}
 folder=ROOT/'hardware/electronics/full-cat/tail-stationary-local-r3'
 for name in ('XB32','XB33','XS33'):
  for suffix,r in [('0_CENTERLINE',1.05),('1_CENTERLINE',1.05),('2_CENTERLINE',1.05),('SLEEVE_CENTERLINE',1.7)]:
   path=folder/f'{name}_{suffix}.brep';c=Part.read(str(path));c.translate(A.Vector(0,0,15))
   assert c.isValid() and c.Edges,path
   curves['local/'+name+'/'+suffix]=(c,r)
   reader.hashes[path.relative_to(ROOT).as_posix()]=P.sha(path)
 # Conservative circumscribed round profile of the provisional flat factory
 # cable. A positive overlap here is an envelope conflict, not supplier fact.
 path=folder/'FactoryUncutCentreline.brep';c=Part.read(str(path));c.translate(A.Vector(0,0,15));e=c.Edges[0]
 curves['local/factory_flat_circumscribed_RESERVATION']=(c,math.hypot(1.75,.9))
 targets['local/JR_paired_RESERVATION']=box([113,-51,87,143,-39,97])
 reader.hashes[path.relative_to(ROOT).as_posix()]=P.sha(path)
 return curves

def run(stem='inboard',supports=None):
 tick=time.monotonic();dest=OUT/(stem+'-space-checks.json');assert not dest.exists(),'Receive existing result first'
 p=build();B.save(stem+'-plan.json',p);reader=P.SavedShapes();targets,torso=B.scene(reader);local_curves=retained_local(targets,reader)
 for b in p['carrier_reliefs_mm']:targets['UpperCarrier001']=targets['UpperCarrier001'].cut(box(b))
 targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(Part.makeCylinder(.6,3,A.Vector(86.51,13.97,82.5)))
 targets['W4_F_TY_project_case']=box(p['F_TY']['body_bounds_mm'])
 # Check casing straps and all supports before generating an editable master.
 added={}
 for x in (-39,-30):
  outer=box([x-1.25,-53.2,88.79,x+1.25,-30.55,111.99]);inner=box([x-2,-52,89.99,x+2,-31.75,113])
  added[f'CaseBand{x}']=outer.cut(inner)
  added[f'CaseTieHead{x}']=box([x-2.4,-57.7,92.99,x+2.4,-53.2,96.49])
 added['GroundGripBack']=box([51,-48,119,54.05,-41,129.5])
 added['GroundGripTab']=box([49,-49,129.5,58,-40,132.3])
 added['B3SupportFoot']=box([51,39,74.72,59,54,77.72])
 added['B3InsulationLand']=box([51,46.5,77.72,59,53.5,78.15])
 if supports:added=supports(added)
 r=dict(status='PENDING',contacts=[],pairs=0,outside=[],errors=[],selected=False,W4_complete=False,physical_pass=False)
 curves={n:wire(q['parts']) for n,q in p['routes'].items()};tubes={n:tube(q['parts'],q['radius']) for n,q in p['routes'].items()}
 for n,t in tubes.items():
  assert t.isValid() and len(t.Solids)==1,n
  for m,s in {**targets,**added}.items():
   if not near(t,s,0):continue
   assert s.isValid() and s.Solids,(n,m,'invalid source')
   d=min(curves[n].distToShape(a)[0] for a in s.Solids);r['pairs']+=1
   if d>=p['routes'][n]['radius']-1e-5:continue
   v=t.common(s).Volume
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,distance_mm=d))
  v=t.cut(torso).Volume
  if v>1e-5:r['outside'].append(dict(name=n,volume_mm3=v))
  for m,(c,rr) in local_curves.items():
   # This is a single continuous wire split for accounting only. Prove
   # half-space ownership before allowing its designed shared cut face.
   compare=curves[n]
   if m=='local/'+n+'/2_CENTERLINE':
    end=A.Vector(*p['routes'][n]['parts'][-1]['end']);e=c.Edges[-1]
    assert (end-e.valueAt(e.LastParameter)).Length<1e-6 and c.BoundBox.XMin>=67.999999
    assert e.tangentAt(e.LastParameter).dot(A.Vector(1,0,0))<-.999
    # Only the final straight approaches the same continuous conductor;
    # all other body segments are still checked against its local segment.
    compare=curves[n].cut(Part.makeSphere(2.1,end))
   req=p['routes'][n]['radius']+rr
   if not near(compare,c,req):continue
   r['pairs']+=1;d=compare.distToShape(c)[0]
   if d<req-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=req,basis='Exact centreline distance with round/circumscribed profile, no failed sweep used'))
 for i,n in enumerate(tubes):
  for m in list(tubes)[i+1:]:
   if {n,m} in ({'XS33','XS33_bare'},{'XB32','F_TY_factory_out'}):continue
   if near(tubes[n],tubes[m],0):
    r['pairs']+=1;v=tubes[n].common(tubes[m]).Volume
    if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 for n,s in {'W4_F_TY_project_case':targets['W4_F_TY_project_case'],**added}.items():
  for m,t in targets.items():
   if m==n or m=='UpperCarrier001' and n in ('B3SupportFoot','B3InsulationLand','CarrierW4Addition') or m=='E2Fixture' and (n.startswith('GroundGrip') or n=='E2W4Addition'):continue
   if not near(s,t,0):continue
   r['pairs']+=1;v=s.common(t).Volume
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
  for m,(c,rr) in local_curves.items():
   if not near(s,c,rr):continue
   r['pairs']+=1;d=c.distToShape(s)[0]
   if d<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr))
 for i,(n,s) in enumerate(added.items()):
  for m,t in list(added.items())[i+1:]:
   if not near(s,t,0):continue
   r['pairs']+=1;v=s.common(t).Volume
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 r.update(status='REJECTED_INBOARD_W4_PLAN' if r['contacts'] or r['outside'] else 'CURRENT_W4_SHARED_SPACE_CANDIDATE',
  source_sha256={**p['source_sha256'],**reader.hashes},worker_seconds=round(time.monotonic()-tick,3),lengths_mm={n:c.Length for n,c in curves.items()},finished_utc=datetime.now(timezone.utc).isoformat(),
  still_open=['Complete native supports/bands/input reservation/lid and tools','Current local envelope/body and thirteen tail poses','Assembly/service/stock/reopen/exports/selection'],
  role_rebind={'XB33':'G_TAIL.2->G_TAIL.5, same ground bus; port4XL09 unchanged','F_TY':'Whole inboard pose; input W5 approach invalidated, not selected'})
 B.save(dest.name,r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','outside','worker_seconds')}),flush=True)
if __name__=='__main__':run()
