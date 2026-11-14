import FreeCAD as A,Part,json,math,time
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-ready');D=A.getDocument('DAY14_FIT_KIT_READY');r=json.loads((P/'result.json').read_bytes());T=time.perf_counter();V=A.Vector
base=json.loads((P.parent/'layout.json').read_bytes());classification={x['object']:x['evidence'] for x in base['rows']}
last=r['checks'][-1];assert last['b']=='Rear_aux_open' and last['common_mm3']==1725
r['raw_region_result']=dict(last);last['kind']='ALLOCATED_FLEXIBLE_REGION_INTERFERENCE_NOT_RIGID_PART';last['source_classification']=classification['Rear_aux_open'];r.pop('first_falsifier',None);r['status']='MISSING_NEIGHBOR_CHECKS_RUNNING';r['region_effect']='S0/S1/monitor/fuse free spans remain handlaid before electronics/skin. Old broadbox partialoverlap is not wirecontact; actual connector/length/strain fit remainsFIT2, not digitalPASS.'
def write():(P/'result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def add(x,ok=True):
 r['checks'].append(x);write()
 if not ok:r['status']='HOLD_FIRST_ACTUAL_RIGID_OR_FUNCTIONAL_FALSIFIER';r['first_falsifier']=x;write();raise RuntimeError(json.dumps(x))
def lower(a,b):return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
def box(p,s):return Part.makeBox(*s,V(*p))
own={'Upper_frame_rail__49','Upper_frame_rail_44','Upper_frame_post_101__49','Upper_frame_post_101_44','P06_S0_shared_panel','P05_S0_panel_spacer40','P05_spacer_instance2','P05_spacer_instance3','P05_spacer_instance4','S0_body','S0_neck','S0_key'}|{o.Name for o in D.Objects if o.Name.startswith('H03')}
actors=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and hasattr(o.ViewObject,'ShapeColor')]
targets=[('P06_S0_shared_panel',D.getObject('P06_S0_shared_panel').Shape)]
for n,cy in [('Upper_frame_rail__49',-47.5),('Upper_frame_rail_44',45.5)]:targets.append((n+':changedTongue',D.getObject(n).Shape.common(box((100,cy-3,89),(10,6,5)))))
r['numeric_neighbor_bounds']=[]
for name,s in targets:
 for o in actors:
  if o.Name in own:continue
  if classification.get(o.Name) in ['GROUP_FLEXIBLE_INSTALLATION_SPACE_NOT_CLEARANCE_PASS','APPEARANCE_REFERENCE_NOT_PRINTED'] or 'Silhouette' in o.Name or 'Ola' in o.Name:
   r['numeric_neighbor_bounds'].append(dict(a=name,b=o.Name,classification=classification.get(o.Name),status='FLEX_OR_APPEARANCE_REFERENCE_NOT_RIGID_FOREIGN'));continue
  items=[(o.Name+':solid'+str(i),q) for i,q in enumerate(o.Shape.Solids)] if o.Name=='WAVEGO_complete_126_source_solids' else [(o.Name,o.Shape)]
  for other,q in items:
   lb=lower(s.BoundBox,q.BoundBox)
   if lb>=1.25-1e-6:r['numeric_neighbor_bounds'].append(dict(a=name,b=other,lower_mm=lb,status='CLEAR_CERTIFIED_BBOX_LOWER'));continue
   if other.startswith('Upper_frame_'):
    c=s.common(q).Volume;add(dict(kind='UNBUILT_LOGIC_FRAME_MATCHED_CONTACT',a=name,b=other,common_mm3=c),c<1e-5);continue
   if len(q.Faces)>100:add(dict(kind='UNKNOWN_COMPLEX_LOCAL_SOURCE',a=name,b=other,faces=len(q.Faces),lower_mm=lb),False)
   gap=s.distToShape(q)[0];c=s.common(q).Volume;add(dict(kind='ACTUAL_CHANGED_NEARBY_PART',a=name,b=other,gap_mm=gap,common_mm3=c,valid=q.isValid() and s.isValid()),gap>=1.25-1e-6 and c<1e-5 and q.isValid() and s.isValid())
# All distinct intended printparts: only P03/P06 incident pairs, no whole-source scans.
parts=D.getObject('PRINT_PARTS_world_assembly').Group
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  if not any(x.Name in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel'] for x in [a,b]):continue
  if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
  c=a.Shape.common(b.Shape).Volume;add(dict(kind='DISJOINT_SEPARATE_PRINTS',a=a.Name,b=b.Name,common_mm3=c),c<1e-5)
r['reused']=dict(M3x50='unchanged full12metal shapes vs prior min4mm/washerseats29.931524/fullnut2.4/tip1.1',P06material='same frozen8members0missing, two rails andtwo postbearings nowchecked',P03foreign='onlyremoved36.052513813mm3 and 0added; inherited foreignclearances bysubset',source8_and_factoryparts='unchanged poses/geometry, no audit')
r['status']='CONDITIONAL_UNPOWERED_FIRST_FIT_LOCAL_FEED_AND_SHARED_LOGIC_FUNCTION_CLOSED';r['remaining_physical_FIT']=['FIT1 source8holes/thread/payload/legmotion','FIT2 fullselectedends/stock/4independent220/FHAC/USB+Delock/S0M6family/PiBUSstack','FIT3 cardboardwholeOlaoutline/headtail supports'];r['neighbor_check_wall_seconds']=time.perf_counter()-T;write();D.Label='WAVEGO fit kit — conditional unpowered first fit';D.recompute();D.save();print(json.dumps({'status':r['status'],'checks':len(r['checks']),'bounds':len(r['numeric_neighbor_bounds']),'seconds':r['neighbor_check_wall_seconds']}))
