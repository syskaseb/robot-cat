import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter();moves=[];parts=[];sets=[]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,k='printed_concept'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.43,.58,.61) if k=='printed_concept' else(.66,.67,.69);o.ViewObject.Visibility=True
 if not hasattr(o,'ForeScope'):o.addProperty('App::PropertyString','ForeScope')
 o.ForeScope=k
 if k=='printed_concept':parts.append(n)
 return o
def move(n,target,rot=None):
 o=D.getObject(n);before=bb(o.Shape);vol=o.Shape.Volume
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin)
 moves.append({'name':n,'before':before,'after':bb(o.Shape),'volume_before':vol,'volume_after':o.Shape.Volume})
def shift(n,d):
 b=D.getObject(n).Shape.BoundBox;move(n,[b.XMin+d[0],b.YMin+d[1],b.ZMin+d[2]])
def hexagon(x,y,z,r,h):
 ps=[V(x+r*math.cos(k*math.pi/3),y+r*math.sin(k*math.pi/3),z) for k in range(6)];return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,0,h))
def ring(x,y,z,ro,ri,h):return Part.makeCylinder(ro,h,V(x,y,z)).cut(Part.makeCylinder(ri,h+.2,V(x,y,z-.1)))
def joint(n,x,y,under,L,lowerwasherbottom,nutbottom):
 add(n+'_M3_fullscrew',Part.makeCylinder(1.5,L,V(x,y,under-L)).fuse(Part.makeCylinder(2.75,3,V(x,y,under))),'steel')
 add(n+'_headwasher',ring(x,y,under-.5,3.5,1.6,.5),'steel');add(n+'_nutwasher',ring(x,y,lowerwasherbottom,3.5,1.6,.5),'steel');add(n+'_fullnut',hexagon(x,y,nutbottom,3.175,2.4).cut(Part.makeCylinder(1.3,2.6,V(x,y,nutbottom-.1))),'steel')
 sets.append({'n':n,'qty':1,'nominal':'M3x'+str(L)+' socket+2washers+fullnut','underhead':under,'tip':under-L,'nut_bottom':nutbottom,'engagement':2.4,'protrusion':nutbottom-(under-L),'status':'NEEDED_UNCONFIRMED_NOTPURCHASE'})
# ONE coherentfore/pairedpower/operatorlayer. Sourcecamera/2MG/headmechanism do notmove.
for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female']:shift(n,[-34,1,0])
for n in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']:shift(n,[35,0,0])
shift('PBAY_P_SYS',[0,-9,0]);move('Speaker',[-112,-66,100])
for n in ['S0_body','S0_key','S0_neck','S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0']:shift(n,[0,19,0])
for n in ['MAIN_Pololu4853','MAIN_UNSHRUNK_FAMILY_SCOPE']:move(n,[24,-8,76])
move('S1_NKK_S821_installed',[38,-72,99]);move('Monitor_MOD05015',[-8,-72,112],A.Rotation(V(1,0,0),90))
# Functionalforecrossmember relief forWHOLEtwo-nodebodylayer, not boughtcut/nominalcaseairwaiver.
grid=D.getObject('NIGHT_SHARED_LOAD_GRID').Shape;relief=box(-45.01,-62.25,45.51,6.02,24.5,3.02);grid=grid.cut(relief)
# Actualreceivers under fourPi throughmounts. No transversePi bar crossing eitherWAGO.
for x0,x1 in [(-106,-96),(-48,-38)]:
 for y0,y1 in [(-75,-63),(-26,-13)]:grid=grid.fuse(box(x0,y0,45.0,x1-x0,y1-y0,3.52))
# Gridreceivers forcommonMTA base bolts: avoid actualFHACenvelopeby1.5 and connect existingcross/outerrails.
for x0,x1 in [(-114,-96.5),(114,132)]:
 for y in [45,62]:grid=grid.fuse(box(x0,y-6,45.0,x1-x0,12,3.52))
# Onefixedpostset/base/lowerreceiver. ActualsourceMTAclipinterface remains nominalcoupon, not plasticbbox pressure.
fixed=box(-114.5,28.25,48.52,245.3,2.5,8).fuse(box(-114.5,73,48.52,245.3,10,8))
for x0 in [-114.5,120.8]:fixed=fixed.fuse(box(x0,25,48.52,10,58,8))
posts=[(-109.5,30),(125.8,30),(-109.5,78),(125.8,78)]
for i,(x,y) in enumerate(posts):
 post=box(x-5,y-5,55.52,10,10,56.48)
 post=post.cut(Part.makeCylinder(1.7,12,V(x,y,101.9)))
 # Realfullnut/washer sidefeed beforewholefixedpart mounts; farends open, antirotationflatwidth5.9<nutcirc6.35.
 if x<0:x0=x-7;L=9
 else:x0=x-2;L=9
 post=post.cut(box(x0,y-2.95,105.9,L,5.9,2.8)).cut(box(x0,y-3.7,108.3,L,7.4,.9)).cut(hexagon(x,y,106,3.3,2.6))
 fixed=fixed.fuse(post)
 # Two opposite locatingkeys onactual posttop, realuppermatching recess.
 if i in [0,3]:fixed=fixed.fuse(box(x-3,y-3,112,6,6,1))
# Lowerreceiver ringjoins allfourposts with realcornermaterial.
lower=box(-114.5,25,77,245.3,58,3).cut(box(-100,32,76.9,217,44,3.2));fixed=fixed.fuse(lower)
upper=box(-114.5,25,112,245.3,58,6).cut(box(-100,32,111.9,217,44,6.2))
for i,(x,y) in enumerate(posts):
 upper=upper.cut(Part.makeCylinder(1.7,6.2,V(x,y,111.9)))
 if i in [0,3]:upper=upper.cut(box(x-3.2,y-3.2,111.99,6.4,6.4,1.21))
 joint('FORE_UPPER_'+str(i),x,y,118.5,16,108.5,106.1)
for x in [-108,125]:
 for y in [45,62]:
  fixed=fixed.cut(Part.makeCylinder(1.7,9,V(x,y,48)));grid=grid.cut(Part.makeCylinder(1.7,5,V(x,y,44.5)));joint('FORE_MTA_BASE_'+str(x)+'_'+str(y),x,y,57.02,16,45.02,42.62)
add('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER',fixed);add('FORE_MTA_REMOVABLE_UPPER_RECEIVER',upper)
for n in ['NIGHT_MTA_LOWER_OPEN_TIER_FRAME','NIGHT_MTA_UPPER_OPEN_TIER_FRAME']:D.getObject(n).ViewObject.Visibility=False
# Sharedheadbeam routes clear actualfixedpostset atY25; stationarysaddle69.5 retained, no movingfork fusion.
h=box(-86,15,45.52,12,8,21).fuse(box(-147,15,66.5,73,8,7)).fuse(box(-147,-13,66.5,28,36,3));D.getObject('NIGHT_HEAD_FIXED_SADDLE_ROOT').Shape=h
# OneU-shapedPi mountingframe, fourrealprimaryaxes/3mmstandoffs, no false support throughG1/P_FRONTcases.
tray=box(-104,-74.5,48.52,64.5,3,2).fuse(box(-104,-17.5,48.52,64.5,3,2)).fuse(box(-104,-74.5,48.52,3,60,2))
for x in [-100.5,-42.5]:
 for y in [-68.5,-19.5]:
  yy=-74.5 if y< -30 else -22.5
  tray=tray.fuse(box(x-3,yy,48.52,6,9,2)).fuse(Part.makeCylinder(3,3,V(x,y,50.52)))
  hole=Part.makeCylinder(1.4,10,V(x,y,44));tray=tray.cut(hole);grid=grid.cut(hole)
  # Full M2.5x16 throughpost/frame/grid washer/nut; retainedsourcePCBdatum.
  n='FORE_PI_'+str(x)+'_'+str(y);add(n+'_screw',Part.makeCylinder(1.25,16,V(x,y,39.62)).fuse(Part.makeCylinder(2.25,2.5,V(x,y,55.62))),'steel');add(n+'_upperwasher',ring(x,y,55.12,2.5,1.35,.5),'steel');add(n+'_lowerwasher',ring(x,y,45.02,2.5,1.35,.5),'steel');add(n+'_fullnut',hexagon(x,y,43.02,2.9,2).cut(Part.makeCylinder(1.1,2.2,V(x,y,42.9))),'steel')
add('FORE_PI_OPEN_U_FRAME',tray);D.getObject('NIGHT_SHARED_LOAD_GRID').Shape=grid
# Plannedoperatorfacecut inexistingPROVISIONALenvelope ONLY; NOTnewskin/printmass.
env=D.getObject('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT');env.Shape=env.Shape.cut(box(-10,-150,92,118,122,52))
(P/'whole-fore-layer-effectivity.json').write_bytes((json.dumps({'moves':moves,'new_print_concepts':parts,'MTA_fixed_posts':posts,'complete_M3_sets':sets,'retired':['twooverlappingMTApostsets','oldforecrossbeamsegment onlyreplacedbyconnectedperimeterloadpath'],'PCA_E1':'wholekit rigid+35X, no desolder','S0':'whole11 +19Y sameorientation; oneoperatorface withS1/monitor','Pi':'wholeports/cooling rigid[-34,1,0], PCBdatum53.52 retained','headbodycameraMG':'boughtposes unchanged','source12ST3MG_leglength':'unchanged','assembly':'preload allfour actualnut+washer throughopenfeeds onbench; mountfixedframe beforetailroot/headbridge iftoolneeds; lowerMTA installed/prewired BEFOREtrueupperreceiver thenupperMTA; speaker AFTERP_SYSleversclosed; no virtualintegralpostremoval','upper_bodycase_clip_fit':'primary2mmpanel interface stillrequiresactualdatum/coupon; thisreceiverstructure is not claimallcasessecured','no_STL_release':True,'physicalPASS':False},indent=2)+'\n').encode())
D.recompute();D.save();print(json.dumps({'saved':True,'parts':parts,'fixed_solids':len(fixed.Solids),'upper_solids':len(upper.Solids),'Pi_solids':len(tray.Solids),'seconds':time.perf_counter()-t,'objects':len(D.Objects)}))
