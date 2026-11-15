import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
D=A.getDocument('DAY15_MODULE_RETENTION');P=Path(D.FileName).parent;plan=json.loads((P/'retention-plan.json').read_bytes());grp=D.getObject('RETENTION_INTERFACES_PLANNING_NOT_PRINTS')
for row in plan['groups']:
 o=D.getObject(row['id']+'_RETENTION_PROPOSAL') or D.addObject('App::FeaturePython',row['id']+'_RETENTION_PROPOSAL');o.Label=row['id']+' '+','.join(row['modules'][:2]);grp.addObject(o)
 for prop,key in [('ActualRoot','root'),('MatingInterface','interface'),('RetentionPrinciple','retention'),('OpenAssembly','assembly_access'),('PhysicalFitUnknown','FIT')]:
  if prop not in o.PropertiesList:o.addProperty('App::PropertyString',prop)
  setattr(o,prop,row[key])
 if 'ReleaseStatus' not in o.PropertiesList:o.addProperty('App::PropertyString','ReleaseStatus')
 o.ReleaseStatus='PLAN_ONLY_NO_NEW_PRINT_MATERIAL'
holes=json.loads((P/'known-board-hole-interfaces.json').read_bytes())['Pi4B_actual_PCB'];support=[]
for i,h in enumerate(holes):
 c=h['centre'];o=D.getObject('Pi_actual_hole_axis_'+str(i)) or D.addObject('PartDesign::Feature','Pi_actual_hole_axis_'+str(i));o.Shape=Part.makeLine(A.Vector(c[0],c[1],92.52),A.Vector(c[0],c[1],103));o.ViewObject.LineColor=(1.0,.1,.1);o.ViewObject.LineWidth=3;grp.addObject(o)
 post=D.getObject('CF_Pi_post_'+str(i));s=post.Shape;support.append(dict(post=post.Name,actual_post_bounds=str(s.BoundBox),PCB_gap=s.distToShape(D.getObject('Pi4B_actual_PCB').Shape)[0],hole_axis=c,printed_standoff_height=3,retention='NOT SECURED: M2.5 fullset/nutfeed stillneeded; matchedholes are actualsource r1.375 not electricalvias'))
(P/'Pi-current-bearing-interface.json').write_bytes((json.dumps(dict(status='FOUR_EXISTING_POSTS_SEATED_BUT_RETENTION_UNBUILT',rows=support,physical_pass=False),indent=2)+'\n').encode())
for o in D.Objects:
 if hasattr(o,'Shape') and hasattr(o.ViewObject,'Visibility'):
  o.ViewObject.Visibility=(o.Name.startswith(('P1','CS_')) or o.Name=='XT60H_mated_with_boots' or (o in D.getObject('Retained_whole_layout_REFERENCE').Group and not o.Name.startswith('Ola_') and o.Name not in ['Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits']))
for i in range(4):D.getObject('Pi_actual_hole_axis_'+str(i)).ViewObject.Visibility=True
D.getObject('F0_SINGLE_OD6_MARGIN04_LOCAL_CAPACITY').ViewObject.Visibility=True
old=A.getDocument('DAY15_POWER_CAPACITY')
if old:A.closeDocument(old.Name)
D.Label='DAY15 MODULE RETENTION — whole PLAN / unpowered / FIT2 F0';D.recompute();D.save();G.getDocument(D.Name).Modified=False
(P/'native-save-received.json').write_bytes((json.dumps(dict(doc=D.Name,objects=len(D.Objects),pid=17796,modified=bool(G.getDocument(D.Name).Modified),pending=None,utc=datetime.now(timezone.utc).isoformat(),file=D.FileName),indent=2)+'\n').encode());print({'doc':D.Name,'objects':len(D.Objects),'saved':D.FileName,'modified':bool(G.getDocument(D.Name).Modified),'retention_material_added':False})
