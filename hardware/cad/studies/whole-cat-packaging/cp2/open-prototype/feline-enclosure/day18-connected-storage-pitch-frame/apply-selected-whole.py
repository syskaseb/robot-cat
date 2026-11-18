import FreeCAD as A, FreeCADGui as G, Part, json, pathlib, datetime
D=A.ActiveDocument; P=pathlib.Path(__file__).parent; V=A.Vector
def write(n,x): (P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode('utf-8'))
newpath=str(P/'connected-storage-pitch-frame.FCStd')
D.saveAs(newpath)
changes=[]
def move(names,old,new,axis=(1,0,0),angle=0,role=''):
 R=A.Rotation(V(*axis),angle); T=A.Placement(V(*new)-R.multVec(V(*old)),R)
 for n in sorted(set(names)):
  o=D.getObject(n)
  if o is None: raise ValueError('missing '+n)
  s=o.Shape; vol=s.Volume; o.Placement=T.multiply(o.Placement); b=o.Shape.BoundBox
  changes.append(dict(name=n,role=role,volume_before=vol,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],transform=T.toMatrix().A))
def select(prefixes,visible=True):
 return [o.Name for o in D.Objects if o.Name.startswith(tuple(prefixes)) and hasattr(o,'Shape') and (not visible or o.ViewObject.Visibility)]
pi=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','CF17_POL1992_FULL_MATED_BODY','CF17_POL1992_FACTORY_END_REGION','CF17_POWER_DELOCK60047_APPROX_FULL','CF17_POWER_K1474_SEALED_BOOT_FULL']+select(['CF17_PI_'],False)
move(pi,[-108,24,125],[-108,-28,98],angle=90,role='WHOLE_FIXED_PI_LOW_HORIZONTAL_ALL_PORTS_STEEL_COOLING')
cam=['Camera3_NoIR_Wide','CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT','CAMERA_SOURCE_OPTICAL_WINDOW_REFERENCE']+select(['CAM_standoff_','CAM_primary_upper_'])
move(cam,[-209.6,0,145],[-164.6,0,145],angle=90,role='WHOLE_CAMERA_CLOCK180_AND_COMPACT_TRUE_PITCH_RECEIVER')
tof=['VL53L5CX','TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT']+select(['TOF_standoff_','TOF_primary_'])
move(tof,[0,0,0],[45,0,0],role='WHOLE_TOF_AND_FULL_TWO_MOUNTSETS')
bus=['BUS25514_installed','N17_PRIMARY_BUS_BOARD_NO_EXTRA_BOM','N17_ALL117_BUS_PRIMARY_EXTENT_REFERENCE_NOT_MATERIAL']+select(['CF17_BUS_CSK10_'])+[o.Name for o in D.Objects if o.Name.startswith('CB_BUS_') and o.ViewObject.Visibility]
move(bus,[-29,-31,116.5],[29,36.5,119],angle=90,role='WHOLE_FIXED_BUS_PORT_PRIMARY_BOARD_AND_FULL_STEEL')
move(['Speaker'],[0,0,0],[33.5,-.5,-2],role='SPEAKER_LOW_ACOUSTIC_UP_FULL_SOURCE')
move(['MAX98357A_amp']+select(['CB_AMP_']),[9,19,111.6],[-20,-43.5,140],angle=-90,role='WHOLE_AMP_VERTICAL_SAFE_HOLE_MOUNTS')
move(['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']+select(['CB_PCA_']),[0,0,0],[12,0,0],role='WHOLE_SOLDERED_PCA_E1_KIT_NO_VIRTUAL_UNPLUG')
move(select(['OP_S1_'],False),[0,0,0],[-50,0,-1],role='WHOLE_S1_OPERATOR_WELL_AND_FULL_STOCK')
move(['PBAY_P_AUX'],[0,0,0],[-58,0,-23],role='P_AUX_OPEN_LOWER_TERMINAL_LAYER')
fore=[]
for o in D.Objects:
 if o.Name.startswith('WAGO415_data_') and o.ViewObject.Visibility and o.Name!='WAGO415_data__1_6':
  b=o.Shape.BoundBox
  if b.XMin<0 and b.ZMin>149: fore.append(o.Name)
move(fore,[0,0,0],[0,0,-18],role='FORE_TERMINALS_SEPARATE_FROM_FULL_DATA500_STORAGE')
# Reverse the COMPLETE standard crosspin set, not a head/tip alone.
move(select(['PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_']),[-135,25,121],[-135,25,121],axis=(0,0,1),angle=180,role='FULL_EXISTING_M2x20_SET_SIDE_NUT_LOADING_AND_PLUS_X_DRIVER')
write('actual-selected-placement-delta.json',changes)
write('progress.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='RIGID_PLACEMENTS_SAVED_BEFORE_NAMED_CHECKS',source_commit='75a7d5450973cdc9698e240ccfcf59a318a96597',source_native_sha='72cb20fb5094806a89973e5ada91d26a7dd47fa04dd602151ac562b5d74f3593',physical_PASS=False))
D.Label='DAY18_CONNECTED_STORAGE_TRUE_PITCH_WORKING'; D.recompute(); D.save()
print('SELECTED_WHOLE_SAVED',len(changes),len(fore))
