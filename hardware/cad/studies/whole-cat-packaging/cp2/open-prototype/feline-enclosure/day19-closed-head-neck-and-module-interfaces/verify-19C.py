"""Verify the saved handoff by its exact files and source identities."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
from xml.etree import ElementTree as E
import json,hashlib,re
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files="""whole-cat19C.FCStd START_HERE.md material-index.json final-members.json aperture-seat.json before-aperture.json optical-apertures.json shell-fit.json first-shell-fit.json changed-seam.json first-changed-seam.json face-inserts.json side-return.json first-side-return.json two-head-jr-units.json whole-head-lay.json outer-cheek-rejection.json lateral-whole-lay.json first-critical-sections.png first-three-quarter.png front.png side.png three-quarter.png interior.png critical-sections.png views-receipt.json build-receipt.json pre-aperture-pins.json head-and-shoulder.py head-jr.py integrate-reception.py shoulder-layout.py side-return.py lateral-lay.py show-lay.py views.py shoulder-sections.py changed-seam.py shell-fit.py optical-apertures.py face-inserts.py face-aperture.py print-material.py finish-inserts.py bind-aperture.py verify-19C.py""".split()
read=lambda n:json.loads((P/n).read_bytes())
x=read("material-index.json")
files.extend(r["stl"] for r in x["parts"] if r["stl"] and r["stl"].startswith("individual-parts/"))
files.extend(s["path"] for s in x["steps"]);assert len(files)==len(set(files))
native=P/"whole-cat19C.FCStd";digest=sha(native)
for n in ["material-index.json","shell-fit.json","optical-apertures.json","changed-seam.json"]:assert read(n)["native_sha256"]==digest
assert len(read("shell-fit.json")["motion"])==10
assert len(read("optical-apertures.json")["rows"])==38
assert max(q["common_mm3"] for q in read("optical-apertures.json")["rows"])<1e-6
for row in x["parts"]:
    assert max(row["envelope_with_allowance"])<=256
    if row["stl"]:assert sha(P/row["stl"])==row["sha256"]
for s in x["steps"]:assert sha(P/s["path"])==s["sha256"]
for href in re.findall(r"\]\(([^)]+)\)",(P/"START_HERE.md").read_text(encoding="utf8")):
    if not href.startswith("https://"):assert (P/href).is_file(),href
with ZipFile(native) as z:
    assert z.testzip() is None;count=len(z.namelist());objs=len(E.fromstring(z.read("Document.xml")).findall("./ObjectData/Object"))
assert objs==443
source=P.parent/"day19-common-floor-and-bundle-assembly/whole-cat19B.FCStd"
assert sha(source)==x["source_19B_sha256"]=="8c67eab6722ceaa73eb0ab6881bb93bce59c13e55281e1e893fb3fd1c8c31807"
for n in files:
    path=P/n
    if path.suffix in {".json",".py",".md"}:
        b=path.read_bytes();v=b.replace(b"\r\n",b"\n")
        if b!=v:path.write_bytes(v)
receipt=dict(verified_utc=datetime.now(timezone.utc).isoformat(),saved_utc=datetime.fromtimestamp(native.stat().st_mtime,timezone.utc).isoformat(),native_sha256=digest,source_19B_sha256=sha(source),native_zip_crc_members=count,gui_pid=17796,document="whole_cat19C",objects=objs,modified=False,owned_compute="ended",whole_print_kit=False,physical_PASS=False,actual_fit_cut_slack=None,files={n:sha(P/n) for n in files})
(P/"verified-19C.json").write_bytes((json.dumps(receipt,indent=1)+"\n").encode())
print(digest,count,objs,len(files)+1)

