"""One current head fixed-anchor architecture, with complete moving wires.

The old outside-cover anchor is not kept by adding another outside cover.
Allocate the whole anchor, root, band and all three constant-length wires first.
"""
import json,math,time
from datetime import datetime,timezone
import plan_current_head_wiring as H
import head_local_rigid_conductors_r1 as L
A,Part,P,ROOT,BASE,OUT=H.A,H.Part,H.P,H.ROOT,H.BASE,H.OUT
END=A.Vector(-52,76,136)
PACK=L.F.PACK
GUIDE_LENGTH=300

def guide(yaw):
 start=H.moved(Part.Vertex(A.Vector(-219.2,130,166)),yaw).Vertexes[0].Point
 ta=A.Rotation(A.Vector(0,0,1),yaw).multVec(A.Vector(0,1,0))
 def make(a,b):
  c=Part.BezierCurve();c.setPoles([start,start+ta*a,END+A.Vector(0,b,0),END]);return c.toShape()
 best=None
 for a in range(24,185,4):
  lo,hi=1.,320.
  if not make(a,lo).Length<GUIDE_LENGTH<make(a,hi).Length:continue
  for _ in range(30):
   b=(lo+hi)/2
   if make(a,b).Length>GUIDE_LENGTH:hi=b
   else:lo=b
  e=make(a,(lo+hi)/2);r=min(1/e.curvatureAt(i/200) for i in range(201))
  if best is None or r>best[0]:best=(r,e)
 assert best is not None,'No constant-length shared guide'
 return best[1],best[0]
def conductor(base,side,normal,bump=0):
 pts=[]
 for i in range(301):
  u=i/300;t=base.tangentAt(u);t.normalize()
  z=A.Vector(0,0,1);vertical=z-t*z.dot(t);vertical.normalize()
  n=z.cross(t);n.normalize();angle=math.pi/2*(u*u*(3-2*u))
  b=vertical*math.cos(angle)+n*math.sin(angle)
  scale=1+.2*math.sin(math.pi*u)**2
  pts.append(base.valueAt(u)+(b*side+b.cross(t)*normal)*scale+n*bump*math.sin(math.pi*u)**2)
 c=Part.BSplineCurve();c.interpolate(pts);return c.toShape()
def curves():
 bases={y:guide(y)[0] for y in (-15,0,15)}
 raw={(y,n):conductor(b,*q) for y,b in bases.items() for n,q in PACK.items()}
 targets={n:math.ceil(max(raw[y,n].Length for y in bases)*10)/10+.1 for n in PACK}
 paths={};meta=[];separation=[]
 for y,b in bases.items():
  for n,q in PACK.items():
   lo,hi=-8.,8.;a=conductor(b,*q,lo).Length;z=conductor(b,*q,hi).Length
   assert a<targets[n]<z,(y,n,a,targets[n],z)
   for _ in range(30):
    mid=(lo+hi)/2;e=conductor(b,*q,mid)
    if e.Length>targets[n]:hi=mid
    else:lo=mid
   e=conductor(b,*q,(lo+hi)/2);assert abs(e.Length-targets[n])<1e-4
   r=L.radius(e);paths[y,n]=e
   meta.append(dict(yaw=y,wire=n,length_mm=e.Length,target_mm=targets[n],minimum_sampled_radius_mm=r,
    start_mm=list(e.valueAt(e.FirstParameter)),end_mm=list(e.valueAt(e.LastParameter)),middle_bump_mm=(lo+hi)/2))
  names=list(PACK)
  for i,n in enumerate(names):
   for m in names[i+1:]:separation.append(dict(yaw=y,a=n,b=m,distance_mm=paths[y,n].distToShape(paths[y,m])[0],required_mm=2.1))
 return paths,meta,separation
def solids():
 box=H.T.box
 # Planning material, not selected/printed geometry. Native roots are only
 # accepted after testing actual carrier intersections, not its bounding box.
 return {
  'CarrierRootBridge':box([-62,-24,74.72,-42,-14,77.72]),
  'AnchorFoot':box([-62,-24,77.72,-42,-14,80.72]),
  'AnchorPost':box([-56,-23,80.72,-48,-15,127.4]),
  'AnchorSouthBridge':box([-60,-23,127.4,-48,-15,133.4]),
  'AnchorEastOfKey':box([-60,-23,127.4,-54,41,133.4]),
  'AnchorNorthOfKey':box([-74,33,127.4,-54,41,133.4]),
  'AnchorWestOfATO':box([-74,33,127.4,-66,78,133.4]),
  'AnchorNorthBridge':box([-74,70,127.4,-48,78,133.4]),
  'AnchorInsulationLand':box([-56,70,133.4,-48,78,134.3]),
 }
def run():
 tick=time.monotonic();assert not (OUT/'anchor-space-checks.json').exists()
 plan=H.read(OUT/'plan.json');plan.update(fixed_anchor_current_mm=list(END),
  historical_fixed_pitch_transition_retired=True,guide_length_mm=GUIDE_LENGTH,
  rejected_short_loop='260mm rejected in2.531s before native or body checks: yaw+15 requiresR20.933<31.5. Preserve radius requirement, allocate40mm more custom HELU span and stock; no repeated scalar anchor displacement.',
  rejected_bank_layout='Anchor(-52,68,124) lies inside retainedF_L1 housing[-67,54.5,97.5,-39,69.5,126]; three contacts at firstyaw, owned process10144 stopped withpartial retained. Do not repeat. Allocate entire anchor/branch WEST of retainedbank, not another tiny wire offset.',
  rejected_west_layout='Guide300 to(-104,38,124) rejected in2.594s before native: minimum sampledR12.456<31.5. No repeated west anchor offset. Raise entire support OVER retainedbank top126 with armbottom130.4; fixed anchor(-52,76,136) beyond banknorthY69.5. Full route and support both checked.',
  native_root_plan='Two M3x10 stacksX-57/-47,Y-19 on actual carrier south-west floor;20x10 carrier root bridge. Complete6mm-high dogleg runs EAST of real S0key(maxX-62), NORTH of key(maxY31), WEST of ATO(minX-62.55,Y59.45..64.55,top144.8), then to fixed land beyond bank. NOT a straight over-ATO beam. Captive nuts and access before boards.',
  W3_shared_allocation={'yaw_boundary':[-112,-56.8,85.2],'pitch_boundary':list(END),
    'F_HY_proposed_case_mm':[-106,-60,89.99,-85.75,-9,111.99],
    'F_HP_proposed_case_mm':[-106,9,89.99,-85.75,60,111.99],
    'G_AUX_proposed_case_mm':[-111,-40.8,118.89378221735,-92,-10.8,127.89378221735],
    'same_bus_port_permutation':'PitchXB23 usesG_AUX3 north; yawXB13 usesG_AUX4 south; bothG_AUX, no AUX/MAIN parallel. Other3ports retain9mm entry reservations; W1 alreadyOPEN.',
    'head_holder_note':'Both input stubs remain W5, keep9mm straight insulation lands. Whole2holders/native roots/outputs and all6feeds must be checked together before W3 selection.',
    'ground_and_PWM':'DedicatedG_AUX3/4 and known1608B1/B2. Exact current endpoints still to be allocated, not inventedU1 pins.'},
  assembly_anchor=['Install two captive nuts and foot screws on bare carrier before PCBs','Prepare head complete factory/JR/sleeves off PETG; retain uncut250mm','Lay individual free spans without solder or common overwrap; one independent anchor band on intact insulation','For removal release3bodyends on bench with supported board, unplug2JR and cut designated bands before lifting modules'],
  band_plan='T18I2.5x1.2 under-arm returnY73..75.5, sides outside8mm landX-56..-48. Add9mm straight fixed tail from loopendY76 to W3boundaryY67 so band never grips moving bend; head above upper wire. Native channels and real band/head checked before selection.',
  selected=False,phase1_complete=False)
 H.save('anchor-plan.json',plan)
 prior=OUT/'anchor-direct-arm-rejection.json'
 reuse=H.read(prior) if prior.exists() else None
 if reuse:
  assert reuse['outside']==[] and len(reuse['contacts'])==1 and reuse['contacts'][0]['a']=='AnchorArm'
  assert all((A.Vector(*v['end_mm'])-END).Length<3 for v in reuse['poses'])
  paths={(y,n):Part.read(str(OUT/f'{n}_yaw{y:+}_CurrentLoop.brep')) for y in (-15,0,15) for n in PACK}
  poses,sep=reuse['poses'],reuse['separation']
 else:paths,poses,sep=curves()
 r=dict(status='PENDING',poses=poses,separation=sep,contacts=[],pairs=0,physical_pass=False,selected=False)
 if min(x['minimum_sampled_radius_mm'] for x in poses)<31.5 or min(x['distance_mm'] for x in sep)<2.1-1e-4:
  r.update(status='REJECTED_BEFORE_NATIVE_CURVE_GATE',worker_seconds=round(time.monotonic()-tick,3));H.save('anchor-space-checks.json',r);print(json.dumps(r),flush=True);return
 print('Constant-length whole head loop preflight',min(x['minimum_sampled_radius_mm'] for x in poses),flush=True)
 reader=P.SavedShapes();targets,torso=H.scene(reader)
 for y in (() if reuse else (-15,0,15)):
  current=H.head(reader,y,0)
  for n in PACK:
   e=paths[y,n]
   for name,t in {**targets,**{'head/'+n:s for n,s in current.items()},**solids()}.items():
    if not H.T.near(e,t,1.05):continue
    assert t.isValid() and t.Solids,(name,'invalid context')
    r['active_pair']=[y,n,name];H.save('anchor-progress.json',r)
    r['pairs']+=1;d=min(e.distToShape(c)[0] for c in t.Solids)
    if d<1.05-1e-5:r['contacts'].append(dict(yaw=y,a=n,b=name,distance_mm=d,required_mm=1.05))
   e.exportBrep(str(OUT/f'{n}_yaw{y:+}_CurrentLoop.brep'))
  # Changed shell context for each selected pitch pose, not old fullmatrix.
  for pitch in (-10,5):
   for name,t in H.head(reader,y,pitch).items():
    if name not in H.PITCH:continue
    for n in PACK:
     e=paths[y,n]
     if not H.T.near(e,t,1.05):continue
     r['pairs']+=1;d=min(e.distToShape(c)[0] for c in t.Solids)
     if d<1.05-1e-5:r['contacts'].append(dict(yaw=y,pitch=pitch,a=n,b='head/'+name,distance_mm=d,required_mm=1.05))
  print('Received new head anchor loop yaw',y,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True)
  H.save('anchor-progress.json',r)
  if r['contacts']:
   r.update(status='REJECTED_CURRENT_HEAD_ANCHOR_LAYOUT',worker_seconds=round(time.monotonic()-tick,3))
   H.save('anchor-space-checks.json',r);print(json.dumps(r['contacts']),flush=True);return
 roots={n:s for n,s in solids().items()}
 # Reuse received unchanged9curves/45body+head pairs. Only the changed
 # complete dogleg load path needs new wire/support and support/body checks.
 if reuse:
  r['reused_loop_body_pairs']=45;r['unchanged_loop_geometry_sha256']={f'{n}_yaw{y:+}_CurrentLoop.brep':P.sha(OUT/f'{n}_yaw{y:+}_CurrentLoop.brep') for y,n in paths}
  for (y,n),e in paths.items():
   for m,t in roots.items():
    if H.T.near(e,t,1.05):
     r['pairs']+=1;d=e.distToShape(t)[0]
     if d<1.05-1e-5:r['contacts'].append(dict(yaw=y,a=n,b=m,distance_mm=d))
 outside=[];carrier=targets['UpperCarrier001'];root=roots.pop('CarrierRootBridge')
 assert root.common(carrier).Volume>1,('Actual root has no carrier material',root.common(carrier).Volume)
 roots['CarrierRootBridge']=root
 for n,s in roots.items():
  v=s.cut(torso).Volume
  if v>1e-5:outside.append(dict(name=n,volume_mm3=v))
  for name,t in {**targets,**{'head/'+n:s for n,s in H.head(reader).items()}}.items():
   if name=='UpperCarrier001' and n in ('AnchorFoot','CarrierRootBridge'):continue # native receiver material/flat mounting face
   if not H.T.near(s,t,0):continue
   r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
   if v>1e-5:r['contacts'].append(dict(a=n,b=name,volume_mm3=v))
 r.update(status='CURRENT_HEAD_ANCHOR_SPACE_CANDIDATE' if not r['contacts'] and not outside else 'REJECTED_CURRENT_HEAD_ANCHOR_LAYOUT',outside=outside,
  root_actual_common_mm3=root.common(carrier).Volume,source_sha256={**reader.hashes,H.Path(__file__).relative_to(ROOT).as_posix():P.sha(H.Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
 H.save('anchor-space-checks.json',r)
 print(json.dumps({k:r[k] for k in ('status','pairs','contacts','outside','worker_seconds')}),flush=True)
if __name__=='__main__':run()
