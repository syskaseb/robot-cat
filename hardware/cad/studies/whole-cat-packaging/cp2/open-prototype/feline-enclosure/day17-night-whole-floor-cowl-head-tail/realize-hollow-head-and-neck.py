import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def ell(x,y,z,rx,ry,rz):
 m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(x,y,z));return s
def fuse(ss):
 q=ss[0]
 for s in ss[1:]:q=q.fuse(s)
 return q
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def obj(n,s,col=(.12,.125,.135)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def metal(n,p,axis,L):
 a=V(*axis);p=V(*p);u=V(0,1,0) if abs(a.x)>.9 else V(1,0,0);v=a.cross(u);np=p+a*(L-2.4)
 def cy(r,h,t):return Part.makeCylinder(r,h,p+a*t,a)
 pts=[np+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*(4/math.sqrt(3)) for k in range(6)]
 shapes=[('M2x'+str(L),cy(1,L,0).fuse(cy(1.9,2,-2))),('headwasher',cy(2.5,.5,0).cut(cy(1.1,.52,-.01))),('nutwasher',cy(2.5,.5,L-2.9).cut(cy(1.1,.52,L-2.91))),('fullnut',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*1.6).cut(cy(1.025,1.62,L-2.41)))]
 for tag,s in shapes:obj(n+'_'+tag,s,(.65,.66,.69))
def run():
 t=time.perf_counter();D.save();cam=D.getObject('CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL').Shape;tof=D.getObject('TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL').Shape
 lobes=[(-181,0,134,62,77,67),(-213,0,166,30,59,43),(-222,-31,118,28,35,30),(-222,31,118,28,35,30),(-237,0,111,17,27,20),(-225,-42,149,15,24,27),(-225,42,149,15,24,27)]
 outer=fuse([ell(*s) for s in lobes]);inner=fuse([ell(*s[:3],*[r-1.6 for r in s[3:]]) for s in lobes])
 ears=[]
 for sy,n in [(-1,'Ola_ear__1'),(1,'Ola_ear_1')]:
  e=D.getObject(n).Shape.copy();e.translate(V(-18,sy*4,25));b=e.BoundBox;c=b.Center;m=A.Matrix();m.A11=.7;m.A22=.84;m.A33=.9;ei=e.copy();ei.translate(-c);ei=ei.transformGeometry(m);ei.translate(c)
  outer=outer.fuse(e);inner=inner.fuse(ei);ears.append({'source':n,'outer_translation':[-18,sy*4,25],'outer_volume':e.Volume,'cavity_volume':ei.Volume,'root_overlap_main':e.common(fuse([ell(*s) for s in lobes[:2]])).Volume})
 # Rear socket is concentric with the actual YAW axis in neutral. Its limited band
 # is a real moving skin, not a fixed torus or a new mechanism.
 yaw=V(-106,0,127);band=box(-151,-85,45,23,170,180)
 socket=Part.makeSphere(70.2,yaw).common(band);outer=outer.fuse(socket)
 inner=inner.fuse(Part.makeSphere(68.6,yaw))
 # Actual rear neck exit; do not leave old opaque solid envelope behind the shell.
 outer=outer.common(box(-280,-100,50,152,200,200));head=outer.cut(inner).cut(cam).cut(tof)
 front=head.common(box(-280,-100,50,75,200,200));back=head.common(box(-205,-100,50,77,200,200))
 # Four actual source arm-end bores X-152..-146, Y±49/Z110,146.
 mounts=[];frame=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Shape.copy()
 for y in [-49,49]:
  for z in [110,146]:
   boss=Part.makeCylinder(2.9,12,V(-146,y,z),V(1,0,0))
   rib=box(-146,46.1 if y>0 else -63,z-2,12,16.9,4).common(outer)
   back=back.fuse(boss).fuse(rib)
   bore=Part.makeCylinder(1.15,23,V(-155,y,z),V(1,0,0));back=back.cut(bore)
   metal('HC_BACK_'+str(y)+'_'+str(z),[-152.5,y,z],[1,0,0],25)
   mounts.append({'axis':[y,z],'actual_arm_contact_X':-146,'frame_bore_extent':[-152,-146],'boss_end':-134,'nominal_head_under_X':-152.5,'L':25,'tip':-127.5,'nut_end':-131.9,'tip_beyond':4.4})
 # Two front/back complete throughsets; no twelve cosmetic mounts.
 for y in [-52,52]:
  z=181;front=front.fuse(Part.makeCylinder(4.5,20,V(-225,y,z),V(1,0,0)));back=back.fuse(Part.makeCylinder(4.5,5,V(-205,y,z),V(1,0,0)))
  bore=Part.makeCylinder(1.15,33,V(-228,y,z),V(1,0,0));front=front.cut(bore);back=back.cut(bore);metal('HC_FRONT_'+str(y),[-225.5,y,z],[1,0,0],30)
 # Actual shallow matching lip, not interpenetration of the two prints.
 lipout=fuse([ell(*s[:3],*[r-1.85 for r in s[3:]]) for s in lobes[:2]])
 lipin=fuse([ell(*s[:3],*[r-3.0 for r in s[3:]]) for s in lobes[:2]])
 lip=lipout.cut(lipin).common(box(-207,-95,60,3.5,190,180));ledge=outer.cut(lipin).common(box(-205,-95,60,1.5,190,180))
 back=back.fuse(lip).fuse(ledge).cut(cam).cut(tof)
 front=front.removeSplitter();back=back.removeSplitter();obj('HC_FRONT_HOLLOW_MASK',front);obj('HC_BACK_HOLLOW_EARS_SOCKET',back)
 # Native surface colour guides: coat geometry, NOT extra bought eyes or printed mass.
 # The printed mask itself has integrated volumetric orbits and cheeks.
 paints=[]
 for sy in [-1,1]:
  y=sy*42;coat=ell(-225,y,149,15.12,24.12,27.12).cut(ell(-225,y,149,15.02,24.02,27.02))
  def aperture(ry,rz):
   m=A.Matrix();m.A11=1;m.A22=ry;m.A33=rz;c=Part.makeCylinder(1,32,V(-250,0,0),V(1,0,0)).transformGeometry(m);c.translate(V(0,y,149));return c
  dark=coat.common(aperture(14.2,16.2)).cut(cam).cut(tof);gold=coat.common(aperture(16.5,18.5)).cut(aperture(14.8,16.8)).cut(cam).cut(tof)
  obj('HC_BLACK_PAINT_GUIDE_'+str(sy),dark,(.012,.014,.018));obj('HC_GOLD_PAINT_GUIDE_'+str(sy),gold,(.72,.48,.1));paints.append({'sy':sy,'dark_volume':dark.Volume,'rim_volume':gold.Volume,'status':'PAINT_SCHEME_NOT_EXTRA_MASS_NOT_STL'})
 # Fixed upper collar: real hollow guard, open underneath for the moving loom.
 # Whole moving socket clear for continuous yaw±20/pitch±10, analytically bounded.
 cap=Part.makeSphere(62,yaw).cut(Part.makeSphere(60.4,yaw)).common(box(-151,-80,154,72.6,160,60))
 for sy in [-1,1]:
  n='FC_F_POS' if sy>0 else 'FC_F_NEG';q=D.getObject(n).Shape
  clearance=Part.makeSphere(71.55,yaw).common(box(-152,-80,50,73.6,160,160));q=q.cut(clearance)
  half=cap.common(box(-155,0 if sy>0 else -90,150,90,90,70));web=box(-82,43 if sy>0 else -47,159,3.6,4,14)
  D.getObject(n).Shape=q.fuse(half).fuse(web).removeSplitter()
 # Retire old unbuilt visual/head-fastener roles only, source actuators/optics unchanged.
 for o in D.Objects:
  if o.Name in ['NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT','OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER','Ola_ear__1','Ola_ear_1','Ola_eye_gold__1','Ola_eye_gold_1','Ola_nose'] or o.Name.startswith(('HN_DECORATIVE_','DECORATIVE_BLACK_EYE','FRONT_MASK_','BACK_COVER_')):o.ViewObject.Visibility=False
 D.recompute();D.save();d=math.hypot(29,6);bound=68.6-62-2*d*math.sin(math.radians(5))
 put('hollow-head-neck-realization.json',{'ears':ears,'back_primary_mounts':mounts,'front_back_common':front.common(back).Volume,'front_valid':front.isValid(),'front_solids':len(front.Solids),'back_valid':back.isValid(),'back_solids':len(back.Solids),'front_volume':front.Volume,'back_volume':back.Volume,'camera_FOV_common':front.common(cam).Volume+back.common(cam).Volume,'ToF_both_optics_common':front.common(tof).Volume+back.common(tof).Volume,'paint_scheme':paints,'paint_not_extra_printmass':True,'bought_parts_pose_changes':[],'ranges':{'yaw':[-20,20],'pitch':[-10,10]},'collar_socket_CONTINUOUS_radial_clearance':bound,'collar_bound_basis':'Rinner68.6 - Rfixed62 - 2*hypot(29,6)*sin(pitch10/2). Yaw preserves centre radius. Only the declared sphere/cap interface, not all head hardware/motion.','full_headframe_hardware_motion_and_tools':'Finite named gate still required','source_horn_centre_and_bearings':'unchanged; no splinefiction/newdrives','source_FFC200_ToF_JR':'regional leading remains OPEN unless subsequent proof','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'front':[front.isValid(),len(front.Solids),front.Volume],'back':[back.isValid(),len(back.Solids),back.Volume],'socket_bound':bound,'seconds':time.perf_counter()-t}))
run()
