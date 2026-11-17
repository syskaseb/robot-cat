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
   boss=box(-146,y-2.9,z-3.5,12,5.8,7)
   rib=box(-146,46.1 if y>0 else -63,z-2,12,16.9,4).common(outer)
   back=back.fuse(boss).fuse(rib)
   bore=Part.makeCylinder(1.15,23,V(-155,y,z),V(1,0,0));back=back.cut(bore)
   metal('HC_BACK_'+str(y)+'_'+str(z),[-152.5,y,z],[1,0,0],25)
   mounts.append({'axis':[y,z],'actual_arm_contact_X':-146,'frame_bore_extent':[-152,-146],'boss_end':-134,'nominal_head_under_X':-152.5,'L':25,'tip':-127.5,'nut_end':-131.9,'tip_beyond':4.4})
 # Two front/back complete throughsets; no twelve cosmetic mounts.
 for y in [-52,52]:
  z=181;front=front.fuse(box(-225,y-4.5,z-4.5,20,9,9));back=back.fuse(box(-205,y-4.5,z-4.5,5,9,9))
  bore=Part.makeCylinder(1.15,33,V(-228,y,z),V(1,0,0));front=front.cut(bore);back=back.cut(bore);metal('HC_FRONT_'+str(y),[-225.5,y,z],[1,0,0],30)
 # Actual shallow matching lip, not interpenetration of the two prints.
 lipout=fuse([ell(*s[:3],*[r-1.85 for r in s[3:]]) for s in lobes[:2]])
 lipin=fuse([ell(*s[:3],*[r-3.0 for r in s[3:]]) for s in lobes[:2]])
 lip=lipout.cut(lipin).common(box(-207,-95,60,3.5,190,180));ledge=outer.cut(lipin).common(box(-205,-95,60,1.5,190,180))
 back=back.fuse(lip).fuse(ledge).cut(cam).cut(tof)
 front=front.removeSplitter();back=back.removeSplitter();obj('HC_FRONT_HOLLOW_MASK',front);obj('HC_BACK_HOLLOW_EARS_SOCKET',back)

 # Rectangular bearing bosses replace exactly the invalid cylindrical/rib junctions.
 # No face deletion/healing and no source actuator/optics move.
 rows=[]
 for n,z,h in [('HC_BACK_LOWER',50,84),('HC_BACK_UPPER',134,120)]:
  q=back.common(box(-280,-110,z,170,220,h)).removeSplitter();obj(n,q);rows.append({'name':n,'valid':q.isValid(),'solids':len(q.Solids),'volume':q.Volume})
 D.getObject('HC_BACK_HOLLOW_EARS_SOCKET').ViewObject.Visibility=False
 for y in [-49,49]:
  for z in [110,146]:
   pre='HC_BACK_'+str(y).replace('-','_')+'_'+str(z)
   D.getObject(pre+'_nutwasher').Shape=Part.makeCylinder(2.5,.5,V(-134,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,.52,V(-134.01,y,z),V(1,0,0)))
   pts=[V(-133.5,y+4/math.sqrt(3)*math.cos(k*math.pi/3),z+4/math.sqrt(3)*math.sin(k*math.pi/3)) for k in range(6)]
   D.getObject(pre+'_fullnut').Shape=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(1.6,0,0)).cut(Part.makeCylinder(1.025,1.62,V(-133.51,y,z),V(1,0,0)))
 for y in [-52,52]:
  pre='HC_FRONT_'+str(y).replace('-','_');z=181
  D.getObject(pre+'_nutwasher').Shape=Part.makeCylinder(2.5,.5,V(-200,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,.52,V(-200.01,y,z),V(1,0,0)))
  pts=[V(-199.5,y+4/math.sqrt(3)*math.cos(k*math.pi/3),z+4/math.sqrt(3)*math.sin(k*math.pi/3)) for k in range(6)]
  D.getObject(pre+'_fullnut').Shape=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(1.6,0,0)).cut(Part.makeCylinder(1.025,1.62,V(-199.51,y,z),V(1,0,0)))
 f=D.getObject('FC_F_NEG');q=f.Shape.fuse(box(78,-116,101,2,8,8)).removeSplitter();f.Shape=q
 D.recompute();D.save()
 put('head-bearing-junction-completion.json',{'parts':rows,'front':[front.isValid(),len(front.Solids)],'rear_parting_common':D.getObject('HC_BACK_UPPER').Shape.common(D.getObject('HC_BACK_LOWER').Shape).Volume,'negative_cowl_connected':[q.isValid(),len(q.Solids)],'sourceposes':'unchanged','change':'Purposeful rectangular complete bearing bosses in place of invalid cylinder/rib contact; actual throughholes/fullsteel retained. Negative side lip connected by full2x8x8web.','seconds':time.perf_counter()-t})
 print(rows,q.isValid(),len(q.Solids),time.perf_counter()-t)
run()
