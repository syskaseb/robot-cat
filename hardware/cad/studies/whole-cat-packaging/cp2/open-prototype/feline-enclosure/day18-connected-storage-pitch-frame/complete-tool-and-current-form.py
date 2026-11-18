import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
# Ordinary shared tool slot: two useful 2.5mm webs remain in the 14mm arm. No fictitious detached integral arm.
o=D.getObject('D18C_TRUE_PITCH_OPTICAL_RECEIVER');old=o.Shape;slot=Part.makeBox(2.2,15.7,9,V(-144.2,22.3,116.5));o.Shape=old.cut(slot).removeSplitter();o.Shape.exportBrep(str(P/'true-pitch-receiver.brep'))
wr('true-pitch-real-tool-phase.json',dict(removed_for_full4mm_nut_spanner_mm3=old.Volume-o.Shape.Volume,remaining_top_bottom_web_mm=2.5,spanner_PROJECT_head_radius_mm=4.25,spanner_thickness_mm=1.6,feed_open_positive_Y=True,complete_M2x20_head_driver_side='+X BEFORE Pi and body banks',all_four_source_crosspin_parts_retained=True,valid=o.Shape.isValid(),solids=len(o.Shape.Solids),current_volume_mm3=o.Shape.Volume,physical_tool_confirmation='4mm spanner/driver and actual nut sample, no purchased-stock assertion'))
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
def form(n,s,col):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=n+' / PROPOSED_NOT_PRINT_NOT_MASS';o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode='Shaded';return o
for o in D.Objects:
 if o.Name.startswith(('D18B_HEAD_','D18B_GOLD_','D18B_DARK_')):o.ViewObject.Visibility=False
head=ell((-131,0,136),(50,72,65))
for sign in [-1,1]:head=head.fuse(ell((-178,sign*20,112),(15,24,21)))
for n in ['D18C_CAM_MODEL_CLOCK_BOUND_FOV','D18C_TOF_MODEL_CLOCK_BOUND_FOV']:head=head.cut(D.getObject(n).Shape)
form('D18C_HEAD_FACE_CLOCK_BOUND_FORM',head,(.14,.15,.17))
for side in [-1,1]:
 form('D18C_GOLD_RIM_'+str(side).replace('-','m'),ell((-173,side*34,147),(3.5,16,18)),(.65,.43,.13))
 form('D18C_DARK_EYE_'+str(side).replace('-','m'),ell((-176.3,side*34,147),(2.5,12.5,14.5)),(.015,.02,.025))
for n in ['Ola_ear__1','Ola_ear_1']:D.getObject(n).Placement.Base+=V(45,0,0)
# A provisional local shoulder receiving envelope is explicit, no solid capacity counted as print mass.
hood=ell((-75,-16,168),(37,31,29))
form('D18C_LOCAL_NECK_RECEIVING_FORM_NOT_PRINT',hood,(.13,.14,.16))
# Full BUS plug installation reservation stays explicit and conservative, rather than a supplier-exact smaller boot.
o=D.addObject('PartDesign::Feature','D18C_DATA_BUS_FULL26_PROJECT_BOOT');o.Shape=Part.makeBox(26,26,26,V(27.11,-6.804,96.77));o.ViewObject.ShapeColor=(.12,.12,.13)
wr('form-effectivity-and-apertures.json',dict(retired_OWN_unbuilt=['old high hood/arch9fb','D18B_CAMERA_LOAD_RECEIVER line','old HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','old camera clock90 head envelope','old Pi vertical4posts and obsolete BUS/E1 bridge mounts'],new_actual_print_material=['D18C_TRUE_PITCH_OPTICAL_RECEIVER','D18C_COMMON_PI_OPEN_CARRIER','D18C_P02_THREE_ROOT_THROUGH_VERSION'],provisional_not_mass=['D18B_BODY_FORM','D18C_HEAD_FACE_CLOCK_BOUND_FORM','D18C_LOCAL_NECK_RECEIVING_FORM_NOT_PRINT','D18C_GOLD_RIM_*','D18C_DARK_EYE_*'],head_clock_aperture_source='actual-clock-FOV-and-load-binding.json',ears_pose_delta=[45,0,0],still_open=['actual hollow body/head parting and joints','moving neck/shoulder collar no pinch','full ToF/JR occupied motion reserve and actual source grommets','four required full MTA0100335 samples dependent closure','speaker basket and acoustic opening current side orientation','all changed stationary module bearing roots besides realized Pi carrier'],physical_PASS=False))
# Save a concise current major-object metadata set; cached broad bounds, no global exact or volume replay.
names=list(json.loads((P/'current-major-bounds.json').read_text()));meta={}
for n in names:
 o=D.getObject(n)
 if o:
  b=o.Shape.BoundBox;meta[n]=dict(bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],visible=o.ViewObject.Visibility)
wr('final-major-bounds.json',meta)
D.Label='DAY18_CONNECTED_STORAGE_TRUE_PITCH_CONDITIONAL';D.recompute();D.save()
print('WHOLE CURRENT SAVED; form provisional, no whole kit/physical PASS')
