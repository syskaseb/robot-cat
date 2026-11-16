import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
baseline=json.loads((P.parent/'day16-whole-power-entry-and-full-CSI/rough-mass-readonly/measurement-selection-and-source.json').read_text());moves=[];newprints=[]
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def add(n,s,kind='printed',color=(0.5,0.62,0.65)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.addProperty('App::PropertyString','ConceptScope').ConceptScope=kind
 if kind=='printed':newprints.append(n)
 return o
def repose(n,target,rot=None):
 o=D.getObject(n)
 if not o:return
 old=bb(o.Shape);volume=o.Shape.Volume
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin);o.ViewObject.Visibility=True
 moves.append({'name':n,'before':old,'after':bb(o.Shape),'volume_before':volume,'volume_after':o.Shape.Volume})
def shift(n,delta):
 o=D.getObject(n)
 if o and hasattr(o,'Shape') and not hasattr(o,'Group'):
  b=bb(o.Shape);repose(n,[b[i]+delta[i] for i in range(3)])
# Explicit retire/replacement scope: old shared portals/carrying panels are not bought products.
headkeep=set()
for group in ['CONTINUOUS_HEAD_TAIL_REAL_PRINTS','HEAD_FACTORY_REFERENCE_NOT_BOM','HEAD_SOURCE_SENSORS_AND_REAL_MASK']:
 for o in D.getObject(group).Group:
  if not o.Name.startswith('TAIL_'):headkeep.add(o.Name)
headkeep.update(['Camera3_NoIR_Wide','VL53L5CX','MG92B_Head_yaw','MG92B_Head_pitch','Yaw608_120','Yaw608_134','Pitch688','Ola_ear__1','Ola_ear_1','Ola_eye_gold__1','Ola_eye_gold_1','Ola_nose'])
kept_prints=set(n for n in baseline['selected_print_objects'] if n in headkeep or n in ['P01_load_rail','P01_load_rail_instance2'])
# Tail full bought/mechanism group moves together; fixed P07 rebuilt from actual lower base and rear bearing seat below.
tailnames=[o.Name for o in D.Objects if hasattr(o,'Shape') and not hasattr(o,'Group') and (o.Name.startswith('TAIL_') or o.Name in ['MG92B_Tail','Tail608'])]
kept_prints.update(n for n in baseline['selected_print_objects'] if n in tailnames)
for n in baseline['selected_print_objects']:
 if n not in kept_prints:D.getObject(n).ViewObject.Visibility=False
# Remove only unbuilt hardware demands/old analytic fields, not selected purchased parts.
for o in D.Objects:
 n=o.Name
 if n.startswith(('CF_','CL_','AL_','COVER_','WIRE_','SECTION_','FEED_','KEY_','DIRECT_','CAPTURE_','STRAP','W043_','EV_','YTAIL_','PB_TIE','PB_KEEP','BASE','CS_','OPEN_M2','OPEN_ROOT','ROOT_','CAP0','CAP1','ROW_','REAR_PAIR','BANK_','LEG0_','LEG1_','LEG2_','LEG3_','POST412_','TIE_','T30L_')) and hasattr(o,'ViewObject'):o.ViewObject.Visibility=False
for n in ['Battery_tray_shared','Neck_shared_root','Ola_body_ENVELOPE','Ola_head_ENVELOPE','Ola_tail_ENVELOPE','Ola_muzzle','Ola_short_shoulder_blend_PROPOSED','Ola_shared_cheek_mask_PROPOSED']:D.getObject(n).ViewObject.Visibility=False
for n in headkeep:shift(n,[0,0,-20])
for n in tailnames:shift(n,[0,0,-42])
# Actual source base/12ST3215/leg lengths retained unchanged.
# All twelve complete MTA0300330+TE+ATO units laid on their side in two staggered banks.
for sign,start,y in [('_',-30,-93.43),('',-139,22)]:
 for i in range(6):
  n=('Motor_ATO4A__1_' if sign=='_' else 'Motor_ATO4A_1_')+str(i)
  repose(n,[start+24*i,y,54],A.Rotation(V(1,0,0),90))
# Pi and all its source ports/cooling/mating fields are one translated module group.
for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female']:shift(n,[-30,-28,-38])
repose('Battery_GEA223S30X6GT',[-15,-17.5,55.52])
# Preserve entire soldered PCA/E1 kit by the SAME rigid transform (not virtual unplug).
R=A.Rotation(V(1,0,0),90);T=A.Placement(V(5,121,47),R)
for n in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']:
 o=D.getObject(n);before=bb(o.Shape);o.Placement=T.multiply(o.Placement);moves.append({'name':n,'before':before,'after':bb(o.Shape),'whole_soldered_kit_transform':'same R/T'})
repose('MAIN_Pololu4853',[70,-10,87.5]);repose('MAIN_UNSHRUNK_FAMILY_SCOPE',[70,-10,87.5])
repose('AUX_Pololu4092',[102,-10,87.5]);repose('AUX_FULL9p5_POPULATED_SCOPE',[102,-10,85.7])
repose('BUS25514_installed',[-74,-17,100])
repose('Speaker',[-108,-71,90],A.Rotation(V(1,0,0),90))
repose('MAX98357A_amp',[-37,-45,94],A.Rotation(V(1,0,0),90))
repose('BNO085',[-74,-45,94]);repose('ReSpeakerLite_on_REMOVABLE_back',[-5,-17.5,116]);repose('TTP223_touch',[-60,24,120])
repose('S1_NKK_S821_installed',[116,-21,91]);repose('Monitor_MOD05015',[137,23,107])
# FULL eleven-part S0 group rotated to horizontal side operation; no case/key/metal lost.
T=A.Placement(V(12-107.12161254882812,117.52,126),A.Rotation(V(1,0,0),90))
for n in ['S0_body','S0_key','S0_neck','S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0']:
 o=D.getObject(n);before=bb(o.Shape);o.Placement=T.multiply(o.Placement);moves.append({'name':n,'before':before,'after':bb(o.Shape),'whole_S0_transform':True})
# ALL16WAGO415 roles in open two side rails, same complete bodies, not allDATA.
for side,y in [('_',-94),('',75)]:
 for i in range(8):
  n=('WAGO415_data__1_' if side=='_' else 'WAGO415_data_1_')+str(i)
  if n=='WAGO415_data_1_0':n='PBAY_P_AUX'
  repose(n,[-135+31*i,y,85],A.Rotation(V(0,0,1),90))
repose('WAGO615_power_0_0',[-40.5,-18.5,52]);repose('WAGO615_power_0_1',[-40.5,29,85])
repose('PBAY_P_SYS',[75,26.5,80],A.Rotation(V(0,0,1),90).multiply(A.Rotation(V(0,1,0),90)))
repose('PBAY_P_REAR',[126,26.5,80],A.Rotation(V(1,0,0),-90))
# Five complete FHACs horizontal, two staggered rows with BOTH free ends accessible.
fuses=[('PBAY_F_PI',[40,72,55]),('PBAY_F_AUX',[94,72,55]),('PBAY_F_HY',[148,72,55]),('PBAY_F_HP',[75,46,55]),('PBAY_F_TY',[129,46,55])]
for n,pos in fuses:
 b=D.getObject(n).Shape.BoundBox
 rot=A.Rotation(V(0,1,0),90) if b.ZLength>40 else None
 repose(n,pos,rot)
# The two inherited vertical boxes after rotation are51X22Y20.25, no body shrink.
repose('PBAY_POST_F0',[-129,20,56]);repose('F0_FHAC0002_30A',[-139,-2,50],A.Rotation(V(1,0,0),90))
repose('XT60H_mated_with_boots',[50,-16,79])
# Full actual0100335 is unbound; keep each supplied placeholder plus explicit accessible adjustable envelope, not mfgPASS.
for i,(x,y) in enumerate([(-100,-55),(-100,55),(100,-55),(100,55)]):
 repose('Leg_protected_MTA0100335_'+str(i),[x-17.75,y-4.05,94]);q=add('LOW_MINIVAL_UNBOUND_SPACE_'+str(i),box(x-22.5,y-10,94,45,20,22),'source-uncertainty',(0.65,0.55,0.3));q.ViewObject.Transparency=75
# Few common skeletal load parts, contact the existing two P01 rails, not a full heavy cage.
def skeleton(x0,L):
 a=box(x0,-95,45.52,L,190,3);a=a.cut(box(x0+8,-87,45.51,L-16,174,3.02))
 for y in [-22.5,22.5]:a=a.fuse(box(x0,y-3,45.52,L,6,8))
 for x in [x0+8,x0+L/2,x0+L-14]:a=a.fuse(box(x,-95,45.52,6,190,3))
 return a
front=add('LOW_FRONT_LOAD_GRID',skeleton(-143,173));rear=add('LOW_REAR_LOAD_GRID',skeleton(30,175))
# Battery/platform and Pi tray are finite parts with material bearing, not label-only standoffs.
plate=box(-18,-20,53.52,113,40,2)
for y in [-20,17]:plate=plate.fuse(box(-18,y,48.52,113,3,7))
for x in [7.2,72.7]:plate=plate.cut(box(x,-21,50.1,15.6,42,3.02))
add('LOW_BATTERY_STRAP_BRIDGE_PLATFORM',plate)
tray=box(-131,-69,55.12,91,62,2.4)
for x in [-104.5,-46.5]:
 for y in [-62.5,-13.5]:tray=tray.fuse(Part.makeCylinder(3,3,V(x,y,57.52))).cut(Part.makeCylinder(1.4,8,V(x,y,54)))
for x in [-128,-47]:
 for y in [-66,-12]:tray=tray.fuse(box(x,y,48.52,4,4,8))
add('LOW_PI_COMMON_TRAY',tray)
logic=box(-92,-5,82.6,225,35,2.4)
for x in [-88,-20,70,125]:logic=logic.fuse(box(x,-5,53.52,4,4,29.08)).fuse(box(x,26,53.52,4,4,29.08))
add('LOW_COMMON_LOGIC_SHELF',logic)
# Common two panel strips; primary 2mm clip zones, nominal window only; not catalogcase bbox Own waiver.
for tag,x0,y in [('POS',-139,43),('NEG',-30,-73)]:
 panel=box(x0-2,y,52,147,2,32)
 for i in range(6):panel=panel.cut(box(x0+i*24+5.25,y-.1,56,11.3,2.2,22.2))
 for x in [x0-2,x0+139]:panel=panel.fuse(box(x,y-5,48.52,6,12,5.48))
 add('LOW_MTA_'+tag+'_COMMON_PANEL',panel)
for tag,y in [('NEG',-94),('POS',75)]:add('LOW_WAGO_'+tag+'_OPEN_COMMON_RAIL',box(-137,y,82.5,253,19,2.5))
# Tail lower support: preserve source rear bearing seat and actual base, fill ordinary connections later, no new couplerfamily.
old=D.getObject('P07_open_tail_root_U').Shape;seat=old.common(box(160,-18,130,54,8,50));seat.translate(V(0,0,-42));base=old.common(box(170,-15,52.52,29,30,4))
root=base.fuse(box(171,-15,48.52,27,30,4)).fuse(box(171,-18,55.52,27,6,41)).fuse(seat)
root=root.fuse(box(167,-50.6,52.52,46,42.6,4))
for x in [167,207]:root=root.fuse(box(x,-50.6,54,6,3.1,74))
for z in [96,119.25]:root=root.fuse(box(172,-50.6,z,36,3.1,8.75))
add('LOW_TAIL_COMMON_SOURCE_ROOT',root)
# Head whole-two-axis pose is lower; actual bearing/head parts retained. New short shared portal to source rails.
portal=box(-138,-12,48.52,24,24,3)
for y in [-12,8]:portal=portal.fuse(box(-138,y,48.52,5,4,58))
portal=portal.fuse(box(-138,-12,103.52,24,24,3))
add('LOW_HEAD_SOURCE_BRIDGE',portal)
# New NONLOAD thin closed shell, four real prospective parts under256. Shape is not a filled envelope for mass.
def profile(x,w,z0,zt,thick=0):
 w-=thick;z0+=thick;zt-=thick;r=12;ze=zt-12
 def p(y,z):return V(x,y,z)
 pts=[];e=[]
 e.append(Part.makeLine(p(-w+r,z0),p(w-r,z0)))
 e.append(Part.Arc(p(w-r,z0),p(w-r+r*.707,z0+r-r*.707),p(w,z0+r)).toShape())
 e.append(Part.makeLine(p(w,z0+r),p(w,ze)))
 e.append(Part.Arc(p(w,ze),p(w*.55,zt-3.5),p(0,zt)).toShape())
 e.append(Part.Arc(p(0,zt),p(-w*.55,zt-3.5),p(-w,ze)).toShape())
 e.append(Part.makeLine(p(-w,ze),p(-w,z0+r)))
 e.append(Part.Arc(p(-w,z0+r),p(-w+r-r*.707,z0+r-r*.707),p(-w+r,z0)).toShape())
 return Part.Wire(e)
stations=[(-160,83,48,125),(-142,103,44,140),(-80,103,42,145),(40,103,42,145),(130,103,44,143),(185,85,54,140),(215,42,78,125)]
outer=Part.makeLoft([profile(*q) for q in stations],True,True);inner=Part.makeLoft([profile(*q,thick=2) for q in stations],True,True);skin=outer.cut(inner)
# Real seam/end access is prototype openassembly; headneck and tail openings are source-oriented reliefs, not hiddenparts.
skin=skin.cut(Part.makeCylinder(43,45,V(-170,0,117),V(1,0,0)))
skin=skin.cut(Part.makeCylinder(10,28,V(185,-1.5,112),V(0,1,0)))
for xa,xb,ytag,y0,y1 in [(-160,30,'F_NEG',-150,0),(-160,30,'F_POS',0,150),(30,216,'R_NEG',-150,0),(30,216,'R_POS',0,150)]:
 piece=skin.common(box(xa,y0,0,xb-xa,y1-y0,200));add('LOW_THIN_BODY_'+ytag,piece,color=(0.15,0.17,0.2))
# Coarse required occupied regions, not rigid wire axes or print material; no omitted stock credit.
regions=[('CSI200_FULL_HEAD_TO_PI',[-230,-32,62,150,48,95]),('POWER_SHARED_HANDLAY',[38,38,76,160,34,35]),('LEFT_DATA_AND_12MTA_ENDS',[-139,-75,82,253,25,28]),('RIGHT_BANK_FHAC_FULL_ENDS',[-139,48,82,338,27,28]),('E2_JPWM_FOUR_INDEPENDENT_225',[-95,-12,53,190,24,28]),('USB500_SEPARATE_AUDIO_GROVE_UNKNOWN',[-95,-30,96,190,58,34])]
for n,b in regions:q=add('LOW_REGION_'+n,box(*b),'allocated_flexible_group',(0.8,0.5,0.15));q.ViewObject.Transparency=85;q.ViewObject.Visibility=False
# Preserve both whole selected200 textile units as source references, explicit routing remains future group proof.
for i in [0,1]:
 for n in ['STRAP'+str(i)+'_bodyloop_full2p2','STRAP'+str(i)+'_whole_tail','STRAP'+str(i)+'_closure_fullunit_projectfield']:
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False
summary={'status':'ONE_WHOLE_LOWER_LIGHTER_CONCEPT_NOT_MOUNT_RELEASE','new_prints':newprints,'retained_print_names':sorted(kept_prints),'superseded_print_names':sorted(set(baseline['selected_print_objects'])-kept_prints),'moves':moves,'bought_source_126_unchanged':True,'12ST3215_and_leglength_unchanged':True,'head_pose_change':[0,0,-20],'tail_pose_change':[0,0,-42],'tail_axis_Y_point':[185,0,112],'body_outer_height_Z':[42,145],'old_body_maxZ':185.20099394964424,'full_textile_units':{'quantity':2,'nominal_each_mm':200,'selected_total210_includesbuckle':True,'actualrouting':'source fields superseded not counted deleted; platform closed slots pending actual full loop/buckle/tail proof'},'structural_effectivity':'few load grids/shelves replace deep portals/P11/P12; exact roots, useful join coverage and complete bolts still prototype engineering, not physicalFIT excuse','affected_ports':['ALL Pi CSI/USB-C/USB_DATA/40GPIO/cooling/USB_AUDIO','complete E1/PCA same rigidtransform','MAIN/AUX source pads/hole/support and stock','S0 complete11 sourcefunctions/key/steel','full 12MTA housingflanges/TE/ATO2rows','all9PBAY roles/FHAC10ends/WAGO25chambers','head2axes/CSI/ToF and tailMG/608 fullcoupling'],'all_unknowns':['actual MTA0100335 sample/body/lid/tether/leads','USB_AUDIO/Grove actualwholeunits','complete CSI200 pose/terminations/slack gate','whole84.5..94.5 FHAC ends/surplus/localR before keeperfreeze','source hardware and motion/payload/thermal physical checks'],'no_STL_release':True,'physicalPASS':False,'wholekit':False}
(P/'whole-low-layout-effectivity.json').write_bytes((json.dumps(summary,indent=2)+'\n').encode())
D.recompute();D.save();v=G.activeDocument().activeView();d=V(-1.5,-1,.65);d.normalize();r=V(0,0,1).cross(d);r.normalize();v.setCameraOrientation(A.Rotation(r,d.cross(r),d,'ZXY').Q);v.fitAll();v.redraw()
print(json.dumps({'new_prints':len(newprints),'retained_prints':len(kept_prints),'moved_units':len(moves),'objects':len(D.Objects),'saved':D.FileName}))
