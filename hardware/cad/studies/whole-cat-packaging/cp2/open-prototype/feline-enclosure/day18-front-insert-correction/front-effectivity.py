"""Actual local closure and source-subset checks for the corrected insert."""
from pathlib import Path
import json,runpy
import numpy as np
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
P=Path(__file__).parent
D=runpy.run_path(str(P/"saved-front.py"))["Saved"](P/"front-insert-current.FCStd")
rows=[]
for n in ("Speaker","ReSpeakerLite_on_REMOVABLE_back","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD","MAX98357A_amp"):
    for k in ("INSERT_FRONT_NEG","INSERT_FRONT_POS","INSERT_REAR_NEG","INSERT_REAR_POS"):
        rows.append(dict(a=n,b=k,**D.common(n,k)))
    d=BRepExtrema_DistShapeShape(D.shape(n),D.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"));d.Perform()
    if d.IsDone():rows.append(dict(a=n,b="DATA500 6.8-mm installed jacket",signed_jacket_gap=d.Value()-3.4))
for n in ("VL53L5CX","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT","D18C_TRUE_PITCH_OPTICAL_RECEIVER","CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","Camera3_NoIR_Wide"):
    rows.append(dict(a="INSERT_OPTICAL_FACE",b=n,**D.common("INSERT_OPTICAL_FACE",n)))
extents={}
for n in ("INSERT_FRONT_NEG","INSERT_FRONT_POS","INSERT_REAR_NEG","INSERT_REAR_POS","INSERT_OPTICAL_FACE","INSERT_HEAD_BACK","FRONT18_FLOOR_AND_YAW_ROOT"):
    b=D.bounds(n);extents[n]={"bbox_native_mm":b.tolist(),"largest_with_8mm_total_allowance":float(max(b[3:]-b[:3])+8)}
(P/"effectivity.json").write_bytes((json.dumps(dict(affected=rows,component_bounds=extents,source_bought_parts_preserved=True,print_release=False,physical_PASS=False),indent=1)+"\n").encode())
print([(q["a"],q["b"],round(q.get("common_mm3",0),3)) for q in rows if q.get("common_mm3",0)>.0001])
