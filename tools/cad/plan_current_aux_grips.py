"""Shared W1 load paths, complete bands and side-opening service allocation.

Plans material before editing native CAD. No selected part is overwritten.
Ordinary cuttable ties grip insulation, never the WAGO levers or PCB pads.
"""
import time,json,math
from pathlib import Path
import plan_current_aux_wiring as W
from plan_current_tail_complete import tie_x,tie_z
A,Part,ROOT,BASE,OUT=W.A,W.Part,W.ROOT,W.BASE,W.OUT
box=W.box

def allocation():
 p=W.build();pads=[];cuts=[];bands={};grips=[];material={};purchased={}
 def add(owner,n,b):
  pads.append(dict(owner=owner,name=n,bounds_mm=b));material[n]=box(b)
 def cut(owner,n,b):cuts.append(dict(owner=owner,name=n,bounds_mm=b))
 def horizontal(owner,n,x,y,z,r,base,width=7):
  top=z-r-.05;y0,y1=y-r-1.3,y+r+1.3;z0,z1=top-2.7,z+r+1.3
  add(owner,n+'Seat',[x-width/2,y-r-1.25,base,x+width/2,y+r+1.25,top])
  band,_=tie_x(x,y0,y1,z0,z1);bands[n+'Band']=band
  bands[n+'Head']=box([x-2.4,y-1.75,z1,x+2.4,y+1.75,z1+4.5])
  cut(owner,n+'Return',[x-1.5,y0-.2,z0-.1,x+1.5,y1+.2,z0+1.4])
  for i,(a,b) in enumerate(((y0-.2,y0+1.25),(y1-1.25,y1+.2))):cut(owner,n+'Side'+str(i),[x-1.5,a,z0-.1,x+1.5,b,z1+.2])
  grips.append(dict(name=n,axis='X',centre_mm=[x,y,z],radius_mm=r,T18I=1))
 # P_AUX is seated above G_TAIL. Root on the actual E2 west tab, not a
 # tall post through the retained FTY cradle or W3 pitch-ground conductor.
 add('E2Fixture','PAuxRootBridge',[4,-36,129.5,10,-22,132.3])
 add('E2Fixture','PAuxPost',[4,-36,132.3,10,-32,146.01])
 add('E2Fixture','PAuxBridge',[4,-36,146.01,28,-23,148.01])
 add('E2Fixture','PAuxFloor',[9,-50,146.01,28,-20,148.01])
 add('E2Fixture','PAuxReliefFloor',[28,-33,146.01,37,-23,148.01])
 purchased['PAuxSJ4570']=box([9.5,-46,148.01,27.5,-36,150.5])
 # One paired jaw, physically independent from the adhesive case retention.
 for y in (-25.5,-30.25):add('E2Fixture','PAuxSeat'+str(y),[29,y-2.5,148.01,36,y+2.5,153.7])
 band,_=tie_x(32.5,-32.8,-22.95,151,157.55);bands['PAuxBand']=band
 bands['PAuxHead']=box([30.1,-29.625,157.55,34.9,-26.125,162.05])
 cut('E2Fixture','PAuxReturn',[31,-33,150.9,34,-22.75,152.4])
 for i,(a,b) in enumerate(((-33,-31.55),(-24.2,-22.75))):cut('E2Fixture','PAuxSide'+str(i),[31,a,150.9,34,b,157.75])
 grips.append(dict(name='PAux',axis='X',centre_mm=[32.5,-27.875,155],wires=['XA03','XB11'],T18I=1))
 # Entire G2 is supported outside Pi/known PWM board footprints. Its
 # independent source jaw is outside the body/lever face.
 add('UpperCarrier001','G2RootBridge',[110,24,74.72,116,52,77.72])
 add('UpperCarrier001','G2Post',[110,44,77.72,116,52,145.01])
 add('UpperCarrier001','G2Floor',[82.5,29,145.01,118,59,148.01])
 purchased['G2SJ4570']=box([83,30,148.01,101,40,150.5])
 horizontal('UpperCarrier001','G2Source',106,53.5,155,1.25,148.01)
 # Preserve W3's existing two-port source jaw. Stagger adjacent bands
 # along the full9mm insulation stubs rather than overlaying five heads.
 z=123.39378221735
 for n,x,y in [('GAux1',-110,-16.3),('GAux2',-114,-21.05),('GAux5',-114,-35.3)]:horizontal('Foundation',n,x,y,z,1.25,116.40378221735,width=5)
 cut('Foundation','RetainedW3SouthBandClearance',[-112.95,-33.2,119.39,-110.05,-31.85,125.9])
 # The retained ring has TWO side legs. Its north leg also passes the
 # adjacent port2 seat; both slots remain outside the original W3 post.
 cut('Foundation','RetainedW3NorthBandClearance',[-112.95,-24.6,119.39,-110.05,-23.15,125.9])
 horizontal('E2Fixture','GTail1',43.5,-25.5,141,1.25,132.3)
 # Horizontal FHAC rolled90deg: its lid faces south, clear of the fixed
 # overhead VOUT. This is a nominal35mm service budget, not a catalog
 # claim for the delivered hinge. Both factory exits remain on-axis.
 x0,y0,z0,x1,y1,z1=p['F_AUX_case_mm'];floor=z0-3
 add('E2Fixture','FAuxFootA',[x0+4,9,132.3,x0+10,17,floor])
 add('E2Fixture','FAuxFootB',[x1-10,9,132.3,x1-4,17,floor])
 add('E2Fixture','FAuxFloor',[x0-9,y0-1.3,floor,x1+9,y1+1.3,z0])
 horizontal('E2Fixture','FAuxInput',x0-4.5,14.5,149,2,z0)
 horizontal('E2Fixture','FAuxOutput',x1+4.5,14.5,149,2,z0)
 horizontal('E2Fixture','UnfusedSource',33.5,13,138,2,132.3)
 for i,x in enumerate((x0+15,x1-15)):
  band,_=tie_x(x,y0-1.3,y1+1.3,floor+.3,z1+1.3);bands['FAuxCase'+str(i)+'Band']=band
  # Top heads leave the north neighbour G2 and south lid space free.
  bands['FAuxCase'+str(i)+'Head']=box([x-2.4,12.75,z1+1.3,x+2.4,16.25,z1+5.8])
  cut('E2Fixture','FAuxCaseReturn'+str(i),[x-1.5,y0-1.5,floor+.2,x+1.5,y1+1.5,floor+1.7])
  for k,(a,b) in enumerate(((y0-1.5,y0+.1),(y1-.1,y1+1.5))):cut('E2Fixture','FAuxCaseSide'+str(i)+str(k),[x-1.5,a,floor+.2,x+1.5,b,z0+.1])
 # Vertical F_AUX custom/factory lap: stationary splice grip rooted on
 # E2's rear post, not a free hanging shrink sleeve or board solder joint.
 x=p['routes']['XA02']['parts'][0]['start'][0]
 # Root on the NORTH side of the complete downward return bend. Only
 # the high cantilever reaches the sleeve; no low wall across the wire.
 add('E2Fixture','FAuxJointRoot',[118,-27,114,121,-18,138.5])
 add('E2Fixture','FAuxJointBacker',[118,-36,126,x-2.45,-24,138.5])
 bands['FAuxJointBand'],bands['FAuxJointHead']=tie_z(134,116.8,x+3.7,-37.2,-28.8)
 bands['FAuxJointHead']=box([x+3.7,-35.4,132.25,x+8.2,-30.6,135.75])
 cut('E2Fixture','FAuxJointReturn',[116.6,-37.4,132.55,x-1.05,-28.6,135.45])
 grips.append(dict(name='FAuxJoint',axis='Z',centre_mm=[x,-33,134],radius_mm=2.4,T18I=1))
 # FHY input joint sits on the existing south wing. The bridge is SOUTH
 # of the received W3 underpass and below its whole yaw fanout.
 add('Foundation','FHYInputBridge',[-110,-93,107,-70,-87,110])
 horizontal('Foundation','FHYInputJoint',-74,-85.125,120,2.4,110)
 # Three spread, intact vertical board tails. Backers are above PCB,
 # rooted west of it; no pad clamping or full conductor through1.02drill.
 add('UpperCarrier001','AuxFanoutRoot',[25,-8,77.72,29,-5,94])
 add('UpperCarrier001','AuxFanoutBridge',[25,-8,94,45,-5,97])
 for n,x,y,z,b in [
  ('AuxVIN',31.27,-1.27,97,[28.77,-5.57,94,33.77,-2.57,99.5]),
  ('AuxGND',41.27,1.27,101,[38.77,-5,94,43.77,-.03,103.5]),
  ('AuxVOUT',36.27,6.35,105,[33.77,-5,94,38.77,5.05,107])]:
  add('UpperCarrier001',n+'Backer',b)
  # The three-mm taped jacket overlap ends atZ94.32. Its larger OD
  # needs a bottom-edge relief BEFORE the plain-jacket clamping land.
  cut('UpperCarrier001',n+'TapeOverlapClearance',[x-2.6,y-1.63,94,x+2.6,y-.9,94.52])
  x0,x1=x-3.7,x+3.7;ya,yb=b[1]-1.2,y+2.55
  bands[n+'Band'],bands[n+'Head']=tie_z(z,x0,x1,ya,yb)
  # All four legs, including a neighbouring backer, are planned before
  #native pockets. These are useful through-slots, not post-hoc collision
  #waivers; remaining material still has to be a connected native solid.
  for i,bb in enumerate(([x0-.2,ya-.2,z-1.45,x0+1.4,yb+.2,z+1.45],
   [x1-1.4,ya-.2,z-1.45,x1+.2,yb+.2,z+1.45],
   [x0-.2,ya-.2,z-1.45,x1+.2,ya+1.4,z+1.45],
   [x0-.2,yb-1.4,z-1.45,x1+.2,yb+.2,z+1.45])):cut('UpperCarrier001',n+'Slot'+str(i),bb)
  grips.append(dict(name=n,axis='Z',centre_mm=[x,y,z],T18I=1))
 return dict(pads=pads,cuts=cuts,bands=bands,purchased=purchased,grips=grips,
  T18I_new=len(grips)+2,SJ4570_reused_pairs=2,SJ4570_trim_pair_mm=[18,10],
  source_plan=p,physical_pass=False,selected=False,
  service='All power/USB removed. F_AUX: support body, cut two case bands and use nominal SOUTH lid space; factory/custom insulation bands remain. Delivered hinge/hand/puller fit remains phase2 gate. WAGO levers clear above cages, case adhesive is not wire relief. Install native receiving floors/slots before boards; bench solder/insulate ends, thread vertical comb and cut dedicated wire ties for board removal.')

def run():
 tick=time.monotonic();g=allocation();p=g['source_plan'];W.save('grip-plan.json',{k:v for k,v in g.items() if k not in ('bands','purchased')})
 reader=W.SavedShapes();targets,torso=W.current_scene(reader,p)
 original={n:targets[n] for n in ('Foundation','UpperCarrier001','E2Fixture')};native={};added={}
 for owner,s in original.items():
  s=s.copy()
  pads=[box(row['bounds_mm']) for row in g['pads'] if row['owner']==owner]
  cuts=[box(row['bounds_mm']) for row in g['cuts'] if row['owner']==owner]
  # Union the small new tools first. Repeated Booleans against an unchanged
  # complex inherited body waste minutes without improving the evidence.
  if pads:s=s.fuse(pads[0].multiFuse(pads[1:]))
  if cuts:s=s.cut(cuts[0].multiFuse(cuts[1:]))
  native[owner]=s.removeSplitter();added[owner]=native[owner].cut(original[owner]);targets.pop(owner)
 targets.update(g['purchased']);targets.update(native)
 from build_current_aux_power import insulation
 tape=insulation(p)
 r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False,native_files_changed=0,
  removed_retained_material_mm3={n:original[n].cut(s).Volume for n,s in native.items()})
 def solid(n,s,m,t):
  if not s.Solids or not t.Solids or not W.near(s,t,0):return
  if not s.isValid() or not t.isValid():r['errors'].append([n,m,'invalid']);return
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 def curve(n,c,rr,m,t):
  if not t.Solids or not W.near(c,t,rr):return
  r['pairs']+=1;d=c.distToShape(t)[0]
  if d<rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr))
 for owner,s in native.items():
  if not s.isValid() or len(s.Solids)!=1:r['errors'].append([owner,'disconnected/invalid',len(s.Solids)])
  if r['removed_retained_material_mm3'][owner]>1e-5:r['errors'].append([owner,'retained material removed',r['removed_retained_material_mm3'][owner]])
 for n,s in tape.items():
  for m,t in {**targets,**g['bands']}.items():solid(n,s,m,t)
  for m,t in tape.items():
   if n<m:solid(n,s,m,t)
 for n,s in {**{'added/'+n:s for n,s in added.items()},**g['bands']}.items():
  for m,t in targets.items():
   if n=='added/'+m:continue
   solid(n,s,m,t)
  for m,t in g['bands'].items():
   if n<m:solid(n,s,m,t)
  print('W1 common grip',n,'contacts',len(r['contacts']),flush=True);W.save('grip-progress.json',r)
 paths={n:(W.makewire(v['parts']),v['radius']) for n,v in p['routes'].items()}
 for folder,filename in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
  for n,v in json.loads((BASE/folder/filename).read_text())['routes'].items():
   if 'reserved' not in n and n!='F_HY_input_prefix':paths['retained/'+n]=(W.makewire(v['parts']),v['radius'])
 for n,(c,rr) in paths.items():
  for m,t in {**added,**g['bands']}.items():curve(n,c,rr,m,t)
 service=box(p['F_AUX_side_service_mm'])
 for n,t in {**targets,**g['bands']}.items():
  if n.startswith('FAuxCase'):continue # Cut these two designated bands first.
  solid('FAuxNominalLidSpace',service,n,t)
 for n,(c,rr) in paths.items():curve(n,c,rr,'FAuxNominalLidSpace',service)
 if not r['contacts'] and not r['errors']:
  for yaw in (-15,0,15):
   for pitch in (-10,0,5):
    for m,t in W.F.H.head(reader,yaw,pitch).items():
     if m=='Foundation':continue
     for n,s in {**added,**g['bands'],**tape}.items():solid(n,s,'head/'+m,t)
   for n,(c,rr,_) in W.F.H.local(yaw).items():
    for m,t in {**added,**g['bands'],**tape}.items():curve(n,c,rr,m,t)
   print('Changed W1 supports head pose',yaw,'contacts',len(r['contacts']),flush=True)
 r.update(status='SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN' if not r['contacts'] and not r['errors'] else 'REJECTED_SHARED_SUPPORT_ALLOCATION',source_sha256=reader.hashes,
  worker_seconds=round(time.monotonic()-tick,3),planned_T18I=g['T18I_new'],insulation_included=True)
 W.save('grip-checks.json',r);print(json.dumps(r),flush=True)

def receive_joint_root():
 tick=time.monotonic();g=allocation();p=g['source_plan'];prev=OUT/'checks-before-joint-root.json';oldplan=OUT/'support-before-joint-root.json'
 old=json.loads(prev.read_text());was=json.loads(oldplan.read_text());now={k:v for k,v in g.items() if k not in ('bands','purchased')}
 assert not old['errors'] and old['insulation_included']
 assert old['contacts']==[dict(a='XA02',b='E2Fixture',distance_mm=0.0,required_mm=1.25)]
 changed={'FAuxJointRoot','FAuxJointBacker'}
 a={**was,'pads':[v for v in was['pads'] if v['name'] not in changed]}
 b={**now,'pads':[v for v in now['pads'] if v['name'] not in changed]}
 assert a==b,'Only two E2 load-path features may differ from the recorded full gate'
 assert all(W.sha(ROOT/n)==digest for n,digest in old['source_sha256'].items())
 reader=W.SavedShapes();targets,_=W.current_scene(reader,p);original=targets.pop('E2Fixture')
 pads=[box(v['bounds_mm']) for v in g['pads'] if v['owner']=='E2Fixture'];cuts=[box(v['bounds_mm']) for v in g['cuts'] if v['owner']=='E2Fixture']
 native=original.fuse(pads[0].multiFuse(pads[1:])).cut(cuts[0].multiFuse(cuts[1:])).removeSplitter()
 assert native.isValid() and len(native.Solids)==1
 assert original.cut(native).Volume<1e-5
 delta=native.cut(original);r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False,native_files_changed=0)
 def solid(n,s,m,t):
  if not s.Solids or not t.Solids or not W.near(s,t,0):return
  assert s.isValid() and t.isValid(),(n,m)
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
 def curve(n,c,rr,m,t):
  if not t.Solids or not W.near(c,t,rr):return
  r['pairs']+=1;d=c.distToShape(t)[0]
  if d<rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr))
 from build_current_aux_power import insulation
 tape=insulation(p)
 for m,t in {**targets,**g['bands'],**g['purchased'],**tape}.items():solid('added/E2Fixture',delta,m,t)
 for n,v in p['routes'].items():curve(n,W.makewire(v['parts']),v['radius'],'E2Fixture',delta)
 for folder,filename in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
  for n,v in json.loads((BASE/folder/filename).read_text())['routes'].items():
   if 'reserved' not in n and n!='F_HY_input_prefix':curve('retained/'+n,W.makewire(v['parts']),v['radius'],'E2Fixture',delta)
 solid('FAuxNominalLidSpace',box(p['F_AUX_side_service_mm']),'E2Fixture',delta)
 if not r['contacts']:
  for yaw in (-15,0,15):
   for pitch in (-10,0,5):
    for n,t in W.F.H.head(reader,yaw,pitch).items():
     if n!='Foundation':solid('added/E2Fixture',delta,'head/'+n,t)
   for n,(c,rr,_) in W.F.H.local(yaw).items():curve(n,c,rr,'E2Fixture',delta)
 r.update(status='SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_SHARED_SUPPORT_ALLOCATION',insulation_included=True,
  removed_retained_material_mm3={**old['removed_retained_material_mm3'],'E2Fixture':0.0},worker_seconds=round(time.monotonic()-tick,3),prior_full_worker_seconds=old['worker_seconds'],
  reuse=dict(prior_pairs=old['pairs'],scope='Unchanged Foundation/UpperCarrier/bands/tape and mutual contacts retained. All E2 added-material interfaces rechecked; prior XA02/E2 conflict NOT waived.'),
  source_sha256={**reader.hashes,prev.relative_to(ROOT).as_posix():W.sha(prev),oldplan.relative_to(ROOT).as_posix():W.sha(oldplan)},planned_T18I=g['T18I_new'])
 W.save('grip-plan.json',now);W.save('grip-checks.json',r);print(json.dumps(r),flush=True)

if __name__=='__main__':
 import sys
 receive_joint_root() if '--receive-joint-root' in sys.argv else run()
 if json.loads((OUT/'grip-checks.json').read_text())['status']=='SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN':W.solid_gate()
