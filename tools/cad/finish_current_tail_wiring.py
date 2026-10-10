"""Receive complete connector approaches, current tail motion and service.

Factory250 includes3mm exit and10mm final connector approach. R21 is a
NEW explicit6x3.5mm project assumption, not a numerical tolerance or supplier
rating. HistoricalR22/247-free-loop receipt remains an unselected candidate.
"""
import json,time,math,shutil,tempfile
from pathlib import Path
import numpy as np
import build_current_tail_wiring as N
E,Q,C,B,A,Part,P,ROOT,BASE,OUT=N.E,N.Q,N.Q.C,N.B,N.A,N.Part,N.P,N.ROOT,N.BASE,N.OUT
MODEL=OUT/'TailWiringCurrentFinal.FCStd'

def factory():
 old,_=E.factory();approach=Part.Wire(old.Edges[:-1]);remaining=237-approach.Length
 u=np.linspace(0,1,601);s=10*u**3-15*u**4+6*u**5;a=np.pi/2+2*np.pi*u;f=(1-np.cos(np.pi*u))/2
 lo,hi=22.,30.
 for _ in range(40):
  radius=(lo+hi)/2;pts=np.column_stack([149+16*f+radius*np.cos(a),-41.5-6.5*s+radius*(np.sin(a)-1),120.5-8.5*s])
  c=Part.BSplineCurve();c.interpolate([A.Vector(*v) for v in pts]);edge=c.toShape()
  if edge.Length>remaining:hi=radius
  else:lo=radius
 path=Part.Wire(list(approach.Edges)+[edge,Part.makeLine(A.Vector(165,-48,112),A.Vector(155,-48,112))])
 assert path.isValid() and abs(path.Length+3-250)<1e-4
 minimum=min(22,E.radius(edge));assert minimum>=21
 return path,dict(total_uncut_mm=250,exit_mm=3,external_with_JR_approach_mm=path.Length,storage_and_approach_mm=path.Length-10,
  final_JR_approach_mm=10,minimum_sampled_radius_mm=minimum,required_project_radius_mm=21,
  basis='Provisional3.5x1.8mm profile,6xmaximum_width21mm design assumption; delivered cable/exit/length/radius must be dry-fitted before fabrication. Not manufacturer minimum.')

def run():
 tick=time.monotonic();assert not MODEL.exists(),'Receive existing final result first'
 old=B.read(OUT/'native-checks.json');assert old['status']=='CURRENT_W4_NATIVE_STATIC_PREPARED' and not old['contacts'] and not old['outside']
 assert P.sha(OUT/'TailWiringCurrent.FCStd')==old['model_sha256']
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False)
 d=A.openDocument(str(OUT/'TailWiringCurrent.FCStd'));reader=P.SavedShapes();targets,torso=E.scene(reader);local=E.local(targets,reader)
 try:
  # One matched native modification; material removal only, no carrier rebuild.
  d.W4FactoryGuardLand.Length=7.8;d.recompute()
  native={n:d.getObject(n).Shape for n in ('UpperCarrier001','E2Fixture','FTYCradle','TailLocalRail')}
  for n,s in native.items():assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
  current={o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature' and o.Name.startswith('W4_')}
  targets.update(native);targets.update(current)
  targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(N.cylinder(86.51,13.97,82.5,.6,3))
  fac,meta=factory();local['local/factory_flat_circumscribed_RESERVATION']=(fac,math.hypot(1.75,.9))
  # Explicit previously omitted8mm JR-extension approaches; compact triangle
  # is preserved through the assigned case face, not an invented new pinout.
  prefixes={}
  for name in ('XB32','XB33','XS33'):
   curve,rr=local['local/'+name+'/0_CENTERLINE'];edge=curve.Edges[0];v=edge.valueAt(edge.FirstParameter)
   assert abs(v.x-117)<1e-5,(name,v)
   prefixes['JR/'+name]=(Part.makeLine(A.Vector(125,v.y,v.z),v),1.05)
  local.update(prefixes)
  # Replace reference centreline, retaining exact current total length.
  for ob in d.Objects:
   if ob.Label.startswith('local/factory_flat_circumscribed_RESERVATION /'):
    ob.Shape=fac;ob.ProfileRadius=math.hypot(1.75,.9)
  for n,(s,rr) in prefixes.items():
   ob=d.addObject('Part::Feature','W4Reference_'+n.replace('/','_'));ob.Label=n+' / nominal connector entry';ob.Shape=s
  def check(n,s,m,t):
   if not C.near(s,t,0):return
   assert s.isValid() and t.isValid(),(n,m)
   v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
  def curvecheck(n,c,rr,m,t):
   if not C.near(c,t,rr):return
   assert c.isValid() and t.isValid(),(n,m)
   dist=c.distToShape(t)[0];r['pairs']+=1
   if dist<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr))
  print('Complete factory250 and both connector approaches',flush=True)
  for name,(c,rr) in {'factory':local['local/factory_flat_circumscribed_RESERVATION'],**prefixes}.items():
   for m,t in targets.items():
    compare=c
    if m=='local/JR_paired_RESERVATION':
     # Assigned planar terminal boundary, not a blanket housing waiver.
     # End10mm is straight intoX155; prefix starts onX125. Flat ends touch.
     if name=='factory':compare=Part.Wire(c.Edges[:-1]);assert abs(c.Edges[-1].Length-10)<1e-5
     else:
      bb=c.BoundBox;assert abs(bb.XMax-125)<1e-5 and abs(bb.XMin-117)<1e-5
      t=t.common(Q.box([125.00001,-100,0,200,0,200]));continue
    curvecheck(name,compare,rr,m,t)
  # Full coil against every other local curve, including final connector
  # stub; no invalid pipe used for a positive clearance verdict.
  for n,(c,rr) in local.items():
   if 'factory' in n:continue
   if C.near(fac,c,rr+math.hypot(1.75,.9)):
    dist=fac.distToShape(c)[0];r['pairs']+=1
    if dist<rr+math.hypot(1.75,.9)-1e-5:r['contacts'].append(dict(a='factory',b=n,distance_mm=dist))
  approach=Part.Wire(fac.Edges[:-2]);end=approach.Vertexes[-1].Point;ball=Part.makeSphere(6,end)
  distance=approach.cut(ball).distToShape(fac.Edges[-2].cut(ball))[0]
  assert distance>=2*math.hypot(1.75,.9),distance
  # Connector stub is a separate nonlocal return, excluding shared end only.
  end=fac.Edges[-2].Vertexes[-1].Point;ball=Part.makeSphere(6,end)
  assert fac.Edges[-1].cut(ball).distToShape(Part.Wire(fac.Edges[:-1]).cut(ball))[0]>=2*math.hypot(1.75,.9)
  print('Thirteen changed tail poses; retain M3 internal receipt',flush=True)
  tp=B.read(BASE/'tail-mount-checkpoint/tail-assembly-checks.json')
  new={**current,'Cradle':native['FTYCradle'],'Rail':native['TailLocalRail']}
  # Receiver addition against moving tail only; retained body is not repeated.
  oldcarrier=reader.shape(BASE/'pwm-branch-checkpoint/PWMBranchCurrentFinal.FCStd','UpperCarrier001')
  new['CarrierAdded']=native['UpperCarrier001'].cut(oldcarrier)
  oldfixture=reader.shape(BASE/'pwm-branch-checkpoint/PWMBranchCurrentFinal.FCStd','E2Fixture')
  new['FixtureAdded']=native['E2Fixture'].cut(oldfixture)
  for angle in range(-30,31,5):
   for name in tp['moving_identities']:
    shape=targets['tail/'+name].copy();shape.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
    for n,s in new.items():check(n,s,f'{name}@{angle}',shape)
    for n,(c,rr) in local.items():curvecheck(n,c,rr,f'{name}@{angle}',shape)
  r['tail_motion_samples']=list(range(-30,31,5))
  print('ATO/finger/bench service allowances',flush=True)
  allowances={'ATO_tool':Q.box([-46.5,-46.875,111.99,-24.5,-36.875,146.99]),
   'G_TAIL5_finger':Q.box([24,-48.5,145.5,35,-40.5,163.5]),
   'G_TAIL3_finger':Q.box([24,-39,145.5,35,-31,163.5])}
  for name,s in allowances.items():
   for m,t in targets.items():
    if name=='ATO_tool' and m in ('W4_F_TY_case','W4_Band_CaseA','W4_Band_CaseB','W4_TieHead_CaseA','W4_TieHead_CaseB'):continue
    check(name,s,m,t)
  # Housing-only lift10 then north15, after bothsource ends/pairedtie free.
  h=B.read(BASE/'pwm-branch-checkpoint/final-plan.json')['housing_bounds_mm']
  for name,box in [('JPWM_lift10',[h[0],h[1],h[2],h[3],h[4],h[5]+10]),('JPWM_north15',[h[0],h[1]-15,h[2]+10,h[3],h[4],h[5]+10])]:
   for m,t in targets.items():
    if m in ('JPWM','Band_Housing0','Band_Housing1','TieHead_Housing0','TieHead_Housing1'):continue
    # Only retained fixture/carrier/new W4 changed neighbours. E2 internal
    # release proof remains valid for untouched factory pair material.
    if m not in native and not m.startswith('W4_'):continue
    check(name,Q.box(box),m,t)
  r['service']='All power absent. ATO: cut two case bands, support holder, withdraw fuse into nominal tool space; delivery lid/ATO fit gate. JR: cut case band, support wire ends and unplug on open rail. To lift rail, first free G_TAIL5/B3 and factoryJR, cut two rail bands and local wire bands; no sweep of attached cables claimed. For complete tail root removal use M3 selected sequence after rail/three ends freed. Free both E2 source ends and paired ground band before JPWM lift10/north15; PCB supported, bench fallback.'
  r['factory']=meta;r['factory_nonlocal_distance_mm']=distance
  r['local_lengths']={n:dict(length_mm=c.Length,start_mm=list(c.Edges[0].valueAt(c.Edges[0].FirstParameter)),end_mm=list(c.Edges[-1].valueAt(c.Edges[-1].LastParameter))) for n,(c,rr) in local.items() if 'factory' not in n}
  r['native_parameter_restore']=old['native_parameter_restore'];r['native_validity']=N.validate(d,[d.getObject(n) for n in native])
  exports=[]
  for name in native:
   ob=d.getObject(name);mesh=N.MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
   assert mesh.isSolid() and not mesh.hasNonManifolds(),name
   bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
   dest=OUT/(name+'_final_x1.stl');mesh.write(str(dest));exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),object=name,quantity=1,size_mm=size,brim_mm=5,print_ready=False))
  d.saveAs(str(MODEL));A.closeDocument(d.Name)
  with tempfile.TemporaryDirectory(prefix='cat-w4-final-') as td:
   path=Path(td)/MODEL.name;shutil.copy2(MODEL,path);d=A.openDocument(str(path));N.validate(d,[d.getObject(n) for n in native]);assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  r.update(status='CURRENT_W4_FINAL_REJECTED' if r['contacts'] else 'CURRENT_W4_FINAL_PREPARED',worker_seconds=round(time.monotonic()-tick,3),
   exports=exports,fresh_relocated_reopen=True,model_sha256=P.sha(MODEL),
   source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),(OUT/'native-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'native-checks.json'),(OUT/'TailWiringCurrent.FCStd').relative_to(ROOT).as_posix():P.sha(OUT/'TailWiringCurrent.FCStd')})
  B.save('final-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds')}),flush=True)
 finally:
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
