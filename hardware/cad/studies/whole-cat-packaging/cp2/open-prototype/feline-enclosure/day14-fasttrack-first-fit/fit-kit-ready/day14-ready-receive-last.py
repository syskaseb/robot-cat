import FreeCAD as A,Part,json,math,time
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-ready');D=A.getDocument('DAY14_FIT_KIT_READY');r=json.loads((P/'result.json').read_bytes());T=time.perf_counter();V=A.Vector
def write():(P/'result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def add(x,ok=True):
 r['checks'].append(x);write()
 if not ok:r['status']='HOLD_FIRST_NEW_MISSING_INTERFACE';r['first_falsifier']=x;write();raise RuntimeError(json.dumps(x))
def lower(a,b):return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
r['raw_cosmetic_overlap']=r.pop('first_falsifier');r['checks'][-1]['kind']='COSMETIC_ENVELOPE_REFERENCE_NOT_RIGID_MATERIAL';old=Part.Shape();old.read(str(P/'Upper_frame_rail_44-frozen-source.brep'));added=D.getObject('Upper_frame_rail_44').Shape.cut(old);newgap=r['inherited_logic_trial_gap']['actual_added_material_gap_mm'];oldgap=1.0
base=json.loads((P.parent/'layout.json').read_bytes());classification={x['object']:x['evidence'] for x in base['rows']};actors=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and hasattr(o.ViewObject,'ShapeColor')]
# Continue only unreceived tail after explicit cosmetic reference, no received exact pair replay.
start=next(i for i,o in enumerate(actors) if o.Name=='Ola_body_ENVELOPE')+1
for o in actors[start:]:
 if classification.get(o.Name) in ['GROUP_FLEXIBLE_INSTALLATION_SPACE_NOT_CLEARANCE_PASS','COSMETIC_ENVELOPE_NOT_PRINT_READY'] or o.Name.startswith('H03') or o.Name.startswith('P0'):continue
 lb=lower(added.BoundBox,o.Shape.BoundBox)
 if lb>=1.25-1e-6:continue
 if o.Name.startswith('Upper_frame_'):continue
 gap=added.distToShape(o.Shape)[0];c=added.common(o.Shape).Volume;add(dict(kind='REMAINING_ADDED_TONGUE_FOREIGN',b=o.Name,gap_mm=gap,common_mm3=c),gap>=1.25-1e-6 and c<1e-5)
# Actual accessible side of panel: 25x19.75 mm vertical local window around its edge. It is a handlay access proof, not a completeconnector/radius/length proof.
window=Part.makeBox(25,19.75,20,V(130,20.25,80));rows=[]
for o in actors:
 if classification.get(o.Name) in ['GROUP_FLEXIBLE_INSTALLATION_SPACE_NOT_CLEARANCE_PASS','COSMETIC_ENVELOPE_NOT_PRINT_READY'] or 'Silhouette' in o.Name or 'Ola' in o.Name:continue
 items=[(o.Name+':solid'+str(i),q) for i,q in enumerate(o.Shape.Solids)] if o.Name=='WAVEGO_complete_126_source_solids' else [(o.Name,o.Shape)]
 for other,q in items:
  lb=lower(window.BoundBox,q.BoundBox)
  if lb>=1.25-1e-6:rows.append(dict(b=other,lower_mm=lb));continue
  if len(q.Faces)>100:add(dict(kind='UNKNOWN_COMPLEX_PANEL_SIDE_ACCESS',b=other),False)
  gap=window.distToShape(q)[0];c=window.common(q).Volume;add(dict(kind='ACTUAL_PANEL_SIDE_HANDLAY_WINDOW',b=other,gap_mm=gap,common_mm3=c),gap>=1.25-1e-6 and c<1e-5)
r['panel_side_access']=dict(bounds_mm=[[130,20.25,80],[155,40,100]],crosssection_mm=[25,19.75],continuous_past_panel_z=[88.52,92.5],scope='hands lay flexible branches aroundopenY+edge before tray/upperPCB/skin. No rigidwholefreewirecurve. Factoryend/R/length/independentstrain acceptance remainsFIT2',certified_bounds=rows);window.exportBrep(str(P/'panel-side-access.brep'))
parts=D.getObject('PRINT_PARTS_world_assembly').Group
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  if not any(x.Name in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel'] for x in [a,b]):continue
  if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
  c=a.Shape.common(b.Shape).Volume;add(dict(kind='DISJOINT_SEPARATE_PRINTS',a=a.Name,b=b.Name,common_mm3=c),c<1e-5)
r['status']='CONDITIONAL_UNPOWERED_FOUNDATION_FIT_FEEDS_AND_NEW_SOCKET_FUNCTION_CLOSED_LOGIC_TRIAL_OPEN';r['wholecat_accepted']=False;r['wholeupperlogic_mount_accepted']=False;r['reused_joint']='frozen44d7b4ec M3x50 full12metal min4mm sourcecover gap/fullnut2.4/tip1.1/allwasherseats29.931524; no rerun';r['reused_P06_members']='frozen8members0missing/material/extent unchanged; newbearings52.8x2/posts9x2 andcontinuouskey insertionreceived';r['missing_final_checks_wall_seconds']=time.perf_counter()-T;write();D.Label='WAVEGO fit kit — unpowered foundation fit only';D.recompute();D.save();print(json.dumps({'status':r['status'],'checks':len(r['checks']),'newtongue_AUXgap':newgap,'inherited_trial':oldgap,'seconds':r['missing_final_checks_wall_seconds']}))
