"""One coupled six-feed plan: separated PCB fanouts and both fuse exits.

The accepted arm and moving head remain unchanged. Nothing in this spatial
receipt earns W3 before native independent grips, service and stock exist.
"""
import json,time,math
from pathlib import Path
import plan_current_head_bundle as Q
import plan_current_head_access as C
H,O,A,Part,P,ROOT,BASE=Q.H,Q.O,Q.A,Q.Part,C.P,C.ROOT,C.BASE
OUT=BASE/'head-supply-checkpoint'
line,arc=O.line,O.arc
ZR,ZS=O.ZR,O.ZS

def save(n,v):
 OUT.mkdir(exist_ok=True);(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')

def straight(q,p):q.append(line(q[-1]['end'],p))
def turn(q,c,p):q.append(arc(c,q[-1]['end'],p))
def move(q,axis,delta):O.spatial_shift(q,axis,delta)

def recipe(s):
 out=[]
 for e in s.Edges:
  a,b=e.valueAt(e.FirstParameter),e.valueAt(e.LastParameter)
  if 'Line' in str(type(e.Curve)):out.append(line(list(a),list(b)))
  else:out.append(dict(kind='arc',start=list(a),mid=list(e.valueAt((e.FirstParameter+e.LastParameter)/2)),end=list(b)))
 return out

def layout():
 p=Q.N.C.layout()
 # Actual selected SJ4570 mated2.49 envelope; case height is NOT raised
 # again. Lower the ground support, never pretend adhesive has no thickness.
 p['GroundFloor'].translate(A.Vector(0,0,-2.49))
 p['GroundPost']=H.T.box([-103,-30,74.52,-95,-22,113.40378221735])
 # Move the COMPLETE pitch fuse to the free north/east neck quadrant.
 # Its old EAST output faced directly into S0. Both new faces and the
 # one-piece load path are allocated together, not a shifted wire column.
 for n,b in {
  'F_HP_case':[-97,77,89.99,-46,97.25,111.99],
  'FoundationNorthWing':[-168,26,68.52,-44,99,71.52],
  'FHPFoot':[-99,77,71.52,-44,97.25,74.52],
  'FHPPost':[-76,83,74.52,-68,91,86.99],
  'FHPFloor':[-99,75.5,86.99,-44,99,89.99]}.items():p[n]=H.T.box(b)
 return p

def build():
 OUT.mkdir(exist_ok=True)
 Q.START=A.Vector(-99,-85,139.0124355652982)
 oldsave=H.save;H.save=save
 try:tails=Q.bundle()
 finally:H.save=oldsave
 routes={};red=tails['XB12']['start'];g=tails['XB13']['start'];s=tails['XS13']['start']
 q=[line([-160,-85.125,135.99],[-139.5,-85.125,135.99])]
 lane=g[1]+2.2
 move(q,[1,0,0],[0,lane+85.125,0]);move(q,[1,0,0],[0,0,red[2]-135.99]);move(q,[1,0,0],[0,red[1]-lane,0])
 straight(q,red);q.append(tails['XB12']);routes['XB12']=q
 y,z=g[1:]
 q=[line([-117,-30.55,123.39378221735],[-108,-30.55,123.39378221735])]
 straight(q,[-102.6,-30.55,123.39378221735]);turn(q,[-102.6,-30.55,110.79378221735],[-90,-30.55,110.79378221735])
 straight(q,[-90,-30.55,72.6]);turn(q,[-90,-43.15,72.6],[-90,-43.15,60]);straight(q,[-90,-85.4,60])
 turn(q,[-102.6,-85.4,60],[-102.6,-98,60]);straight(q,[-162.6,-98,60]);turn(q,[-162.6,-98,72.6],[-175.2,-98,72.6])
 straight(q,[-175.2,-98,z-12.6]);turn(q,[-162.6,-98,z-12.6],[-162.6,-98,z]);move(q,[1,0,0],[0,y+98,0]);straight(q,g);q.append(tails['XB13']);routes['XB13']=q
 y,z=s[1:];x=81.43
 q=[arc([68.83,14.97,79.2],[x,14.97,79.2],[68.83,27.57,79.2])]
 straight(q,[45,27.57,79.2]);move(q,[-1,0,0],[0,0,40.8]);move(q,[-1,0,0],[0,19.43,0])
 straight(q,[-90,47,120]);turn(q,[-90,34.4,120],[-102.6,34.4,120]);straight(q,[-102.6,-72.8,120])
 turn(q,[-102.6,-72.8,107.4],[-102.6,-85.4,107.4]);straight(q,[-102.6,-85.4,76.8])
 turn(q,[-115.2,-85.4,76.8],[-115.2,-85.4,64.2]);move(q,[-1,0,0],[0,-12.6,0]);straight(q,[-142.6,-98,64.2])
 turn(q,[-142.6,-98,76.8],[-155.2,-98,76.8]);straight(q,[-155.2,-98,z-12.6]);turn(q,[-142.6,-98,z-12.6],[-142.6,-98,z])
 move(q,[1,0,0],[0,y+98,0]);straight(q,s);q.append(tails['XS13']);routes['XS13']=q
 # Pitch red inherits the received whole U-turn. The added8mm prefix
 # explicitly shares the factory splice, rather than a zero-length joint.
 routes['XB22']=[line([-95,72.05,ZR],[-66,72.05,ZR]),arc([-66,85,ZR],[-66,72.05,ZR],[-53.05,85,ZR])]
 q=[line([-117,-25.8,123.39378221735],[-108,-25.8,123.39378221735])]
 turn(q,[-108,-13.2,123.39378221735],[-95.4,-13.2,123.39378221735]);straight(q,[-95.4,30,123.39378221735])
 move(q,[0,1,0],[0,0,12]);yy=q[-1]['end'][1];rr=66-yy;assert rr>=12.6
 turn(q,[-95.4+rr,yy,ZR],[-95.4+rr,66,ZR]);move(q,[1,0,0],[0,3.95,0]);straight(q,[-66,69.95,ZR])
 turn(q,[-66,85,ZR],[-50.95,85,ZR]);routes['XB23']=q
 x=83.97;q=[line([x,12.97,79.2],[x,-15,79.2])]
 turn(q,[71.37,-15,79.2],[71.37,-27.6,79.2]);straight(q,[40,-27.6,79.2]);move(q,[-1,0,0],[0,0,30.8])
 straight(q,[-104,-27.6,110]);turn(q,[-104,-15,110],[-116.6,-15,110]);move(q,[0,1,0],[0,0,30])
 straight(q,[-116.6,58.4,140]);turn(q,[-104,58.4,140],[-104,71,140]);straight(q,[-78,71,140]);move(q,[1,0,0],[0,0,ZS-140])
 straight(q,[-66,71,ZS]);turn(q,[-66,85,ZS],[-52,85,ZS]);routes['XS23']=q
 # Formed bare ends only, radius of0.5mm2 copper. Insulation/support gate
 # covers the part outside the assigned pad, never all PCB as an exception.
 routes['XS13_bare']=[arc([81.43,14.97,80.2],[81.43,14.97,79.2],[81.43,13.97,80.2]),line([81.43,13.97,80.2],[81.43,13.97,85.8202])]
 routes['XS23_bare']=[arc([83.97,12.97,80.2],[83.97,12.97,79.2],[83.97,13.97,80.2]),line([83.97,13.97,80.2],[83.97,13.97,85.8202])]
 q=[line([-166,-85.125,120],[-180,-85.125,120])];turn(q,[-180,-85.125,126],[-186,-85.125,126]);straight(q,[-186,-85.125,129.99]);turn(q,[-180,-85.125,129.99],[-180,-85.125,135.99]);straight(q,[-152,-85.125,135.99]);routes['F_HY_out']=q
 q=[line([-97,87.125,99.99],[-106,87.125,99.99])]
 turn(q,[-106,81.125,99.99],[-112,81.125,99.99]);straight(q,[-112,78.05,99.99])
 turn(q,[-112,78.05,105.99],[-112,72.05,105.99]);straight(q,[-112,72.05,ZR-6])
 turn(q,[-106,72.05,ZR-6],[-106,72.05,ZR]);straight(q,[-87,72.05,ZR]);routes['F_HP_out']=q
 routes['F_HY_input_prefix']=[line([-115,-85.125,120],[-106,-85.125,120])]
 routes['F_HP_input_prefix']=[line([-46,87.125,99.99],[-37,87.125,99.99])]
 # FactoryOD4/spliceOD4.8 MUST finish before the HELU triangle packs.
 # Separate the complete pitch fanout until east of both20mm sleeves.
 routes['XB12_sleeve']=[line([-166,-85.125,135.99],[-146,-85.125,135.99])]
 routes['XB22_sleeve']=[line([-101,72.05,ZR],[-81,72.05,ZR])]
 for port,y in [(1,-16.3),(2,-21.05),(5,-35.3)]:routes['G_AUX_reserved_'+str(port)]=[line([-117,y,123.39378221735],[-108,y,123.39378221735])]
 return dict(status='WHOLE_HEAD_SUPPLY_PLAN_NOT_SELECTED',physical_pass=False,selected=False,
  routes={n:dict(parts=q,radius=math.sqrt(.5/math.pi) if n.endswith('_bare') else 2.4 if n.endswith('_sleeve') else 2 if n.startswith('F_') else 1.05) for n,q in routes.items()},
  assumptions='FHACOD4/R6/100mm nominal and84.5mm minimum delivered usable tail are delivery assumptions, not catalogL140. HELUOD2.1/fixedR12.6. No externalU1 pinout. Remaining3G_AUXports reserved, W1 not claimed. Source beyond9mm isW5.',
  factory_splices=dict(XB12=dict(lap_mm=8,centre_mm=[-156,-85.125,135.99]),XB22=dict(lap_mm=8,centre_mm=[-91,72.05,ZR])),
  changed_topology='B1 immediately north then west; B2 south. Shared yaw bundle aboveFHYcase. Complete pitch fuse+load path moved north/east beyondS0 and head, outputWEST/inputEAST with full straight prefixes. Ground floor lowered2.49 for actual SJ4570, ground case unchanged.')

def run():
 tick=time.monotonic()
 prior=OUT/'space-checks.json'
 if prior.exists() and not (OUT/'rejected-old-pitch-exit.json').exists():save('rejected-old-pitch-exit.json',json.loads(prior.read_text()))
 p=build();save('plan.json',p);paths={n:Q.makewire(v['parts']) for n,v in p['routes'].items()}
 r=dict(status='PENDING',contacts=[],pairs=0,lengths_mm={},radius_mm={},selected=False,physical_pass=False)
 for n,w in paths.items():
  r['lengths_mm'][n]=w.Length
  for e,f in zip(w.Edges,w.Edges[1:]):
   gap=(e.valueAt(e.LastParameter)-f.valueAt(f.FirstParameter)).Length;dot=e.tangentAt(e.LastParameter).dot(f.tangentAt(f.FirstParameter))
   assert gap<1e-5 and dot>1-1e-5,(n,gap,dot)
  rad=min([1/e.curvatureAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/1000) for e in w.Edges if 'Line' not in str(type(e.Curve)) for i in range(1001) if e.curvatureAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/1000)>1e-8] or [1e9])
  r['radius_mm'][n]=rad;assert rad>=(.99 if n.endswith('_bare') else 5.99 if n.startswith('F_') else 12.599),(n,rad)
  w.exportBrep(str(OUT/(n+'.brep')))
 for i,n in enumerate(paths):
  for m in list(paths)[i+1:]:
   assigned=[('XB12','F_HY_out'),('XB22','F_HP_out'),('XS13','XS13_bare'),('XS23','XS23_bare')]
   assigned += [(name+'_sleeve',part) for name,factory in [('XB12','F_HY_out'),('XB22','F_HP_out')] for part in (name,factory)]
   if frozenset((n,m)) in [frozenset(z) for z in assigned]:continue
   required=p['routes'][n]['radius']+p['routes'][m]['radius']
   if not H.T.near(paths[n],paths[m],required):continue
   r['pairs']+=1;dist,witness,_=paths[n].distToShape(paths[m])
   if dist<required-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=required,witness=[[list(v) for v in z] for z in witness[:2]]))
 if r['contacts']:
  r.update(status='REJECTED_WHOLE_HEAD_SUPPLY_MUTUAL',worker_seconds=time.monotonic()-tick);save('space-checks.json',r);print(json.dumps(r),flush=True);return
 reader=P.SavedShapes();targets,torso=C.F.physical_scene(reader)
 targets.update({n:reader.shape(C.OUT/'HeadWiringAccess.FCStd',n) for n in ('UpperCarrier001','HeadFixedAnchor')});targets.update(layout())
 for n,c in paths.items():
  rr=p['routes'][n]['radius']
  for m,t in targets.items():
   if not t.Solids or not H.T.near(c,t,rr):continue
   test=c
   if n.startswith('F_HY') and m=='F_HY_case' or n.startswith('F_HP') and m=='F_HP_case':test=Part.Wire(c.Edges[1:]) if len(c.Edges)>1 else None
   if (n in ('XB13','XB23') or n.startswith('G_AUX_reserved_')) and m=='G_AUX_case':test=Part.Wire(c.Edges[1:]) if len(c.Edges)>1 else None
   if n.endswith('_bare') and m=='PWM1608NominalPCB':
    x=81.43 if n=='XS13_bare' else 83.97;t=t.cut(Part.makeCylinder(.6,3,A.Vector(x,13.97,82.5)))
   if test is None:continue
   r['pairs']+=1;dist=min(test.distToShape(s)[0] for s in t.Solids)
   if dist<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr))
  for y in (-15,0,15):
   for pitch in (-10,0,5):
    for m,t in H.head(reader,y,pitch).items():
     if not t.Solids or not H.T.near(c,t,rr):continue
     r['pairs']+=1;dist=min(c.distToShape(s)[0] for s in t.Solids)
     if dist<rr-1e-5:r['contacts'].append(dict(a=n,b='head/'+m,pose=[y,pitch],distance_mm=dist,required_mm=rr))
  print('Whole head supply',n,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True);save('progress.json',r)
 r.update(status='CURRENT_WHOLE_HEAD_SUPPLY_SPACE_ONLY' if not r['contacts'] else 'REJECTED_WHOLE_HEAD_SUPPLY_SPACE',
  worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))})
 save('space-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds','lengths_mm')}),flush=True)
if __name__=='__main__':run()
