"""Whole W2/W3 receiving interface behind ATO, before new native details.

Retain the root and the accepted torso. The extended terminal arm belongs to
the external head/neck, above the intentionally omitted cosmetic upper shell.
It is not disguised as material inside that shell. No new power topology.
"""
import json, math, time
from pathlib import Path
import plan_current_head_anchor as K
import finish_current_head_anchor as F
H,A,Part,P,ROOT,BASE=K.H,K.A,K.Part,K.P,K.ROOT,K.BASE
OUT=BASE/'head-wiring-access-checkpoint'
END=A.Vector(-52,94,136)
def save(n,v):
 OUT.mkdir(exist_ok=True);(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def solids():
 s=K.solids()
 s['AnchorWestOfATO']=H.T.box([-74,33,127.4,-66,98,133.4])
 s['AnchorNorthBridge']=H.T.box([-74,88,127.4,-48,98,133.4])
 s['AnchorInsulationLand']=H.T.box([-56,88,133.4,-48,96,134.3])
 return s
def approaches():
 # A common three-wire turn; offsets transported together, not intersecting
 # independent columns. Final 14mm quarter starts Y71, beyond ATO max64.55.
 line,arc=H.T.line,H.T.arc
 c=H.T.wire([line([-121,42,136],[-130,42,136]),
  arc([-130,56,136],[-130,42,136],[-144,56,136]),
  line([-144,56,136],[-144,57,136]),
  arc([-130,57,136],[-144,57,136],[-130,71,136]),
  line([-130,71,136],[-66,71,136]),
  arc([-66,85,136],[-66,71,136],[-52,85,136])])
 q={};metadata=[]
 for n,(side,normal) in K.PACK.items():
  # K.PACK offsets correspond to the selected -Y terminal. At this new
  # source-to-head +Y approach the physical endpoint remains unchanged.
  off=A.Vector(side,0,-normal);edges=[]
  for e in c.Edges:
   pts=[]
   for i in range(81):
    u=e.FirstParameter+(e.LastParameter-e.FirstParameter)*i/80
    t=e.tangentAt(u);ang=math.degrees(math.atan2(-t.x,t.y))
    pts.append(e.valueAt(u)+A.Rotation(A.Vector(0,0,1),ang).multVec(off))
   if 'Line' in str(type(e.Curve)):z=Part.makeLine(pts[0],pts[-1])
   else:z=Part.Arc(pts[0],pts[40],pts[-1]).toShape()
   edges.append(z)
  q[n]=Part.Wire(edges)
  metadata.append(dict(wire=n,start_mm=list(q[n].Vertexes[0].Point),
   end_mm=list(q[n].Vertexes[-1].Point),minimum_radius_mm=min(
    [1/e.curvatureAt((e.FirstParameter+e.LastParameter)/2) for e in edges if 'Line' not in str(type(e.Curve))])))
 return q,metadata
def run():
 tick=time.monotonic();OUT.mkdir(exist_ok=True);K.END=END;K.GUIDE_LENGTH=280
 paths,poses,separation=K.curves();incoming,entries=approaches()
 r=dict(status='PENDING',contacts=[],pairs=0,poses=poses,separation=separation,
  receiving_approaches=entries,physical_pass=False,selected=False)
 assert min(x['minimum_sampled_radius_mm'] for x in poses)>=31.5
 assert min(x['distance_mm'] for x in separation)>=2.1-1e-4
 assert min(x['minimum_radius_mm'] for x in entries)>=12.6
 for v in poses:
  end=A.Vector(*v['end_mm'])-A.Vector(0,9,0)
  e=incoming[v['wire']].Edges[-1]
  assert (e.valueAt(e.LastParameter)-end).Length<1e-5
 reader=P.SavedShapes();targets,torso=F.physical_scene(reader)
 targets['UpperCarrier001']=reader.shape(K.OUT/'HeadWiringCurrent.FCStd','UpperCarrier001')
 targets.update({n:s for n,s in solids().items() if n not in ('CarrierRootBridge','AnchorFoot')})
 for y in (-15,0,15):
  for n in K.PACK:
   paths[y,n].exportBrep(str(OUT/f'{n}_yaw{y:+}_Loop.brep'))
   end=A.Vector(*next(v['end_mm'] for v in poses if v['yaw']==y and v['wire']==n))
   tail=Part.makeLine(end-A.Vector(0,9,0),end)
   assert (incoming[n].Vertexes[-1].Point-tail.Vertexes[0].Point).Length<1e-5
   for m,t in {**targets,**{'head/'+m:s for m,s in H.head(reader,y).items()}}.items():
    for label,c in [(n,paths[y,n]),(n+'_tail',tail)]:
     if not t.Solids or not H.T.near(c,t,1.05):continue
     r['pairs']+=1;d=min(c.distToShape(s)[0] for s in t.Solids)
     if d<1.05-1e-5:r['contacts'].append(dict(yaw=y,a=label,b=m,distance_mm=d))
   # Retain explicit pitch extremes, rather than rest-only head acceptance.
   for pitch in (-10,5):
    for m,t in H.head(reader,y,pitch).items():
     if m not in H.PITCH or not H.T.near(paths[y,n],t,1.05):continue
     r['pairs']+=1;d=min(paths[y,n].distToShape(s)[0] for s in t.Solids)
     if d<1.05-1e-5:r['contacts'].append(dict(yaw=y,pitch=pitch,a=n,b='head/'+m,distance_mm=d))
  print('Received access loop yaw',y,'pairs',r['pairs'],'contacts',len(r['contacts']),flush=True)
  save('progress.json',r)
 for n,c in incoming.items():
  c.exportBrep(str(OUT/(n+'_ReceivingApproach.brep')))
  for m,t in targets.items():
   if not t.Solids or not H.T.near(c,t,1.05):continue
   r['pairs']+=1;d=min(c.distToShape(s)[0] for s in t.Solids)
   if d<1.05-1e-5:r['contacts'].append(dict(a=n+'_approach',b=m,distance_mm=d))
  for y in (-15,0,15):
   for pitch in (-10,0,5):
    for m,t in H.head(reader,y,pitch).items():
     if not H.T.near(c,t,1.05):continue
     r['pairs']+=1;d=min(c.distToShape(s)[0] for s in t.Solids)
     if d<1.05-1e-5:r['contacts'].append(dict(a=n+'_approach',b='head/'+m,pose=[y,pitch],distance_mm=d))
 for i,n in enumerate(incoming):
  for m in list(incoming)[i+1:]:
   d=incoming[n].distToShape(incoming[m])[0];r['pairs']+=1
   if d<2.1-1e-4:r['contacts'].append(dict(a=n+'_approach',b=m+'_approach',distance_mm=d))
 r.update(status='CURRENT_HEAD_ACCESS_SPACE_CLEAR' if not r['contacts'] else 'REJECTED_HEAD_ACCESS_SPACE',
  worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,
   Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))},
  support_bounds_mm={n:H.bb(s) for n,s in solids().items()},
  functional_neck='Same325x200x160 torso, upper cosmetic shell remains off. Added neck arm maxY98; outside curved shell is explicitly external neck material, not a false inside-shell PASS. Root/fasteners unchanged; actual geometry contacts checked.',
  W3_open='Receiving approaches only, not whole six feeds, stock or native insulation grips.')
 save('space-checks.json',r);print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
if __name__=='__main__':run()
