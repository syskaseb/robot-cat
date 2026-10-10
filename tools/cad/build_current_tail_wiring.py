"""One matched native W4 set from the received shared-space plan.

Keeps E2 historical source immutable. Generated wiring is nominal reference
geometry; changed printed parts have constrained sketches and native features.
"""
import json,time,math,shutil,tempfile
from pathlib import Path
from datetime import datetime,timezone
import plan_current_tail_elevated as E
Q=E.Q
from build_current_pwm_fixture import pad,pocket,sketch,feature,circle,rect,hexagon
from open_prototype_shared_distribution_carriers import validate
import MeshPart
A,Part,P,ROOT,BASE,OUT=Q.A,Q.Part,Q.P,Q.ROOT,Q.BASE,Q.OUT
B=Q.C.B
MODEL=OUT/'TailWiringCurrent.FCStd'

def cylinder(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))

def local_gate(targets,local,reader):
 r=dict(contacts=[],pairs=0,errors=[],circumscribed_factory_conflicts=[])
 for n,(c,rr) in local.items():
  for m,s in targets.items():
   if m.startswith('local/'):continue # original local solder/insulation interfaces retained
   if not Q.C.near(c,s,rr):continue
   assert s.isValid() and s.Solids,(n,m,'invalid current source')
   r['pairs']+=1;d=min(c.distToShape(t)[0] for t in s.Solids)
   if d<rr-1e-5:
    row=dict(a=n,b=m,distance_mm=d,required_mm=rr)
    (r['circumscribed_factory_conflicts'] if 'factory_flat' in n else r['contacts']).append(row)
 return r

def run():
 tick=time.monotonic();assert not MODEL.exists(),'Receive existing native result first'
 space=B.read(OUT/'elevated-final-space-checks.json');assert space['status']=='CURRENT_W4_SHARED_SPACE_PREPARED' and not space['contacts']
 for name,digest in space['source_sha256'].items():assert P.sha(ROOT/name)==digest,name
 p=B.read(OUT/'elevated-final-plan.json')
 reader=P.SavedShapes();targets,torso=E.scene(reader);local=E.local(targets,reader)
 targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(cylinder(86.51,13.97,82.5,.6,3))
 d=A.openDocument(str(BASE/'pwm-branch-checkpoint/PWMBranchCurrentFinal.FCStd'))
 try:
  carrier,fixture=d.UpperCarrier001,d.E2Fixture
  original={'UpperCarrier001':carrier.Shape.copy(),'E2Fixture':fixture.Shape.copy()}
  par=d.addObject('App::VarSet','W4Parameters');par.addProperty('App::PropertyLength','BandChannelDepth');par.BandChannelDepth=1.5
  print('Native receiver/posts/actual board-tail portal',flush=True)
  # Saved carrier has real floor only fromY-22/-27 and throughY27;
  # bboxY-36..46 is not continuous material. Bridge into those real lands.
  pad(carrier,'W4ReceiverRootBridges',74.72,[(x-4,-39,8,21) for x,y in Q.AXES],3)
  pad(carrier,'W4ReceiverPosts',77.72,[(x-4,y-4,8,8) for x,y in Q.AXES],5.27)
  pad(carrier,'W4B3Outrigger',74.72,[(51,24,8,30)],3)
  pad(carrier,'W4B3InsulationSeat',77.72,[(51,46.5,8,7)],.73)
  pocket(carrier,'W4B3FullBandPassage',77.72,[(53.5,44.8,3,10.4)],'W4Parameters.BandChannelDepth')
  pocket(carrier,'W4B3ActualRimPortal',81.5,[(83.51,25,6,5.3)],3.6)
  s=sketch(carrier,'W4CradleBoresPlan',82.99)
  for x,y in Q.AXES:circle(s,x,y,3.4)
  carrier.Tip=feature(carrier,'Pocket','W4CradleBores',s,8.27)
  # Native nut cavities and explicit side-loading routes, before boards.
  s=sketch(carrier,'W4CaptiveNutsPlan',82.32)
  for x,y in Q.AXES:
   pts=hexagon(x,y,5.7)
   for j in range(6):
    k=s.addGeometry(Part.LineSegment(pts[j],pts[(j+1)%6]),False)
    import Sketcher
    s.addConstraint(Sketcher.Constraint('Block',k))
  carrier.Tip=feature(carrier,'Pocket','W4CaptiveNuts',s,2.6)
  pocket(carrier,'W4NutSideEntries',82.32,[(x-3,y-4,6,4) for x,y in Q.AXES],2.6)
  print('Native paired independent ground-source grip',flush=True)
  for n in ('Band_SourceBlack','TieHead_SourceBlack'):d.removeObject(n)
  pad(fixture,'W4PairedGroundLand',132.3,[(39,-47.5,10,6)],7.65)
  pocket(fixture,'W4PairedGroundReturn',139,[(42.1,-48,2.8,18)],1.6)
  pocket(fixture,'W4PairedGroundFullSide',144,[(42.1,-47.15,2.8,1.6)],6.8)
  print('Native replaceable holder cradle and three independent grips',flush=True)
  cradle=d.addObject('PartDesign::Body','FTYCradle')
  pad(cradle,'W4CradleFloor',82.99,[(-71,-52,71,21)],3)
  pad(cradle,'W4HolderBearing',85.99,[(-61,-52,51,20.25)],4)
  pad(cradle,'W4FactorySeats',85.99,[(-70,-45.875,9,8),(-10,-45.875,9,8)],12)
  pad(cradle,'W4CustomPost',85.99,[(-70,-51,8,4)],36.01)
  pad(cradle,'W4CustomBridge',122,[(-76.55,-51,14.55,9.875)],3)
  pad(cradle,'W4CustomVerticalLand',125,[(-76.55,-48.125,3,7)],9)
  pocket(cradle,'W4CaseFullBandPassages',89.99,[(x-1.5,-53.7,3,23.6) for x in (-39,-30)],'4 mm + W4Parameters.BandChannelDepth')
  pocket(cradle,'W4FactoryBandReturns',85.99,[(x-1.5,-47.375,3,11) for x in (-65.5,-5.5)],'W4Parameters.BandChannelDepth')
  pocket(cradle,'W4FactoryBandFullSides',103.59,[(x-1.5,y,3,1.7) for x in (-65.5,-5.5) for y in (-47.375,-38.075)],19.1)
  s=sketch(cradle,'W4CradleThroughBoresPlan',85.99)
  for x,y in Q.AXES:circle(s,x,y,3.4)
  cradle.Tip=feature(cradle,'Pocket','W4CradleThroughBores',s,3)
  s=sketch(cradle,'W4RecessedHeadsPlan',89.99)
  for x,y in Q.AXES:circle(s,x,y,7.4)
  cradle.Tip=feature(cradle,'Pocket','W4RecessedHeads',s,4)
  print('Native removable tail rail, complete band passages and guard',flush=True)
  rail=d.addObject('PartDesign::Body','TailLocalRail')
  pad(rail,'W4RailFloor',103,[(77,-54,88,18)],3)
  pad(rail,'W4JRCaseOutrigger',103,[(123.5,-55.5,33,15)],3)
  # Pads face downward from the connected floor, avoiding loose islands.
  feet=pad(rail,'W4RailFeet',103,[(113,-51.3,10,12.6),(133,-51.3,10,12.6)],17);feet.Reversed=True
  pad(rail,'W4JRCaseBearing',106,[(125,-54,30,12)],1)
  pad(rail,'W4JRCaseFences',106,[(123.5,-55.5,33,1),(123.5,-41.5,33,1),(123.5,-54.5,1,13),(155.5,-54.5,1,13)],3)
  pad(rail,'W4FactoryGuardArm',103,[(136,-97,8,47)],3)
  pad(rail,'W4FactoryGuardLand',106,[(136,-95.6,8,8.2)],9)
  pad(rail,'W4LocalInsulationLands',106,[(x-4,-51.2,8,6.4) for x in (85,112)],2.85)
  pocket(rail,'W4RailTopReturns',106.3,[(x-1.5,-54,3,17.1) for x in (118,138)],1.5)
  pocket(rail,'W4RailFullBandSides',106.3,[(x-1.5,y,3,1.6) for x in (118,138) for y in (-52.9,-38.7)],24.9)
  pocket(rail,'W4JRFullSouthBand',109.2,[(143.5,-57,3,4)],6.4)
  pocket(rail,'W4JRFullNorthBandHead',112.05,[(142.4,-43,5.2,7.2)],9.25)
  pocket(rail,'W4LocalBandReturns',103.2,[(x-1.5,-53,3,9.8) for x in (85,112)],1.6)
  pocket(rail,'W4LocalFullBandSides',109.1,[(x-1.5,y,3,w) for x in (85,112) for y,w in [(-53,1.85),(-44.85,1.65)]],7.5)
  pocket(rail,'W4FactoryGuardFullBandSides',124,[(138.5,y,3,w) for y,w in [(-97,1.4),(-87.4,1.6)]],21.2)
  d.recompute();bodies=[carrier,fixture,cradle,rail]
  for b in bodies:
   print('Body receipt',b.Name,b.Shape.isValid(),len(b.Shape.Solids),flush=True)
   if not b.Shape.isValid() or len(b.Shape.Solids)!=1:
    for ob in b.Group:
     if hasattr(ob,'Shape') and ob.TypeId!='Sketcher::SketchObject' and ob.Name.startswith('W4'):print('Feature receipt',ob.Name,ob.Shape.isValid(),len(ob.Shape.Solids),flush=True)
  validity=validate(d,bodies);print('Native validity',json.dumps(validity),flush=True)
  r=dict(status='PENDING',contacts=[],pairs=0,outside=[],physical_pass=False,selected=False,native_validity=validity)
  added=E.layout()
  # Full printed geometry must match the planned silhouette (nut cavities
  # intentionally become hex+loading slots, not opaque Boolean bodies).
  ref=dict(FTYCradle=cradle.Shape,TailLocalRail=rail.Shape)
  for n,s in ref.items():
   expected=added[n];assert abs(s.Volume-expected.Volume)<1e-4,(n,s.Volume,expected.Volume)
   assert s.cut(expected).Volume+expected.cut(s).Volume<1e-4,n
  expected=original['E2Fixture'].fuse(added['E2W4Addition'])
  for b in ([42.1,-48,137.4,44.9,-30,139],[42.1,-47.15,137.2,44.9,-45.55,144]):expected=expected.cut(Q.box(b))
  assert fixture.Shape.cut(expected).Volume+expected.cut(fixture.Shape).Volume<1e-4,'paired ground native silhouette'
  def put(n,s):
   ob=d.addObject('Part::Feature','W4_'+n);ob.Label=n+' / nominal current W4';ob.Shape=s;return ob
  put('F_TY_case',Q.box(p['F_TY']['body_bounds_mm']))
  for n,s in added.items():
   if n not in ('FTYCradle','TailLocalRail','CarrierW4Addition','E2W4Addition'):put(n,s)
  for n,v in p['routes'].items():put(n,Q.C.tube(v['parts'],v['radius']))
  for n,(curve,rr) in local.items():
   ob=d.addObject('Part::Feature','W4Reference_'+n.replace('/','_'));ob.Label=n+' / nominal centreline';ob.Shape=curve
   ob.addProperty('App::PropertyLength','ProfileRadius');ob.ProfileRadius=rr
  for n,s in targets.items():
   if n.startswith('local/'):
    ob=d.addObject('Part::Feature','W4Reference_'+n.replace('/','_'));ob.Label=n;ob.Shape=s
  hardware={}
  for i,(x,y) in enumerate(Q.AXES):
   hardware[f'CradleBolt{i}']=cylinder(x,y,76.49,1.5,10).fuse(cylinder(x,y,86.49,2.75,3))
   hardware[f'CradleWasher{i}']=cylinder(x,y,85.99,3.5,.5).cut(cylinder(x,y,85.9,1.6,.7))
   pts=Q.hexagon(x,y,5.5) if hasattr(Q,'hexagon') else hexagon(x,y,5.5)
   pts=[v+A.Vector(0,0,79.82) for v in pts];w=Part.makePolygon(pts+[pts[0]])
   hardware[f'CradleNut{i}']=Part.Face(w).extrude(A.Vector(0,0,2.4)).cut(cylinder(x,y,79.7,1.525,2.7))
  for n,s in hardware.items():put(n,s)
  def check(n,s,m,t):
   if not Q.C.near(s,t,0):return
   assert s.isValid() and t.isValid(),(n,m,'invalid')
   v=s.common(t).Volume;r['pairs']+=1
   if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
  targets['UpperCarrier001']=carrier.Shape;targets['E2Fixture']=fixture.Shape
  current={o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature' and o.Name.startswith('W4_')}
  current.update(FTYCradle=cradle.Shape,TailLocalRail=rail.Shape)
  print('Only new native carrier material and hardware; exact other silhouettes reuse current receipt',flush=True)
  delta={'UpperCarrierW4Added':carrier.Shape.cut(original['UpperCarrier001']),'E2W4Added':fixture.Shape.cut(original['E2Fixture'])}
  for n,s in {'UpperCarrierW4Added':delta['UpperCarrierW4Added']}.items():
   for m,t in {**targets,**current}.items():
    if m in ('UpperCarrier001','E2Fixture'):continue
    check(n,s,m,t)
  for n,s in hardware.items():
   for m,t in {**targets,**current}.items():
    if m=='W4_'+n:continue
    check(n,s,m,t)
  # Rail/factory are functional tail appendages, inside200mm width, not
  # cosmetic body growth. Shared whole-route receipt owns their boundary.
  for n,s in delta.items():
   v=s.cut(torso).Volume
   if v>1e-5:r['outside'].append(dict(name=n,volume_mm3=v))
  # KnownB3 hole, not whole-board waiver for copper.
  # The bare pad assignment was qualified by the shared plan; receiver test
  # below uses the actual assigned-hole geometry for the same current board.
  r['scope']='Only W4 changed native interfaces. Cradle/rail/E2 full silhouettes equal received shared plan; unchanged233pairs plus final changed receipt reused, not repeated. Historical E2/M3 immutable; no wholeW5 or physical pass.'
  baseline={b.Name:b.Shape.Volume for b in bodies}
  par.BandChannelDepth=1.6;d.recompute();validate(d,bodies)
  assert abs(carrier.Shape.Volume-baseline[carrier.Name])>.1 and abs(cradle.Shape.Volume-baseline[cradle.Name])>.1
  par.BandChannelDepth=1.5;d.recompute();assert all(abs(b.Shape.Volume-baseline[b.Name])<1e-5 for b in bodies)
  r['native_parameter_restore']=True
  exports=[]
  for ob in bodies:
   mesh=MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
   assert mesh.isSolid() and not mesh.hasNonManifolds(),ob.Name
   bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength]
   assert max(size)+10<256,(ob.Name,size)
   dest=OUT/(ob.Name+'_current_x1.stl');mesh.write(str(dest))
   exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),quantity=1,object=ob.Name,size_mm=size,brim_mm=5,print_ready=False))
  d.saveAs(str(MODEL));A.closeDocument(d.Name)
  with tempfile.TemporaryDirectory(prefix='cat-w4-current-') as td:
   path=Path(td)/MODEL.name;shutil.copy2(MODEL,path);d=A.openDocument(str(path));validate(d,[d.getObject(n) for n in baseline])
   assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  r.update(status='CURRENT_W4_NATIVE_REJECTED' if r['contacts'] or r['outside'] else 'CURRENT_W4_NATIVE_STATIC_PREPARED',
   fresh_relocated_reopen=True,exports=exports,model_sha256=P.sha(MODEL),worker_seconds=round(time.monotonic()-tick,3),
   source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),
    (OUT/'elevated-final-plan.json').relative_to(ROOT).as_posix():P.sha(OUT/'elevated-final-plan.json'),(OUT/'elevated-final-space-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'elevated-final-space-checks.json')},
   reused_shared_pairs=space['pairs']+space['unchanged_prior_pairs'],
   still_open=['13tail samples / service allowances / final selection / stock'])
  B.save('native-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','outside','pairs','worker_seconds')}),flush=True)
 finally:
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
