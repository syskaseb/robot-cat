import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
new=[];revisions=[];hardware=[]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def obj(n,s,kind='printed',color=(0.46,0.58,0.61)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=True
 if not hasattr(o,'CorrectionScope'):o.addProperty('App::PropertyString','CorrectionScope')
 o.CorrectionScope=kind
 if kind=='printed':new.append(n)
 return o
def rev(n,s):D.getObject(n).Shape=s;revisions.append(n)
def move(n,t,rot=None):
 o=D.getObject(n)
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*t)-V(b.XMin,b.YMin,b.ZMin)
def csk(s,x,y,top,length):
 return s.cut(Part.makeCylinder(1.7,length,V(x,y,top-length))).cut(Part.makeCone(1.5,3,1.5,V(x,y,top-1.5)))
def hexagon(x,y,z,r,h):
 pts=[V(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
def fullcsk(tag,x,y,top,L):
 # Standard CS length includes whole head. complete nut/washer/shaft/tip; demand UNCONFIRMED.
 sh=Part.makeCylinder(1.5,L-1.5,V(x,y,top-L)).fuse(Part.makeCone(1.5,3,1.5,V(x,y,top-1.5)))
 obj(tag+'_M3_CS_FULL',sh,'steel',(0.66,0.66,0.68));z=45.52
 wa=Part.makeCylinder(3.5,.5,V(x,y,z-.5)).cut(Part.makeCylinder(1.6,.6,V(x,y,z-.55)))
 nu=hexagon(x,y,z-2.9,3.175,2.4).cut(Part.makeCylinder(1.3,2.6,V(x,y,z-3)))
 obj(tag+'_washer',wa,'steel',(0.66,0.66,0.68));obj(tag+'_fullnut',nu,'steel',(0.66,0.66,0.68));hardware.append({'tag':tag,'type':'M3 countersunk','length_includinghead':L,'qty':1,'washer':1,'fullnut':1,'head_top':top,'nut_bottom':z-2.9,'tip':top-L,'status':'NEEDED_UNCONFIRMED'})
# ONE whole front/operator allocation, bought shapes unchanged in size.
move('Speaker',[-108,53,90],A.Rotation(V(0,0,1),180));move('S1_NKK_S821_installed',[138,-30,91])
# Finite diagnosed full-module underside -> ordinary 4.52mm standoff layer, no IC pressing.
for n in ['MAIN_Pololu4853','MAIN_UNSHRUNK_FAMILY_SCOPE','AUX_Pololu4092','AUX_FULL9p5_POPULATED_SCOPE']:
 o=D.getObject(n);o.Placement.Base+=V(0,0,2.02)
for n in ['MAIN_all_terminal_field_FIT2','AUX_all_terminal_field_FIT2']:
 o=D.getObject(n)
 if o:o.Placement.Base+=V(0,0,2.02)
# Actual grid bearing on P01 top Z45.52; source eight axes retained, no realframe drill.
f=D.getObject('LOW_FRONT_LOAD_GRID').Shape;r=D.getObject('LOW_REAR_LOAD_GRID').Shape
# Finite roots under Pi legs, actual connected transverse ribs cross source load spines.
for x in [-128,-47]:f=f.fuse(box(x,-70,45.52,8,62,3))
for x in [-88,-20]:f=f.fuse(box(x,-8,45.52,6,42,8))
for x in [70,125]:r=r.fuse(box(x,-8,45.52,6,42,8))
# Real complementary horizontal half-lap between two separately printed grids.
f=f.fuse(box(24,-26,45.52,6,52,8)).fuse(box(30,-26,45.52,6,52,4)).cut(box(24,-26,49.52,6,52,4.01))
r=r.fuse(box(30,-26,45.52,6,52,8)).fuse(box(24,-26,49.52,6,52,4)).cut(box(30,-26,45.51,6,52,4.01))
for x in [27,33]:
 for y in [-8,8]:
  f=csk(f,x,y,53.52,15);r=csk(r,x,y,53.52,15);fullcsk('LC_GRID_'+str(x)+'_'+str(y),x,y,53.52,12)
for x in [-80,-70,112,122]:
 for y in [-22.5,22.5]:
  hole=Part.makeCylinder(1.4,8.1,V(x,y,45.5))
  if x<30:f=f.cut(hole)
  else:r=r.cut(hole)
  # Existing source attachment pattern; entering source-hole not supplier thread proof.
  sh=Part.makeCylinder(1.25,12,V(x,y,42.02)).fuse(Part.makeCylinder(2.25,2.5,V(x,y,54.02)))
  obj('LC_SOURCE_'+str(x)+'_'+str(y),sh,'steel',(0.66,0.66,0.68));hardware.append({'type':'M2.5x12 socket/source pattern','axis':[x,y],'thread':'source physical P00 FIT; 3.5mm modeled entry, no drilling','qty':1,'status':'NEEDED_UNCONFIRMED'})
# Pi mounting feet actual receiving bars; full M3x16 roots before PCB, no second spacer.
tray=D.getObject('LOW_PI_COMMON_TRAY').Shape
for x in [-128,-47]:
 for y in [-66,-12]:
  tray=tray.fuse(box(x,y,48.52,6,6,6.6));tray=csk(tray,x+3,y+3,57.52,18);f=csk(f,x+3,y+3,57.52,18);fullcsk('LC_PITRAY_'+str(x)+'_'+str(y),x+3,y+3,57.52,16)
rev('LOW_PI_COMMON_TRAY',tray);rev('LOW_FRONT_LOAD_GRID',f);rev('LOW_REAR_LOAD_GRID',r)
# Four full selected Pi M2.5-throughsets, safe annulus remains onephysical FIT.
for x in [-104.5,-46.5]:
 for y in [-62.5,-13.5]:
  tag='LC_PI_'+str(x)+'_'+str(y);sh=Part.makeCylinder(1.25,12,V(x,y,50.62)).fuse(Part.makeCylinder(2.25,2.5,V(x,y,62.62)))
  obj(tag+'_screw',sh,'steel',(0.66,0.66,0.68))
  for z in [62.12,54.62]:obj(tag+'_washer'+str(z),Part.makeCylinder(2.5,.5,V(x,y,z)).cut(Part.makeCylinder(1.35,.6,V(x,y,z-.05))),'steel',(0.66,0.66,0.68))
  obj(tag+'_fullnut',hexagon(x,y,52.62,2.9,2).cut(Part.makeCylinder(1.1,2.2,V(x,y,52.5))),'steel',(0.66,0.66,0.68));hardware.append({'type':'M2.5x12 +2washers+fullnut','qty':1,'status':'NEEDED_UNCONFIRMED'})
# Whole source2mm MTA panels already connected to root feet; strengthen common upper speaker seat above all full-unit Z82.
panel=D.getObject('LOW_MTA_POS_COMMON_PANEL').Shape.fuse(box(-141,43,83,147,2,5))
rev('LOW_MTA_POS_COMMON_PANEL',panel)
audio=box(-110,43,86.6,104,32,2.4)
# open center avoids diaphragm/magnet underside; only safe basket edge lands adjustable physicalFIT.
audio=audio.cut(box(-102,48,86.5,88,23,2.6))
for x in [-108,-12]:audio=audio.fuse(box(x,45,88,4,28,2))
obj('LC_COMMON_SPEAKER_BASKET_SEAT',audio)
# Two real 200mm textile units, full declared15x2.2 cross section, lap+buckle+all remainder represented as fields.
strap=[]
for i,x in enumerate([7.2,72.7]):
 # closed capacity perimeter actually encloses platform/floor+cell, sourceband full nominal crosssection.
 outer=box(x,-22.4,48.3,15,44.8,32.4);inner=box(x-.1,-20.2,50.5,15.2,40.4,28.0);ring=outer.cut(inner)
 obj('LC_STRAP'+str(i)+'_fullclosedloop',ring,'nylon_stock',(0.26,0.26,0.28))
 # centerline rectangular perimeter145.6, 30lap,24.4uncutremainder; corners bend shape andbuckle delivery FIT.
 obj('LC_STRAP'+str(i)+'_lap30',box(x,-21.3,80.7,15,30,2.2),'nylon_stock',(0.26,0.26,0.28))
 obj('LC_STRAP'+str(i)+'_remainder24p4',box(x,-45.7,83,15,24.4,2.2),'nylon_stock',(0.26,0.26,0.28))
 o=obj('LC_STRAP'+str(i)+'_buckleFIT',box(x-1,-26,79,17,17,7),'source_uncertainty',(0.6,0.55,0.3));o.ViewObject.Transparency=70
 strap.append({'xstation':x,'loop_center_perimeter_mm':145.6,'lap_mm':30,'whole_remainder_mm':24.4,'sum_nominal_textile':200,'captured_print':'LOW_BATTERY_STRAP_BRIDGE_PLATFORM','inner_yz':[-20.2,20.2,50.5,78.5],'meaning':'closed band encloses actual connected platform, not mere nearfield; buckle/endshape thickness/corner takeup FIT','total210_includes_buckle_notextra':True})
# Split too-long WAGO rails into realtwo-part tracks with local half-lap and fullM3 fixings, not STL253+brim.
for side,y in [('NEG',-94),('POS',75)]:
 old=D.getObject('LOW_WAGO_'+side+'_OPEN_COMMON_RAIL');old.ViewObject.Visibility=False
 a=box(-137,y,82.5,125,19,2.5).fuse(box(-12,y,82.5,8,19,1.25))
 b=box(-12,y,83.75,8,19,1.25).fuse(box(-4,y,82.5,120,19,2.5))
 obj('LC_WAGO_'+side+'_FRONT',a);obj('LC_WAGO_'+side+'_REAR',b)
 # Actualopenassembly bolted seam/feed still prior to WAGOcases; detailed complete railroot sets OPEN ifnotreceived.
# Nonload skin superseded later in SAMEcorrection, keep frozen newcopy before checks.
(P/'whole-interface-realization.json').write_bytes((json.dumps({'new_prints':new,'revised':revisions,'hardware':hardware,'straps':strap,'module_changes':{'Speaker':'whole module to positiveY53..74, front faces +Y; GPIOunchanged','S1':'whole switch to138,-30,91 away fullAUX','MAIN_AUX':'wholemodules+2.02Z to PCBnominal89.52 and underside87.72'},'root_hypothesis':'sourceP01eightaxes -> half-lapped grids -> receivingribs -> trays/panels; source screwthread actualP00FIT','unreceived':['complete all secondary shelf/panel boltsets','textile actual buckle/lap/corners/tension fit','complete stockspace and CSI movingflatfield']},indent=2)+'\n').encode())
D.recompute();D.save();print(json.dumps({'new_prints':len(new),'revised':len(revisions),'hardware_groups':len(hardware),'saved':D.FileName}))
