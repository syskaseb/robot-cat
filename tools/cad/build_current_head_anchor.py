"""Editable current W2 anchor; matched carrier, real band and bolt stack.

No opaque printed Boolean master. Retained M2 head remains locally editable;
new receiver material is checked against the full retained W4/E2 context.
"""
import time,json,math,shutil,tempfile
from pathlib import Path
import plan_current_head_anchor as K
from build_current_pwm_fixture import pad,pocket,sketch,feature,circle,hexagon
from open_prototype_shared_distribution_carriers import validate
import MeshPart,Sketcher
H=K.H;A,Part,P,ROOT,BASE,OUT=H.A,H.Part,H.P,H.ROOT,H.BASE,H.OUT
MODEL=OUT/'HeadWiringCurrent.FCStd'
AXES=[(-60,-19),(-44,-19)]

def cylinder(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))

def run():
 tick=time.monotonic();assert not MODEL.exists(),'Receive native worker before starting another'
 q=H.read(OUT/'anchor-space-checks.json');assert q['status']=='CURRENT_HEAD_ANCHOR_SPACE_CANDIDATE' and not q['contacts'] and not q['outside']
 reader=P.SavedShapes();targets,torso=H.scene(reader);current_head=H.head(reader)
 source=A.openDocument(str(BASE/'tail-wiring-checkpoint/TailWiringRelease.FCStd'))
 d=A.openDocument(str(H.HEAD))
 try:
  carrier=d.copyObject(source.UpperCarrier001,True);d.recompute()
  assert len(carrier.Shape.Solids)==1
  original=carrier.Shape.copy();A.closeDocument(source.Name)
  par=d.addObject('App::VarSet','W2Parameters');par.addProperty('App::PropertyLength','BandChannelDepth');par.BandChannelDepth=1.5
  # Wider complete footprint than space-plan20mm avoids head/tool clashes
  # with the8mm post. Two axes16mm apart leave >=1.25mm to socket heads.
  pad(carrier,'W2AnchorReceiver',74.72,[(-66,-24,28,10)],3)
  feet=pad(carrier,'W2NutBosses',74.72,[(x-4,y-4,8,8) for x,y in AXES],2.6);feet.Reversed=True
  s=sketch(carrier,'W2RootBorePlan',77.72)
  for x,y in AXES:circle(s,x,y,3.4)
  carrier.Tip=feature(carrier,'Pocket','W2RootBores',s,5.6)
  s=sketch(carrier,'W2NutPocketPlan',74.72)
  for x,y in AXES:
   pts=hexagon(x,y,5.7)
   for i in range(6):
    j=s.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%6]),False);s.addConstraint(Sketcher.Constraint('Block',j))
  carrier.Tip=feature(carrier,'Pocket','W2CaptiveNuts',s,2.6)
  b=d.addObject('PartDesign::Body','HeadFixedAnchor')
  pad(b,'W2Foot',77.72,[(-66,-24,28,10)],3)
  for name,shape in K.solids().items():
   if name in ('CarrierRootBridge','AnchorFoot'):continue
   bounds=H.bb(shape);pad(b,'W2'+name,bounds[2],[(bounds[0],bounds[1],bounds[3]-bounds[0],bounds[4]-bounds[1])],bounds[5]-bounds[2])
  pocket(b,'W2FullBandReturn',133.4,[(-60,73,16,2.5)],'W2Parameters.BandChannelDepth')
  s=sketch(b,'W2FootBorePlan',80.72)
  for x,y in AXES:circle(s,x,y,3.4)
  b.Tip=feature(b,'Pocket','W2FootBores',s,3)
  d.recompute();print('Native current head anchor built',flush=True)
  validity=validate(d,[carrier,b]);assert len(carrier.Shape.Solids)==len(b.Shape.Solids)==1
  added=carrier.Shape.cut(original);assert added.isValid()
  r=dict(status='PENDING',contacts=[],outside=[],pairs=0,native_validity=validity,selected=False,physical_pass=False)
  hardware={}
  for i,(x,y) in enumerate(AXES):
   hardware[f'Bolt{i}']=cylinder(x,y,71.22,1.5,10).fuse(cylinder(x,y,81.22,2.75,3))
   hardware[f'Washer{i}']=cylinder(x,y,80.72,3.5,.5).cut(cylinder(x,y,80.6,1.6,.8))
   pts=[p+A.Vector(0,0,72.32) for p in hexagon(x,y,5.5)]
   hardware[f'Nut{i}']=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,2.4)).cut(cylinder(x,y,72.2,1.525,2.7))
  box=H.T.box
  band=box([-57.2,73,131.9,-46.8,75.5,133.1]).fuse(box([-57.2,73,131.9,-56,75.5,139.6])).fuse(box([-48,73,131.9,-46.8,75.5,139.6])).fuse(box([-57.2,73,138.4,-46.8,75.5,139.6])).removeSplitter()
  hardware['Band']=band;hardware['TieHead']=box([-46.8,72.85,137.1,-42.1,75.65,140.3])
  def put(n,s):
   o=d.addObject('Part::Feature','W2_'+n);o.Shape=s;return o
  for n,s in hardware.items():put(n,s)
  tail={}
  for n,v in K.PACK.items():
   end=A.Vector(*next(p['end_mm'] for p in q['poses'] if p['wire']==n and p['yaw']==0));tail[n]=Part.makeLine(end,end+A.Vector(0,-9,0))
   put(n+'_FixedTail',tail[n]);put(n+'_MovingLoop',Part.read(str(OUT/f'{n}_yaw+0_CurrentLoop.brep')))
  retained=H.local(0)
  for n,(c,rr,p) in retained.items():
   if n.startswith('flex/'):continue
   ob=put(n.replace('/','_'),c);ob.addProperty('App::PropertyLength','ProfileRadius');ob.ProfileRadius=rr
  def check(n,s,m,t):
   if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
   assert s.isValid() and t.isValid(),(n,m,'invalid')
   r['pairs']+=1;vol=sum(a.common(bb).Volume for a in s.Solids for bb in t.Solids)
   if vol>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=vol))
  for n,s in {'ReceiverAdded':added,'Anchor':b.Shape,**hardware}.items():
   for m,t in {**targets,**{'head/'+n:s for n,s in current_head.items()}}.items():
    if m=='UpperCarrier001':continue # exact carrier and foot/hardware tested below
    check(n,s,m,t)
   v=s.cut(torso).Volume
   if v>1e-5:r['outside'].append(dict(name=n,volume_mm3=v))
  for n,s in hardware.items():
   check(n,s,'Carrier',carrier.Shape);check(n,s,'Anchor',b.Shape)
  # Actual bolt tool, continuous vertical insertion on bare carrier.
  for x,y in AXES:check('SocketKey',cylinder(x,y,84.22,1.5,50),'Anchor',b.Shape)
  for name,c in tail.items():
   for m,t in {**targets,**{'Anchor':b.Shape,**hardware}}.items():
    if m=='UpperCarrier001' or not H.T.near(c,t,1.05):continue
    r['pairs']+=1;dist=min(c.distToShape(s)[0] for s in t.Solids)
    if dist<1.05-1e-5:r['contacts'].append(dict(a=name+'_FixedTail',b=m,distance_mm=dist,required_mm=1.05))
  # Old native head identities/frames remain exactly selectedM2. Shared
  # moving-loop receipt is reused; no unchanged whole mechanical audit.
  baseline={o.Name:o.Shape.Volume for o in (carrier,b)}
  par.BandChannelDepth=1.6;d.recompute();validate(d,[carrier,b]);assert abs(b.Shape.Volume-baseline[b.Name])>.1
  par.BandChannelDepth=1.5;d.recompute();assert all(abs(d.getObject(n).Shape.Volume-v)<1e-5 for n,v in baseline.items())
  exports=[]
  for ob in (carrier,b):
   mesh=MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
   assert mesh.isSolid() and not mesh.hasNonManifolds(),ob.Name
   bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
   dest=OUT/(ob.Name+'_current_x1.stl');mesh.write(str(dest));exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),size_mm=size,quantity=1,print_ready=False))
  d.saveAs(str(MODEL));A.closeDocument(d.Name)
  with tempfile.TemporaryDirectory(prefix='cat-w2-native-') as td:
   dest=Path(td)/MODEL.name;shutil.copy2(MODEL,dest);d=A.openDocument(str(dest));d.recompute();validate(d,[d.getObject(n) for n in baseline])
   assert all(abs(d.getObject(n).Shape.Volume-v)<1e-5 for n,v in baseline.items())
   assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  r.update(status='CURRENT_W2_NATIVE_PREPARED' if not r['contacts'] and not r['outside'] else 'REJECTED_CURRENT_W2_NATIVE',
   model_sha256=P.sha(MODEL),exports=exports,native_parameter_restore=True,fresh_relocated_reopen=True,
   root_axes_mm=AXES,bolt_stack_mm=dict(head_start=81.22,shaft_end=71.22,nut_bottom=72.32,nut_top=74.72,washer_bottom=80.72),
   fixed_tail_boundary_y_mm=67,unchanged_moving_loop_pairs=45,
   worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),
    (OUT/'anchor-space-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'anchor-space-checks.json')})
  H.save('anchor-native-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','outside','pairs','worker_seconds')}),flush=True)
 finally:
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
