"""Build the one jointly qualified W1 candidate, never overwrite its sources.

Queue native features before recompute. Three receiving bodies retain their
original history; case adhesion and wire relief remain separate functions.
"""
import json,time,tempfile,shutil
from pathlib import Path
import plan_current_aux_grips as G
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from open_prototype_shared_distribution_carriers import validate
from build_current_pwm_fixture import tube
import MeshPart
W=G.W;A,Part,ROOT,BASE,OUT=W.A,W.Part,W.ROOT,W.BASE,W.OUT
MODEL=OUT/'AUXPowerCurrent.FCStd'
WORK=OUT/'AUXPowerNativeWork.FCStd'
SOURCE=BASE/'head-supply-checkpoint/HeadSupplyCurrent.FCStd'
E2SOURCE=BASE/'tail-wiring-checkpoint/TailWiringRelease.FCStd'
SHIFT=A.Vector(-42,0,25)

def world(body):
 s=body.Shape.copy()
 if body.Name=='Foundation':s.translate(SHIFT)
 return s

def bounds_feature(body,row,cut=False,parameter=False):
 x,y,z,xx,yy,zz=row['bounds_mm']
 if body.Name=='Foundation':x+=42;xx+=42;z-=25;zz-=25
 inv=body.Placement.inverse();lo=inv.multVec(A.Vector(x,y,z));hi=inv.multVec(A.Vector(xx,yy,zz))
 x,y,z=lo;xx,yy,zz=hi
 oldtip=body.Tip
 sk=sketch(body,'W1_'+row['name']+'Plan',zz if cut else z)
 rect(sk,x,y,xx-x,yy-y)
 ob=body.newObject('PartDesign::Pocket' if cut else 'PartDesign::Pad','W1_'+row['name'])
 ob.Profile=sk;ob.BaseFeature=oldtip
 if cut and parameter:ob.setExpression('Length',f'{zz-z:.12f} mm + W1Parameters.BandClearance - 0.2 mm')
 else:ob.Length=zz-z
 body.Tip=ob;sk.Visibility=False
 return ob

def insulation(plan):
 result={}
 for n in ('XA02','XA03','XA04'):
  bare=plan['routes'][n+'_bare'];outer=tube(bare['parts'],bare['radius']+.33)
  wire=W.makewire(plan['routes'][n]['parts']);edge=wire.Edges[-1 if n=='XA02' else 0]
  a=edge.getParameterByLength(edge.Length-3) if n=='XA02' else edge.FirstParameter
  b=edge.LastParameter if n=='XA02' else edge.getParameterByLength(3)
  jacket=Part.Wire([edge.Curve.toShape(a,b)])
  overlap=jacket.makePipeShell([Part.Wire([Part.makeCircle(1.58,edge.valueAt(a),edge.tangentAt(a))])],True,False)
  result[n+'_FormedTapeEnvelope']=outer.fuse(overlap).removeSplitter()
  assert result[n+'_FormedTapeEnvelope'].isValid() and len(result[n+'_FormedTapeEnvelope'].Solids)==1,n
 # These are finished sleeve envelopes, not printable solid replacements.
 for n in ('XA02_sleeve','XB11_sleeve'):result[n]=tube(plan['routes'][n]['parts'],2.4)
 return result

def run():
 tick=time.monotonic();q=json.loads((OUT/'grip-checks.json').read_text());s=json.loads((OUT/'whole-layout-solid-checks.json').read_text())
 assert q['status']=='SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN' and not q['contacts'] and not q['errors'],q['status']
 assert s['status']=='SOLID_CLEARANCE_ONLY_MOUNTS_OPEN' and not s['contacts'] and not s['reservation_conflicts'] and not s['errors'],s['status']
 assert not MODEL.exists() and not WORK.exists(),'Receive the saved native candidate; do not build a duplicate'
 g=G.allocation();p=g['source_plan']
 assert json.loads((OUT/'grip-plan.json').read_text())=={k:v for k,v in g.items() if k not in ('bands','purchased')},'Support allocation changed after qualification'
 assert json.loads((OUT/'whole-layout-plan.json').read_text())==p,'Route allocation changed after qualification'
 reader=W.SavedShapes();targets,_=W.current_scene(reader,p)
 d=A.openDocument(str(SOURCE));d.Label='Current AUX power and retained head receiving parts';e=A.openDocument(str(E2SOURCE))
 # Recursive copy preserves the editable native history and its parameter
 # dependency graph. Renaming, if any, is recorded, never silently assumed.
 e2=d.copyObject(e.E2Fixture,True);A.closeDocument(e.Name)
 bodies={'Foundation':d.Foundation,'UpperCarrier001':d.UpperCarrier001,'E2Fixture':e2}
 params=d.addObject('App::VarSet','W1Parameters');params.addProperty('App::PropertyLength','BandClearance');params.BandClearance=.2
 old={n:world(b) for n,b in bodies.items()}
 for owner,body in bodies.items():
  for row in g['pads']:
   if row['owner']==owner:bounds_feature(body,row)
  owned_cuts=[row for row in g['cuts'] if row['owner']==owner]
  # Use a slot THROUGH actual new material, not an empty clearance at the
  # end of the feature list. Nominal dimensions and allocations stay fixed.
  controlled={'Foundation':'GAux1Return','UpperCarrier001':'AuxVINSlot2','E2Fixture':'PAuxReturn'}
  for row in owned_cuts:bounds_feature(body,row,cut=True,parameter=row['name']==controlled[owner])
  d.recompute();print('W1 native body',owner,'solids',len(body.Shape.Solids),flush=True)
  if not body.Shape.isValid() or len(body.Shape.Solids)!=1:
   W.save('native-failure.json',dict(body=owner,history=[dict(name=o.Name,state=list(o.State),solids=len(o.Shape.Solids)) for o in body.Group if hasattr(o,'Shape')]))
   d.saveAs(str(WORK));raise AssertionError(owner)
 validate(d,list(bodies.values()))
 # Preserve the editable candidate before any expensive/fallible acceptance
 # gate. A failed last assertion must not discard the whole construction.
 d.saveAs(str(WORK));print('Native W1 candidate saved before final checks',flush=True)
 current={n:world(b) for n,b in bodies.items()};delta={n:s.cut(old[n]) for n,s in current.items()}
 removed={n:old[n].cut(s).Volume for n,s in current.items()}
 assert all(v<1e-5 for v in removed.values()),removed
 tape=insulation(p);r=dict(status='PENDING',contacts=[],errors=[],pairs=0,physical_pass=False,selected=False,removed_retained_material_mm3=removed)
 def solid(n,s,m,t):
  if not s.Solids or not t.Solids or not W.near(s,t,0):return
  assert s.isValid() and t.isValid(),(n,m)
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 def curve(n,c,rr,m,t):
  if not t.Solids or not W.near(c,t,rr):return
  r['pairs']+=1;distance=c.distToShape(t)[0]
  if distance<rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=distance,required_mm=rr))
 for name in bodies:targets.pop(name,None)
 targets.update(g['purchased'])
 for n,s in {**{'added/'+n:s for n,s in delta.items()},**g['bands'],**tape}.items():
  for m,t in {**targets,**current}.items():
   if n=='added/'+m:continue
   solid(n,s,m,t)
  for m,t in g['bands'].items():
   if n<m:solid(n,s,m,t)
 paths={n:W.makewire(v['parts']) for n,v in p['routes'].items()}
 for n,c in paths.items():
  for m,t in {**delta,**g['bands']}.items():curve(n,c,p['routes'][n]['radius'],m,t)
  for m,t in tape.items():
   if (m.startswith(n.removesuffix('_bare')+'_Formed') or m==n or
    m=='XA02_sleeve' and n in ('XA02','F_AUX_factory_out') or
    m=='XB11_sleeve' and n in ('XB11','F_HY_factory_in')):continue
   curve(n,c,p['routes'][n]['radius'],m,t)
 # Geometry of the final native receiving bodies, not a saved green box
 # proposal, is checked against all retained fixed wiring.
 for folder,filename in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
  for n,v in json.loads((BASE/folder/filename).read_text())['routes'].items():
   if 'reserved' in n or n=='F_HY_input_prefix':continue
   for m,t in {**delta,**g['bands'],**tape}.items():curve('retained/'+n,W.makewire(v['parts']),v['radius'],m,t)
 local_pins={}
 for yaw in (-15,0,15):
  for pitch in (-10,0,5):
   for m,t in W.F.H.head(reader,yaw,pitch).items():
    if m=='Foundation':continue
    for n,s in {**delta,**g['bands'],**tape}.items():solid(n,s,'head/'+m,t)
  local=W.F.H.local(yaw)
  for n in ('XB22','XB23','XS23'):
   filename=BASE/'head-wiring-access-checkpoint'/f'{n}_yaw{yaw:+}_Loop.brep'
   local[n+'_CurrentLoop']=(Part.read(str(filename)),1.05,filename)
  for n,(c,rr,filename) in local.items():
   local_pins[filename.relative_to(ROOT).as_posix()]=W.sha(filename)
   for m,t in {**delta,**g['bands'],**tape}.items():curve(n,c,rr,m,t)
   for m,w in paths.items():
    required=rr+p['routes'][m]['radius']
    if W.near(c,w,required):
     r['pairs']+=1;distance=c.distToShape(w)[0]
     if distance<required-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=distance,required_mm=required,yaw=yaw))
  print('Native W1 head yaw',yaw,'contacts',len(r['contacts']),flush=True);W.save('native-progress.json',r)
 if r['contacts'] or r['errors']:
  d.saveAs(str(WORK));A.closeDocument(d.Name)
  r.update(status='REJECTED_NATIVE_W1',worker_seconds=round(time.monotonic()-tick,3));W.save('native-checks.json',r);print(json.dumps(r),flush=True);return
 volumes={n:b.Shape.Volume for n,b in bodies.items()};params.BandClearance=.3;d.recompute();validate(d,list(bodies.values()))
 assert all(abs(b.Shape.Volume-volumes[n])>.01 for n,b in bodies.items())
 params.BandClearance=.2;d.recompute();validate(d,list(bodies.values()))
 assert all(abs(b.Shape.Volume-volumes[n])<1e-5 for n,b in bodies.items())
 group=d.addObject('App::DocumentObjectGroup','W1References')
 refs={**paths,**g['bands'],**tape,**g['purchased'],**{n:targets[n] for n in ('P_AUX_CP2','G2_CP2','F_AUX_candidate_case','W4_TieHead_PairedSourceGround')}}
 for n,s in refs.items():
  ob=d.addObject('PartDesign::Feature','W1Ref_'+n);ob.Shape=s;group.addObject(ob)
  if n in paths:ob.addProperty('App::PropertyLength','ProfileRadius');ob.ProfileRadius=p['routes'][n]['radius']
 exports=[]
 for n,body in bodies.items():
  mesh=MeshPart.meshFromShape(Shape=body.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
  assert mesh.isSolid() and not mesh.hasNonManifolds(),n
  b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
  size=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(size)+10<256,(n,size)
  dest=OUT/(n+'_current_x1.stl');mesh.write(str(dest));exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=W.sha(dest),size_mm=size,quantity=1,print_ready=False))
 names={n:b.Name for n,b in bodies.items()};d.recompute();d.saveAs(str(MODEL));A.closeDocument(d.Name)
 with tempfile.TemporaryDirectory(prefix='cat-aux-power-') as td:
  relocated=Path(td)/MODEL.name;shutil.copy2(MODEL,relocated);d=A.openDocument(str(relocated));d.recompute()
  validate(d,[d.getObject(n) for n in names.values()])
  assert all(abs(d.getObject(names[n]).Shape.Volume-v)<1e-5 for n,v in volumes.items())
  assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  A.closeDocument(d.Name)
 r.update(status='CURRENT_NATIVE_W1_PREPARED',model_sha256=W.sha(MODEL),native_bodies=names,exports=exports,
  native_parameter_restore=True,fresh_relocated_reopen=True,T18I_new=g['T18I_new'],worker_seconds=round(time.monotonic()-tick,3),
  source_sha256={**reader.hashes,**local_pins,**{f.relative_to(ROOT).as_posix():W.sha(f) for f in (SOURCE,E2SOURCE,Path(__file__),Path(G.__file__),Path(W.__file__),OUT/'grip-checks.json',OUT/'whole-layout-solid-checks.json',OUT/'whole-layout-plan.json')}})
 W.save('native-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','worker_seconds')}),flush=True)

if __name__=='__main__':run()
