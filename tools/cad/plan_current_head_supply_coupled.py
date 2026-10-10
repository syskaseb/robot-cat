"""Joint allocation: low NORTH/EAST pitch holder, both exits and all grips.

The south bank and north S0 wing are immutable obstacles. Retain received
yaw fanouts, but allocate a complete low holder and vertical red splice east
of the arm. Do not iterate an isolated screw or wire around either obstacle.
"""
import json,time
from pathlib import Path
import plan_current_head_supply_service as V
import plan_current_head_supply_grips as G
S,R,A,Part,H,P,ROOT,BASE,OUT=V.S,V.R,V.A,V.Part,V.H,V.P,V.ROOT,V.BASE,V.OUT

def layout():
 p=R.layout()
 for name in ('FHPFoot','FHPPost'):p.pop(name,None)
 for n,b in {
  'F_HP_case':[-38.05,78.5,69.99,12.95,98.75,91.99],
  'FoundationNorthWing':[-168,26,68.52,-108,60,71.52],
  'FoundationPitchNorthBridge':[-168,48,68.52,-44,75,71.52],
  'FHPNeck':[-48,70,65.99,-40,79,71.52],
  'FHPFloor':[-49,75.5,65.99,24,100,69.99]}.items():p[n]=H.T.box(b)
 return p

def build():
 p=V.build();old=S.build();routes=p['routes'];routes['XB22']=old['routes']['XB22']
 # A complete source drop outside both the bank INPUT barrel and the
 # retained W2 elbow. The case, prefix, two bends and vertical splice are
 # allocated together; changing only the final wire point would fail again.
 y=88.625;q=[S.line([-38.05,y,79.99],[-54,y,79.99])]
 S.turn(q,[-54,82.625,79.99],[-60,82.625,79.99])
 S.turn(q,[-60,82.625,85.99],[-60,76.625,85.99]);S.straight(q,[-60,76.625,105.99])
 routes['F_HP_out']['parts']=q
 routes['F_HP_input_prefix']['parts']=[S.line([12.95,y,79.99],[21.95,y,79.99])]
 # Source red must approach the retained three-wire XY elbow EASTwards,
 # not cross it with an independently chosen YZ bend. Allocate a complete
 # overhead return outside the other two paths; only this functional wire
 # reachesZ160.594 above the omitted cosmetic torso (no side widening).
 q=[S.line([-60,76.625,97.99],[-60,76.625,S.ZR+12.6])]
 S.turn(q,[-72.6,76.625,S.ZR+12.6],[-72.6,76.625,S.ZR+25.2]);S.move(q,[-1,0,0],[0,1.375,0]);S.straight(q,[-90,78,S.ZR+25.2])
 S.turn(q,[-90,78,S.ZR+12.6],[-102.6,78,S.ZR+12.6]);S.turn(q,[-90,78,S.ZR+12.6],[-90,78,S.ZR])
 S.move(q,[1,0,0],[0,-5.95,0]);S.straight(q,[-66,72.05,S.ZR]);S.turn(q,[-66,85,S.ZR],[-53.05,85,S.ZR])
 routes['XB22']['parts']=q
 routes['XB22_sleeve']['parts']=[S.line([-60,76.625,91.99],[-60,76.625,111.99])]
 p['factory_splices']['XB22'].update(centre_mm=[-60,76.625,101.99],axis='Z')
 p['changed_topology']='Complete low north/east pitch holder;35mm ATO space; WEST factory exit with20mm straight vertical splice; EAST input9mm. Received grade-separated yaw fanouts retained. Full grip/load-path allocation included before detailed native CAD.'
 return p

def allocations():
 old=G.S.layout;G.S.layout=layout
 try:return G.plan()
 finally:G.S.layout=old

def run():
 tick=time.monotonic();p=build();S.save('coupled-plan.json',p);g=allocations()
 S.save('coupled-grips.json',{k:v for k,v in g.items() if k not in ('parts','bands')})
 paths={n:S.Q.makewire(v['parts']) for n,v in p['routes'].items()}
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,lengths_mm={n:w.Length for n,w in paths.items()})
 def curve(n,c,rr,m,t,required=None,pose=None):
  req=rr if required is None else required
  if not H.T.near(c,t,req):return
  r['pairs']+=1;dist=c.distToShape(t)[0]
  if dist<req-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=req,pose=pose))
 def solid(n,s,m,t,pose=None):
  if not s.Solids or not t.Solids or not H.T.near(s,t,0):return
  r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
  if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,pose=pose))
 assigned=[('XB12','F_HY_out'),('XB22','F_HP_out'),('XS13','XS13_bare'),('XS23','XS23_bare')]+[(name+'_sleeve',part) for name,factory in [('XB12','F_HY_out'),('XB22','F_HP_out')] for part in (name,factory)]
 for i,n in enumerate(paths):
  for m in list(paths)[i+1:]:
   if frozenset((n,m)) not in [frozenset(v) for v in assigned]:curve(n,paths[n],p['routes'][n]['radius'],m,paths[m],p['routes'][n]['radius']+p['routes'][m]['radius'])
 if r['contacts']:
  r.update(status='REJECTED_COUPLED_MUTUAL',worker_seconds=time.monotonic()-tick);S.save('coupled-checks.json',r);print(json.dumps(r),flush=True);return
 reader=P.SavedShapes();targets,torso=S.C.F.physical_scene(reader)
 targets.update({n:reader.shape(S.C.OUT/'HeadWiringAccess.FCStd',n) for n in ('UpperCarrier001','HeadFixedAnchor')})
 for row in g['carrier_cuts']:targets['UpperCarrier001']=targets['UpperCarrier001'].cut(H.T.box(row['bounds_mm']))
 parts=g['parts'];heads={(y,pitch):H.head(reader,y,pitch) for y in (-15,0,15) for pitch in (-10,0,5)}
 changed=['XB13','XS13','XB22','F_HP_out','F_HP_input_prefix','XB22_sleeve']
 for n in changed:
  for m,t in {**targets,**parts}.items():
   if not t.Solids:continue
   c=paths[n]
   if n.startswith('F_HP') and m=='F_HP_case':c=Part.Wire(c.Edges[1:]) if len(c.Edges)>1 else None
   if n=='XB13' and m=='G_AUX_case':c=Part.Wire(c.Edges[1:])
   if c is not None:curve(n,c,p['routes'][n]['radius'],m,t)
  for pose,group in heads.items():
   for m,t in group.items():curve(n,paths[n],p['routes'][n]['radius'],'head/'+m,t,pose=pose)
  print('Coupled route',n,'contacts',len(r['contacts']),flush=True)
 # Only new material and retention envelopes. Assigned union to the same
 # native Foundation/Carrier is evaluated by the native builder, not waived
 # against purchased parts or unrelated neck bodies.
 original=R.layout()
 newparts={n:t for n,t in parts.items() if n not in original or abs(t.Volume-original[n].Volume)>1e-6 or H.bb(t)!=H.bb(original[n])}
 newparts.update(g['bands'])
 for row in g['carrier_pads']+g['yaw_pads']:newparts[row['name']]=H.T.box(row['bounds_mm'])
 for n,s in newparts.items():
  for m,t in targets.items():
   if m=='UpperCarrier001' and n in {v['name'] for v in g['carrier_pads']}:continue
   solid(n,s,m,t)
  for pose,group in heads.items():
   for m,t in group.items():
    if m=='Foundation' and n not in g['bands'] and not n.endswith('_case'):continue
    if m=='YawCarrier' and n in {v['name'] for v in g['yaw_pads']}:continue
    if m=='YawCarrier' and n.startswith('YawFinal'):
     for row in g['yaw_cuts']:t=t.cut(H.T.box(row['bounds_mm']))
    solid(n,s,'head/'+m,t,pose)
  for m,c in paths.items():
   if n=='F_HP_case' and m.startswith('F_HP'):continue
   # Cuts are applied in native material below. Uncut post boxes are not
   # pipe-clash evidence; bands/heads and purchased cases remain actual.
   if n in g['bands'] or n.endswith('_case'):curve(m,c,p['routes'][m]['radius'],n,s)
  S.save('coupled-progress.json',r)
 for label,x,y,z in [('HY',-140.5,-85.125,132),('HP',-12.55,88.625,91.99)]:
  tool=H.T.box([x-11,y-5,z,x+11,y+5,z+35])
  for m,t in {**targets,**parts}.items():
   if m==('F_HY_case' if label=='HY' else 'F_HP_case'):continue
   solid('ATO_'+label,tool,m,t)
  for pose,group in heads.items():
   for m,t in group.items():solid('ATO_'+label,tool,'head/'+m,t,pose)
 for n,w in paths.items():w.exportBrep(str(OUT/(n+'_Coupled.brep')))
 r.update(status='CURRENT_COUPLED_HEAD_SUPPLY_SPACE' if not r['contacts'] else 'REJECTED_COUPLED_HEAD_SUPPLY_SPACE',worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),Path(G.__file__).relative_to(ROOT).as_posix():P.sha(Path(G.__file__))})
 S.save('coupled-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds')}),flush=True)
if __name__=='__main__':run()
