import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cy(x,y,z,r,h,a=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),a)
def ell(x,y,z,rx,ry,rz):
 m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(x,y,z));return s
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 if D.getObject('OLA_REAL_FRONT_MASK'):return print('mask already built')
 t=time.perf_counter();gr=D.addObject('App::DocumentObjectGroup','HEAD_SOURCE_SENSORS_AND_REAL_MASK');parts=[];check=[];fast=[]
 def add(n,s,col=(.1,.105,.12),visible=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=visible;gr.addObject(o);return o
 def metal(n,p,a,L,protr):
  u=V(0,1,0) if abs(a.x)>.9 else V(1,0,0);v=a.cross(u);np=p+a*(L-protr-1.6);rad=4/math.sqrt(3);pts=[np+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*rad for k in range(6)];nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*1.6).cut(Part.makeCylinder(1,1.62,np-a*.01,a))
  for tag,s in [('fullM2x'+str(L),Part.makeCylinder(1,L,p,a).fuse(Part.makeCylinder(1.9,2,p-a*2,a))),('upperwasher',Part.makeCylinder(2.5,.3,p,a).cut(Part.makeCylinder(1.1,.32,p-a*.01,a))),('lowerwasher',Part.makeCylinder(2.5,.3,np-a*.3,a).cut(Part.makeCylinder(1.1,.32,np-a*.31,a))),('fullnut',nut)]:add(n+'_'+tag,s,(.7,.71,.75))
  fast.append(dict(role=n,M2_length=L,fullnut=True,washer2=True,protrusion=protr,stock='NEEDED_UNCONFIRMED'))
 # Correct completecaptiveretainerstack: flatfullnut itself bears the roof;
 # lowerwasher withdrawn from this UNBUILT demand. Originalfactory screw untouched.
 for o in list(D.Objects):
  if not o.Name.startswith('YAW_FIXED_CAP_'):continue
  if o.Name.endswith('_nutwasher'):D.removeObject(o.Name)
  elif o.Name.endswith('_fullnut'):
   s=o.Shape.copy();s.translate(V(0,0,-1.5));o.Shape=s;o.Label='YAW_FIXED_CAP fullnut roof133.7; no lowerwasher/wholebearingfunction'
 # PrimaryPCB coordinates: u->-Y,v->Z,n->-X. All former installationfields
 # retained as explicit analytic capacity references, not catalogPCB material.
 rot=A.Rotation(V(0,1,0),-90)*A.Rotation(V(0,0,1),-90)
 def tr(s,p):
  q=s.copy();q.rotate(V(),rot.Axis,math.degrees(rot.Angle));q.translate(V(*p));return q
 camera=box(0,0,0,25,24,1.12)
 for u in [2,23]:
  for v in [2,14.5]:camera=camera.cut(cy(u,v,-.01,1.1,1.14))
 oldcam=D.getObject('Camera3_NoIR_Wide');keep=box(-242,-12.5,150.6,12.4,25,24);add('CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT',keep,(.35,.5,.7),False);oldcam.Shape=tr(camera,(-229.6,12.5,150.6));oldcam.Label='Camera3 primaryPCB4holes / wholeposechosen forcentralforehead / fullcapacity retained'
 add('CAMERA_SOURCE_OPTICAL_WINDOW_REFERENCE',cy(-230.72,0,165,3.475,11.28,V(-1,0,0)),(.04,.04,.045))
 ts=Part.Shape();ts.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/reference/component-selection-2026-09-22/vl53l5cx-pololu-3417.step');planes=[]
 for f in ts.Faces:
  b=f.BoundBox
  if b.ZLength<1e-5 and f.Area>80:planes.append(b.ZMin)
 assert planes;datum=min(planes);tof=D.getObject('VL53L5CX');tof.Shape=tr(ts,(-247+datum,6.35,114));tof.Label='Pololu3417 actualsourceSTEP / primary2mounts not8electricalholes'
 add('TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT',box(-252,-13,110,14,26,26),(.35,.5,.7),False)
 # Actualsource sensorframe holes alreadylocated; twoopposedCAMclamps plusfourpads.
 for y in [-10.5,10.5]:
  for z in [152.6,165.1]:add('CAM_standoff_'+str(y)+'_'+str(z),cy(-229.6,y,z,2,5,V(1,0,0)).cut(cy(-229.61,y,z,1.1,5.02,V(1,0,0))),(.7,.71,.75))
  metal('CAM_primary_upper_'+str(y),V(-231.02,y,165.1),V(1,0,0),12,.68)
 for z in [116.54,129.24]:add('TOF_standoff_'+str(z),cy(-247,-3.81,z,2,3,V(1,0,0)).cut(cy(-247.01,-3.81,z,1.1,3.02,V(1,0,0))),(.7,.71,.75));metal('TOF_primary_'+str(z),V(-248.32,-3.81,z),V(1,0,0),10,.78)
 # RealL parting of the EXISTING ownfrontwings; backspine remains integral.
 frame=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE');oldframe=frame.Shape.copy()
 for y in [34,-53]:frame.Shape=frame.Shape.cut(box(-224.61,y,126.5,3.01,19,43))
 # Sourcebased continuous FOV fields: camera opticalwindowØ6.95+0.525radial
 # covers the 12..12.4 axial installation uncertainty (.4*tan51<.525).
 def frustum(x,y,z,w,h,H,VV):
  wires=[]
  for xx in [x,-285]:
   dx=x-xx;u=w+dx*math.tan(math.radians(H/2));v=h+dx*math.tan(math.radians(VV/2));wires.append(Part.Wire(Part.makePolygon([A.Vector(xx,y-u,z-v),A.Vector(xx,y+u,z-v),A.Vector(xx,y+u,z+v),A.Vector(xx,y-u,z+v),A.Vector(xx,y-u,z-v)]).Edges))
  return Part.makeLoft(wires,True,False)
 camf=frustum(-242,0,165,4,4,102,67);toff=frustum(-249.62,0,122.89,6.85,9.39,45,45);add('CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL',camf,(.8,.6,.2),False);add('TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL',toff,(.8,.6,.2),False)
 main=ell(-191,0,145,58,72,62);neck=ell(-152,0,137,20,52,36);outer=main.fuse(neck);inner=ell(-191,0,145,55.6,69.6,59.6).fuse(ell(-152,0,137,17.6,49.6,33.6))
 cheeks=[ell(-245,y,127,11,17,13) for y in [-15,15]];ci=[ell(-245,y,127,8.6,14.6,10.6) for y in [-15,15]];outer=fu([outer]+cheeks);inner=fu([inner]+ci);head=outer.cut(inner).cut(camf).cut(toff)
 # Honestoperating rearneck opening; fixed overlapguard/bodyclosure NOTqualified here.
 neckpass=cy(-126,0,90,20,100);head=head.cut(neckpass)
 front=head.common(box(-280,-100,70,68,200,160));back=head.common(box(-212,-100,70,120,200,160));fb=[];bb=[];fbc=[];bbc=[]
 for y in [-49,49]:
  for z in [130,166]:
   boss=cy(-245,y,z,4.5,23.4,V(1,0,0)).common(outer);fb.append(boss);fbc += [cy(-231,y,z,1.1,16,V(1,0,0)),box(-226.0,min(y,35 if y>0 else -35)-2.3,z-2.1,1.8,abs(y-(35 if y>0 else -35))+4.6,4.2)]
   rearboss=cy(-166,y,z,4.5,30,V(1,0,0)).common(outer);bb.append(rearboss);bbc += [cy(-170,y,z,1.1,18,V(1,0,0)),box(-161.4,min(y,35 if y>0 else -35)-2.3,z-2.1,1.8,abs(y-(35 if y>0 else -35))+4.6,4.2)]
   metal('FRONT_MASK_'+str(y)+'_'+str(z),V(-218.3,y,z),V(-1,0,0),8,.4);metal('BACK_COVER_'+str(y)+'_'+str(z),V(-169.3,y,z),V(1,0,0),10,.4)
 front=fu([front]+fb).common(box(-280,-100,70,68,200,160));back=fu([back]+bb)
 # Matchingcase receiverclearance; realcontactplanes remain at-221.6/-166.
 for y in [-49,49]:
  for z in [130,166]:
   clear=box(-221.59,y-2.2,z-2.2,55.6,4.4,4.4);front=front.cut(clear);back=back.cut(clear)
 for q in fbc:front=front.cut(q)
 for q in bbc:back=back.cut(q)
 # Seam alignmenttongue is actualseparatepartgeometry, not virtual detach.
 lipout=ell(-191,0,145,55.3,69.3,59.3).fuse(ell(-152,0,137,17.3,49.3,33.3));lipin=ell(-191,0,145,54.1,68.1,58.1).fuse(ell(-152,0,137,16.1,48.1,32.1));lip=lipout.cut(lipin).common(box(-214,-100,70,3.5,200,160));ledge=outer.cut(lipin).common(box(-212,-100,70,1.5,200,160));back=fu([back,lip,ledge]).cut(neckpass).cut(camf).cut(toff)
 for n in ['CLOSED_HEAD_LOWER','CLOSED_HEAD_UPPER']:
  o=D.getObject(n);o.ViewObject.Visibility=False;o.Label='RETIRED priorheadshell / actualfrontmask+backcover replaces'
 fronto=add('OLA_REAL_FRONT_MASK',front);backo=add('OLA_REAL_BACK_COVER',back);parts.extend([fronto,backo])
 # Paired3Ddecorativeeyes; no LED/electricalextras. Realopticalfields subtractallcosmetics.
 for sy,n in [(-1,'Ola_eye_gold__1'),(1,'Ola_eye_gold_1')]:
  y=31*sy;rim=ell(-243.5,y,151,4.5,14,15).cut(ell(-243.6,y,151,4.7,10.5,11.5)).cut(camf).cut(toff);D.getObject(n).Shape=rim;D.getObject(n).ViewObject.Visibility=True;D.getObject(n).ViewObject.ShapeColor=(.8,.55,.12)
  add('DECORATIVE_BLACK_EYE_'+str(sy),ell(-244,y,151,4.4,10.4,11.4).cut(camf).cut(toff),(.025,.028,.032))
 nose=ell(-254,0,140.5,4,6,3.2).cut(camf).cut(toff);n=D.getObject('Ola_nose');n.Shape=nose;n.ViewObject.Visibility=True;n.ViewObject.ShapeColor=(.10,.075,.065)
 # Existingears/legs unchanged actualgeometry. No image generation/hiddenprotrusions.
 D.Label='DAY16 HEAD TAIL CONTINUOUS NOMINAL + OLA 3D FACE / OPEN FIT3';D.recompute();D.save();G.getDocument(D.Name).Modified=False
 r=dict(utc=datetime.now(timezone.utc).isoformat(),wholemodule_changes=dict(camera_full_capacity=[[-242,-12.5,150.6],[12.4,25,24]],camera_PCBback=-229.6,lensaxis=[-242,0,165],CSI_exit='rear+X/bottomedge provisional contactfacing/stockFIT3, actualplate17x10openfeed',ToF_full14x26x26_retained=[[-252,-13,110],[14,26,26]],ToF_actualPCBbottomface=-247,ToF_actualPCBplane_from_source=datum,ToF_two_actualmounts=[[-247,-3.81,116.54],[-247,-3.81,129.24]],all_affected='headplate/sourceCAM/ToFmouths/header/CSI/reach/skinFOV new; oldsourcewirelength NOcredit; no unrelatedboardmove'),FOV=dict(camera=[102,67],primary_opticalwindow6p95=True,project_nearaperture8=True,source_axial12to12p4_uncertainty_covered=True,ToF=[45,45],nearwholePCB12p7x17p78_plusmargin1=True,both_TX_RX_open=True),parts=[dict(name=o.Name,valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume=o.Shape.Volume) for o in parts],front_back_common=front.common(back).Volume,fasteners=fast,cosmetics='coherenthollow3Dcheeks/muzzle andpaireddecorativeeyes; no LED/noopaqueIRglass',rear_neck_overlap_guard_OPEN=True,ear_mounts_to_newcover_OPEN=True,front_back_receiver_contacts_and_screwfeed_needsfinalscope=True,physical_pass=False,wholekit_ready=False,actual_fit_cut_slack=None,seconds=time.perf_counter()-t,objects=len(D.Objects));wr('mask-sensor-realization.json',r);print(json.dumps(dict(saved=D.FileName,parts=r['parts'],frontbackcommon=r['front_back_common'],seconds=r['seconds'],objects=r['objects'])))
run()
