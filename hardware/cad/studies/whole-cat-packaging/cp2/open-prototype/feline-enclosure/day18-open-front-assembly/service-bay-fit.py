"""Test the whole existing monitor and retained keeper at the fixed battery service bay."""
from pathlib import Path
import json,math,runpy
import numpy as np
from OCP.gp import gp_Trsf,gp_Vec,gp_Ax1,gp_Pnt,gp_Dir
from OCP.TopLoc import TopLoc_Location
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
def shift(v):
    m=gp_Trsf();m.SetTranslation(gp_Vec(*v));return m
def rotation(ax):
    m=gp_Trsf();m.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(*ax)),math.pi/2);return m
rx=rotation([0,0,1]).Multiplied(rotation([0,1,0]))
center=np.array([19.,36.,82.5]);bb=D.bounds("Monitor_MOD05015")
m=shift(center).Multiplied(rx).Multiplied(shift(-(bb[:3]+bb[3:])/2))
keep=shift(np.array([19.,45.,89.5])-np.array([128.5,-90.5,134.]))
parts={}
for n in ["Monitor_MOD05015"]+[n for n in D.members if n.startswith("OP_MONITOR_")]:
    trial="trial_"+n;D.shapes[trial]=D.shape(n).Moved(TopLoc_Location(m if n=="Monitor_MOD05015" else keep));parts[trial]=D.bounds(trial).tolist()
neighbors=["Battery_GEA223S30X6GT","F0_FHAC0002_30A","F2_COMMON_PI_BUS_PCA_RECEIVER","BUS25514_installed","PBAY_P_REAR","PBAY_F_AUX",
          "PCA9685_Adafruit815_PCB","Pi4B_actual_PCB","OPEN_SINGLE_FRONT_FLOOR","OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_BATTERY_DOOR",
          "NIGHT_INLINE_RR_W052","NIGHT_INLINE_RR_W053"]+[n for n in D.members if n.startswith("Motor_ATO4A_")]
hits=[]
for name in parts:
    for n in neighbors:
        c=D.common(name,n)
        if c.get("common_mm3",0)>.001 or "error" in c:hits.append(dict(a=name,b=n,**c))
(P/"service-bay-fit.json").write_bytes((json.dumps(dict(parts=parts,positive_or_unresolved=hits,
    intended="Whole voltage monitor above battery, read with top removed and leave factory balance connector attached until pack removal. Actual length and access unknown.",physical_PASS=False),indent=1)+"\n").encode())
print(hits)
