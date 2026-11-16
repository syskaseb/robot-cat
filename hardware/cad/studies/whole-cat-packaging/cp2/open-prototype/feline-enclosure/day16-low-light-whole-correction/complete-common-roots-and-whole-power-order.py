import FreeCAD as A,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
ns={};exec(compile((P/'realize-whole-front-and-load-connections.py').read_text().split('# ONE whole front/operator')[0] if False else '','<none>','exec'),ns)
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def add(n,s,k='printed'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(.43,.55,.58) if k=='printed' else (.6,.6,.62)
 if not hasattr(o,'CorrectionScope'):o.addProperty('App::PropertyString','CorrectionScope')
 o.CorrectionScope=k;return o
def hexnut(x,y,z):
 pts=[V(x+3.175*math.cos(i*math.pi/3),y+3.175*math.sin(i*math.pi/3),z) for i in range(6)];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.3,2.6,V(x,y,z-.1)))
def steel(n,x,y,top,L,csk=True):
 s=Part.makeCylinder(1.5,L-1.5 if csk else L,V(x,y,top-L));s=s.fuse(Part.makeCone(1.5,3,1.5,V(x,y,top-1.5))) if csk else s.fuse(Part.makeCylinder(2.75,3,V(x,y,top)))
 add(n+'_fullscrew',s,'steel');add(n+'_washer',Part.makeCylinder(3.5,.5,V(x,y,45.02)).cut(Part.makeCylinder(1.6,.6,V(x,y,44.97))),'steel');add(n+'_fullnut',hexnut(x,y,42.62),'steel')
def bore(s,x,y,z0,h):return s.cut(Part.makeCylinder(1.7,h,V(x,y,z0)))
def move(n,target,rot=None):
 o=D.getObject(n)
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin)
# Complete wholepower end/operatorlayer, not a newFHACcurve. Allfivechambers face +Y, levers +Z.
move('PBAY_P_SYS',[75,34,93.5],A.Rotation(V(1,0,0),90));move('PBAY_P_REAR',[140,34,93.5],A.Rotation(V(1,0,0),90))
move('Monitor_MOD05015',[126,-67,107])
# Derived bankspacing: cell/real15x2.2wholeband outerY22.4 +foreign1.25 -> closest terminal bound25.65.
for side,dy in [('NEG',-3.65),('POS',3.65)]:
 pref='Motor_ATO4A__1_' if side=='NEG' else 'Motor_ATO4A_1_'
 for i in range(6):D.getObject(pref+str(i)).Placement.Base+=V(0,dy,0)
 D.getObject('LOW_MTA_'+side+'_COMMON_PANEL').Placement.Base+=V(0,dy,0)
# Complete two keyed commonlogic roots and realreceiver pads, not generic8floatingfeet.
front=D.getObject('LOW_FRONT_LOAD_GRID').Shape;rear=D.getObject('LOW_REAR_LOAD_GRID').Shape
logic=box(-92,-5,82.6,225,35,2.4)
for x,n in [(-86,'F'),(132,'R')]:
 # two integral7x7columns plusunderplate crosshead; collar has positive usefulthroughweb.
 logic=logic.fuse(box(x-3.5,-7.5,50.52,7,7,34.48)).fuse(box(x-4,-7.5,78.6,8,37.5,6.4))
 receiver=box(x-5,-9,45.52,10,12,8)
 receiver=receiver.cut(box(x-3.7,-7.7,50.52,7.4,7.4,3.1))
 if n=='F':front=front.fuse(receiver);front=bore(front,x,-4,40,50)
 else:rear=rear.fuse(receiver);rear=bore(rear,x,-4,40,50)
 logic=bore(logic,x,-4,45,45);steel('LC_LOGIC_'+n,x,-4,85.5,45,False)
D.getObject('LOW_COMMON_LOGIC_SHELF').Shape=logic
# Headroot realfoursets andreceivingpad onfrontgrid. Tail realfoursets and reargridloadpath.
head=D.getObject('LOW_HEAD_SOURCE_BRIDGE').Shape;tail=D.getObject('LOW_TAIL_COMMON_SOURCE_ROOT').Shape
front=front.fuse(box(-138,-12,45.52,24,24,3));rear=rear.fuse(box(171,-15,45.52,27,30,3))
for x in [-129,-118]:
 for y in [-5,5]:
  head=bore(head,x,y,45,10).cut(Part.makeCone(1.5,3,1.5,V(x,y,50.02)));front=bore(front,x,y,40,15);steel('LC_HEADROOT_'+str(x)+'_'+str(y),x,y,51.52,10)
for x in [177,192]:
 for y in [-8,8]:
  tail=bore(tail,x,y,40,20).cut(Part.makeCone(1.5,3,1.5,V(x,y,55.02)));rear=bore(rear,x,y,35,30);steel('LC_TAILROOT_'+str(x)+'_'+str(y),x,y,56.52,16)
D.getObject('LOW_FRONT_LOAD_GRID').Shape=front;D.getObject('LOW_REAR_LOAD_GRID').Shape=rear;D.getObject('LOW_HEAD_SOURCE_BRIDGE').Shape=head;D.getObject('LOW_TAIL_COMMON_SOURCE_ROOT').Shape=tail
# Complete existingbelt stock with actualclosedloop and purposefulS-rise beforelap outside logicplane.
for i,x in enumerate([7.2,72.7]):
 D.getObject('LC_STRAP'+str(i)+'_lap30').Shape=box(x,-57.3,84.5,15,30,2.2)
 D.getObject('LC_STRAP'+str(i)+'_remainder24p4').Shape=box(x,-72.275222,84.5,15,14.975222,2.2)
 D.getObject('LC_STRAP'+str(i)+'_buckleFIT').Shape=box(x-1,-24.4,81.8,17,17,7)
 c=x+7.5;a=V(c,-21.3,79.6);b=V(c,-24.3,82.6);e=V(c,-27.3,85.6)
 arc1=Part.Arc(a,V(c,-23.42132,80.47868),b).toShape();arc2=Part.Arc(b,V(c,-25.17868,84.72132),e).toShape();path=Part.Wire([arc1,arc2])
 pp=[V(x,-21.3,78.5),V(x+15,-21.3,78.5),V(x+15,-21.3,80.7),V(x,-21.3,80.7)];sec=Part.Wire(Part.makePolygon(pp+[pp[0]]));solid=path.makePipeShell([sec],True,False);add('LC_STRAP'+str(i)+'_WHOLE_S_TRANSITION',solid,'nylon_stock')
# Full stockcase surfaces not interpreted as electronicboxes*rho.
r={'source_strap_spacing_derivation':'whole15x2.2loop outsideY22.4 +1.25foreign -> nearestbank25.65; whole12units+theiractualpanel moved3.65outward together','two_textile_unit_accounting_mm':{'loop_rect_centerline':145.6,'S2quarterR3':3*math.pi,'lap':30,'whole_remainder':200-145.6-3*math.pi-30,'sum':200,'buckle_nominal_total210_not_extra':True},'real_roots':['P01eightaxes','two grids actual complementarylap/fullfourM3sets','Pi tray receivingribs/fullfourM3 +actualfourPCBthroughsets','two keyed commonlogicfoot receivers/fullM3x45','front headactualfourM3x10+rearcartridgefourM3x16'], 'root_threaddelivery_and_fullclothFIT':'physicalsinglecoupon/sample remains; no physicalstrengthPASS','whole_power_case_changed':{'P_SYS':[75,34,93.5],'P_REAR':[140,34,93.5],'entrynormal':[0,1,0],'leveraccessnormal':[0,0,1],'monitor':[126,-67,107]},'affected_unit_ports':['all12MTAfullTE/ATO movedaswhole withpanels','all5P_SYS/P_REAR mouths andleveraccess','W043/F_PI.in andF_AUX.out full84.5..94.5each end','S1 andmonitor allwiredends','fullPiGPIO/CSIunchanged fromlowerconcept'],'unknowns':['actualFHACmouthnormal andselectedWAGOindividualchambers physicalFIT','25chamberconnectedoccupiedregions andwholeuncutendstorage notyetclaimedclear','allwholeunitmouths/complete secondarykeeper/toolcheck','beltactualclosure/stock/cornertakeup and sourcebuckle delivery']}
(P/'completed-common-root-and-power-order.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save();print({'saved':True,'objects':len(D.Objects),'head_rootvol':head.Volume,'tail_rootvol':tail.Volume})
