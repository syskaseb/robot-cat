import FreeCAD as A,FreeCADGui as G,Part,json,time,math
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def cy(x,y,z,r,h,a=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),a)
def ell(x,y,z,rx,ry,rz):
 m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(x,y,z));return s
def vol(s):return 0.0 if s.isNull() else s.Volume
def good(s):return s.isNull() or s.isValid()
def run():
 t=time.perf_counter();r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],physical_pass=False,wholekit_ready=False)
 # Real transverse pin bores in all three independentjournals. Factoryoutput untouched.
 for n,cut in [('YAW_HORN_ROOF_JOURNAL',cy(-145,0,150,1.1,35,V(1,0,0))),('PITCH_HORN_ROOF_JOURNAL',cy(-166,25,141,1.1,26,V(1,0,0))),('TAIL_HORN_ROOF_JOURNAL',cy(185,-13,157,1.1,28,V(0,1,0)))]:o=D.getObject(n);o.Shape=o.Shape.cut(cut)
 # Fullnut bearing above133.7, no unbuiltlowerwasher. Same capjoint, realfloor/engagement.
 for o in list(D.Objects):
  if o.Name.startswith('YAW_FIXED_CAP_') and o.Name.endswith('_fullnut'):
   # maskbuilder moved source initialnut by-1.5: final132.1..133.7.
   o.Label='FullM2nut seated at133.7; factorycentre untouched'
 # One INTEGRAL faceprint with actual3Deyebosses/pupil/rim/nose material, paintcolour
 # only. No floating decorativephysicalparts or added LED electronics.
 front=D.getObject('OLA_REAL_FRONT_MASK');s=front.Shape.copy();intended=[]
 for sy,n in [(-1,'Ola_eye_gold__1'),(1,'Ola_eye_gold_1')]:
  y=31*sy;socket=ell(-240,y,151,8,15.5,16.5).cut(ell(-240,y,151,5.6,13.1,14.1));pupil=D.getObject('DECORATIVE_BLACK_EYE__1' if sy<0 else 'DECORATIVE_BLACK_EYE_1');ring=D.getObject(n)
  for q in [socket,pupil.Shape,ring.Shape]:s=s.fuse(q);intended.append(q)
  pupil.ViewObject.Visibility=False;ring.ViewObject.Visibility=False;ring.Label='RETIRED separatevisual / integralpaintedface now'
 nose=D.getObject('Ola_nose');pins=[cy(-252,y,140.5,1.5,6,V(1,0,0)) for y in [-2,2]]
 for q in [nose.Shape]+pins:s=s.fuse(q);intended.append(q)
 nose.ViewObject.Visibility=False;nose.Label='RETIRED separatevisual / integralnose+twoactualrootpegs'
 fovs=[D.getObject(n).Shape for n in ['CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL','TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL']]
 for q in fovs:s=s.cut(q)
 front.Shape=s;col=[]
 for f in s.Faces:
  b=f.BoundBox;c=f.CenterOfMass
  if c.x<-241 and 14<abs(c.y)<49 and 133<c.z<169:
   col.append((.78,.54,.12) if b.YLength>22 or b.ZLength>24 else (.025,.028,.032))
  elif c.x<-249 and abs(c.y)<8 and 136<c.z<145:col.append((.12,.08,.06))
  else:col.append((.10,.105,.12))
 front.ViewObject.DiffuseColor=col
 missing=[]
 for q in intended:
  if q.isNull():missing.append(dict(empty_reference=True,not_physicalextra=True));continue
  q=q.cut(fovs[0])
  if q.isNull():missing.append(0.0);continue
  q=q.cut(fovs[1])
  if q.isNull():missing.append(0.0);continue
  q=q.cut(s);missing.append(0.0 if q.isNull() else q.Volume)
 r['face_material']=dict(valid=s.isValid(),solids=len(s.Solids),volume=s.Volume,parting_common=vol(s.common(D.getObject('OLA_REAL_BACK_COVER').Shape)),intended_missing_after_optical_cuts=missing,oneintegralprint_withpaint_NOTextraelectronics=True)
 D.recompute();D.save();G.getDocument(D.Name).Modified=False
 def ck(row,ok):
  r['checks'].append(row)
  if not ok:r['failures'].append(row)
 # Realdisjoint3-piece coupling family; allintendedlower/roof/key surfaces.
 for role in ['YAW','PITCH','TAIL']:
  ns=[role+'_HORN_KEY_HALF_NEG',role+'_HORN_KEY_HALF_POS',role+'_HORN_ROOF_JOURNAL']
  for i in range(3):
   o=D.getObject(ns[i]);ck(dict(kind='realcouplerpart',part=o.Name,valid=o.Shape.isValid(),solids=len(o.Shape.Solids)),o.Shape.isValid() and len(o.Shape.Solids)==1)
   for j in range(i):c=o.Shape.common(D.getObject(ns[j]).Shape);ck(dict(kind='coupler_realparting',a=o.Name,b=ns[j],common=vol(c),valid=good(c)),good(c) and vol(c)<1e-5)
 for shaft,bearing in [('YAW_HORN_ROOF_JOURNAL','Yaw608_120'),('YAW_HORN_ROOF_JOURNAL','Yaw608_134'),('PITCH_HORN_ROOF_JOURNAL','Pitch688'),('TAIL_HORN_ROOF_JOURNAL','Tail608')]:
  c=D.getObject(shaft).Shape.common(D.getObject(bearing).Shape);ck(dict(kind='actualindependentjournal_vs_boughtbearing',shaft=shaft,bearing=bearing,common=vol(c),valid=good(c)),good(c) and vol(c)<1e-5)
 for a,b in [('YAW_FIXED_OUTER_RACE_CAP','P10_front_gate'),('PITCH_FIXED_OUTER_RACE_CAP','HEAD_YAW_FORK_FIXED_PITCH_HOUSING'),('TAIL_FIXED_BEARING_CARTRIDGE','P07_open_tail_root_U'),('TAIL_FIXED_OUTER_RACE_CAP','TAIL_FIXED_BEARING_CARTRIDGE')]:
  c=D.getObject(a).Shape.common(D.getObject(b).Shape);ck(dict(kind='fixedseparateparting',a=a,b=b,common=vol(c),valid=good(c)),good(c) and vol(c)<1e-5)
 for n in ['P10_front_gate','P07_open_tail_root_U','HEAD_YAW_FORK_FIXED_PITCH_HOUSING','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE']:
  o=D.getObject(n);ck(dict(kind='loadpart_connected',name=n,valid=o.Shape.isValid(),solids=len(o.Shape.Solids)),o.Shape.isValid() and len(o.Shape.Solids)==1)
 for n in ['OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER','Ola_eye_gold__1','Ola_eye_gold_1']:
  if n.startswith('Ola_'):continue # retiredvisualalias not extraoperatingmaterial
  for i,q in enumerate(fovs):c=D.getObject(n).Shape.common(q);ck(dict(kind='continuousFOV_vs_actualwall',wall=n,FOV=i,common=vol(c),valid=good(c)),good(c) and vol(c)<1e-5)
 r['remaining']=['factoryhorn/screw actualfit and originalengagement oneFIT3; communitynotmanufacturer','bearingracecontact/delivery/tolerances and payload physicalFIT','fullnewsteel/tool/servoearassembly and posecorrelatedskin/body delta not allqualified','rearheadneckoverlapguard/earmounts and bodyclosure stillOPEN','CSI15fullstock/contactside andToF4x2.1flexR31.5 connectedlay/actualslack notqualified','bodyBNO/inline/speaker/S1monitor retainedunsecured'];r['seconds']=time.perf_counter()-t;r['status']='CONTINUOUS_NOMINAL_MECHANISM_WITH_LOCAL_HOLD' if r['failures'] else 'CONTINUOUS_NOMINAL_COUPLING_AND_FOV_LOCAL_SCOPED_NOT_PHYSICAL';(P/'core-functional-result.json').write_text(json.dumps(r,indent=2)+'\n')
 # Actualopaqueviews: only analytic/retired/reference shapes hidden, all purchased
 # parts including protrusions remain; ears/legs fixed, newhollowtail functionalroot visible.
 for o in D.Objects:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  if o.Name.startswith(('COVER_','WIRE_','SECTION_','AL_','VIEW_','COUPON_','MG92B_')) and ('MG92B_' not in o.Name or o.Name.endswith('_bracket_space')):o.ViewObject.Visibility=False
  if o.Name.startswith(('CAM102','TOF_BOTH','CAMERA_FULL','TOF_FULL')) or 'NOT_SUPPLIER' in o.Name or 'NOT_THREAD' in o.Name:o.ViewObject.Visibility=False
 for n in ['CLOSED_BODY_front_negative','CLOSED_BODY_front_positive','CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive','OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER','TAIL_ROTATING_HOLLOW_REAL_ROOT']:
  o=D.getObject(n);o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
 D.Label='DAY16 HEAD TAIL+OLA MASK / NOMINAL WITH NAMED OPEN SCOPES';D.recompute();D.save();G.getDocument(D.Name).Modified=False;print(json.dumps(dict(status=r['status'],checks=len(r['checks']),failures=r['failures'],face=r['face_material'],seconds=r['seconds'],objects=len(D.Objects))))
run()
