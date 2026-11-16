import FreeCAD as A,FreeCADGui as G,Part,json,zipfile,xml.etree.ElementTree as E,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;P=Path(__file__).parent;t=time.perf_counter()
z=zipfile.ZipFile(P/'head-tail-mask.FCStd');root=E.fromstring(z.read('Document.xml'))
# Recover ONLY the previously valid saved front; no second model/writer or shape variant.
for x in root.findall('.//ObjectData/Object'):
 if x.get('name')=='OLA_REAL_FRONT_MASK':
  f=x.find("./Properties/Property[@name='Shape']/Part").get('file');q=Part.Shape();q.importBrepFromString(z.read(f).decode());D.getObject('OLA_REAL_FRONT_MASK').Shape=q
r=dict(utc=datetime.now(timezone.utc).isoformat(),status='NOMINAL_LOAD_AND_COUPLING_WITH_EXPLICIT_OPEN_CHECKS',checks=[],failures=[],technical_failure='integralface BOP returned null; restored exact valid front BRep from same saved checkpoint, no material-loss acceptance',physical_pass=False,wholekit_ready=False)
def vol(s):return 0.0 if s.isNull() else s.Volume
for role in ['YAW','PITCH','TAIL']:
 ns=[role+'_HORN_KEY_HALF_NEG',role+'_HORN_KEY_HALF_POS',role+'_HORN_ROOF_JOURNAL']
 for i,n in enumerate(ns):
  s=D.getObject(n).Shape;v=s.isValid() and len(s.Solids)==1;r['checks'].append(dict(name=n,valid=s.isValid(),solids=len(s.Solids)))
  if not v:r['failures'].append(n)
  for m in ns[:i]:
   c=s.common(D.getObject(m).Shape);row=dict(kind='separate_coupler_parting',a=n,b=m,common=vol(c),valid=c.isNull() or c.isValid());r['checks'].append(row)
   if row['common']>1e-5 or not row['valid']:r['failures'].append(row)
for n in ['P10_front_gate','P07_open_tail_root_U','HEAD_YAW_FORK_FIXED_PITCH_HOUSING','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER']:
 s=D.getObject(n).Shape;r['checks'].append(dict(kind='actual_part_material',name=n,valid=s.isValid(),solids=len(s.Solids),volume=vol(s)))
 if s.isNull() or not s.isValid() or len(s.Solids)!=1:r['failures'].append(n)
r['remaining']=['factoryhorn/screw interface exactdelivery FIT3, no printed spline or extra factoryscrew stack','full newsteel/tool/initialinsertion and bearingrace widths not all checked','continuousyaw20/pitch10/tail20 newcase/coupler/skin delta OPEN','CSI15 and ToF4coreR31.5 actualconnected route/slack OPEN; no lengthcredit','decorativeeye/nose references currentlynotmechanicallysecured, ears/newcoverroots OPEN','rear-neckguard/bodyclosure OPEN','bodyBNO/inline8/speaker/S1monitor OPEN']
r['seconds']=time.perf_counter()-t
(P/'core-functional-result.json').write_text(json.dumps(r,indent=2)+'\n')
# Hide analytic allocations and obsolete source visual aliases only.
for o in D.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull():continue
 n=o.Name
 if n.startswith(('COVER_','WIRE_','SECTION_','AL_','VIEW_','COUPON_','CAM102','TOF_BOTH','CAMERA_FULL','TOF_FULL')) or 'NOT_SUPPLIER' in n or 'NOT_THREAD' in n or n.endswith('_bracket_space'):o.ViewObject.Visibility=False
for n in ['CLOSED_HEAD_LOWER','CLOSED_HEAD_UPPER','Ola_tail_ENVELOPE']: 
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=False
for n in ['CLOSED_BODY_front_negative','CLOSED_BODY_front_positive','CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive','OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER','TAIL_ROTATING_HOLLOW_REAL_ROOT','Ola_eye_gold__1','Ola_eye_gold_1','DECORATIVE_BLACK_EYE__1','DECORATIVE_BLACK_EYE_1','Ola_nose']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
D.getObject('OLA_REAL_FRONT_MASK').ViewObject.ShapeColor=(.10,.105,.12)
D.Label='DAY16 HEAD TAIL OLA / NOMINAL OPEN FIT AND MOTION';D.recompute();D.save();G.getDocument(D.Name).Modified=False
print(json.dumps(dict(checks=len(r['checks']),failures=r['failures'],objects=len(D.Objects),seconds=r['seconds'],saved=True)))
