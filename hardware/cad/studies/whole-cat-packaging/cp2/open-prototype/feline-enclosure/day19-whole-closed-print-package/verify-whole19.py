"""Verify this bounded packet and the unchanged baseline before an owned-only commit."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib
P=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=P.parent/"day18-body-reception-and-closed-fit"/"body-reception.FCStd"
assert sha(src)=="486abd0561488c91ea7d09344476c3b63c636c5f785238faa34ac36f7bf910d4"
budget=P.parent/"day19-source-bom-budgets"/"source-budget.json"
assert sha(budget)=="ddd9e05c23e73123b6e371d766de9c572d89f6f2a3b265838fc1bbfe0b3a2e48"
native=P/"whole-cat19.FCStd"
assert json.loads((P/"current-whole-gate.json").read_bytes())["native_sha256"]==sha(native)
with ZipFile(native) as z:
    assert z.testzip() is None
    crc=len(z.infolist())
ext={".py",".json",".png",".md",".txt",".FCStd"}
selected=sorted(p for p in P.iterdir() if p.suffix in ext and p.name!="verified-whole19.json")
sources={p.relative_to(P.parent).as_posix():sha(p) for p in (src,budget,budget.parent/"README.md")}
r=dict(basis_commit="d5baf5e6ce1598ff8031edb8b82f1a1011b4fada",sources=sources,
       helper_source_pins=json.loads(budget.read_bytes())["sources"],native_sha256=sha(native),native_zip_crc_entries=crc,
       files={q.name:sha(q) for q in selected},physical_PASS=False,whole_accepted=False,actual_fit=None,actual_cut=None,installed_slack=None)
(P/"verified-whole19.json").write_bytes((json.dumps(r,indent=1)+"\n").encode())
print(json.dumps(dict(files=len(selected)+1,source_pins=len(sources),helper_pins=len(r["helper_source_pins"]),crc=crc,native_sha=r["native_sha256"])))
