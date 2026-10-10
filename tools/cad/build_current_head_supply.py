"""One matched editable head-supply Foundation/board carrier.

Current W2 remains unchanged except its carrier gains two independent wire
grips. Historical documents are never saved. All material is native pads and
pockets with a return-slot parameter, not a final opaque replacement BRep.
"""
import json,time,tempfile,shutil
from pathlib import Path
import plan_current_head_supply_coupled as C
from build_current_pwm_fixture import pad,pocket,tube
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import circle
from open_prototype_shared_distribution_carriers import validate
import MeshPart
A,Part,H,P,ROOT,BASE,OUT=C.A,C.Part,C.H,C.P,C.ROOT,C.BASE,C.OUT
MODEL=OUT/'HeadSupplyCurrent.FCStd'
WORK=OUT/'HeadSupplyNativeWork.FCStd'
SHIFT=A.Vector(-42,0,25)

def world(shape,local):
 q=shape.copy()
 if local:q.translate(SHIFT)
 return q

def bounds_feature(body,name,b,local,cut=False,parameter=False):
 x,y,z,xx,yy,zz=b
 if local:x+=42;xx+=42;z-=25;zz-=25
 # Sketches are body-local; Body.Shape already includes Body.Placement.
 # Foundation hasZ42.52, so subtracting only the head/root shift would
 # create three disconnected bodies42.52mm too high.
 lo=body.Placement.inverse().multVec(A.Vector(x,y,z));hi=body.Placement.inverse().multVec(A.Vector(xx,yy,zz))
 x,y,z=lo;xx,yy,zz=hi
 if cut:
  pocket(body,name,zz,[(x,y,xx-x,yy-y)],'W3Parameters.BandChannelDepth' if parameter else zz-z)
 else:pad(body,name,z,[(x,y,xx-x,yy-y)],zz-z)

def run():
 tick=time.monotonic();q=H.read(OUT/'coupled-checks.json')
 assert q['status']=='CURRENT_COUPLED_HEAD_SUPPLY_SPACE' and not q['contacts'],q['status']
 assert not MODEL.exists(),'Receive the existing native candidate before any rebuild'
 p=C.build();g=C.allocations();reader=P.SavedShapes();source=C.S.C.OUT/'HeadWiringAccess.FCStd'
 C.S.save('received-grips.json',{k:v for k,v in g.items() if k not in ('parts','bands')})
 paths={n:C.S.Q.makewire(v['parts']) for n,v in p['routes'].items()};radii={}
 for n,w in paths.items():
  for e,f in zip(w.Edges,w.Edges[1:]):
   assert (e.valueAt(e.LastParameter)-f.valueAt(f.FirstParameter)).Length<1e-5,n
   assert e.tangentAt(e.LastParameter).dot(f.tangentAt(f.FirstParameter))>1-1e-5,n
  bends=[1/e.curvatureAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/1000) for e in w.Edges if 'Line' not in str(type(e.Curve)) for i in range(1001) if e.curvatureAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/1000)>1e-8]
  radii[n]=min(bends or [1e9]);assert radii[n]>=(.99 if n.endswith('_bare') else 5.99 if n.startswith('F_') else 12.599),n
 for n in ('F_HY_out','F_HP_out'):assert paths[n].Length<=84.5,n
 d=A.openDocument(str(WORK if WORK.exists() else source))
 if WORK.exists():
  bodies={'Foundation':d.Foundation,'UpperCarrier001':d.UpperCarrier001}
  old={n:world(reader.shape(source,n),n!='UpperCarrier001') for n in bodies}
  params=d.W3Parameters
  if 'FramesCorrected' not in params.PropertiesList:
   for body in bodies.values():
    for ob in body.Group:
     if ob.TypeId=='Sketcher::SketchObject' and ob.Name.startswith('W3'):
      ob.Placement=body.Placement.inverse()*ob.Placement
   params.addProperty('App::PropertyBool','FramesCorrected');params.FramesCorrected=True
  if 'RetentionSimplified' not in params.PropertiesList:
   # Remove only the unselected extra grip, not W2's retained native graph.
   pose=d.Head_YawCarrier.LinkPlacement;d.Head_YawCarrier.setLink(d.Interface14);d.Head_YawCarrier.LinkPlacement=pose
   extra=d.getObject('W3YawCarrierNative')
   if extra:
    for ob in reversed(list(extra.Group)):
     if ob.Name!=d.Interface14.Name:d.removeObject(ob.Name)
    d.removeObject(extra.Name)
   for name,dz,dh in [('YawSourceBridgeRoot',0,1.3),('YawSourceBridge',1.3,0),('YawSourcePost',1.3,-1.3)]:
    ob=d.getObject('W3_'+name);ob.Profile[0].Placement.Base.z+=dz;ob.Length=ob.Length.Value+dh
   for row in g['cuts']:
    if 'CaseSide' in row['name']:
     bounds_feature(d.Foundation,'W3_'+row['name'],row['bounds_mm'],True,cut=True)
   params.addProperty('App::PropertyBool','RetentionSimplified');params.RetentionSimplified=True
   d.recompute();d.saveAs(str(WORK))
  d.recompute()
  native_names={n:b.Name for n,b in bodies.items()}
  print('Received saved native graph; body-local frames corrected once',flush=True)
 else:
  build_new(d,reader,source,g)
  bodies={'Foundation':d.Foundation,'UpperCarrier001':d.UpperCarrier001}
  native_names={n:b.Name for n,b in bodies.items()};params=d.W3Parameters
  old={n:world(reader.shape(source,n),n!='UpperCarrier001') for n in bodies}
 return finish(d,bodies,native_names,params,old,paths,radii,p,g,reader,source,tick)

def build_new(d,reader,source,g):
 bodies={'Foundation':d.Foundation,'UpperCarrier001':d.UpperCarrier001}
 native_names={n:b.Name for n,b in bodies.items()}
 old={n:world(b.Shape,n!='UpperCarrier001') for n,b in bodies.items()}
 params=d.addObject('App::FeaturePython','W3Parameters');params.addProperty('App::PropertyLength','BandChannelDepth');params.BandChannelDepth=1.5
 foundation=bodies['Foundation'];material={n:s for n,s in g['parts'].items() if not n.endswith('_case') and 'SJ4570' not in n}
 # Build connected load paths, not dictionary order: the low floor must
 # follow its neck/bridge, otherwise PartDesign rejects a second solid.
 pending=dict(material);joined=old['Foundation'].copy();i=0
 while pending:
  connected=None
  for n,s in pending.items():
   candidate=joined.fuse(H.T.box(H.bb(s)))
   if candidate.isValid() and len(candidate.Solids)==1:connected=(n,candidate);break
  assert connected is not None,('Disconnected load paths',list(pending))
  n,joined=connected;s=pending.pop(n);bounds_feature(foundation,'W3_'+n,H.bb(s),True);i+=1
  print('Native Foundation pad',i,n,flush=True)
 # Reproduce the two retained root holes and L-shaped floor; their boxes
 # were allocation conveniences, never permission to fill these clearances.
 sk=sketch(foundation,'W3RetainedRootBoresPlan',71.52-25-foundation.Placement.Base.z)
 for x in (-122,-112):circle(sk,x+42-foundation.Placement.Base.x,-22.5-foundation.Placement.Base.y,2.2)
 foundation.Tip=feature(foundation,'Pocket','W3RetainedRootBores',sk,3.52)
 bounds_feature(foundation,'W3GroundFloorBridgeClearance',[-137,-27,113.40378221735,-123,-10,116.40378221735],True,cut=True)
 padgroups={'Foundation':g['pads'],'YawCarrier':g['yaw_pads'],'UpperCarrier001':g['carrier_pads']}
 # Foundation pads are already in material. The other two belong to their
 # actual supporting native body, not a floating post in the Foundation.
 for name in ('UpperCarrier001',):
  for row in padgroups[name]:bounds_feature(bodies[name],'W3_'+row['name'],row['bounds_mm'],name!='UpperCarrier001')
 cutgroups={'Foundation':g['cuts'],'UpperCarrier001':g['carrier_cuts']}
 for name,rows in cutgroups.items():
  for row in rows:bounds_feature(bodies[name],'W3_'+row['name'],row['bounds_mm'],name!='UpperCarrier001',cut=True,parameter='Return' in row['name'])
  print('Native slots',name,len(rows),flush=True)
 params.addProperty('App::PropertyBool','FramesCorrected');params.FramesCorrected=True
 params.addProperty('App::PropertyBool','RetentionSimplified');params.RetentionSimplified=True

def finish(d,bodies,native_names,params,old,paths,radii,p,g,reader,source,tick):
 for name,body in bodies.items():
  if not body.Shape.isValid() or len(body.Shape.Solids)!=1 or body.Shape.check(True):
   diagnosis=[]
   for ob in body.Group:
    if hasattr(ob,'Shape') and ob.Shape.Solids:
     diagnosis.append(dict(name=ob.Name,valid=ob.Shape.isValid(),solids=len(ob.Shape.Solids),volume=ob.Shape.Volume,state=list(ob.State)))
   C.S.save('native-failure.json',dict(body=name,history=diagnosis,worker_seconds=time.monotonic()-tick))
   d.saveAs(str(WORK))
   print('Native diagnostic',name,diagnosis[-8:],flush=True)
 validate(d,list(bodies.values()))
 current={n:world(b.Shape,n!='UpperCarrier001') for n,b in bodies.items()}
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False)
 def solid(n,s,m,t,pose=None):
  if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,pose=pose))
 def curve(n,c,rr,m,t,pose=None):
  if not H.T.near(c,t,rr):return
  r['pairs']+=1;dist=c.distToShape(t)[0]
  if dist<rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr,pose=pose))
 delta={n:s.cut(old[n]) for n,s in current.items()}
 targets,torso=C.S.C.F.physical_scene(reader);targets.pop('UpperCarrier001',None)
 targets['HeadFixedAnchor']=reader.shape(source,'HeadFixedAnchor')
 targets.update({n:s for n,s in g['parts'].items() if n.endswith('_case')})
 for n,s in delta.items():
  for m,t in targets.items():solid('added/'+n,s,m,t)
 for n,s in current.items():
  for m,t in current.items():
   if n<m:solid(n,s,m,t)
 for n,s in g['bands'].items():
  for m,t in {**targets,**current,**{k:v for k,v in g['parts'].items() if k.endswith('_case')}}.items():solid(n,s,m,t)
  for m,t in g['bands'].items():
   if n<m:solid(n,s,m,t)
 # Every planned route vs final cut native material/bands, with only its
 # assigned purchase case/pad exceptions inherited from the spatial proof.
 for n,c in paths.items():
  for m,t in {**current,**g['bands']}.items():curve(n,c,p['routes'][n]['radius'],m,t)
 # Explicit insulation on two formed0.5mm2 board ends outside solder pads.
 tape={}
 for n in ('XS13','XS23'):
  bare=p['routes'][n+'_bare']['parts'];lower=[bare[0],C.S.line(bare[0]['end'],[bare[1]['end'][0],13.97,82.5])]
  tape[n+'_FormedInsulation']=tube(lower,p['routes'][n+'_bare']['radius']+.33)
  first=paths[n].Edges[0];u=first.getParameterByLength(3)
  edge=first.Curve.toShape(first.FirstParameter,u)
  wire=Part.Wire([edge]);start=edge.valueAt(edge.FirstParameter)
  tape[n+'_JacketOverlap']=wire.makePipeShell([Part.Wire([Part.makeCircle(1.38,start,edge.tangentAt(edge.FirstParameter))])],True,False)
  for key in (n+'_FormedInsulation',n+'_JacketOverlap'):
   assert tape[key].isValid() and len(tape[key].Solids)==1,key
   for m,t in {**targets,**current,**g['bands']}.items():solid(key,tape[key],m,t)
 for y in (-15,0,15):
  for pitch in (-10,0,5):
   for m,t in H.head(reader,y,pitch).items():
    for n,s in {**delta,**g['bands'],**tape}.items():
     if m=='Foundation':continue # Same static receiving body checked above.
     solid(n,s,'head/'+m,t,[y,pitch])
  locals={n:(w,rr) for n,(w,rr,_) in H.local(y).items() if n.startswith('local/')}
  for name in C.S.C.K.PACK:
   locals[name+'_CurrentLoop']=(Part.read(str(C.S.C.OUT/f'{name}_yaw{y:+}_Loop.brep')),1.05)
  for n,(w,rr) in locals.items():
   for m,t in {**delta,**g['bands']}.items():curve(n,w,rr,m,t,pose=y)
  for name in ('XB13','XS13','XB22'):
   for n,(w,rr) in locals.items():
    if n.startswith('local/') and '/'+name+'/' in n:continue
    required=rr+1.05
    if H.T.near(paths[name],w,required):
     r['pairs']+=1;dist=paths[name].distToShape(w)[0]
     if dist<required-1e-4:r['contacts'].append(dict(a=name,b=n,pose=y,distance_mm=dist,required_mm=required))
  print('Native changed interfaces yaw',y,'contacts',len(r['contacts']),flush=True);C.S.save('native-progress.json',r)
 if r['contacts']:
  r.update(status='REJECTED_NATIVE_HEAD_SUPPLY',worker_seconds=time.monotonic()-tick);C.S.save('native-checks.json',r);d.saveAs(str(WORK));A.closeDocument(d.Name);print(json.dumps(r),flush=True);return
 volumes={n:b.Shape.Volume for n,b in bodies.items()};params.BandChannelDepth=1.6;d.recompute();validate(d,list(bodies.values()))
 assert all(abs(b.Shape.Volume-volumes[n])>.01 for n,b in bodies.items())
 params.BandChannelDepth=1.5;d.recompute();validate(d,list(bodies.values()));assert all(abs(b.Shape.Volume-volumes[n])<1e-5 for n,b in bodies.items())
 group=d.addObject('App::DocumentObjectGroup','W3SupplyReferences')
 for name,s in {**paths,**g['bands'],**tape,**{n:s for n,s in g['parts'].items() if n.endswith('_case') or 'SJ4570' in n}}.items():
  ob=d.addObject('PartDesign::Feature','W3Ref_'+name);ob.Shape=s;group.addObject(ob)
  if name in paths:ob.addProperty('App::PropertyLength','ProfileRadius');ob.ProfileRadius=p['routes'][name]['radius']
 exports=[]
 for n,b in bodies.items():
  mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
  assert mesh.isSolid() and not mesh.hasNonManifolds(),n
  bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
  size=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(size)+10<256,(n,size)
  dest=OUT/(n+'_current_x1.stl');mesh.write(str(dest));exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),size_mm=size,quantity=1,print_ready=False))
 d.recompute();d.saveAs(str(MODEL));A.closeDocument(d.Name)
 with tempfile.TemporaryDirectory(prefix='cat-head-supply-') as td:
  moved=Path(td)/MODEL.name;shutil.copy2(MODEL,moved);d=A.openDocument(str(moved));d.recompute();validate(d,[d.getObject(native_names[n]) for n in bodies])
  assert all(abs(d.getObject(native_names[n]).Shape.Volume-volumes[n])<1e-5 for n in bodies)
  assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  A.closeDocument(d.Name)
 r.update(status='CURRENT_NATIVE_HEAD_SUPPLY_PREPARED',model_sha256=P.sha(MODEL),exports=exports,native_parameter_restore=True,fresh_relocated_reopen=True,minimum_radii_mm=radii,
  source_sha256={**reader.hashes,source.relative_to(ROOT).as_posix():P.sha(source),Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),(OUT/'coupled-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'coupled-checks.json'),Path(C.G.__file__).relative_to(ROOT).as_posix():P.sha(Path(C.G.__file__)),(OUT/'received-grips.json').relative_to(ROOT).as_posix():P.sha(OUT/'received-grips.json')},
  native_bodies=native_names,T18I_new=g['T18I_new'],SJ4570_reused_pairs=1,formed_end_insulation={'layers':2,'nominal_added_radius_mm':.33,'intact_overlap_mm':3,'below_assigned_PCB_pad_z_mm':82.5},
  limits='Functional neck wire reachesZ160.594 above omitted cosmetic torso; no torso widening/closed-shell or physical fit claim.',worker_seconds=round(time.monotonic()-tick,3))
 C.S.save('native-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','worker_seconds')}),flush=True)
if __name__=='__main__':run()
