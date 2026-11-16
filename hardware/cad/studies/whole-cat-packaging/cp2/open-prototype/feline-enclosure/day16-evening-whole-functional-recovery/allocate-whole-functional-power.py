import FreeCAD as A,FreeCADGui as G,Part,json
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
# One functional arrangement: direct facing W043, AUX branch on separate height/function, servo branches retained.
def bounds(o):
 b=o.Shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def reposition(n,rot,target):
 o=D.getObject(n);before=bounds(o);pl=A.Placement(V(),rot).multiply(o.Placement);o.Placement=pl;b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin);return dict(name=n,before=before,after=bounds(o),same_volume_rigid=True)
rows=[]
rows.append(reposition('PBAY_P_SYS',A.Rotation(V(1,0,0),-90),[116,44,56]))
rows.append(reposition('PBAY_P_REAR',A.Rotation(V(0,0,1),90).multiply(A.Rotation(V(1,0,0),-90)),[142,22,76]))
rows.append(reposition('PBAY_F_AUX',A.Rotation(V(0,1,0),-90),[144,48,70]))
# Full selected units retained; obsolete stock paths are references pending new own-function support, never BOM deletions.
for o in D.Objects:
 if o.Name.startswith('PB_') or o.Name.startswith('W043_ALLOCATED'):
  o.ViewObject.Visibility=False
# Full original cover and new positions, no reduced modules. Remaining six functions retain positions.
rolemap={}
for n in ['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX','PBAY_POST_F0']:
 o=D.getObject(n);rolemap[n]=bounds(o);o.Label=n+' EVENING FUNCTIONAL PROPOSAL / retention NOT accepted'
# These are regional planning operands, not literal rigid cables or exports.
def region(n,b,col):
 o=D.addObject('PartDesign::Feature',n);o.Shape=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]));o.ViewObject.ShapeColor=col;o.ViewObject.Transparency=70;o.Label=n+' ALLOCATION_NOT_DELIVERED_MATERIAL';return o
regions=[('EV_W043_SAME_FACE_HANDLAY',[106,56,56,116,78,75.25],(0.9,0.2,0.2)),('EV_AUX_REAR_BRANCH',[138,44,43,180,78,70],(0.9,0.5,0.1)),('EV_NEG_SERVO_BRANCH',[53,-70,68,124,-64,112],(0.9,0.6,0.1)),('EV_CENTRAL_POWER_TRANSFER',[42,19,70,110,34,89],(0.85,0.3,0.1)),('EV_HEAD_FLEX_GROUP',[-157,-31,112,-113,-18,151],(0.2,0.7,0.7)),('EV_TAIL_FIXED_TO_SERVO_FEED',[158,-55,123,178,-34,148],(0.2,0.7,0.7))]
for n,b,c in regions:region(n,b,c)
# ENTRY FACE is primary orientation; actual individual mouth axes remain UNKNOWN.
face={'P_SYS':{'plane':'X=116','normal_out':[-1,0,0],'width_axis':[0,1,0],'lever_access':[0,0,1],'bounds':[116,44,56,116,81,67]},'P_REAR':{'plane':'Y=44','normal_out':[0,1,0],'width_axis':[1,0,0],'lever_access':[0,0,1],'bounds':[142,44,76,179,44,87]}}
source=json.loads((P.parent/'day16-functional-power-bay/current-function-and-end-regions.json').read_text())
ch=source['chambers']
for c in ch:
 c.pop('proposed_mouth_region',None)
 role=c['logical'].split('.')[0]
 if role in face:c['whole_entry_face_region']=face[role]
 c['individual_mouth_axis_verified']=False
plan={'one_configuration_only':True,'moved_whole_units':rows,'nine_case_bounds':rolemap,'primary_615_face_frames':face,'chambers':ch,'qualified_wire_ROUTE_upper':None,'W043_conditional_plan':{'method':'straight common face-normal exterior band; no bend assumed between facing ports','exterior_box_bound_mm':10,'WAGO_consumption_planning_mm':14,'lay_slack_planning_mm':5,'conditional_total_mm':29,'guaranteed_raw_mm':84.5,'qualification':'ONLY if actual FHAC exit and assigned chamber lie in overlapping YZ band; chamber axes and FHAC mouths UNKNOWN. Not an actual routed upper.','strip_included_not_extra':True},'regions':[dict(name=n,bounds=b) for n,b,c in regions],'affected_interfaces':['P11 old two615 rack and FHAC-AUX retention MUST be functionally replaced, NOT selected','P_SYS W043 W066 W067 W068','P_REAR W065 XA01 XP01 W044 W052','F_AUX XA01 XA02 composite ends and MAIN/AUX nearby ports','old PB stock fields retired as paths only; full units retained in BOM/assembly plan'],'power_status':'PROPOSAL_NOT_PASS; nominal source end and support links OPEN'}
(P/'whole-functions-end-regions-and-short-budget.json').write_text(json.dumps(plan,indent=2))
D.recompute();D.save();print(json.dumps({'case_changes':rows,'W043':plan['W043_conditional_plan']}))
