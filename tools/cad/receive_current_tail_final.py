"""Changed-only guard band and complete formedB3 insulation receipt."""
import math,time,json,shutil,tempfile
from pathlib import Path
import finish_current_tail_wiring as F
A,Part,P,B,C,Q,ROOT,BASE,OUT=F.A,F.Part,F.P,F.B,F.C,F.Q,F.ROOT,F.BASE,F.OUT
MODEL=OUT/'TailWiringSelected.FCStd'

def coating(plan):
 # Nominal two-layer0.15mm Temflex165 wrap,0.33mm conservative material
 # budget. Primary3M sheet supports half-lapped application, NOT acceptance
 # on this tiny formed terminal. Coverage/adhesion is an explicit phase2 gate.
 copper=plan['routes']['XS33_bare'];body=plan['routes']['XS33'];rr=copper['radius'];outer=rr+.33
 cover=C.tube(copper['parts'],outer)
 start=A.Vector(*copper['parts'][0]['start'])
 cover=cover.fuse(Part.makeSphere(1.38,start)).fuse(Part.makeCylinder(1.38,3,start,A.Vector(0,1,0)))
 cover=cover.common(Q.box([80,10,77,92,25,82.72]))
 cover=cover.cut(C.tube(copper['parts'],rr+.001)).cut(C.tube(body['parts'],1.051)).removeSplitter()
 assert cover.isValid() and cover.Solids and not cover.check(True)
 return cover

def run():
 tick=time.monotonic();assert not MODEL.exists(),'Receive existing selected model first'
 prior=B.read(OUT/'final-checks.json');assert len(prior['contacts'])==1 and prior['contacts'][0]['b']=='W4_Band_FactoryGuard'
 assert P.sha(OUT/'TailWiringCurrentFinal.FCStd')==prior['model_sha256']
 d=A.openDocument(str(OUT/'TailWiringCurrentFinal.FCStd'));reader=P.SavedShapes();targets,torso=F.E.scene(reader);local=F.E.local(targets,reader)
 try:
  s=d.W4FactoryGuardFullBandSides.Profile[0]
  for i in reversed(range(s.GeometryCount)):s.delGeometry(i)
  for y,width in [(-97,1.4),(-85.4,1.6)]:F.N.rect(s,138.5,y,3,width)
  d.recompute()
  band,head=Q.tie_x(140,-97,-84,101.8,123.5)
  d.W4_Band_FactoryGuard.Shape=band;d.W4_TieHead_FactoryGuard.Shape=head
  p=B.read(OUT/'elevated-final-plan.json');cover=coating(p)
  ob=d.addObject('Part::Feature','W4_B3FormedEndInsulation');ob.Label='B3 formed terminal / provisional two-layer Temflex165';ob.Shape=cover
  r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,reused_final_pairs=prior['pairs'])
  natives={n:d.getObject(n).Shape for n in ('UpperCarrier001','E2Fixture','FTYCradle','TailLocalRail')};targets.update(natives)
  targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(F.N.cylinder(86.51,13.97,82.5,.6,3))
  targets.update({o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature' and o.Name.startswith('W4_')})
  fac,meta=F.factory();local['factory']=(fac,math.hypot(1.75,.9));local.pop('local/factory_flat_circumscribed_RESERVATION')
  changed={'W4_Band_FactoryGuard':band,'W4_TieHead_FactoryGuard':head,ob.Name:cover}
  def check(n,s,m,t):
   if n==m or not C.near(s,t,0):return
   assert s.isValid() and t.isValid(),(n,m)
   v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
  for n,shape in changed.items():
   for m,t in targets.items():check(n,shape,m,t)
   for m,(curve,rr) in local.items():
    if n==ob.Name:continue # physical jacket/copper are already checked by positive material intersections above
    if not C.near(shape,curve,rr):continue
    dist=shape.distToShape(curve)[0];r['pairs']+=1
    if dist<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr))
  tp=B.read(BASE/'tail-mount-checkpoint/tail-assembly-checks.json')
  for angle in range(-30,31,5):
   for name in tp['moving_identities']:
    t=targets['tail/'+name].copy();t.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
    for n,shape in changed.items():check(n,shape,f'{name}@{angle}',t)
  # Only changed guard land was removed; verify its native parameter and
  # restore, without recomputing the unchanged receiver history.
  baseline=d.TailLocalRail.Shape.Volume;d.W4FactoryGuardLand.Length=7.9;d.recompute();assert abs(d.TailLocalRail.Shape.Volume-baseline)>1
  d.W4FactoryGuardLand.Length=7.8;d.recompute();assert abs(d.TailLocalRail.Shape.Volume-baseline)<1e-5
  validity=F.N.validate(d,[d.getObject(n) for n in natives])
  exports=[]
  for name in natives:
   mesh=F.N.MeshPart.meshFromShape(Shape=d.getObject(name).Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
   assert mesh.isSolid() and not mesh.hasNonManifolds();bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);bb=mesh.BoundBox
   size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
   dest=OUT/(name+'_selected_x1.stl');mesh.write(str(dest));exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),object=name,quantity=1,size_mm=size,brim_mm=5,print_ready=False))
  d.saveAs(str(MODEL));A.closeDocument(d.Name)
  with tempfile.TemporaryDirectory(prefix='cat-w4-selected-') as td:
   dest=Path(td)/MODEL.name;shutil.copy2(MODEL,dest);d=A.openDocument(str(dest));F.N.validate(d,[d.getObject(n) for n in natives]);assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  r.update(status='CURRENT_W4_COMPLETE_PREPARED' if not r['contacts'] else 'CURRENT_W4_COMPLETE_REJECTED',
   native_validity=validity,guard_parameter_restore=True,native_parameter_restore=prior['native_parameter_restore'],fresh_relocated_reopen=True,
   tail_motion_samples=prior['tail_motion_samples'],factory=meta,local_lengths=prior['local_lengths'],service=prior['service'],
   insulation=dict(sku='3M Temflex165 black15mm, LAPP61721030',nominal_layer_mm=.15,material_reservation_mm=.33,blank_mm=[15,50],
    primary_source='https://multimedia.3m.com/mws/media/2145173O/3m-temflex-vinyl-electrical-tape-165-datasheet-en-ner.pdf',
    instructions='Before board seating, wrap formedB3 lead to board underside with overlapping layers; overlap intact jacket>=3mm. Keep assigned hole/solder face clean, no soldered bare lead belowPCB. Inspect full coverage/adhesion and sleeve compatibility unpowered before any energizing. Project material reservation, not physical coverage verification.'),
   exports=exports,model_sha256=P.sha(MODEL),worker_seconds=round(time.monotonic()-tick,3),
   source_sha256={Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),(OUT/'final-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'final-checks.json'),(OUT/'TailWiringCurrentFinal.FCStd').relative_to(ROOT).as_posix():P.sha(OUT/'TailWiringCurrentFinal.FCStd')})
  B.save('complete-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds')}),flush=True)
 finally:
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
