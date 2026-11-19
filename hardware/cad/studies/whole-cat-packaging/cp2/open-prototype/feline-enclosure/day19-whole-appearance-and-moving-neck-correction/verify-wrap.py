"""Verify the handoff, source identities and equivalence of the GUI save to tested material."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
from datetime import datetime,timezone
import hashlib,json,re
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
A=P.parent/"day19-whole-closed-print-package";B=P.parent/"day19-common-floor-and-bundle-assembly";H=next(a for a in P.parents if a.name=="hardware")
old=P/"before-wrap.FCBak";native=P/"whole-cat19D.FCStd"
def sha(p):return hashlib.sha256(p.resolve().read_bytes()).hexdigest()
def read(f):return json.loads((P/f).read_bytes())
d=read("material-index.json");evidence=d["native_sha256"];assert evidence=="edbaa54bf71811869eb165f61f444ef3dd370f453b1dd7ae1d2e90e92ccf10e0"
newsha=sha(native)
with ZipFile(native) as z:
    assert z.testzip() is None;entries=len(z.namelist())
    root=E.fromstring(z.read("Document.xml"));objs=root.findall("./ObjectData/Object")
    assert len(objs)==461
    if old.exists():
        assert sha(old)==evidence
        with ZipFile(old) as zo:
            assert zo.testzip() is None and set(zo.namelist())==set(z.namelist())
            orig=E.fromstring(zo.read("Document.xml"))
            assert E.tostring(orig.find("ObjectData"))==E.tostring(root.find("ObjectData"))
            changed=[n for n in z.namelist() if z.read(n)!=zo.read(n)]
            assert not any(n.lower().endswith(".brp") for n in changed)
            guiequal=z.read("GuiDocument.xml")==zo.read("GuiDocument.xml")
            prop=lambda r:{p.get("name"):E.tostring(p) for p in r.find("Properties")}
            xx,yy=prop(orig),prop(root);doc_delta=[k for k in xx if xx[k]!=yy[k]]
            equal=dict(tested_native_sha256=evidence,saved_native_sha256=newsha,identical_object_data=True,identical_BRep_streams=True,gui_xml_identical=guiequal,changed_archive_members=changed,document_property_changes=doc_delta)
    else:
        equal=read("native-save-equivalence.json");assert equal["saved_native_sha256"]==newsha
(P/"native-save-equivalence.json").write_bytes((json.dumps(equal,indent=1)+"\n").encode())
for n in ["final-joints.json","motion-screen.json","optical-apertures.json","sensor-window.json","joint-fields.json","bearing-and-tabs.json"]:
    assert read(n)["native_sha256"]==evidence,n
assert len(read("motion-screen.json")["rows"])==45 and len(read("joint-fields.json")["rows"])==207
assert len(read("optical-apertures.json")["rows"])==44
assert not any(r["hits"] for r in read("sensor-window.json")["rows"])
assert len(read("bearing-and-tabs.json")["pads"])==8
for r in d["parts"]:
    assert r["volume_total_mm3"]>0 and max(r["envelope_with_allowance"])<=256,r["part"]
    if r["stl"]:assert sha(P/r["stl"])==r["sha256"]
for r in d["steps"]:assert sha(P/r["path"])==r["sha256"]
assert abs(sum(r["volume_total_mm3"] for r in d["parts"])*.00127-d["geometric_P_g"])<1e-7
for link in re.findall(r"\]\(([^)]+)\)",(P/"START_HERE.md").read_text(encoding="utf8")):
    if not link.startswith("https://"):assert (P/link).is_file(),link
files="""START_HERE.md whole-cat19D.FCStd preserved-unsaved-19C.FCStd saved-idle.json native-save-equivalence.json reconciliation.json material-index.json final-joints.json motion-screen.json sensor-window.json optical-apertures.json bearing-and-tabs.json joint-fields.json unit-stations.json whole-lay.json over-bus-rejection.json bus-return.json aft-attachment.json articulated-covers.json articulated-sections.json seam-profiles.json assembly-interfaces.json form-members.json build.json interface-final.json views-receipt.json face-fragments.json pinch-location.json pre-attachment-shapes.json front.png side.png three-quarter.png interior.png critical-sections.png ola-and-19D.png first-critical-sections.png first-three-quarter.png first-joint-fields.json first-joint-moving.json first-joint-mounts.json first-whole-lay.json axial-joint-fields.json axial-joint-moving.json axial-joint-mounts.json axial-critical-sections.png axial-three-quarter.png forward-tab-screen.json forward-tab-moving.json forward-tab-mounts.json reconcile.py whole-lay.py form-and-neck.py joint-solid.py joint-fields.py neck-sections.py views.py longitudinal-lay.py diaphragm-profiles.py close-moving-interface.py optical-fields.py seat-and-close.py finish-face.py sensor-window.py unit-stations.py over-bus-return.py swept-sections.py articulated-covers.py pinch-location.py aft-yaw-attachment.py moving-seam-screen.py final-joints.py effective-parts.py integrated-mass.py bearing-and-tabs.py appearance-sheet.py verify-wrap.py""".split()
files.extend(r["stl"] for r in d["parts"] if r["stl"] and r["stl"].startswith("individual-parts/"));files.extend(r["path"] for r in d["steps"])
assert len(set(files))==len(files)
for n in files:
    if (P/n).suffix in (".md",".py",".json"):
        f=P/n;b=f.read_bytes();new=b.replace(b"\r\n",b"\n");new.decode("utf8")
        if new!=b:f.write_bytes(new)
sources=[C/"whole-cat19C.FCStd",C/"material-index.json",B/"whole-cat19B.FCStd",B/"anchor-seats.py",A/"actor-effectivity.json",P.parent/"day19-source-bom-budgets/source-budget.json",P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd",H/"reference/appearance/ola-cat-reference.jpg",H/"electronics/kicad-current/design.json",H/"electronics/kicad-current/selected-components.csv",H/"electronics/full-cat/closed-prototype-add7-2026-11-16/connections.json"]
sourcepins={p.relative_to(H).as_posix():sha(p) for p in sources};assert sha(C/"whole-cat19C.FCStd")==read("reconciliation.json")["source_sha"]
assert sha(P/"preserved-unsaved-19C.FCStd")==read("reconciliation.json")["preserved_sha"]
with ZipFile(P/"preserved-unsaved-19C.FCStd") as z:assert z.testzip() is None;backup_crc=len(z.namelist())
t=read("saved-idle.json");assert t["pid"]==17796 and t["touched"] is False and t["open_docs"]==["whole_cat19D"]
receipt=dict(verified_utc=datetime.now(timezone.utc).isoformat(),saved_file_utc=datetime.fromtimestamp(native.stat().st_mtime,timezone.utc).isoformat(),saved_native_sha256=newsha,tested_native_sha256=evidence,native_zip_crc_members=entries,backup_zip_crc_members=backup_crc,objects=len(objs),document=t["document"],gui_pid=t["pid"],modified=False,owned_compute="ended",scope="19D wrap after human steering; previous input 01a1f4ae interrupted",whole_print_kit=False,physical_PASS=False,actual_fit_cut_slack=None,files={n:sha(P/n) for n in files},source_pins_from_hardware=sourcepins)
(P/"verified-19D.json").write_bytes((json.dumps(receipt,indent=1)+"\n").encode())
print(newsha,len(files)+1,len(sourcepins),entries,backup_crc,equal)

