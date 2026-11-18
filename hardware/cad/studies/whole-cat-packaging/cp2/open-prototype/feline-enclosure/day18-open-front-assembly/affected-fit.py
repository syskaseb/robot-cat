"""Check the revised material only at the named shared-layer interfaces."""
from pathlib import Path
import json,runpy
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
import numpy as np
P=Path(__file__).parent
d=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
assert "FIT_AFT_COWL" in d.members
res={"data_support":[],"prior_witnesses":[],"audio":[]}
def write():(P/"affected-fit.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
for n in ["FIT_DATA_SEATS_0","FIT_DATA_SEATS_1"]:
    for target in ["FIT_FRONT_COWL"]+[s for s in d.members if s.startswith("Motor_ATO4A_")]:
        v=d.common(n,target)
        if v.get("bounds_separation_mm",0)<3:res["data_support"].append(dict(part=n,target=target,**v))
    ds=BRepExtrema_DistShapeShape(d.shape(n),d.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"))
    if ds.IsDone():res["data_support"].append(dict(part=n,target="DATA500",jacket_gap=ds.Value()-3.4))
    write()
# The original shell/body gate for these four confirmed solids is unchanged;
# the following checks use only the new front and aft material.
for name in ["Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD"]:
    for skin in ["FIT_FRONT_COWL","FIT_AFT_COWL"]:
        res["audio"].append(dict(part=name,skin=skin,**d.common(name,skin)))
    write()
for report in json.loads((P/"occupied-gate.json").read_bytes())["poses"]:
    for group in report["checks"]:
        for hit in group["hits"]:
            if hit["part"] not in ("OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_FORE_BANK_AND_DATA_FRAME"):continue
            nn=["FIT_DATA_SEATS_0","FIT_DATA_SEATS_1","FRONT18_FORE_NEG_PANEL","FRONT18_FORE_POS_PANEL"] if hit["part"]=="OPEN_FORE_BANK_AND_DATA_FRAME" else ["FIT_FRONT_COWL" if hit["part"]=="OPEN_FRONT_COWL" else "FIT_AFT_COWL"]
            still=[n for n in nn if d.inside(n,np.array([hit["point"]])) is not None]
            res["prior_witnesses"].append(dict(yaw=report["yaw"],pitch=report["pitch"],group=group["group"],old=hit["part"],point=hit["point"],still_inside=still))
    write()
res["scope"]="Previously positive fixed material witnesses only. Missing new positives and continuous motion remain open."
res["done"]=True;res["physical_PASS"]=False;write()
