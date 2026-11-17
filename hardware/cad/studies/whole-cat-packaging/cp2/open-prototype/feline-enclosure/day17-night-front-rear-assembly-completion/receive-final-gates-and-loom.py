import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def vol(s):return 0. if s.isNull() else s.Volume
def run():
 rows=[]
 def check(n,s,other,q,scope,matched=False):
  l=low(s,q);r={'part':n,'neighbor':other,'scope':scope,'lower':l,'threshold':1.25,'matched_interface':matched}
  if l>=1.25 and not matched:r['clear_scoped']=True
  else:
   d=s.distToShape(q)[0];r.update(gap=d,valid=s.isValid() and q.isValid(),clear_scoped=None if matched else d>=1.25-1e-7)
   if matched or d<1.25:r.update(common=vol(s.common(q)))
  rows.append(r)
 pi=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']
 for y,p in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
  for hn,kind in [('MG92B_Head_pitch','yaw'),('HEAD_YAW_FORK_FIXED_PITCH_HOUSING','yaw'),('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','pitch')]:
   q=D.getObject(hn).Shape.copy()
   if kind=='pitch':q.rotate(V(-135,0,121),V(0,1,0),p)
   q.rotate(V(-106,0,127),V(0,0,1),y)
   for n in pi:check(n,D.getObject(n).Shape,hn,q,{'yaw':y,'pitch':p})
 put('final-current-delta-gates.json',{'rows':rows,'failures':[r for r in rows if r['clear_scoped'] is False],'continuous_motion_PASS':False})
 names=['PBAY_F_HP','PBAY_F_TY','Battery_GEA223S30X6GT','S0_body','S0_key','XT60H_mated_with_boots','F0_FHAC0002_30A','PBAY_POST_F0','PBAY_F_PI','PBAY_P_SYS','PBAY_F_AUX','PBAY_P_REAR','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','WAGO615_power_0_0','WAGO615_power_0_1']
 names += [o.Name for o in D.Objects if o.Name.startswith(('Motor_ATO4A','NIGHT_INLINE_')) and o.ViewObject.Visibility and hasattr(o,'Shape')]
 for n in pi+['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER']:
  s=D.getObject(n).Shape
  for name in names:
   q=D.getObject(name)
   if not q:continue
   matched=n.startswith('RG_REAR') and name in ['F0_FHAC0002_30A','PBAY_POST_F0']
   check(n,s,name,q.Shape,'currentchangedinterfaces',matched)
 # New actualfullsteel, PCBbores and complete source-neighbor cull.
 for o in D.Objects:
  if not o.Name.startswith('FS_PI_'):continue
  for i,q in enumerate(D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids):
   if low(o.Shape,q)<1.25:check(o.Name,o.Shape,'WAVEGOsolid'+str(i),q,'newfullsteel/sourceonlycandidate')
  if o.Name.endswith('_M2p5x12_full'):
   check(o.Name,o.Shape,'Pi4B_actual_PCB',D.getObject('Pi4B_actual_PCB').Shape,'actualprimarybore',True)
   # Realdriver fromouterportface, beforeinlineFL+latecovers. Full shaft phase.
   b=o.Shape.BoundBox;x=(b.XMin+b.XMax)/2;z=(b.ZMin+b.ZMax)/2
   tool=Part.makeCylinder(3,25,V(x,-96,z),V(0,1,0))
   for hn in ['MG92B_Head_yaw','MG92B_Head_pitch','NIGHT_INLINE_FL_W041','NIGHT_INLINE_FL_W026']:
    check(o.Name+'_driver',tool,hn,D.getObject(hn).Shape,'Pi initialdriver fromside beforelateclosures')
 put('final-current-delta-gates.json',{'rows':rows,'failures':[r for r in rows if r['clear_scoped'] is False],'continuous_motion_PASS':False,'primaryonly':'componentreservation at4catalogmounts notexactSMDpressure proof; actualannulusFIT3','reargapF0':D.getObject('F0_FHAC0002_30A').Shape.distToShape(D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape)[0]})
 # One connected curved route premise using current realproject endpoint.
 # No borrowedunit/end10 reduction; finite analytical lengths notwirePASS.
 R=13.5
 def unit(v):v=V(v);v.normalize();return v
 def rot(v,o,axis,a):return o+A.Rotation(axis,a).multVec(v-o)
 def pose(v,y,p):return rot(rot(v,V(-135,0,121),V(0,1,0),p),V(-106,0,127),V(0,0,1),y)
 lengths=[]
 for y,p in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
  ps=[pose(V(-193.35,0,121.1),y,p),pose(V(-174.35,0,121.1),y,p),rot(V(-150,-22,92),V(-106,0,127),V(0,0,1),y),V(-123,-87,94.5),V(-100,-87,94.5)]
  seg=[(b-a).Length for a,b in zip(ps,ps[1:])];cuts=[];angles=[]
  for i in range(1,len(ps)-1):
   u=unit(ps[i]-ps[i-1]);v=unit(ps[i+1]-ps[i]);a=math.acos(max(-1,min(1,u.dot(v))));angles.append(a);cuts.append(R*math.tan(a/2))
  remaining=[s-(cuts[i-1] if i else 0)-(cuts[i] if i<len(cuts) else 0) for i,s in enumerate(seg)]
  L=sum(seg)-2*sum(cuts)+R*sum(angles)+math.pi*R
  lengths.append({'yaw':y,'pitch':p,'arcR':R,'exact_center_route':L,'ends_once':10,'center_plus10':L+10,'remaining_same200_center':190-L,'straight_corners_fit':min(remaining)>=0,'stock_fromwhole_width_twist':'UNRECEIVED; centerL is NOT physicalFFCdebitupper','pose_knots':[list(v) for v in ps]})
 put('current-FFC200-connected-route-premise.json',{'single_selected_unit':200,'end_project_once':10,'fullprofile':[16.8,1.8],'center_R13p5_keepsallocated_inner_R12p5':True,'source_camera_C0':[-206.85,0,134.6],'Pi_end':[-86.5,-73.5,94.5],'lastquarter':'XY atZ94.5 from(-100,-87) to(-86.5,-73.5), widthZ matchesnewnominalCSIrow; actualcontactsidemouthFIT3','rows':lengths,'actual_continuous_family_or_space_PASS':False,'required_next_qualification':'fullflatnormals/twist/currentcasepinches + usable200surplus, notcenterlengthonly; ToF4xOD2.1/R31.5 andJR groups remainconnectedmotionOPEN','no_otherunit_borrow':True})
 print(json.dumps({'checks':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'FFC_center_plus10':[min(r['center_plus10'] for r in lengths),max(r['center_plus10'] for r in lengths)]}))
run()
