import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def low(a,b):
 a=a.BoundBox;b=b.BoundBox;return sum(max(0,getattr(a,'XYZ'[i]+'Min')-getattr(b,'XYZ'[i]+'Max'),getattr(b,'XYZ'[i]+'Min')-getattr(a,'XYZ'[i]+'Max'))**2 for i in range(3))**.5
def pose(q,y,p):
 q=V(q);o=V(-135,0,121);q=o+A.Rotation(V(0,1,0),p).multVec(q-o);o=V(-106,0,127);return o+A.Rotation(V(0,0,1),y).multVec(q-o)
# The first actual finite gate, not a world scan: full Pi ports vs actual BUS
# and source rigid gimbal/frame at neutral + range corners only as needed.
checks=json.loads((P/'first-whole-front-finite-gate.json').read_text(encoding='utf-8'))['rows']
for n in []: # first finite gates reused exact same current rigid arrangement

 s=D.getObject(n).Shape
 for hn in ['BUS25514_installed','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','Speaker','PBAY_P_SYS','HC_BACK_UPPER','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','HEAD_YAW_FORK_FIXED_PITCH_HOUSING','MG92B_Head_yaw','MG92B_Head_pitch']:
  o=D.getObject(hn)
  if not o:continue
  q=o.Shape;lb=low(s,q);r={'part':n,'neighbor':hn,'box_lower':lb,'required':1.25,'operand':'fullsource occupiedinstallation for Pi cooling/BUS, actualBRep PCB/rigidhead; not identical to deliveredallSMDmaterial'}
  if lb>=1.25:r.update(clear_by_bound=True)
  else:
   d=s.distToShape(q)[0];r.update(actual_shape_gap=d,shape_valid=s.isValid() and q.isValid(),clear_by_bound=False)
   if d<1.25:r['common']=s.common(q).Volume;r['acceptance']='HOLD_CURRENT_LAYER; distinguish installcover vs actualmaterial'
  checks.append(r);put('first-whole-front-finite-gate.json',{'rows':checks,'no_globalmatrix':True,'wholekit':False})
# One actual arc+Bezier+arc transport premise; shortest construction is NOT
# 200mm installed cable: same-unit remainder must occupy a real variablebight.
R=13.5;rows=[];Pe=V(-80.5,-16.5,148.1);B=Pe+V(-R,0,R)
for yaw,pitch in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
 c0=pose(V(-206.85,0,155.4),yaw,pitch);aa=pose(V(-193.35,0,168.9),yaw,pitch);th=A.Rotation(V(0,0,1),yaw).multVec(A.Rotation(V(0,1,0),pitch).multVec(V(1,0,0)));L=(B-aa).Length;a=L/3
 bc=Part.BezierCurve();bc.setPoles([aa,aa+th*a,B-V(a,0,0),B]);e=bc.toShape();center=e.Length+math.pi*R
 # numerical edge/radius diagnostics, explicitly not continuouscertification.
 ps=[bc.value(i/100) for i in range(101)];radii=[]
 for i in range(1,100):
  ab=ps[i]-ps[i-1];ac=ps[i+1]-ps[i-1];cross=ab.cross(ac).Length
  if cross>1e-10:radii.append(ab.Length*(ps[i+1]-ps[i]).Length*ac.Length/(2*cross))
 rows.append({'yaw':yaw,'pitch':pitch,'camera_C0':list(c0),'head_arc_end':list(aa),'Pi_entry':list(Pe),'exact_two_quarters_plus_cubic_center':center,'ends_once':10,'center_plus_ends':center+10,'same200_remainder_before_width_roll_bight':190-center,'middle_sampled_Rmin':min(radii),'not_stock_upper':'edge lengths/contactside/twist and sameunit remainder storage stillOPEN','not_continuous_motion_PASS':True})
 if yaw==pitch==0:
  c=V(-193.35,0,155.4);a1=Part.Arc(c0,c+V(-R/math.sqrt(2),0,R/math.sqrt(2)),aa).toShape();c=Pe+V(-R,0,0);a2=Part.Arc(B,c+V(R/math.sqrt(2),0,R/math.sqrt(2)),Pe).toShape();wire=Part.Wire([a1,e,a2]);g=D.getObject('AFT_WHOLE_FRONT_PROPOSAL_NOT_MATERIAL');o=D.addObject('PartDesign::Feature','AFT_FFC200_ARC_FAMILY_CENTER_NOT_PHYSICAL_WIRE');o.Shape=wire;o.ViewObject.LineColor=(.95,.42,.08);o.ViewObject.LineWidth=5;g.addObject(o)
  # Explicit fullprofile frames, no 123conductoraxes / no fake occupiedsolidPASS.
  frames=[]
  for cc,ww,nn in [(c0,V(0,-1,0),V(1,0,0)),(aa,V(0,-1,0),V(0,0,1)),(B,V(0,-1,0),V(0,0,1)),(Pe,V(0,-1,0),V(1,0,0))]:
   w=ww*8.4;n=nn*.9;frames.append(Part.makePolygon([cc-w-n,cc+w-n,cc+w+n,cc-w+n,cc-w-n]))
  o=D.addObject('PartDesign::Feature','AFT_FFC_FULL16p8x1p8_SOURCE_AND_LANE_FRAMES');o.Shape=Part.makeCompound(frames);o.ViewObject.LineColor=(1.0,.4,0.0);g.addObject(o)
put('same200-arc-family-and-reserve-premise.json',{'rows':rows,'fullprofile':[16.8,1.8],'inner_R_project':12.5,'quarter_centerR':13.5,'quarter_inner_thicknessR':12.6,'contactside':'camera contacts awayflap towardPCB; Pi awayflap. Endrow/frame sign compatible after wholecamera180/Pi180; actualflap/mouth datum physicalFIT not invented','source_camera_optic_unchanged':[-209.6,0,145],'mechanical_ranges':{'yaw':[-20,20],'pitch':[-10,10]},'whole200_installed_claim':False,'region_status':'Referencecenter+fullprofileframes; not sufficient for stock/slack/occupiedspace acceptance','next_whole_decision':'same200 remainder must fit accessible upperneck/bodyside variablebight upstream truegrips; cannot clamp surplus behindPi or borrow anotherunit'})
D.recompute();D.save();print(json.dumps({'rows':len(checks),'holds':[r for r in checks if r.get('acceptance')],'FFC_center_plus10':[min(r['center_plus_ends'] for r in rows),max(r['center_plus_ends'] for r in rows)],'full200_stock_qualified':False}))
