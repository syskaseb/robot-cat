"""Read the pinned 20C world geometry and screen only the axial-X delta."""
from pathlib import Path
from runpy import run_path
import hashlib
import json
import math
import os

import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex,BRepBuilderAPI_Transform
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Ax1,gp_Dir,gp_Trsf

folder=Path(__file__).resolve().parent
src=folder.parent/"20C"/"whole-cat20C.FCStd"
sha=hashlib.sha256(src.read_bytes()).hexdigest()
assert sha=="92fc832c49983ce98cd8d0c7b182f126481d2aff89de36a9c76ee67842985059"
study=folder.parent.parent
source=run_path(str(study/"day18-front-insert-correction"/"saved-front.py"))["Saved"](src)
dl=run_path(str(folder/"layout.py"))
b=dl["wire_budgets"]()
lids={"E19_ForeLid","E19_RearLid","F19_ForeCap","F19_RearCap","Speaker","E19_ReSpeakerSource"}
real=["H19_FrontFrame","E19_RearBase","E19_UpperYawCover","D19D_YawSaddle","D19D_PitchBack","MG92B_Head_pitch",
      "C20_BatteryUpperBridge","E19_BatteryDoor","BNO085","Pi4B_actual_PCB","AUX_Pololu4092","MAIN_Pololu4853",
      "PCA9685_Adafruit815_PCB","MAX98357A_amp","PBAY_P_AUX","WAGO615_power_0_0","E19_WagoForePos",
      "E19_WagoRearPos","E19_WagoForeNeg","C20_MTA_FL","C20_MTA_FR","C20_MTA_RL","C20_MTA_RR",
      "Motor_ATO4A_1_2","Motor_ATO4A_1_5","B19_ToolEightAnchors","PBAY_F_PI",
      "F3_AUX_0_FULL_M2x16","F3_AUX_1_FULL_M2x16","F3_AUX_2_FULL_M2x16","S0_body",*sorted(lids)]
reservation=["Pi_components_and_cooling","G19_Group_JRP","G19_Group_JRY","G19_Group_JRT",
             "D19_SIDE_BUNDLE_POS","H19_MainTrunk","D19_BODY_CONTROL_TRUNK","D19_JR300_YAW_RESERVE",
             "D19_AUX_POPULATED_9P5_RESERVE","G19_Group_POWER","H19_PowerBranch"]
retired_current_design={"C20_F0_OpenMount","C20_Post_OpenSlottedMount","XT60H_mated_with_boots",
                        "C20_Pack_XT60_F","C20_Pack_XT60_Stroke","F0_FHAC0002_30A","PBAY_POST_F0"}
def make_box(r):
    return BRepPrimAPI_MakeBox(gp_Pnt(*r[:3]),gp_Pnt(*r[3:])).Shape()
def get_bounds(s):
    q=Bnd_Box();BRepBndLib.AddOptimal_s(s,q,False,False)
    return np.r_[q.CornerMin().Coord(),q.CornerMax().Coord()]
def vols(a,b):
    op=BRepAlgoAPI_Common(a,b)
    if not op.IsDone():return None
    p=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),p)
    return round(p.Mass(),4)
def intersects(a,b):
    return bool(np.all(np.minimum(a[3:],b[3:])-np.maximum(a[:3],b[:3])>1e-4))
def classify(box,opened):
    q=np.array(box);shape=make_box(box)
    d={}
    for n in real+reservation:
        if opened and (n in lids or (box[4]>100 and n in {"E19_BatteryDoor","C20_BatteryUpperBridge"})):continue
        if not intersects(q,source.bounds(n)):continue
        hit=vols(shape,source.shape(n))
        if hit is None or hit>.05:
            d[n]={"volume_mm3":hit,"type":"reserved occupation" if n in reservation else "hard geometry"}
    return d
areas={
    "stationary_full_XT60H_M":(dl["BOX_M"],False),
    "parked_full_pack_F":(dl["BOX_F"],False),
    "full_factory_F_14mm_linear_sweep":(dl["BOX_SWEEP"],True),
    "grip_on_installation":(dl["HAND_M"],True),
    "grip_on_pack_full_travel":(dl["HAND_F"],True),
    "hand_approach_from_open_top":(dl["HAND_F_UPPER"],True),
    "pack_half_manual_hold":(dl["STOW"],True),
    "closed_F0_complete_21p5":(dl["F0"],False),
    "open_F0_cap_and_hands":(dl["F0_OPEN"],True),
    "POST_full_adjustment":(dl["POST_SWEEP"],False),
    "POST_lever_and_end_access":(dl["POST_ACCESS"],True),
    "short_W075":([-20,27.4,142.5,dl["FIXED_X"],32.85,152],False),
    "small_full_factory_plug_parked":(dl["SMALL_PLUG"],False),
    "small_full_factory_plug_supported_throat":([69,55.2,53,93,105.6,67],True),
    "unplugged_full_F_passage_through_throat_from_20C":([67,53,54,93,104,71.5],True),
}
structural={n:{"bbox_mm":bb,"lid_removed":o,"intersections":classify(bb,o)} for n,(bb,o) in areas.items()}
print("full parts",[(k,v["intersections"]) for k,v in structural.items()],flush=True)
# Named upper rear web, AUX board edge, BNO and PCA face. These checks
# use actual surfaces because a bundle box overlaps several unused corners.
named=["AUX_Pololu4092","BNO085","PCA9685_Adafruit815_PCB","E19_RearBase","E19_RearLid",
       "E19_ForeLid","H19_FrontFrame","Motor_ATO4A_1_2","Battery_GEA223S30X6GT",
       "PBAY_F_PI","F3_AUX_0_FULL_M2x16","F3_AUX_1_FULL_M2x16","F3_AUX_2_FULL_M2x16",*reservation]
def jacket_gap(points,which,stride=5):
    results={}
    for n in which:
        bb=source.bounds(n)
        # Compare only the samples near that surface.
        ps=[v for v in points[::stride] if np.all(v>=bb[:3]-12) and np.all(v<=bb[3:]+12)]
        if not ps:continue
        s=source.shape(n)
        distances=[]
        for p in ps:
            op=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Shape(),s)
            if op.IsDone():
                if n=="Battery_GEA223S30X6GT" and p[0]<dl["EXIT_X"]+2.5:continue
                distances.append(op.Value()-2.4)
        if distances:results[n]=round(min(distances),3)
    return results
pack_profiles={}
for label,d,shift in dl["PACK_POSES"]:
    pp=dl["nominal_pack_curve"]("plus",d,shift)
    nn=dl["nominal_pack_curve"]("minus",d,shift)
    both=np.linalg.norm((pp[::3,None,:]-nn[None,::3,:]),axis=2)
    names=[n for n in named if label=="parked" or n not in lids]
    pack_profiles[label]={"inter_jacket_gap_mm":round(float(both.min())-4.8,3),
                          "positive":jacket_gap(pp,names),
                          "negative":jacket_gap(nn,names)}
print("delta pack profiles",pack_profiles,flush=True)
# Only the changed stations are near the head. Use the original kinematics
# and the selected sweep, with exact overlap on AABB candidates.
affected=np.array([-119,-56,137,-103,9,163.5],float)
root=np.array([-113,-39.2,107.4,-100.8,-26.4,120.7],float)
upright=np.array([-104.65,-39.2,118.,-100.8,-34.6,139.9],float)
fuse_near=np.array([-73,18,131,-19,51,156],float)
actors={"yaw":["E19_UpperYawCover","D19D_YawSaddle","BR_FLANK_HP_PAIR","MG92B_Head_pitch"],
        "pitch":["D19D_PitchBack","D19D_OpticsCarrier","D19D_Face","Camera3_NoIR_Wide","VL53L5CX"]}
motion=[]
def rotated(n,a,p,owner):
    t=gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(-130,0,127),gp_Dir(0,0,1)),math.radians(a))
    if owner=="pitch":
        u=gp_Trsf();u.SetRotation(gp_Ax1(gp_Pnt(-159,0,121),gp_Dir(0,1,0)),math.radians(p))
        t.Multiply(u)
    return BRepBuilderAPI_Transform(source.shape(n),t,False).Shape()
for y in (-20,-10,0,10,20):
    for owner,names in actors.items():
        for pitch in ((-10,0,10) if owner=="pitch" else (0,)):
            for n in names:
                s=rotated(n,y,pitch,owner)
                sb=get_bounds(s)
                for key,bb in (("POST",affected),("POST_low_foot_and_arm",root),("POST_aft_upright",upright),("F0",fuse_near)):
                    if not intersects(bb,sb):continue
                    v=vols(s,make_box(bb))
                    if v is None or v>.05:motion.append({"station":key,"actor":n,"yaw":y,"pitch":pitch,"intersection_mm3":v})
print("normal motion witnesses",motion,flush=True)
def write(path,value):
    t=path.with_suffix(".tmp")
    with t.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")
    os.replace(t,path)
write(folder/"20D-final-gate.json",{
    "basis":{"source_sha256":sha,"reviewed_source":"57e29fc2cc1f2a8f136d4266d51a1e59a64e2200",
             "coordinate_datum":"original world coordinates verified by Saved VLC53L5CX datum"},
    "actual_input":"01a1f975-9551-7b13-8ba2-af112b5d1030","installed_method":"fixed axial X; pack held level, only its loose half slides +X",
    "areas":structural,"sampled_pack_profiles":pack_profiles,"affected_head_motion":motion,
    "closed_source_clearance_reused":"20C open throat, upper bridge and MTA untouched. Close-in position of separate protruding plugs checked in 20D; continuous manual transfer with the pack remains physical.",
    "battery_exit_basis":{"selected_sku":"GEA223S30X6GT","photo_sha256":"0c4f0c2736dc73bf55bf4088aa4a5856e16b1093080c8e51482a63d2fdcda69c",
      "orientation":"short end +X and power exit towards upper inboard corner, planning hypothesis only",
      "start_yz":[[29.15,69],[23.85,69]],"selected_fixed_connection_x":dl["FIXED_X"],
      "outer_x_apex_range":[115,123.8],"small_plug_parked_proxy_mm":dl["SMALL_PLUG"]},
    "replaced_installed_envelopes":sorted(retired_current_design),"physicalPASS":False,"actualfit":None,"cut":None,"slack":None,
    "wire_budgets":b,
})