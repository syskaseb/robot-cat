"""One coarse low whole allocation, preserving source shapes and physical unit identities."""
from pathlib import Path
import json,math,datetime,traceback
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;S=A.getDocument("whole_front");V=A.Vector
assert Path(S.FileName).resolve()==(P/"whole19.FCStd").resolve()
state=P/"make-low-layout.state.json"
def status(phase,**kw):state.write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,**kw),indent=1)+"\n").encode())
status("copying")
visible=json.loads((P/"source-visible-actors.json").read_bytes())["rows"]
modules=["WAVEGO_complete_126_source_solids","P01_load_rail","P01_load_rail_instance2","F0_FHAC0002_30A","Battery_GEA223S30X6GT","XT60H_mated_with_boots","Pi4B_actual_PCB","Pi_USB_DATA_Delock_mating","PCA9685_Adafruit815_PCB","BUS25514_installed","E1_populated_prototype_board","MAIN_Pololu4853","AUX_Pololu4092","Monitor_MOD05015","Speaker","BNO085","MAX98357A_amp","ReSpeakerLite_on_REMOVABLE_back","TTP223_touch","Camera3_NoIR_Wide","VL53L5CX","MG92B_Head_yaw","MG92B_Head_pitch","MG92B_Tail","Yaw608_120","Yaw608_134","Tail608","Pitch688","D18C_TRUE_PITCH_OPTICAL_RECEIVER","BR_FINISHED_YAW_SADDLE","BR_PAIR_HY","BR_FLANK_HP_PAIR","BR_FLANK_THREE_LAPS","BR_COMMON_OPTICAL_MASK","BR_PARTED_SKULL_BACK"]
prefixes=("WAGO415_","WAGO615_","PBAY_","Motor_ATO","NIGHT_INLINE_","NIGHT_MTA0100335_","YAW_","PITCH_","TAIL_","CAM_","TOF_","CB_","CF17_PI_","CF17_POL1992_","CF17_POWER_","CF17_BUS_CSK","F3_MAIN_","F3_AUX_","F3_HEAD_","HB_MIC_","OP_S1_","OP_MONITOR_","S0_","H01_source_")
names=set(modules)
for q in visible:
    n=q["name"]
    if q["type"]!="PartDesign::Feature":continue
    if n.startswith(prefixes) and "RETIRED" not in q["label"] and "REMOVABLE" not in n and "REFERENCE_NOT_BOM" not in n:names.add(n)
# Current primary port outlines and the complete Pi cooling allocation are separate from hard material.
for o in S.Objects:
    if o.Name.startswith("CF17_PI_PRIMARY_"):names.add(o.Name)
names.add("Pi_components_and_cooling")
names.update(("CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT","D18C_DATA_BUS_FULL26_PROJECT_BOOT"))
# Printed mechanisms selected by source role, kept complete until the whole-interface gate.
for n in ("YAW_REAL_REMOVABLE_SERVO_SADDLE","PITCH_REAL_REMOVABLE_SERVO_SADDLE","TAIL_REAL_REMOVABLE_SERVO_SADDLE","TAIL_FIXED_BEARING_CARTRIDGE","TAIL_ROTATING_HOLLOW_REAL_ROOT"):names.add(n)
# Retired original whole fork is already included in the finished yaw saddle.
names.discard("WAGO415_data_1_0")
N=A.getDocument("cat19") or A.newDocument("cat19");records=[]
for n in sorted(names):
    src=S.getObject(n)
    if not src or not hasattr(src,"Shape") or src.Shape.isNull():continue
    o=N.getObject(n) or N.addObject("PartDesign::Feature",n);o.Shape=src.Shape.copy();o.Label=src.Label
    o.ViewObject.ShapeColor=src.ViewObject.ShapeColor;o.ViewObject.DisplayMode="Shaded"
    if "DiffuseColor" in src.ViewObject.PropertiesList:o.ViewObject.DiffuseColor=src.ViewObject.DiffuseColor
    a=src.Shape.BoundBox;b=o.Shape.BoundBox
    # BoundBox can use a different cached tessellation after copying a curved face.
    # Match its rigid placement and volume, then check the named supplier datum.
    assert max(abs(x-y) for x,y in zip(src.Placement.toMatrix().A,o.Placement.toMatrix().A))<1e-7,n
    assert abs(src.Shape.Volume-o.Shape.Volume)<max(1e-5,abs(src.Shape.Volume)*1e-7),n
    if "SourceIdentity" not in o.PropertiesList:o.addProperty("App::PropertyString","SourceIdentity")
    o.SourceIdentity=n
    kind="source_component_or_full_hardware"
    if n.startswith(("NIGHT_MTA010","CF17_PI_PRIMARY","CF17_POWER")) or n in ("Pi_components_and_cooling","BUS25514_installed","Pi_USB_DATA_Delock_mating","CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT","D18C_DATA_BUS_FULL26_PROJECT_BOOT"):kind="source_capacity_or_unmeasured_unit"
    if "EvidenceKind" not in o.PropertiesList:o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=kind
    o.ViewObject.Visibility=not n.startswith("CF17_PI_PRIMARY") and n not in ("Pi_components_and_cooling","CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT")
    records.append(dict(name=n,kind=kind,source_visible=src.ViewObject.Visibility,source_volume=src.Shape.Volume))
assert N.getObject("WAGO415_data_1_0") is None
assert len([o for o in N.Objects if o.Name.startswith("Motor_ATO")])==12
assert len([o for o in N.Objects if o.Name.startswith("WAGO415_")])+1==16
assert abs(N.VL53L5CX.Shape.BoundBox.XMin+208.566)<1e-4
N.recompute();N.saveAs(str(P/"whole-cat19.FCStd"))
(P/"actor-effectivity.json").write_bytes((json.dumps(dict(source_native="day18-body-reception-and-closed-fit/body-reception.FCStd",source_sha256="486abd0561488c91ea7d09344476c3b63c636c5f785238faa34ac36f7bf910d4",selected=records,retired_alias={"WAGO415_data_1_0":"PBAY_P_AUX"},physical_PASS=False),indent=1)+"\n").encode())
A.closeDocument(S.Name);A.setActiveDocument(N.Name)
status("relocating")
D=N;moves=[]
def bounds(o):
    b=o.Shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def move_group(names,target=None,rotation=None,delta=None):
    os=[D.getObject(n) for n in names if D.getObject(n)]
    assert os,names
    before={o.Name:bounds(o) for o in os}
    T=A.Placement(V(),rotation or A.Rotation())
    if rotation:
        for o in os:o.Placement=T.multiply(o.Placement)
    if target is not None:
        b=Part.makeCompound([o.Shape for o in os]).BoundBox
        offset=V(*target)-V(b.XMin,b.YMin,b.ZMin)
    else:offset=V(*(delta or [0,0,0]))
    for o in os:o.Placement.Base+=offset
    moves.append(dict(names=[o.Name for o in os],before=before,after={o.Name:bounds(o) for o in os},old_routes_unqualified=True))
def pref(*ps):return [o.Name for o in D.Objects if o.Name.startswith(ps)]
# Lay twelve complete fuseholders at one height along both flanks.
for side in (-1,1):
    pref0="Motor_ATO4A_1_" if side==1 else "Motor_ATO4A__1_"
    for i in range(6):
        move_group([pref0+str(i)],target=[-105+74*(i%3),side*68-24+24*(i//3),77],rotation=A.Rotation(V(0,1,0),90))
# PCA and E1 remain one soldered assembly, with all current source mounting metal.
board=["PCA9685_Adafruit815_PCB","E1_populated_prototype_board"]+pref("CB_PCA_","F3_E1_CAP_")
move_group(board,target=[-17,-20,111],rotation=A.Rotation(V(1,0,0),90))
# Two small regulators lie low above the battery, full source geometry and hardware moved together.
move_group(["MAIN_Pololu4853"]+pref("CB_MAIN_","F3_MAIN_"),target=[17,-29,80],rotation=A.Rotation(V(1,0,0),90))
move_group(["AUX_Pololu4092"]+pref("CB_AUX_","F3_AUX_"),target=[56,-25,89],rotation=A.Rotation(V(1,0,0),90))
# Preserve the real paired P_REAR/F_AUX short-tail relationship exactly.
# Lay all other data WAGOs on top of the flank holders, with exposed levers.
bank=[o.Name for o in D.Objects if o.Name.startswith("WAGO415_")]
for i,n in enumerate(sorted(bank)):
    side=-1 if i<8 else 1;j=i%8
    move_group([n],target=[-103+32*(j%7),side*65-11,111+11*(j//7)],rotation=A.Rotation(V(1,0,0),90))
# Audio is a lower rear removable tray, isolated from the neck flex workspace.
audio=["Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp"]+pref("CB_AMP_","HB_MIC_")
# Preserve speaker and microphone profiles, permit new allocation inside one accessible tray.
move_group(["Speaker"],target=[10,-24,139],rotation=A.Rotation(V(0,0,1),90))
move_group(["ReSpeakerLite_on_REMOVABLE_back"]+pref("HB_MIC_"),target=[-4,-18,125],rotation=A.Rotation(V(0,0,1),90))
move_group(["MAX98357A_amp"]+pref("CB_AMP_"),target=[67,-42,121])
# BUS, BNO and operator board occupy independent low lands.
move_group(["BUS25514_installed","D18C_DATA_BUS_FULL26_PROJECT_BOOT"]+pref("CB_BUS_","CF17_BUS_CSK"),target=[-18,9,78])
move_group(["BNO085"]+pref("CB_BNO_"),target=[39,13,98],rotation=A.Rotation(V(1,0,0),90))
move_group(["TTP223_touch"],target=[-30,-12,144])
move_group(["Monitor_MOD05015"]+pref("OP_MONITOR_"),target=[-1,25,81])
# Fixed whole primary source fields keep their port identities.
(P/"whole-layout-transforms.json").write_bytes((json.dumps(dict(moves=moves,physical_PASS=False,actual_cuts=None,installed_slack=None),indent=1)+"\n").encode())
N.recompute();N.save()
rows=[]
for o in D.Objects:
    if hasattr(o,"Shape"):rows.append(dict(name=o.Name,bounds=bounds(o),volume=o.Shape.Volume,kind=o.EvidenceKind))
(P/"low-actors.json").write_bytes((json.dumps(rows,indent=1)+"\n").encode())
status("idle",objects=len(D.Objects),native_saved=True)
print("LOW_WHOLE19_SAVED",len(D.Objects))
