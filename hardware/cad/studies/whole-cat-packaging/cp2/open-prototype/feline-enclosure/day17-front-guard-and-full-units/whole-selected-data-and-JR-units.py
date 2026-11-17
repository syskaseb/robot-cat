import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;X=V(1,0,0);Z=V(0,0,1)
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def unit(v):v=V(v);v.normalize();return v
def add(n,s,c=(.3,.5,.85),scope='CONNECTED_OCCUPIED_FLEX_GROUP_NOT_PRINT_NOT_MASS'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.Transparency=45;o.ViewObject.Visibility=True
 if not hasattr(o,'Scope'):o.addProperty('App::PropertyString','Scope')
 o.Scope=scope;return o
def Sshape(P0,P1,N=24):
 diff=P1-P0;dx=diff.x;v=diff-X*dx;h=v.Length;v=unit(v);r=(dx*dx+h*h)/(4*h);a=math.acos(1-h/(2*r));out=[]
 for i in range(N+1):
  t=a*i/N;out.append((P0+X*r*math.sin(t)+v*r*(1-math.cos(t)),X*math.cos(t)+v*math.sin(t)))
 B=out[-1][0]
 for i in range(1,N+1):
  t=a*i/N;out.append((B+X*r*(math.sin(a)-math.sin(a-t))+v*r*(math.cos(a-t)-math.cos(a)),X*math.cos(a-t)+v*math.sin(a-t)))
 return out,2*r*a,r

def tube(ss,r):
 ws=[Part.Wire([Part.makeCircle(r,c,unit(t))]) for c,t in ss];return Part.makeLoft(ws,True,True)
def datarecipe(r):
 P0=V(-12,-.66,151.1);B=V(-11.89,-10.73,154.3);E=V(52,-20.33,154.3-r);ss,L,R0=Sshape(P0,E)
 for i in range(1,97):
  u=i/96;a=-math.pi/2+3*math.pi*u;y=-20.33+9.6*(3*u*u-2*u*u*u);d=9.6*(6*u-6*u*u)/(3*math.pi)
  ss.append((V(52+r*math.cos(a),y,154.3+r*math.sin(a)),V(-r*math.sin(a),d,r*math.cos(a))))
 start=ss[-1][0];Q=V(B.x+r,B.y,154.3+r);Lline=(Q-start).Length
 for i in range(1,10):ss.append((start+(Q-start)*i/9,-X))
 for i in range(1,25):
  a=math.pi/2*i/24;ss.append((V(B.x+r-r*math.sin(a),B.y,154.3+r*math.cos(a)),V(-math.cos(a),0,-math.sin(a))))
 coillower=3*math.pi*r;coilupper=coillower+(.4*9.6**2/math.pi)/(2*r)
 return ss,L+coilupper+Lline+math.pi*r/2+52,{'entry_exact_L':L,'entry_R':R0,'coil_L_upper':coilupper,'return_straight':Lline,'return_R':r,'return_arc_L':math.pi*r/2,'both_full_project26enddebits_once':52,'sourcePi_boot_exit':list(P0),'sourceBUS_port_true_face':[-11.89,-10.73,128.3],'BUS_full26boot_exit':list(B)}
D.save();lo=30.;hi=32.
for i in range(45):
 mid=(lo+hi)/2
 if datarecipe(mid)[1]>500:hi=mid
 else:lo=mid
r=(lo+hi)/2;ss,L,m=datarecipe(r);shape=tube(ss,2.9);o=add('FU17_DATA500_WHOLE_OCCUPIED',shape)
# ActualfullBUSUSB-C sourcecomponent, notinvalid117aggregate.
part=Part.Shape();part.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/full-cat/pi-bus-primary-r1/Type_C1.brep');part.Placement=A.Placement(V(-44,-11.9,127.5),A.Rotation(V(1,0,0),-90)).multiply(part.Placement);add('FU17_SOURCE_BUS_TypeC_NO_EXTRA_BOM',part,(.65,.65,.68),'SOURCE_SELECTED_BUS_COMPONENT_NO_EXTRA_BOM')
boot=Part.makeBox(26,26,26,V(-24.89,-23.73,128.3));add('FU17_BUS_DATA_FULL26_BOOT_PROJECT',boot,(.45,.5,.65),'PROJECT_FULL_INSTALLATION_not_mfg_mould_not_literalplastic')
put('whole-DATA500-actual-unit-and-capacity.json',{'unit':'oneLanbergCA-USBO-10CU-0005-BK500; notPOWERDelock','chosen_closed_unit_radius':r,'source_fixed_R_centerline':30,'source_jacket_radius':2.5,'occupied_radius_with_margin':2.9,'nominal_whole_upper':L,'entry_and_coil_and_return':m,'coil_Y_shift':9.6,'minimum_interlap_separation':9.6*20/27,'interlap_occupied_clearance':9.6*20/27-5.8,'coil_R_lower_bound_including_smooth_axial_shift':r/(1+((6*9.6/(3*math.pi)**2)**2+(1.5*9.6/(3*math.pi))**2)/r**2)**.5,'valid':shape.isValid(),'solids':len(shape.Solids),'occupied_bounds':str(shape.BoundBox),'source_BUSB_port':'actualprimaryType_C1 22solids/localboarddatum -44,-11.9,127.5 Rx-90; TypeC sourcefrontlocalY-.804 =>worldZ128.304','26boot':'currentlargerfull26cube notsmaller15x9; actualmould/engagement/500lengthreferenceonephysicalPi+BUS+Lanberg sample. Notmfgportnormalproof','sourcecenterline_minR_notinner_radius':True,'same500_no_trim_no_extraunit':True,'actualcut':None,'physicalPASS':False})
# Sourceactual3wirestub freeendpoint+11.45debitalreadywithin250.
stubs={}
for n in ['MG92B_Head_yaw','MG92B_Head_pitch']:
 o=D.getObject(n);f=[]
 for face in o.Shape.Faces:
  c=face.Surface
  if isinstance(c,Part.Cylinder) and abs(c.Radius-.6)<1e-5:f.append({'center':list(c.Center),'axis':list(c.Axis),'bounds':str(face.BoundBox)})
 stubs[n]=f
put('actual-head-servo-wirestub-source.json',stubs)
# Completefactoryyaw250reference: Slead+onebroadhalfloop, no factorytrim.
def yawrecipe(r):
 ss,L,R=Sshape(V(-95.5,0,53.2),V(18,0,157-r));N=48
 for i in range(1,N+1):
  u=i/N;a=-math.pi/2+math.pi*u;y=3*(3*u*u-2*u*u*u);dy=3*(6*u-6*u*u)/math.pi
  ss.append((V(18+r*math.cos(a),y,157+r*math.sin(a)),V(-r*math.sin(a),dy,r*math.cos(a))))
 return ss,L+math.pi*r+.4*3**2/math.pi/(2*r)+11.45+15,R
lo=20.;hi=28.
for i in range(44):
 mid=(lo+hi)/2
 if yawrecipe(mid)[1]>250:hi=mid
 else:lo=mid
r=(lo+hi)/2;ys,YL,RY=yawrecipe(r);ws=[]
for c,t in ys:
 t=unit(t);w=unit(V(t.z,0,-t.x));n=unit(t.cross(w));a=w*3.55;b=n*1.45;ws.append(Part.Wire(Part.makePolygon([c-a-b,c+a-b,c+a+b,c-a+b,c-a-b]).Edges))
yshape=Part.makeLoft(ws,True,True);add('FU17_FACTORY_YAW250_GROUP_FULL',yshape,(.6,.45,.2));end=ys[-1][0];dock=Part.makeBox(30,14,10,end+V(-30,-7,-5));add('FU17_C_HY_EXISTING_BODY_MATE_ALLOWANCE',dock,(.7,.5,.3),'EXISTING_C_HY_TERMINATION_DOCK_nominalfullmate_notnewconnector_not_verifiedmould')
put('factoryJR-whole250-300-plan.json',{'yaw_fixed_case':{'source_stub_free_end':[-95.5,0,53.2],'case_stub_consumption':11.45,'factory_keyed_end_budget':15,'whole250upper':YL,'S_R':RY,'bight_center_R':r,'inner_R_profile_lower':r-3.55,'full_factory_retained':True,'dock':list(end),'dock_role':'C_HYexistingbodytermination/XB12protectedV+,XB13G_AUX4,XS13R1; no directunfusedPCApower/no newmatesinvented. Existingmatingbindingphysicalcheckbeforeclosure','valid':yshape.isValid()},'pitch_yaw_only_case':{'actual_nominal_stub_free_end':[-135,-43.8,131.5],'case_stub_consumption':11.45,'early_bend':'projectR20 outwardrotateswithyaw BEFOREPiPOWERbed; flat3wiresectionXwidth7.1,Ythickness2.9. Fullcurrentrange±20','existing_pitch_JR300':1,'source_JR250':1,'source_aliases_fixed_joins':['XB23','XB22','XS23'],'lap_each':8,'sleeve_each':20,'new_electrical_joins':0,'planned_fixed_dock':[-22,-60,175],'full_factory250_motionplan':'region + actualcorrelatedupper next; not inheritedoldaxes','300_far_board_trim':'ONLYexistingphase2afterFIT, preservefullJRmatingplug andfactorykeyed250; no actualcut'},'factory_and_extension_are_distinct':True,'actualcuts':None,'physicalPASS':False})
D.recompute();D.save();print(json.dumps({'DATA_R':m,'whole500':L,'DATAvalid':shape.isValid(),'yaw_R':r,'yawwhole':YL,'yaw_valid':yshape.isValid()}))
