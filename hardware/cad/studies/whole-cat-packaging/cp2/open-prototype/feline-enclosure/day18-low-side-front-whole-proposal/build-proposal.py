import FreeCAD as A, Part, json, pathlib, math
D=A.ActiveDocument; V=A.Vector
P=pathlib.Path(__file__).parent
base=json.loads((P/'source-object-metadata.json').read_text()); B={x['name']:x for x in base}
trans=[]
def bb(o):
 b=o.Shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def move(names,T,role):
 for n in names:
  o=D.getObject(n)
  if not o or not hasattr(o,'Shape'):continue
  before=bb(o);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement)
  trans.append(dict(name=n,role=role,before=before,after=bb(o),volume_before=vol,volume_after=o.Shape.Volume,placement=o.Placement.toMatrix().A))
def shift(names,d,role):move(names,A.Placement(V(*d),A.Rotation()),role)
pi=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','CF17_POL1992_FULL_MATED_BODY','CF17_POL1992_FACTORY_END_REGION','CF17_POWER_DELOCK60047_APPROX_FULL','CF17_POWER_K1474_SEALED_BOOT_FULL']+[n for n in B if n.startswith('CF17_PI_')]
R=A.Rotation(V(1,0,0),-90);O=V(-126,-28,145);N=V(-108,24,125)
T=A.Placement(N-R.multVec(O),R);move(pi,T,'PI_FIXED_POSITIVE_INNER_SIDE; PCB source origin transformed once')
shift(['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']+[n for n in B if n.startswith('CB_PCA_')],(0,-19,0),'WHOLE_SOLDERED_PCA_E1; no virtual unplug')
bus=['BUS25514_installed','N17_PRIMARY_BUS_BOARD_NO_EXTRA_BOM','N17_ALL117_BUS_PRIMARY_EXTENT_REFERENCE_NOT_MATERIAL']+[n for n in B if n.startswith('CF17_BUS_CSK10_') or (n.startswith('CB_BUS_') and (n.endswith('PCBwasher') or n.endswith('_nut')))]
shift(bus,(-6,-29.5,-8.5),'BUS_WHOLE_SECOND_FACE; new mount concept required')
shift(['MAX98357A_amp']+[n for n in B if n.startswith('CB_AMP_')],(25,45,27),'AMP_COMMON_TOP_PLANE')
shift(['ReSpeakerLite_on_REMOVABLE_back']+[n for n in B if n.startswith('HB_MIC_')],(10,-2,-13),'MIC_COMMON_REMOVABLE_TOP_PLANE')
shift(['TTP223_touch']+[n for n in B if n.startswith('TOUCH_M2')],(23,33,-13),'TOUCH_SIDE_TOP')
# Full speaker is horizontal above the common controls, not across the S0 body.
R=A.Rotation(V(1,0,0),90);old=V(-50,95,122.5);new=V(42,0,155.5)
move(['Speaker'],A.Placement(new-R.multVec(old),R),'SPEAKER_FULL100x45x21; acoustic normal +Z, basket trial mount pending')
for n in B:
 if n.startswith('Motor_ATO4A_'):
  b=B[n]['bounds'];positive=b[1]<40;target=57 if positive else -78.8486
  shift([n],(0,target-b[1],0),'FULL_MTA_TE_ATO_SYMMETRIC_3X2_LEVEL_SIDE_BANKS')
shift(['PBAY_P_SYS'],(62.5,29.5,-44),'P_SYS; five assigned chambers unchanged')
shift(['PBAY_F_PI'],(62.5,-10,-12),'F_PI input on outward +X; full case unchanged')
shift(['PBAY_P_AUX'],(0,0,6),'P_AUX above P_SYS and below F_PI')
shift([n for n in B if n.startswith('OP_S1_')],(-108,0,0),'S1_FRONT_OPERATOR_FACE; whole case/stem/lever/nuts')
# Keep all four power 615 units; existing rear pair, S0, battery and F0 remain fixed.
for n in B:
 if n.startswith('WAGO415_data') and B[n]['visible']:
  shift([n],(0,0,150-B[n]['bounds'][2]),'SIXTEEN_WAGO415_UPPER_OPEN_HANDLAY_LAYER')
# Camera optical clock restored to down-facing FFC. Full optical axis stays fixed.
R=A.Rotation(V(1,0,0),180);C=V(-209.6,0,145)
cam=['Camera3_NoIR_Wide','CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT','CAMERA_SOURCE_OPTICAL_WINDOW_REFERENCE']+[n for n in B if n.startswith('CAM_standoff_') or n.startswith('CAM_primary_upper_')]
move(cam,A.Placement(C-R.multVec(C),R),'CAMERA_CLOCK0; optics axis unchanged; carrier replacement proposed')
# Withdraw obsolete own mount/guard roles; keep their shapes and raw failures in this native.
withdraw=[]
exact=['A17_INTEGRAL_FRONT_DECK_AND_N1','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','FORE_MTA_REMOVABLE_UPPER_RECEIVER','OP_COMMON_REMOVABLE_OPERATOR_PANEL','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER','TOUCH_REMOVABLE_SAFE_EDGE_TRAY','CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE']
for n in B:
 if n in exact or n.startswith(('FU17_','N17_FFC200_OCCUPIED','CF17_ToF4_OCCUPIED','CF17_SHARED_FIXED','CF17_REMOVABLE_COMMON','CF17_POWER_INDEPENDENT','CF17_ROOT_','CF17_POWER_0_','CF17_POWER_1_','FORE_UPPER_','FORE_MTA_BASE_','CJ_','OP_LEFT_','OP_RIGHT_','SPKR_M2','CB_PSYS_','INT_PI','CARRIER_front_','ROW_POS_','ROW_NEG_','BNO__')):
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False;withdraw.append(n)
# Analytical references hidden for opaque views, not deleted or counted as print material.
for n in B:
 if any(k in n for k in ['OCCUPIED','REFERENCE_NOT_PRINT','STOCK_REGION','STOCK_RING','CONNECTED_COVER']):D.getObject(n).ViewObject.Visibility=False
# A source floor reference preserves the electronics bottom in the proposal; no new load qualification.
for n in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=True
G=D.addObject('App::DocumentObjectGroup','D18_PROPOSAL_NOT_PRINT_NOT_MASS')
def obj(n,s,c,alpha=0):
 o=D.addObject('PartDesign::Feature',n);o.Label=n+' / PROPOSAL_NOT_PRINT_NOT_MASS';o.Shape=s;G.addObject(o);o.ViewObject.ShapeColor=c;o.ViewObject.Transparency=alpha;return o
# Bounded station sections. No offset shell or control-point overshoot.
stations=[(-147,33,139),(-125,85,165),(-90,105,177),(-25,110,184),(45,110,184),(105,104,177),(145,88,163),(178,30,105)]
w=[]
for x,ry,top in stations:
 pts=[]
 for i in range(33):
  t=math.pi*i/32;y=ry*math.copysign(abs(math.cos(t))**.7,math.cos(t));z=48+(top-48)*math.sin(t)**.7;pts.append(V(x,y,z))
 pts+=[pts[0]];w.append(Part.Wire(Part.makePolygon(pts).Edges))
body=obj('D18_BODY_FORM_ONLY',Part.makeLoft(w,True,False),(0.12,.13,.15))
# Provisional volumetric head, open real optical corridor; no print/mass claim.
s=Part.makeSphere(1);m=A.Matrix();m.A11=67;m.A22=72;m.A33=69;s=s.transformGeometry(m);s.translate(V(-193,0,136))
# optical path toward -X, clear both complete optics and their view cones for planning
for x,y,z,rad in [(-209.6,0,145,17),(-229,0,103,18)]:
 s=s.cut(Part.makeCone(rad+35,rad,65,V(x-65,y,z),V(1,0,0)))
head=obj('D18_HEAD_FORM_ONLY',s,(.14,.15,.17))
for n in ['Ola_ear__1','Ola_ear_1','Ola_eye_gold__1','Ola_eye_gold_1','DECORATIVE_BLACK_EYE__1','DECORATIVE_BLACK_EYE_1','Ola_muzzle']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=True
# Free conductor representation: connected local capacity bands, not full cable sweeps.
regions=[]
def region(n,lo,hi,count,profile,role):
 s=Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],V(*lo));o=obj(n,s,(.15,.65,.8),80);o.ViewObject.Visibility=False
 regions.append(dict(name=n,lo=lo,hi=hi,count=count,profile=profile,role=role,status='CAPACITY_PROPOSAL_NOT_CLEARANCE_PROOF'))
region('D18_FFC_SIDE_APPROACH',[-204,-10,106],[-115,54,151],1,'16.8x1.8; innerR12.5','moving camera-down to positive side; source range preserved')
region('D18_FFC_FIXED_CSI_LANDING',[-115,30,102],[-60,54,139],1,'16.8x1.8; distributed quarter-roll','Pi CSI front of components, real cooler/connector bench required')
region('D18_TOF_JR_SHARED_FLEX',[-218,-63,81],[-95,24,148],4,'ToF10.4x2.9/R31.5; JR distinct full ends','open underside/negative neck; fixed yaw and yaw-only pitch branches')
region('D18_DATA500_R30_BAY',[34,-26,76],[107,-14,145],1,'R>=30; full selected500','stationary turns plus connected ports; occupied stock upper not yet qualified')
(P/'whole-placement-delta.json').write_text(json.dumps(dict(transforms=trans,withdrawn_own_unbuilt_roles=withdraw,regions=regions,body_stations=stations,new_print_material=False),indent=2),encoding='utf-8')
D.recompute();D.Label='DAY18_LOW_SIDE_FRONT_WHOLE_PROPOSAL';D.save()
print('WHOLE_PROPOSAL_SAVED',len(trans),'rigid object transforms; no new print material')
