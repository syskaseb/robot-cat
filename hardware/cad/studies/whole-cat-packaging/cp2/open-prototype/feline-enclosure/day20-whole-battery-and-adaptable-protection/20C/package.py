"""Bind the verified print delta, whole CAD, source pins, and views."""
from pathlib import Path
from runpy import run_path
import hashlib
import json
import os
import FreeCAD
folder=Path(__file__).resolve().parent
root=folder.parent
def load(p):
    return json.loads(p.read_bytes())
def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
native=load(folder/"20C-native-readback.json")
assert not native["modified"] and not native["touched"] and native["object_count"]==568
assert sha(folder/native["path"])==native["sha256"]
parts=load(folder/"20C-print-index.json")
assert len(parts)==9
layout=run_path(str(folder/"layout.py"))
wires=layout["wire_budgets"](load(root/"20B-dlugosci.json"))
proof=load(folder/"20C-W076-local.json")
wires["W076_full_factory_output"]["sampled_centerline_R_min_mm"]=min(v["sampled_centerline_radius_min_mm"] for v in proof["nominal_poses"].values())
wires["W076_full_factory_output"].pop("project_center_R_min_mm",None)
review=load(root/"20B-RECEIPT.json")
for name,hash_value in review["pins"].items():
    assert sha(root/name)==hash_value,name
pins={}
for name in ("20C-closed.png","20C-open-service.png","20C-dry-gate.json","20C-W076-local.json","20C-INSTRUKCJA.md","20C-native-readback.json","20C-print-index.json"):
    pins[name]=sha(folder/name)
manifest={
    "task":"20C ONE_COHERENT_REVIEW_CORRECTION_AND_ESSENTIAL_INLET_MTA_KIT",
    "actual_input":"01a1f93f-04bb-7561-bfe1-b9946e5b2f9c",
    "source":{"commit":"1d428594af9db9f49fa931e72d51fe48f611a21d",
              "sha256":sha(root/"whole-cat20A.FCStd"),
              "received20B_manifest_sha256":sha(root/"20B-RECEIPT.json")},
    "native":native, "changed_prints":parts,"pins":pins,
    "retained_hardware":{"foundation_M2p5x16":8,"battery_bridge_M3x12":2,"battery_bridge_M3_nuts":2,
                         "bridge_fasteners_source_role":"declared R2 role, physical quantity to confirm",
                         "planned_ties":{"4_MTA_body_and_mount":12,"F0_body_two_and_seat_one":3,
                                         "XT60_body_and_nearby_relief":2,"POST_body_and_nearby_relief":2},
                         "availability":"physical unknown, existing roles only"},
    "changed_wire_budgets":wires,
    "open":["actual top exit and manual lead passage under positive ATO bank",
            "full factory ends and acceptable radii including FHAC closed cover",
            "local MTA lay near FL/FR/RL mount feet and four delivered full units",
            "steel and wire stock physical counts, bearing and physical fit"],
    "actualfit":None,"cut":None,"slack":None,"physicalPASS":False,
}
target=folder/"20C-manifest.json"
temp=target.with_suffix(".tmp")
with temp.open("x",encoding="utf-8",newline="\n") as f:
    json.dump(manifest,f,ensure_ascii=False,indent=2);f.write("\n")
os.replace(temp,target)
print("20C manifest",sha(target),flush=True)