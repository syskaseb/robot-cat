import FreeCAD as A, FreeCADGui as G, Part, json, math, hashlib, time
from pathlib import Path
D=A.ActiveDocument; P=Path(__file__).parent; V=A.Vector; moves=[]; changed=[]; t=time.perf_counter()
def box(x,y,z,l,w,h): return Part.makeBox(l,w,h,V(x,y,z))
def bounds(s):
 b=s.BoundBox; return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def put(n,d): (P/n).write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def add(n,s,col=(.4,.58,.61),scope='PRINT_CONCEPT_UNRELEASED'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True
 if not hasattr(o,'HeadScope'):o.addProperty('App::PropertyString','HeadScope')
 o.HeadScope=scope;changed.append(n);return o
# One complete functional relocation, not a changed mouth point. All effective
# bearings, horn centre stacks, servo saddles, full sensors and covers move once.
for o in D.Objects:
 if not hasattr(o,'Shape') or not hasattr(o,'Placement') or o.Shape.isNull():continue
 name=o.Name
 sel=name.startswith(('YAW_','PITCH_','HEAD_','CAM_','CAMERA_','TOF_')) or name in ['Camera3_NoIR_Wide','VL53L5CX','MG92B_Head_yaw','MG92B_Head_pitch','Yaw608_120','Yaw608_134','Pitch688','Ola_ear__1','Ola_ear_1','Ola_eye_gold__1','Ola_eye_gold_1','Ola_nose','DECORATIVE_BLACK_EYE__1','DECORATIVE_BLACK_EYE_1','NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT']
 if sel and (o.ViewObject.Visibility or name.startswith(('CAMERA_','TOF_FULL','CAM102','TOF_BOTH'))):
  before=bounds(o.Shape);vol=o.Shape.Volume;o.Placement.Base+=V(20,0,0)
  moves.append({'name':name,'before':before,'after':bounds(o.Shape),'volume_before':vol,'volume_after':o.Shape.Volume,'rigid_delta':[20,0,0]})
# Retain the actual grid foot. Shorten the same useful bridge to the new fixed
# servo saddle; no root is attached to the rotating fork.
root=box(-86,15,45.52,12,8,21).fuse(box(-127,15,66.5,53,8,7)).fuse(box(-127,-13,66.5,28,36,3))
D.getObject('NIGHT_HEAD_FIXED_SADDLE_ROOT').Shape=root;changed.append('NIGHT_HEAD_FIXED_SADDLE_ROOT')
# Open sensor horseshoe: preserve every rear spine, pitch journal, ToF brace,
# cover arm and primary upper camera mounting axis. Replace the obstructing
# full PCB backing sheet with connected side/top/lower load members.
o=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE');old=o.Shape
sheet=box(-204.60001,-32.00001,85.99999,3.00002,62.00002,73.00002)
rest=old.cut(sheet)
members=[box(-204.6,-32,86,3,8,73),box(-204.6,24,86,3,6,73),box(-204.6,-32,94,3,62,4),box(-204.6,-32,141.1,3,62,8),box(-204.6,-32,155,3,62,4)]
# The two existing upper screw sets remain full. The two unbuilt lower metal
# spacers are replaced by edge lands outside the full FFC width+clearance.
for y in [-32,9.8]:members.append(box(-209.6,y,130.6,8,22.2,4))
s=rest
for q in members:s=s.fuse(q)
for y in [-10.5,10.5]:s=s.cut(Part.makeCylinder(1.1,9,V(-206,y,145.1),V(1,0,0)))
o.Shape=s;changed.append(o.Name);retired=[]
for n in ['CAM_standoff__10_5_152_6','CAM_standoff_10_5_152_6']:
 q=D.getObject(n);q.ViewObject.Visibility=False;retired.append(n)
# Speaker/Pi/head must coexist. One full speaker moves to the opposite open
# side, facing out; no change to membrane, stock or the source Pi ports.
sp=D.getObject('Speaker');before=bounds(sp.Shape);vol=sp.Shape.Volume
sp.Placement=A.Placement(V(),A.Rotation(V(0,0,1),180)).multiply(sp.Placement)
b=sp.Shape.BoundBox;sp.Placement.Base+=V(-100,84.5,100)-V(b.XMin,b.YMin,b.ZMin)
moves.append({'name':'Speaker','before':before,'after':bounds(sp.Shape),'volume_before':vol,'volume_after':sp.Shape.Volume,'whole_orientation':'outward +Y acousticface; mounting/lead FIT not accepted'})
# Same body remains PROVISIONAL. Actual acoustic opening in this reference
# surface only; not a printable skin/root or an acoustics claim.
env=D.getObject('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT');env.Shape=env.Shape.cut(box(-101,80,99,102,60,47))
# Reuse the inherited exact full source FOV volumes after the rigid move.
camf=D.getObject('CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL')
toff=D.getObject('TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL')
for q in [camf,toff]:
 if q and q.Name not in [m['name'] for m in moves]:q.Placement.Base+=V(20,0,0)
# Coherent 3D provisional face rather than raised goggle rings. This is solid
# design envelope only: explicitly excluded from print/mass and STL release.
def ell(x,y,z,rx,ry,rz):
 m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz;q=Part.makeSphere(1).transformGeometry(m);q.translate(V(x,y,z));return q
head=ell(-173,0,125,58,62,53).fuse(ell(-199,0,140,34,46,29))
for y in [-25,25]:head=head.fuse(ell(-215,y,116,21,27,22))
head=head.fuse(ell(-227,0,112,18,22,15))
for q in [camf,toff]:
 if q:head=head.cut(q.Shape)
for sy in [-1,1]:
 head=head.cut(ell(-232,sy*31,132,5,12.5,13.5))
 eye=ell(-229.7,sy*31,132,2.2,10.7,11.6)
 for q in [camf,toff]:
  if q:eye=eye.cut(q.Shape)
 add('HN_DECORATIVE_RECESSED_EYE_'+str(sy),eye,(.62,.43,.12),'DECORATION_NOT_PRINT_NOT_HARDWARE')
for n in ['Ola_eye_gold__1','Ola_eye_gold_1','DECORATIVE_BLACK_EYE__1','DECORATIVE_BLACK_EYE_1']:
 q=D.getObject(n)
 if q:q.ViewObject.Visibility=False;retired.append(n)
D.getObject('NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT').Shape=head
D.getObject('NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT').Placement=A.Placement()
changed.append('NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT')
put('whole-head-neck-effectivity.json',{'moves':moves,'changed_print_concepts':changed,'retired_unbuilt_only':retired,'whole_head_shift':20,'fixed_root':'unchangedactualgridfoot -86..-74/Y15..23/45.52; shortened usefulbeam to fixedsaddle69.5','new_topology':'open horseshoe sensorreceiver, fullchannel centralwidth19.6; samepitchjournal andToFbrace preserved','camera_primary_upper_sets':'same two full sets rigid+20; lower metalstandoffs unbuilt demands retired for two connected safeedge lands nominalFIT3','mechanism':'same2MG/2yaw608/pitch688/horns/factorycentre screw with rigidrelativeidentity, not spline8mm','speaker':'whole outward +Yface; sharedsupport and completelead budgets remainOPEN; no deletion','face_scope':'PROVISIONAL_NOTPRINT_NOTMASS, no skinjoints/strength/wholemotionPASS','all_body_sources':'retained includingfull12MTA/57+ADD7/all protection/4MTA0100335UNBOUND','no_STL':True,'physicalPASS':False})
put('receiver-member-coverage.json',{'explicit_replaced_member':'3x62x73fullbackingplate with primary holes; replace not zero-loss claim','members':[{'bounds':bounds(q),'volume':q.Volume,'missing_in_new':q.cut(s).Volume} for q in members],'old_rest_missing':rest.cut(s).Volume,'source_old_volume':old.Volume,'new_volume':s.Volume,'new_solids':len(s.Solids),'new_valid':s.isValid(),'retained_roles':['pitchbearingjournal/crosspin','continuous positiveYpitcharm','ToF nosebrace/two mounts','fourcoverarmspines','two actualupperCAMholeaxes','sidebridge lowerPCBeds clearfullFFC'],'safePCBcontact_physical':'FIT3 actualcomponent/revision/edge land','root_solids':len(root.Solids),'root_valid':root.isValid(),'no_strengthPASS':True})
D.recompute();D.save();print(json.dumps({'saved':D.FileName,'objects':len(D.Objects),'moves':len(moves),'frame_solids':len(s.Solids),'seconds':time.perf_counter()-t}))
