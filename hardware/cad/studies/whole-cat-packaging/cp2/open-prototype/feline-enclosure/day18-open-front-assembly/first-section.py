"""Read the saved assembly and check the structural and equipment allocations."""
from pathlib import Path
import runpy,json
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf,gp_Ax1,gp_Dir,gp_Pnt
import math
P=Path(__file__).parent
S=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
res={}
def write(): (P/"first-section.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
a=S.shape("OPEN_MG_EXIT_BAND")
common=BRepAlgoAPI_Common(a,S.shape("D18C_P02_THREE_ROOT_THROUGH_VERSION")).Shape();bb=Bnd_Box();BRepBndLib.AddOptimal_s(common,bb,False,False)
res["encroaching_floor_bounds"]=[*bb.CornerMin().Coord(),*bb.CornerMax().Coord()]
res["bearing"]=[]
mov=[n for n in S.members if n.startswith(("YAW_SHAFT_FORK_POSITIVE_CROSSPIN","YAW_HORN_CAP_M2_","YAW_HORN_KEY_HALF","YAW_HORN_ROOF","HEAD_YAW_FORK_FIXED","MG92B_Head_pitch")) and "space" not in n]
for yaw in (0,-20,20):
    tf=gp_Trsf();tf.SetRotation(gp_Ax1(gp_Pnt(-130,0,127),gp_Dir(0,0,1)),math.radians(yaw))
    for n in mov:
        name=n+str(yaw);S.shapes[name]=S.shape(n).Moved(TopLoc_Location(tf))
        q=S.common("OPEN_PORTAL_MATERIAL_SUBSET",name)
        if q.get("bounds_separation_mm",0)<2:res["bearing"].append(dict(yaw=yaw,part=n,**q))
write()
allchecks=[]
audio=["Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD"]
moved=json.loads((P/"open-assembly.json").read_bytes())["moves"]
fixed=["Pi4B_actual_PCB","Pi_components_and_cooling","E1_populated_prototype_board","PCA9685_Adafruit815_PCB","F2_COMMON_PI_BUS_PCA_RECEIVER","MG92B_Tail","BUS25514_installed","CF17_POL1992_FULL_MATED_BODY","CF17_POWER_K1474_SEALED_BOOT_FULL","TTP223_touch"]
fixed += [n for n in S.members if n.startswith(("Motor_ATO4A_","WAGO415_data","FRONT18_FORE_","FRONT18_REAR_"))]
beam=["OPEN_DATA_CROSSBEARER_"+str(i) for i in (0,1)]
for n in list(moved)+["INSERT_AUDIO_USB_A_FULL_MATE_FIELD"]+beam:
    if n.startswith(("INSERT_MIC_ACOUSTIC","INSERT_SPEAKER_ACOUSTIC")):continue
    for neighbor in fixed:
        q=S.common(n,neighbor)
        if q.get("common_mm3",0)>.0001 or "error" in q:allchecks.append(dict(a=n,b=neighbor,**q))
    d=BRepExtrema_DistShapeShape(S.shape(n),S.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"))
    if d.IsDone():
        res.setdefault("data_clearance",{})[n]=d.Value()-3.4
    res["equipment_and_bearers"]=allchecks;write()
print(res["encroaching_floor_bounds"],allchecks)
