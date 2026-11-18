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
    "../day14-fasttrack-first-fit/day14-firstfit-build.py",
    "../day17-coherent-front-material-and-loom/build-one-common-front.py",
    "../day18-closed-whole-common-assembly/closed-whole-common-assembly.FCStd",
    "../day18-closed-whole-common-assembly/DATA500-horizontal-stock-plan.json",
    "../day18-closed-whole-common-assembly/JR-and-POWER-unit-budget-plan.json",
    "../day18-closed-whole-common-assembly/ToF4-full-connected-family-and-unit-plan.json",
    "../day18-connected-storage-pitch-frame/separate-FFC200-storage-plan.json",
    "../day18-latest-whole-front/whole-front.FCStd","../day18-latest-whole-front/front-flex.json",
    "../day18-latest-whole-front/shoulder-volume.json","../day18-latest-whole-front/frame-and-panels.json",
    "../day18-latest-whole-front/whole-review-receipt.json","../day18-optical-local-apertures/optical-local-apertures.json"]
pins = {name:sha(p/name) for name in source}
assert pins[source[0]] == "f1b1deba2c9a00f5ad87dcce666d9694d2eda10c834fc342b64eba1836a79bbf"
assert pins[source[1]] == "b475c23b2950be341a3dc5190a7b2a9911b5e7abaa5757a7df1fcebaa648c7d7"
assert sha(p/"insert-regions.py") == "8f9ada2861c10f834efea2ff13ef9207257ec8516690ea24b1f950b00b7a1053"
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
    native_receipt_utc="2026-11-18T11:37:40Z",gui_pid=17796,open_documents=1,modified=False,ordinary_usage_allowed_at_receipt=True,
    source_disposition=dict(Pi_26mm="components and cooling air allocation; CSI channel conditional",
        JR_yaw="assumed exit and tested 250 path hit column and PCB; other exits and paths open",
        DATA500="sample flexible lay conflicts with audio; retain complete unit and ports"),
    bounded_result="REJECT_SAMPLED_LAYOUT_FRONT_INSERT_CONCEPT_OPEN",stage_complete=False,
    whole_ready=False,physical_PASS=False,actual_fit=None,actual_cut=None,actual_installed_slack=None)
if sys.argv[1:] == ["--write"]:
    (p/"result-pins.json").write_bytes((json.dumps(record,indent=1)+"\n").encode())
assert record == read("result-pins.json")
for target in re.findall(r"\]\(([^)]+)\)",(p/"START_HERE.md").read_text(encoding="utf-8")):
    assert (p/target).is_file(), target
print(len(artifacts),"artifact hashes,",len(pins),"source hashes,",entries,"CRC,",len(objects),"objects",native_sha)
