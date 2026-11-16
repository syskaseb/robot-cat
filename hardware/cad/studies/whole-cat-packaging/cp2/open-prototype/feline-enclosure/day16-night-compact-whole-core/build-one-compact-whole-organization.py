import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter();moves=[];newprints=[];retired=[];unknowns=[]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,kind='structural_concept',col=(.45,.58,.61)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True
 if not hasattr(o,'NightScope'):o.addProperty('App::PropertyString','NightScope')
 o.NightScope=kind
 if kind=='structural_concept':newprints.append(n)
 return o
def move(n,target,rot=None):
 o=D.getObject(n)
 if o is None:return
 before=bb(o.Shape);vol=o.Shape.Volume
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin);o.ViewObject.Visibility=True
 moves.append({'name':n,'before':before,'after':bb(o.Shape),'volume_before':vol,'volume_after':o.Shape.Volume})
def translate(n,delta):
 o=D.getObject(n)
 if o is not None:
  b=o.Shape.BoundBox;move(n,[b.XMin+delta[0],b.YMin+delta[1],b.ZMin+delta[2]])
# Explicit whole replacement: oldunbuiltcompactstudystructure/hardware/skins no longeroperatingphysicalalternative.
oldsel=json.loads((P.parent/'day16-low-light-whole-correction/same-density-complete-correction-mass.json').read_text())
keep=[]
for r in oldsel['rows']:
 n=r['name']
 if n.startswith(('TAIL_','YAW_','PITCH_','HEAD_')) or n in ['P01_load_rail','P01_load_rail_instance2','Ola_ear__1','Ola_ear_1','Ola_eye_gold__1','Ola_eye_gold_1','Ola_nose','DECORATIVE_BLACK_EYE__1','DECORATIVE_BLACK_EYE_1']:keep.append(n)
 else:
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False;retired.append(n)
for o in D.Objects:
 if o.Name.startswith(('LC_','LOW_REGION_','LOW_MINIVAL_','STRAP','H01_','H02_','H03_','H04_','CF_','CL_','AL_','PB_TIE','PB_KEEP','OPEN_M2','OPEN_ROOT','ROOT_','CAP0','CAP1','INLINE8_')):o.ViewObject.Visibility=False
# Twelve complete MTA units: 3X x2Y x2Z longitudinalfunctional core, fullTE/ATO retained.
R=A.Rotation(V(0,0,1),90)
for layer,pref,z in [(0,'Motor_ATO4A_1_',80),(1,'Motor_ATO4A__1_',118)]:
 for i in range(6):
  ix=i%3;iy=i//3;move(pref+str(i),[-101+73.43*ix,30+23.8486*iy,z],R)
# LowwholePi4 +allactualsourceports/cooling, no unilateralUSB/CSIcredit.
for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female']:translate(n,[38,-7,-7])
move('Battery_GEA223S30X6GT',[-12,-8,52])
# The solderedPCA+E1 remains SAME whole rigidtransform, no virtualunplug.
for n in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']:translate(n,[-15,-9,7])
# Actualremainingfullmodules; mainfamily andAUX9.5 both kept.
for n,target in [('MAIN_Pololu4853',[40,-5,82]),('MAIN_UNSHRUNK_FAMILY_SCOPE',[40,-5,82]),('AUX_Pololu4092',[-3,2.5,78.5]),('AUX_FULL9p5_POPULATED_SCOPE',[-3,2.5,76.7]),('BUS25514_installed',[-59.5,-25,109]),('BNO085',[20,2,107]),('MAX98357A_amp',[-15,2,107]),('ReSpeakerLite_on_REMOVABLE_back',[-5,-24,145]),('TTP223_touch',[-49,14,136]),('Speaker',[-90,-66,88]),('S1_NKK_S821_installed',[108,-21,95]),('Monitor_MOD05015',[79,-72,109])]:move(n,target)
# Speakerfront to negativeY; wholebody rotarypose, fullprofile unchanged.
o=D.getObject('Speaker');R2=A.Rotation(V(0,0,1),180);move('Speaker',[-90,-66,88],R2)
# S0full11 rigidRy90: operator key outside -Y functionalaperture, allstud/ring/nuts retained.
s0=['S0_body','S0_key','S0_neck','S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0']
T=A.Placement(V(),A.Rotation(V(0,1,0),90))
for n in s0:D.getObject(n).Placement=T.multiply(D.getObject(n).Placement)
b=D.getObject('S0_body').Shape.BoundBox;delta=V(60,-49,80)-V(b.XMin,b.YMin,b.ZMin)
for n in s0:translate(n,list(delta))
# All16WAGO415: two shorter4x2banks, not16data. No newelectricalassignment.
for side,pref,y,z in [('POS','WAGO415_data_1_',32,148),('NEG','WAGO415_data__1_',-72,147)]:
 for i in range(8):
  n=pref+str(i)
  if n=='WAGO415_data_1_0':n='PBAY_P_AUX'
  if n=='PBAY_P_AUX':continue
  move(n,[-64+(i%4)*33,y+(i//4)*22,z])
# P_AUX physicallyone ofselected16, deliberatelyinfunctional6Vbranch notfifthoutsideinstance.
move('PBAY_P_AUX',[-88,5,76])
# Keep16physicalcount: P_AUXvacatedpositivebankstation is not aphantomcase.
# Four615 fivechambereach, distinctwholecases. G1/P_FRONT underPiopenassembly; P_SYS pairedfaceabovePi.
for n,tg,rr in [('WAGO615_power_0_0',[-89,-61,40.77],A.Rotation(V(0,0,1),90)),('WAGO615_power_0_1',[-50,-61,40.77],A.Rotation(V(0,0,1),90)),('PBAY_P_SYS',[-89,-42,86.5],A.Rotation(V(0,0,1),-90)),('PBAY_P_REAR',[73,2,96],None)]:move(n,tg,rr)
# FiveFHAC cases pairedbyfunctionalends, no imposedprettyrow.
for n,tg,rr in [('PBAY_F_PI',[-3.5,-38,78],None),('PBAY_F_AUX',[76,-98.6,54],A.Rotation(V(0,0,1),90)),('PBAY_F_HY',[-95,32,47],None),('PBAY_F_HP',[-40,32,47],None),('PBAY_F_TY',[15,32,47],None)]:move(n,tg,rr)
# F0 whole70x35x26 sourcecase: shortunfusedBAT/XT60leftend, no wireextension.
move('F0_FHAC0002_30A',[102,-18,47],A.Rotation(V(0,1,0),90));move('XT60H_mated_with_boots',[108,1,76]);move('PBAY_POST_F0',[84,-43,45])
# EntireYtailcart+sameMG/horn/bearing/steel, axisnow140/0/130. OldLOWtailfootreplaced, notretainedfloating.
for o in list(D.Objects):
 if hasattr(o,'Shape') and not hasattr(o,'Group') and (o.Name.startswith('TAIL_') or o.Name in ['MG92B_Tail','Tail608']):translate(o.Name,[-45,0,18])
# Selected8inline fromreceivedprimary: actual35.5x8.1x8.9 boxREFERENCE, twoopposedports/leverUP.
inline=[]
for leg,x,y,z,ids in [('FL',-105,-103,87,['W041','W026']),('FR',-105,77,87,['W042','W037']),('RL',81,-103,77,['W044','W045']),('RR',81,77,87,['W052','W053'])]:
 for i,w in enumerate(ids):
  n='NIGHT_INLINE_'+leg+'_'+w;add(n,box(x,y+i*10.1,z,35.5,8.1,8.9),'bought_primary_nominal_cover',(.8,.47,.22));inline.append({'instance':n,'wire_joint':w+'_Joint','source':'WAGO2212411 primary35.5x8.1x8.9','opposedmouths':'sourceknownopposedfaces, individualstopunknown','strip11_sameunit':True})
# FourMTA0100335 areUNMODELED fullgeometry: retireWRONGborrowedWAGObox, visiblequestionmarkdatum not capacityproof.
for i,(x,y) in enumerate([(-113,-92),(-113,90),(117,-92),(117,90)]):
 o=D.getObject('Leg_protected_MTA0100335_'+str(i));o.ViewObject.Visibility=False;retired.append(o.Name+' WRONG_BORROWED_WAGO_BOX')
 q=add('NIGHT_MTA0100335_UNKNOWN_'+str(i),Part.makeSphere(4,V(x,y,124)),'UNBOUND_SELECTED_UNIT_NOT_ENVELOPE',(.85,.65,.15));q.Label='? SELECTED MTA0100335 '+str(i)+' FULLBODY/LID/TETHER/LEADS UNKNOWN'
 unknowns.append({'selected_unit':i,'datum':[x,y,124],'fullgeometry_bound':None,'not_a_conservative_numeric_envelope':True,'sample':'oneactualcomplete10Afuse/lid/tether/twoUNCUTleads'})
D.getObject('E2_Molex_and_inline_WAGO').ViewObject.Visibility=False
# Fewactualrootedconceptmembers, notpartmanufacturingrelease. P01source8axes unchanged.
frame=box(-108,-85,45.52,241,169,3).cut(box(-104,-81,45.5,233,161,3.1))
for y in [-22.5,22.5]:frame=frame.fuse(box(-86,y-3,45.52,214,6,7))
for x in [-100,-45,25,112]:frame=frame.fuse(box(x,-85,45.52,6,169,3))
for y in [-22.5,22.5]:frame=frame.fuse(box(108,y-3,41.52,18,6,4))
for x in [-80,-70,112,122]:
 for y in [-22.5,22.5]:frame=frame.cut(Part.makeCylinder(1.4,15,V(x,y,40)))
add('NIGHT_SHARED_LOAD_GRID',frame)
# SourceP01seat actualplanes; ownheadfixedsaddle receivingbridge usesfixedservo saddle69.5, notrotatingfork.
h=box(-86,18.5,45.52,12,9,21).fuse(box(-147,18.5,66.5,73,9,7)).fuse(box(-147,-13,66.5,28,40.5,3))
add('NIGHT_HEAD_FIXED_SADDLE_ROOT',h)
# Actualnewtail fixedcartridge receiver Y-10 face and110/150 boltlevels, positive-Yroot outsideF0.
r=box(111,18.5,41.52,30,9,7).fuse(box(133,18.5,48.52,8,9,54.48)).fuse(box(133,-18,97,14,45.5,6)).fuse(box(133,-18,100,14,8,56))
for z in [110,150]:r=r.cut(Part.makeCylinder(1.1,10,V(140,-19,z),V(0,1,0)))
add('NIGHT_YTAIL_FIXED_RECEIVER_ROOT',r)
# OpenMTA tierreceivingframes; realclipplane/hardware subordinateprimarydatum/coupon, no fakecasefusion.
for z,tag in [(77,'LOWER'),(115,'UPPER')]:
 f=box(-104,28,z,225,50,3).cut(box(-100,32,z-.1,217,42,3.2))
 for x in [-104,117]:f=f.fuse(box(x,28,48.52,4,50,z-45.52))
 add('NIGHT_MTA_'+tag+'_OPEN_TIER_FRAME',f)
# Grouptransport references: accessiblebranchconnections/counts, notmanufacturingwireaxes or unprovedemptybox.
regions=[('P_SYS_F_PI_FULL10_ENDS',[-93,-44,84,142,32,24],'W0433.1+margin; fivefactorypairselsewhere sourcecomposites; regioncapacityOPEN'),('POSITIVE_BRANCH',[-101,26,68,220,54,10],'6factoryMGends +12MTAheldunits; freeleads adaptive,notrigid'),('NECK_CSI200_FULL',[-230,-30,60,150,55,105],'full200 camera-head-neck-Pi, trueport/roll/motioncapacityOPEN'),('E2_FOUR_FACTORY225',[-95,-16,54,206,42,35],'fourindependentmin220, actualcontactsnot inferredfromcombinedE2box'),('USB_AUDIO_GROVE',[-95,-29,104,191,55,34],'separateunits, no500borrowedforunknownaudio')]
for n,b,note in regions:
 o=add('NIGHT_REGION_'+n,box(*b),'GROUP_OCCUPANCY_PREMISE_NOT_CLEARANCE',(.8,.52,.2));o.ViewObject.Transparency=88;o.ViewObject.Visibility=False;o.addProperty('App::PropertyString','OccupancyNote').OccupancyNote=note
# ProportionalwholeOlaenvelope ALONGSIDEallmodules, no printmass orclosedskinclaim.
def profile(q):
 x,w,c,h=q;k=.8;edges=[]
 for ps in [[(0,h),(k*w,h),(w,k*h),(w,0)],[(w,0),(w,-k*h),(k*w,-h),(0,-h)],[(0,-h),(-k*w,-h),(-w,-k*h),(-w,0)],[(-w,0),(-w,k*h),(-k*w,h),(0,h)]]:
  b=Part.BezierCurve();b.setPoles([V(x,y-7,c+z) for y,z in ps]);edges.append(b.toShape())
 return Part.Wire(edges)
st=[(-137,70,109,48),(-116,96,107,61),(-50,102,107,65),(45,102,107,65),(125,96,105,61),(168,67,107,43),(181,18,111,23)]
env=Part.makeLoft([profile(q) for q in st],True,False);add('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT',env,'PROVISIONAL_APPEARANCE_NOT_MASS',(.15,.17,.2))
# Replaceunselectedgoggles/skins visuallybyONEcoherentheadproportionenvelope, retain allhardmechanism/sensors/goldfullprofile.
for n in ['OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER','LC_ORBIT_CHEEK_FRONT_MASK']:D.getObject(n).ViewObject.Visibility=False
m=A.Matrix();m.A11=62;m.A22=74;m.A33=65;head=Part.makeSphere(1).transformGeometry(m);head.translate(V(-191,0,125))
for y in [-24,24]:
 m=A.Matrix();m.A11=12;m.A22=22;m.A33=15;c=Part.makeSphere(1).transformGeometry(m);c.translate(V(-247,y,112));head=head.fuse(c)
for n in ['CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL','TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL']:head=head.cut(D.getObject(n).Shape)
for y in [-31,31]:head=head.cut(Part.makeCylinder(16.5,50,V(-270,y,131),V(1,0,0)))
add('NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT',head,'PROVISIONAL_APPEARANCE_NOT_MASS',(.12,.14,.16))
# Fullknownsourcecases remainvisible evenwhenprotruding. Unknownselectedunits shownquestionmarks, not renderedawayfit.
r={'status':'ONE_COMPACT_WHOLE_HYPOTHESIS_NOT_FIT_OR_PRINT_RELEASE','moves':moves,'new_structural_concepts':newprints,'retained_mechanism_print_names':keep,'retired_operating_own_features':retired,'inline8':inline,'MTA0100335_fullunknown':unknowns,'head2axes_unchanged':True,'tail_Y_axis':[140,0,130],'tail_fullrigid_delta':[-45,0,18],'tailrange_project_deg':[-15,15],'source12ST3215_legs_126_world_unchanged':True,'source8P01axes_unchanged':True,'body_envelope_profiles':st,'provisional_envelopes_not_material_mass':True,'all57plusADD7functions_retained':'knowngeometry moved; fourMTA0100335 fullUNBOUND andfourE2actualendsnotreplacedbybox; no wholegeometrycoverageclaim','frozen_source6a':'b3c41e4ca129d0939ddef80b98d94fac2b71b658f0cb785b8a0e27edb2d2c476','stillOPEN':['all10factoryFHACends/25WAGOchambers connectedaccessible surpluscapacity','E2fourmin220contact/bothends actualroutebinding','CSI200 fullpath/roll/motion/storedremaining','completeallmodulemounts/tiersclips/wholehardware/tools/closedskin','actualMTA0100335sample andmodulefit/payload/thermal/noPhysicalPASS']}
(P/'whole-organization-effectivity.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save();v=G.activeDocument().activeView();d=V(-1.5,-1,.65);d.normalize();right=V(0,0,1).cross(d);right.normalize();v.setCameraOrientation(A.Rotation(right,d.cross(right),d,'ZXY').Q);v.fitAll();v.redraw();print(json.dumps({'saved':True,'moves':len(moves),'new_structural_concepts':len(newprints),'objects':len(D.Objects),'seconds':time.perf_counter()-t}))
