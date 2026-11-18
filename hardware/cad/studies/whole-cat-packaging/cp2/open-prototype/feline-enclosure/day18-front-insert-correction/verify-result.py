"""Verify this bounded result on disk without opening any CAD document."""
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

p = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):
    return json.loads((p/name).read_bytes())

primary = p/"front-insert-current.FCStd"
native_sha = sha(primary)
assert native_sha == read("first-fact.json")["sha256"][primary.name]
with ZipFile(primary) as z:
    assert z.testzip() is None
    entries = len(z.infolist())
    objects = ElementTree.fromstring(z.read("Document.xml")).findall("./ObjectData/Object")
    assert len(objects) == 1588
    names = {obj.get("name") for obj in objects}
    assert {"INSERT_OPTICAL_FACE","I2_JR_THREE_UNITS","I2_FFC_NEUTRAL","I2_TOF_ALL_FOUR","Speaker","ReSpeakerLite_on_REMOVABLE_back","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw"} <= names
source = [
    "../day18-closed-whole-common-assembly/closed-whole-common-assembly.FCStd",
    "../day18-closed-whole-common-assembly/DATA500-horizontal-stock-plan.json",
    "../day18-closed-whole-common-assembly/JR-and-POWER-unit-budget-plan.json",
    "../day18-closed-whole-common-assembly/ToF4-full-connected-family-and-unit-plan.json",
    "../day18-connected-storage-pitch-frame/separate-FFC200-storage-plan.json",
    "../day18-latest-whole-front/whole-front.FCStd","../day18-latest-whole-front/front-flex.json",
    "../day18-latest-whole-front/shoulder-volume.json","../day18-latest-whole-front/frame-and-panels.json",
    "../day18-latest-whole-front/whole-review-receipt.json","../day18-optical-local-apertures/optical-local-apertures.json"]
pins = {name:sha(p/name) for name in source}
assert pins["../day18-latest-whole-front/whole-front.FCStd"] == read("first-fact.json")["parent_native_sha256"]
assert pins[source[-1]] == read("face-apertures.json")["source_sha256"]
assert len(read("occupied-insert-check.json")["poses"]) == 5
assert all(a == b for a,b in read("gate-shape-identity.json")["sha256"].values())
assert len(read("ribbon-twist.json")["poses"]) == 9
for v in read("insert-view-receipt.json")["views"]:
    assert sha(p/v["file"]) == v["sha256"]
artifacts = {f.name:sha(f) for f in sorted(p.iterdir())
             if f.suffix in {".FCStd",".md",".png",".json",".py"} and f.name != "result-pins.json"}
record = dict(constructive_commit="98e254116c1128f13a94742449beddf451461fd5",
    trial_parent_commit="a81c35acc0bed27913a3e5787df48a5f743bee4f",
    first_fact_commit="ddc60a13a1608ffa3ac9f0a0745ec0dfdbe16593",source_sha256=pins,artifact_sha256=artifacts,
    primary_native=primary.name,primary_native_sha256=native_sha,native_crc_members=entries,native_objects=len(objects),
    native_receipt_utc="2026-11-18T11:36:15Z",gui_pid=17796,open_documents=1,modified=False,ordinary_usage_allowed_at_receipt=True,
    bounded_result="REJECT_FRONT_INSERT_ALLOCATION",whole_ready=False,physical_PASS=False,actual_fit=None,actual_cut=None,actual_installed_slack=None)
if sys.argv[1:] == ["--write"]:
    (p/"result-pins.json").write_bytes((json.dumps(record,indent=1)+"\n").encode())
assert record == read("result-pins.json")
for target in re.findall(r"\]\(([^)]+)\)",(p/"START_HERE.md").read_text(encoding="utf-8")):
    assert (p/target).is_file(), target
print(len(artifacts),"artifact hashes,",len(pins),"source hashes,",entries,"CRC,",len(objects),"objects",native_sha)
