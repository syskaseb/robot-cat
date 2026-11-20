"""Run the 20B first clearance screen on the saved 20A world-coordinate BReps."""
import json
import math
from pathlib import Path
from runpy import run_path

import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt

folder = Path(__file__).resolve().parent
source19 = folder.parent / "day19-complete-first-fit"
Saved = run_path(str(folder.parent / "day18-front-insert-correction" / "saved-front.py"))["Saved"]
native = Saved(folder / "whole-cat20A.FCStd")
inventory = json.loads((folder / "20B-native-inlet-inventory.json").read_bytes())["members"]
old_names = json.loads((source19.parent / "day19-shared-open-trunk-and-body-parting" / "space-map.json").read_bytes())["members"]
moved = {"F0_FHAC0002_30A", "PBAY_POST_F0", "XT60H_mated_with_boots"}
lids = {"E19_ForeLid", "E19_RearLid", "F19_ForeCap", "F19_RearCap", "E19_ReSpeakerSource",
        "G19_MIC_C_PlugAllow", "HB_MIC_0_M2x12_full", "HB_MIC_0_fullnut", "HB_MIC_0_nutwasher",
        "HB_MIC_1_M2x12_full", "HB_MIC_1_fullnut", "HB_MIC_1_nutwasher", "E19_BUS_PCB",
        "E19_BUS_population"}
rigid = set(old_names) - moved
rigid |= {"H19_FrontFrame", "E19_RearBase", "BNO085", "WAGO615_power_0_0",
          "Pi_components_and_cooling", "S0_ring_IN_0_0", "OP_S1_PRIMARY_CASE_CONSERVATIVE"}
rigid |= {n for n in inventory if n.startswith("I19_FuseBand_")}
systems = {"Pi_components_and_cooling", "H19_DATA_A_Boot", "G19_PiAudioBoot",
           "G19_MIC_C_PlugAllow"}
regions = {"D19_BODY_CONTROL_TRUNK", "D19_SIDE_BUNDLE_NEG", "D19_SIDE_BUNDLE_POS",
           "D19_JR300_YAW_RESERVE", "D19_JR300_PITCH_RESERVE", "D19_JR300_TAIL_RESERVE",
           "H19_MainTrunk", "H19_PowerBranch", "H19_TailSideTransfer", "G19_Group_BUS",
           "G19_Group_JRP", "G19_Group_JRY", "G19_Group_JRT", "G19_Group_I2S", "G19_Group_POWER"}
rigid |= regions
bounds = {
    "XT60_full_parked": [1, 17, 109, 51, 41, 127],
    "XT60_pack_half_withdrawal": [26, 17, 109, 65, 41, 127],
    "XT60_finger_access": [4, 14, 124, 65, 45, 155],
    "F0_full_closed": [-62, 29, 108, -11, 50, 128],
    "F0_lid_tether_and_fuse_access": [-43, 26, 126, 5, 53, 167],
    "POST_F0_full_closed": [-101, 32.5, 113, -81, 45.5, 123],
    "POST_F0_levers_open": [-100, 31, 123, -81, 47, 140],
    "W075_axial_pocket": [-11, 31, 114, 1, 43, 122],
    "W076_output_approach": [-81, 32, 113, -62, 45, 123],
    "MTA_FL_installed": [-64, -98, 137, -10, -76, 158],
    "MTA_FR_installed": [-64, 75, 128, -10, 97, 149],
    "MTA_RL_installed": [100, -98, 141, 154, -76, 162],
    "MTA_RR_installed": [100, 75, 128, 154, 97, 149],
    "MTA_FL_lid_access": [-58, -98, 158, -16, -76, 181],
    "MTA_FR_lid_access": [-58, 75, 149, -16, 97, 172],
    "MTA_RL_lid_access": [106, -98, 162, 148, -76, 185],
    "MTA_RR_lid_access": [106, 75, 149, 148, 97, 172],
}
import sys
if "raised" in sys.argv:
    # Use the upper axial plane above BNO and the control trunk. The four MTA
    # lands move off the old marker-centered bearing surfaces.
    bounds.update({
        "XT60_full_parked": [1, 22.5, 115, 51, 46.5, 133],
        "XT60_pack_half_withdrawal": [26, 22.5, 115, 65, 46.5, 133],
        "XT60_finger_access": [2, 19, 130, 68, 49.5, 162],
        "F0_full_closed": [-62, 30, 114, -11, 51, 134],
        "F0_lid_tether_and_fuse_access": [-43, 28, 134, 0, 54, 181],
        "POST_F0_full_closed": [-101, 37.25, 119, -81, 50.25, 129],
        "POST_F0_levers_open": [-100, 36, 129, -81, 52, 146],
        "W075_axial_pocket": [-11, 37, 120.5, 1, 44, 127.5],
        "W076_output_approach": [-81, 37, 120.5, -62, 44, 127.5],
        "MTA_FL_installed": [-49, -100, 140, 5, -78, 161],
        "MTA_FR_installed": [-82, 75, 144, -28, 97, 165],
        "MTA_RL_installed": [100, -98, 141, 154, -76, 162],
        "MTA_RR_installed": [141, 60, 140, 195, 82, 161],
        "MTA_FL_lid_access": [-43, -100, 161, -1, -78, 184],
        "MTA_FR_lid_access": [-76, 75, 165, -34, 97, 188],
        "MTA_RL_lid_access": [106, -98, 162, 148, -76, 185],
        "MTA_RR_lid_access": [147, 60, 161, 189, 82, 184],
    })
    lids.update({n for n in rigid if n.startswith("HB_MIC_")})
if "inboard" in sys.argv:
    # Lane defined by the native rear rail, whose first obstruction is y44.7.
    # The fuse tip stays below the front-frame feature beginning at z130.4.
    bounds.update({
        "XT60_full_parked": [1, 18.8, 112.5, 51, 42.8, 130.5],
        "XT60_pack_half_withdrawal": [26, 18.8, 112.5, 65, 42.8, 130.5],
        "XT60_finger_access": [2, 12, 132.3, 68, 47, 161],
        "F0_full_closed": [-70, 30, 111.65, -19, 50, 129.15],
        "F0_lid_tether_and_fuse_access": [-51, 18, 129.15, -5, 41, 175],
        "POST_F0_full_closed": [-106, 36.75, 116.5, -86, 49.75, 126.5],
        "POST_F0_levers_open": [-106, 35, 126.5, -86, 51, 145],
        "W075_axial_pocket": [-19, 32.5, 117.25, 1, 44, 125.75],
        "W076_output_approach": [-86, 36.5, 117.25, -70, 44, 125.75],
        "MTA_FR_installed": [-68, 67.5, 144, -28, 89.5, 165],
        "MTA_FR_lid_access": [-68, 67.5, 165, -28, 89.5, 188],
    })
    rigid.add("B19_ToolEightAnchors")
if "carrier" in sys.argv:
    bounds = {
        "XT60_harness_half_open_stroke": [-13, 18.8, 112.5, 26, 42.8, 130.5],
        "F0_same_carrier_open_stroke": [-84, 30, 111.65, -19, 50, 129.15],
        "POST_F0_same_carrier_open_stroke": [-120, 36.75, 116.5, -86, 49.75, 126.5],
        "W075_same_carrier_open_stroke": [-33, 32.5, 117.25, 1, 44, 125.75],
        "W076_exit_same_carrier_open_stroke": [-100, 36.5, 117.25, -70, 44, 125.75],
        "F0_factory_out_slack_pocket_parked": [-105, 30, 129.5, -71, 59, 162],
        "F0_factory_out_slack_pocket_open_stroke": [-119, 30, 129.5, -71, 59, 162],
        "XT60_inboard_hand_window_open_stroke": [-17, 12, 132.3, 58, 46, 161],
    }
if "pocket" in sys.argv:
    bounds = {
        "F0_out_pocket_above_features": [-105, 30, 134, -71, 59, 166],
        "F0_out_pocket_above_features_open_stroke": [-119, 30, 134, -71, 59, 166],
        "MTA_FR_inboard_lid_access": [-63, 67.5, 165, -28, 89.5, 188],
    }

open_only = {k for k in bounds if k.endswith(("access", "open", "withdrawal", "open_stroke"))}
closed = {k for k in bounds if k not in open_only}
def overlap(b, n):
    a = native.bounds(n)
    return np.all(np.minimum(a[3:], b[3:]) - np.maximum(a[:3], b[:3]) > 1e-5)
def volume(a, b):
    op = BRepAlgoAPI_Common(a, b)
    if not op.IsDone():
        return None
    shape = op.Shape()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return round(abs(props.Mass()), 3)

results = {}
for label, b in bounds.items():
    shape = BRepPrimAPI_MakeBox(gp_Pnt(*b[:3]), gp_Pnt(*b[3:])).Shape()
    touches = []
    for n in sorted(rigid):
        if not overlap(b, n):
            continue
        # The I19 frame has pockets and through openings. Exact common only
        # ranks intersecting rigid boxes for this already named opening hazard.
        v = volume(shape, native.shape(n))
        if v is None or v > 0.1:
            kind = "occupancy region" if n in regions else "connector/cooling allocation" if n in systems else "lid-mounted" if n in lids else "retained body"
            touches.append({"member": n, "kind": kind, "bbox": native.bounds(n).round(3).tolist(), "intersection_mm3": v,
                            "applies_to_pose": label in closed or n not in lids})
    results[label] = touches
    print(label, [(x["member"], x["intersection_mm3"], x["applies_to_pose"]) for x in touches], flush=True)
p = folder / ("20B-pocket-screen.json" if "pocket" in sys.argv else "20B-carrier-screen.json" if "carrier" in sys.argv else "20B-inboard-screen.json" if "inboard" in sys.argv else "20B-raised-screen.json" if "raised" in sys.argv else "20B-first-screen.json")
temp = p.with_suffix(".tmp")
temp.write_bytes((json.dumps({"bounds": bounds, "intersection": results}, indent=2) + "\n").encode())
temp.replace(p)