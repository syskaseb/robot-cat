import FreeCAD as A,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-shared-module-fit');D=A.getDocument('DAY15_SHARED_MODULE_PROPOSAL');plan=json.loads((P/'proposal.json').read_bytes());T=time.perf_counter();CPU=time.process_time();V=A.Vector
r=dict(status='CHECKING_ONLY_FIRST_WHOLE_PREMISE',started_utc=datetime.now(timezone.utc).isoformat(),checks=[],numeric_cull=[],not_received=[])
def write():r.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'first-gate.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def sh(n):return D.getObject(n).Shape
def receive(row,ok=True,a=None,b=None):
 r['checks'].append(row);write()
 if not ok:
  r['status']='HOLD_FIRST_WHOLE_ARCHITECTURE_PREMISE';r['first_falsifier']=row;r['not_received']=['remaining samewholeclamp pairs afterfirstfalsifier','othercommonframe/joint/bank/connector/stock/assemblyqualification'];write()
  if a is not None and b is not None:
   a.exportBrep(str(P/'gate-operand-A.brep'));b.exportBrep(str(P/'gate-operand-B.brep'));c=a.common(b)
   if c.isValid() and c.Volume>1e-6:c.exportBrep(str(P/'gate-common.brep'))
  raise RuntimeError(json.dumps(row))
def lower(a,b):return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
def facearea(sa,sb,z):
 def fs(s):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-z)<1e-6]
 return sum(f.common(g).Area for f in fs(sa) for g in fs(sb))
cool=sh('Pi_components_and_cooling');bus=sh('BUS25514_installed');bridge=sh('CF_BUS_removable_bridge')
receive(dict(kind='NAMED_COOLING_VS_WHOLE_RELOCATED_BUS',gap_mm=cool.distToShape(bus)[0],common_mm3=cool.common(bus).Volume,full_bridge_gap_mm=cool.distToShape(bridge)[0],scope='NominalfullcoolingandfullBUSoccupiedspace; notthermalsimulation'),cool.distToShape(bus)[0]>=1.25 and cool.common(bus).Volume<1e-5)
source=sh('WAVEGO_complete_126_source_solids').Solids
for c in plan['clamp_plan']:
 upper=sh(c['upper']);low=sh(c['lower']);deck=sh(c['plate']);portal=sh('CF_'+('rear' if c['tag'][0]=='R' else 'front')+'_portal')
 top=facearea(upper,deck,48.52);bottom=sum(facearea(low,deck,z) for z in [41.52,45.52]);cu=upper.common(deck);cl=low.common(deck);join=upper.common(portal).Volume
 receive(dict(kind='ACTUAL_WHOLE_CLAMP_DECK_BEARING',tag=c['tag'],top_area_mm2=top,lower_area_mm2=bottom,upper_deck_common_mm3=cu.Volume,lower_deck_common_mm3=cl.Volume,upper_to_portal_intended_integral_join_mm3=join,ownfit='Jawtop/bottom matchedcontact; upperjaw explicitlyINTEGRAL portalfootmember, lowerjaw separate. Notboughtframeownwaiver.'),top>0 and bottom>0 and cu.Volume<1e-5 and cl.Volume<1e-5 and join>0,upper,deck)
 for suffix in ['M3x'+str(c['M3_length']),'washer','nut']:
  name='CL_'+c['tag']+'_'+suffix;s=sh(name)
  for j,q in enumerate(source):
   lb=lower(s.BoundBox,q.BoundBox)
   if lb>=1.25-1e-6:r['numeric_cull'].append(dict(a=name,source_solid=j,lower_mm=lb));continue
   if len(q.Faces)>100:receive(dict(kind='UNKNOWN_COMPLEX_NAMED_LOCAL_SOURCE_NOT_GUI_BOP',a=name,source_solid=j,faces=len(q.Faces),lower_mm=lb),False,s,q)
   gap=s.distToShape(q)[0];common=s.common(q);receive(dict(kind='WHOLE_STANDARD_METAL_VS_ACTUAL_RETAINED_SOURCE',a=name,source_solid=j,gap_mm=gap,common_mm3=common.Volume,valid=s.isValid() and q.isValid() and common.isValid()),gap>=1.25-1e-6 and common.Volume<1e-5 and s.isValid() and q.isValid() and common.isValid(),s,q)
 # Namedbankhazard: root/jaws/completehead adjacentfullbanks, not everywireaxis.
 for row in json.loads((P.parent/'day14-fasttrack-first-fit/layout.json').read_bytes())['rows']:
  n=row['object']
  if not (n.startswith('Motor_ATO') or n.startswith('FHAC') or n in ['F0_FHAC0002_30A','S0_body','S0_key','Battery_GEA223S30X6GT']):continue
  for name in [c['upper'],c['lower'],'CL_'+c['tag']+'_M3x'+str(c['M3_length'])]:
   s=sh(name);q=sh(n);lb=lower(s.BoundBox,q.BoundBox)
   if lb>=1.25-1e-6:continue
   if len(q.Faces)>100:receive(dict(kind='UNKNOWN_COMPLEX_NAMED_BANKCANDIDATE',a=name,b=n,lower_mm=lb),False,s,q)
   gap=s.distToShape(q)[0];common=s.common(q);receive(dict(kind='WHOLE_ROOT_VS_RETAINED_FULL_BANK_CASE',a=name,b=n,gap_mm=gap,common_mm3=common.Volume,valid=common.isValid()),gap>=1.25-1e-6 and common.Volume<1e-5 and common.isValid(),s,q)
r['status']='FIRST_WHOLE_ROOT_AND_BUS_COOLING_PREMISE_CLOSED_SCOPED_NOT_ALL_MODULE_MOUNTS';r['not_received']=['remainingcommonframeparting/boltedendconnections','allboardmounts/fullportends/initiallay/batteryremoval','otherbank/fuse/stock/motionqualification'];write();print(json.dumps({'status':r['status'],'checks':len(r['checks']),'wall':r['wall_seconds'],'CPU':r['cpu_seconds']}))
