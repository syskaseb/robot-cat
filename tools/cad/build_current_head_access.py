"""Change one native terminal arm, retaining every selected head/root feature."""
import time,json,tempfile,shutil
from pathlib import Path
import plan_current_head_access as C
from build_current_pwm_fixture import rect
from open_prototype_shared_distribution_carriers import validate
import MeshPart
H,A,Part,P,ROOT,BASE,OUT=C.H,C.A,C.Part,C.P,C.ROOT,C.BASE,C.OUT
MODEL=OUT/'HeadWiringAccess.FCStd'
def run():
 tick=time.monotonic();q=H.read(OUT/'space-checks.json')
 assert q['status']=='CURRENT_HEAD_ACCESS_SPACE_CLEAR' and not q['contacts']
 assert not MODEL.exists(),'Do not duplicate an existing native candidate'
 source=C.K.OUT/'HeadWiringCurrent.FCStd';reader=P.SavedShapes()
 targets,torso=C.F.physical_scene(reader)
 d=A.openDocument(str(source));old=d.HeadFixedAnchor.Shape.copy()
 b=d.HeadFixedAnchor
 for name,bounds in [('W2AnchorWestOfATOPlan',[-74,33,8,65]),
  ('W2AnchorNorthBridgePlan',[-74,88,26,10]),
  ('W2AnchorInsulationLandPlan',[-56,88,8,8]),
  ('W2FullBandReturnPlan',[-60,91,16,2.5])]:
  s=d.getObject(name);assert s is not None,name
  for i in range(s.GeometryCount-1,-1,-1):s.delGeometry(i)
  rect(s,*bounds)
 # Saving native Shape through a temporary is necessary: FreeCAD property
 # getters return copies; translate the copy then explicitly assign it.
 for name in ('W2_Band','W2_TieHead'):
  obj=d.getObject(name);shape=obj.Shape.copy();shape.translate(A.Vector(0,18,0));obj.Shape=shape
 for n in C.K.PACK:
  curve=Part.read(str(OUT/f'{n}_yaw+0_Loop.brep'));d.getObject('W2_'+n+'_MovingLoop').Shape=curve
  end=curve.Edges[-1].valueAt(curve.Edges[-1].LastParameter)
  d.getObject('W2_'+n+'_FixedTail').Shape=Part.makeLine(end,end-A.Vector(0,9,0))
 d.recompute();validate(d,[b,d.UpperCarrier001]);assert len(b.Shape.Solids)==1
 delta=b.Shape.cut(old);assert delta.isValid()
 hardware={name:d.getObject(name).Shape for name in ('W2_Band','W2_TieHead')}
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False)
 def check(n,s,m,t):
  if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
  r['pairs']+=1;v=sum(a.common(bb).Volume for a in s.Solids for bb in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 for n,s in {'AddedArm':delta,**hardware}.items():
  for m,t in targets.items():
   if m=='UpperCarrier001':continue
   check(n,s,m,t)
 for n,s in hardware.items():check(n,s,'HeadFixedAnchor',b.Shape)
 for y in (-15,0,15):
  for pitch in (-10,0,5):
   for m,t in H.head(reader,y,pitch).items():
    for n,s in {'AddedArm':delta,**hardware}.items():check(n,s,'head/'+m,t)
  curves={n:Part.read(str(OUT/f'{n}_yaw{y:+}_Loop.brep')) for n in C.K.PACK}
  for n,c in curves.items():
   for m,t in {'Anchor':b.Shape,**hardware}.items():
    if not H.T.near(c,t,1.05):continue
    r['pairs']+=1;dist=c.distToShape(t)[0]
    if dist<1.05-1e-5:r['contacts'].append(dict(a=n,b=m,yaw=y,distance_mm=dist))
  for n,(c,rr,_) in H.local(y).items():
   if not n.startswith('local/'):continue
   for label,loop in curves.items():
    if '/'+label+'/' in n or not H.T.near(loop,c,rr+1.05):continue
    r['pairs']+=1;dist=loop.distToShape(c)[0]
    if dist<rr+1.05-1e-4:r['contacts'].append(dict(a=label+'_loop',b=n,yaw=y,distance_mm=dist))
   for m,t in {'AddedArm':delta,**hardware}.items():
    if not H.T.near(c,t,rr):continue
    r['pairs']+=1;dist=c.distToShape(t)[0]
    if dist<rr-1e-5:r['contacts'].append(dict(a=n,b=m,yaw=y,distance_mm=dist))
 print('Received native head access',r['pairs'],r['contacts'],flush=True)
 if r['contacts']:
  r.update(status='REJECTED_NATIVE_HEAD_ACCESS',worker_seconds=time.monotonic()-tick);C.save('native-checks.json',r);A.closeDocument(d.Name);return
 volume=b.Shape.Volume;d.W2Parameters.BandChannelDepth=1.6;d.recompute();validate(d,[b]);assert abs(b.Shape.Volume-volume)>.1
 d.W2Parameters.BandChannelDepth=1.5;d.recompute();validate(d,[b]);assert abs(b.Shape.Volume-volume)<1e-5
 mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
 assert mesh.isSolid() and not mesh.hasNonManifolds();bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
 size=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(size)+10<256
 dest=OUT/'HeadFixedAnchor_current_x1.stl';mesh.write(str(dest));d.saveAs(str(MODEL));name=d.Name;A.closeDocument(name)
 with tempfile.TemporaryDirectory(prefix='cat-head-access-') as td:
  moved=Path(td)/MODEL.name;shutil.copy2(MODEL,moved);d=A.openDocument(str(moved));d.recompute();validate(d,[d.HeadFixedAnchor,d.UpperCarrier001])
  assert abs(d.HeadFixedAnchor.Shape.Volume-volume)<1e-5
  assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  A.closeDocument(d.Name)
 r.update(status='CURRENT_NATIVE_HEAD_ACCESS_PREPARED',model_sha256=P.sha(MODEL),
  exports=[dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),size_mm=size,quantity=1,print_ready=False)],
  native_parameter_restore=True,fresh_relocated_reopen=True,
  external_neck_material_outside_cosmetic_torso_mm3=delta.cut(torso).Volume,
  limits='Accepted torso unchanged. Functional head/neck arm and cable approach stay withinY+/-100 and belowZ158, above omitted cosmetic shell. This is not a closed-shell fit claim.',
  source_sha256={**reader.hashes,source.relative_to(ROOT).as_posix():P.sha(source),
   (OUT/'space-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'space-checks.json'),
   Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 C.save('native-checks.json',r);print(json.dumps(r),flush=True)
if __name__=='__main__':run()
