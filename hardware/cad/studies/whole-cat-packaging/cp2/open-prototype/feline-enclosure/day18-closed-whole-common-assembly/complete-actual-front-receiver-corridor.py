import FreeCAD as A,Part,json
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
rows=[]
for tag,side in [('NEG',-1),('POS',1)]:
 o=D.getObject('F3_BODY_FORE_'+tag);before=o.Shape.copy();s=before.copy()
 # Withdraw just the failed UNBUILT crossarm and nonconnecting vertical web; preserve source bearing receiver and cowl wall.
 removed=[box(-75,43 if side>0 else -88.5,55,10,45.5,3),box(-75,87.5 if side>0 else -93.5,55,10,6,19)]
 for q in removed:s=s.cut(q)
 column=box(-76,84.5 if side>0 else -88.5,43.62,12,4,14.38)
 # Derive the complete 3mm load web from the actual P_AUX right face -70 and P_REAR left face -64:
 # admissible [ -68.75, -65.25 ] after TWO unchanged1.25 clearances. Chosen3mm gives1.5 each.
 arm=box(-68.5,43 if side>0 else -88.5,55,3,45.5,3)
 # The measured actual cowl surface is Y=+/-86.28398,Z74.50724, not an assumed floor point.
 web=box(-68.5,82 if side>0 else -90,55,3,8,23)
 s=s.multiFuse([column,arm,web]).removeSplitter();o.Shape=s
 targets=[]
 for n in ['PBAY_P_AUX','PBAY_P_REAR']:
  q=D.getObject(n).Shape;targets.append({'name':n,'new_arm_gap':arm.distToShape(q)[0],'new_web_gap':web.distToShape(q)[0],'new_arm_common':arm.common(q).Volume,'new_web_common':web.common(q).Volume})
 rows.append({'part':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'whole_source_lower_receiver_retained_below46p02':before.common(box(-160,-115,41.5,360,230,4.52)).cut(s).Volume,'new_member_missing':[q.cut(s).Volume for q in [column,arm,web]],'useful_web_section_mm':[3,8],'local_case_checks':targets,'volume':s.Volume})
(P/'actual-front-corridor-functional-completion.json').write_bytes((json.dumps({'causal_decision':'actual6mm inter-case corridor carries ONE connected3mm crossarm and measured-surface3x8 web; source floor/6bearing tabs uncut. Raw 180common and1.118gap retained in prior check, failed arms explicitly withdrawn','results':rows,'physical_PASS':False},indent=2)+'\n').encode());D.recompute();D.save();print('ACTUAL_FRONT_CORRIDOR_COMPLETED',rows)
