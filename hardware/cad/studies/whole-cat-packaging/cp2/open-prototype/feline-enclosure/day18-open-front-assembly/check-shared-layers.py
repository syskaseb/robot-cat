"""Check the final shared floor, DATA jackets, audio mounting sets and chosen upper/lower layers."""
import json,runpy
from pathlib import Path
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
import numpy as np
P=Path(__file__).parent;prior=P.parent/"day18-front-insert-correction"
D=runpy.run_path(str(prior/"saved-front.py"))["Saved"](P/"open-front.FCStd")
assert "OPEN_SINGLE_FRONT_FLOOR" in D.members
res={}
def write():(P/"shared-layers.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
s=D.shape("OPEN_HANDLAY_OVER_FLOOR");free=BRepAlgoAPI_Cut(s,D.shape("OPEN_SINGLE_FRONT_FLOOR")).Shape()
g=GProp_GProps();BRepGProp.VolumeProperties_s(free,g);it=TopExp_Explorer(free,TopAbs_SOLID);count=0
while it.More():count+=1;it.Next()
res["case_adjacent_connected_void"]=dict(solids=count,available_mm3=g.Mass(),nominal_mm3=14736.06,
    passage="Start from the full 36 mm-wide case-adjacent band. Keep floor and saddle ledges. Open side reach before banks; physical MG exit unknown.")
res["pairs"]=[];res["data_jacket_gap"]={}
fixed=["Pi4B_actual_PCB","Pi_components_and_cooling","E1_populated_prototype_board","PCA9685_Adafruit815_PCB","F2_COMMON_PI_BUS_PCA_RECEIVER","MG92B_Tail","BUS25514_installed","CF17_POL1992_FULL_MATED_BODY","CF17_POWER_K1474_SEALED_BOOT_FULL","TTP223_touch"]
fixed += [n for n in D.members if n.startswith(("Motor_ATO4A_","WAGO415_data","FRONT18_REAR_"))]
moved=json.loads((P/"open-assembly.json").read_bytes())["moves"]
beam=["OPEN_DATA_CROSSBEARER_"+str(i) for i in (0,1)]
shell=["OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_BATTERY_DOOR"]
for n in list(moved)+beam+["INSERT_AUDIO_USB_A_FULL_MATE_FIELD"]:
    for other in fixed+shell:
        pair=D.common(n,other)
        if pair.get("common_mm3",0)>.0001 or "error" in pair:res["pairs"].append(dict(a=n,b=other,**pair))
    e=BRepExtrema_DistShapeShape(D.shape(n),D.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"))
    if e.IsDone():res["data_jacket_gap"][n]=e.Value()-3.4
    write()
for n in shell+["OPEN_SKULL_BACK"]:
    e=BRepExtrema_DistShapeShape(D.shape(n),D.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"))
    if e.IsDone():res["data_jacket_gap"][n]=e.Value()-3.4
    write()
res["data_stock"]=dict(whole=500,ends=[26,26],free=448,transport=194.6255592154,stored=253.3744407846,minimum_R=30,OD=6.8)
res["physical_PASS"]=False;write();print(res["pairs"])
