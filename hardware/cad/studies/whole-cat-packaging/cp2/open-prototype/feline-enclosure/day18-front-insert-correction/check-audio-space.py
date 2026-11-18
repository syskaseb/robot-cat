"""Test both full audio allocations, their ports and the changed terminal bank against actual neighbours."""
from pathlib import Path
import json, runpy
import numpy as np
P=Path(__file__).parent
saved=runpy.run_path(str(P/"saved-front.py"))["Saved"](P/"front-insert.FCStd")
delta=json.loads((P/"audio-bay.json").read_bytes())["moves"]
audio=["Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD"]
major=["Pi4B_actual_PCB","Pi_components_and_cooling","Pi_USB_DATA_Delock_mating","CF17_POL1992_FULL_MATED_BODY","F2_COMMON_PI_BUS_PCA_RECEIVER","F3_E1_REMOVABLE_EDGE_KEEPER","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","BUS25514_installed","TTP223_touch","F0_FHAC0002_30A","Battery_GEA223S30X6GT","S0_body","MG92B_Tail","F3_DATA500_HORIZONTAL_COMPLETE_UNIT"]
banks=[n for n in saved.members if n.startswith(("Motor_ATO4A_","FRONT18_FORE_","FRONT18_REAR_"))]
wago=[n for n in delta if n.startswith("WAGO415_")]
r=[]
for i,n in enumerate(audio+wago):
    for other in major+banks+audio[i+1:] + (wago if n in audio else wago[wago.index(n)+1:]):
        if n==other:continue
        pair=saved.common(n,other)
        if pair.get("bounds_separation_mm",0)>3:continue
        r.append(dict(a=n,b=other,**pair))
# Actual source DATA500 polyline and full jacket. The other USB cable has its
# own acceptance interval and neither consumes nor borrows the BUS data stock.
primary=P.parent/"day18-closed-whole-common-assembly"
plan=json.loads((primary/"DATA500-horizontal-stock-plan.json").read_bytes())
# A static regional budget uses unobstructed orthogonal axes as a conservative
# distance estimate. Corners and wire occupancy remain an installation gate.
def budget(pts):
    return float(np.abs(np.diff(np.array(pts),axis=0)).sum())
usb_pts=[[-1,21,107],[4,21,107],[4,21,145],[4,-45,145],[-9,-45,145],[-9,-45,157],[17,-45,157]]
btl_pts=[[21,8,151],[21,23,151],[0,23,151],[0,39,151],[6,39,155]]
summary=dict(affected_near_pairs=r,source_DATA500_length=500,source_DATA500_plan=list(plan)[:8],
             USB_AUDIO=dict(port_to_port_region=usb_pts,regional_length_upper=budget(usb_pts),conditional_total_requirement="free jacket plus two real connector engagements, bend/assembly slack and shoe storage; USB-A and -C source plugs/length unbound",raw=None),
             BTL=dict(group=["EXT023 AMP.OUT+ to Speaker+","EXT024 AMP.OUT- to Speaker-"],region=btl_pts,
                      regional_length_upper=budget(btl_pts),end_debits="actual amp and basket ends, contact and screw/strip allowances unbound",raw=None),
             actual_fit=None,physical_PASS=False)
(P/"audio-space-check.json").write_bytes((json.dumps(summary,indent=1)+"\n").encode())
print("Positive material/capacity witnesses",[(q["a"],q["b"],round(q["common_mm3"],2)) for q in r if q.get("common_mm3",0)>.0001])
