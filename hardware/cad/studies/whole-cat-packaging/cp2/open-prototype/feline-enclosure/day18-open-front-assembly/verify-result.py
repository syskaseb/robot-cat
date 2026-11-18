"""Verify the saved assembly, declared source subset, pictures, receipts and narrow result files."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import hashlib,json,re,sys
p=Path(__file__).resolve().parent
def h(data):return hashlib.sha256(data).hexdigest()
def sha(f):return h(f.read_bytes())
def read(name):return json.loads((p/name).read_bytes())
old=p.parent/"day18-front-insert-correction"/"front-insert-current.FCStd";current=p/"open-front.FCStd"
assert sha(old)=="898f5f842dadee8078922cbcc11df81a0c0bc41149a413c21e6686485e14bc82"
def member_map(z):
    xml=ET.fromstring(z.read("Document.xml"))
    objs=xml.findall("./ObjectData/Object")
    return len(objs),{obj.get("name"):ref.get("file") for obj in objs if (ref:=obj.find('./Properties/Property[@name="Shape"]/Part')) is not None}
names=["WAVEGO_complete_126_source_solids","MG92B_Head_yaw","MG92B_Head_pitch","MG92B_Tail","TAIL_ROTATING_HOLLOW_REAL_ROOT","Yaw608_120","Yaw608_134",
    "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_fullnut","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_headwasher",
    "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_nutwasher","PBAY_P_REAR","PBAY_F_AUX","Pi4B_actual_PCB","Pi_components_and_cooling","CF17_PI_PRIMARY_CSI",
    "CF17_PI_PRIMARY_USB_A_front","Pi_USB_DATA_Delock_mating","CF17_POWER_K1474_SEALED_BOOT_FULL","CF17_POL1992_FULL_MATED_BODY",
    "PCA9685_Adafruit815_PCB","E1_populated_prototype_board","Camera3_NoIR_Wide","VL53L5CX","INSERT_OPTICAL_FACE","F3_DATA500_HORIZONTAL_COMPLETE_UNIT"]
with ZipFile(current) as z, ZipFile(old) as base:
    count,n=member_map(z);_,original=member_map(base)
    assert z.testzip() is None
    assert count==1611 and len(z.infolist())>8300
    crc=len(z.infolist())
    reused={name:h(z.read(n[name])) for name in names}
    assert all(reused[name]==h(base.read(original[name])) for name in names)
    assert {"FIT_FLOOR_AND_BATTERY_MONITOR","FIT_FRONT_COWL","FIT_AFT_COWL","FIT_DATA_SEATS_1","OPEN_THREE_JR_UNITS","OPEN_KEYS_AND_INSULATED_LANDS"}<=n.keys()
for file in ("view-receipt.json","fit-view-receipt.json","current-view-receipt.json"):
    for item in read(file)["views"]:assert sha(p/item["file"])==item["sha256"]
assert read("affected-fit.json")["done"] and read("shared-layers.json")["physical_PASS"] is False
assert len(read("occupied-gate.json")["poses"])==5 and read("battery-monitor-seat.json")["placed"]
assert abs(read("audio-port-binding.json")["audio_vs_full_DATA_mate_mm3"]-429.26)<.001
assert len(read("current-front-sight.json"))==21
ss=["../day18-front-insert-correction/front-insert-current.FCStd","../day18-front-insert-correction/insert-regions.json","../day18-front-insert-correction/saved-front.py",
    "../day18-front-insert-correction/csi-entry.json","../day18-front-insert-correction/face-apertures.json","../day18-front-insert-correction/result-pins.json",
    "../day18-latest-whole-front/shoulder-volume.json","../day18-closed-whole-common-assembly/DATA500-horizontal-stock-plan.json",
    "../day17-coherent-front-material-and-loom/build-one-common-front.py","../day14-fasttrack-first-fit/day14-firstfit-build.py"]
art={f.name:sha(f) for f in sorted(p.iterdir()) if f.suffix in {".py",".json",".png",".FCStd",".md"} and f.name!="result-pins.json"}
res=dict(source_commit="c21591921ab9e1f2b05f7606204bec7442fd5a7e",first_fact_commit="f6e8273d5ef56feed1167107f735f71326d8ecde",
    source_sha256={s:sha(p/s) for s in ss},same_source_BReps=reused,artifacts=art,primary_native_sha256=sha(current),
    native_crc_entries=crc,native_objects=count,native_receipt_utc="2026-11-18T12:32:57Z",gui_pid=17796,open_documents=1,modified=False,
    gate="Retain open portal, DATA supports and battery-monitor floor for next common trial. Reject current front loom and simultaneous USB mate fields. Appearance open.",
    whole_ready=False,physical_PASS=False,actual_fit=None,actual_cut=None,actual_installed_slack=None)
if sys.argv[1:]==["--write"]:(p/"result-pins.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
assert read("result-pins.json")==res
for link in re.findall(r'\]\(([^)]+)\)',(p/"START_HERE.md").read_text(encoding="utf-8")):assert (p/link).is_file(),link
print(len(art),"result hashes",len(ss),"source hashes",len(reused),"same BReps",crc,"CRC",count,"objects",res["primary_native_sha256"])
