"""Pin this native result and the direct contributors in the frozen input."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
P=Path(__file__).parent
def sha(f):return hashlib.file_digest(f.open("rb"),"sha256").hexdigest()
native=P/"body-reception.FCStd";source=P.parent/"day18-open-front-assembly"/"open-front.FCStd"
assert sha(source)=="6608a8ef6a3081da01eb7409cd97826f363ac71566140e559e6748deef623df4"
with ZipFile(native) as z:
    assert z.testzip() is None
    entries=len(z.infolist())
selected=[q for q in P.iterdir() if q.suffix in {".py",".png",".json",".md",".brep"} and q.name!="verified-reception.json"]
ancestors={q.relative_to(P.parent).as_posix():sha(q) for q in [source,source.parent/"occupied-layout.json",source.parent/"audio-connections.json",source.parent/"audio-port-binding.json",P.parent/"day18-closed-whole-common-assembly"/"current-existing-JR-tail-body-interface-identities.json",P.parent/"day18-optical-local-apertures"/"optical-local-apertures.json"]}
(P/"verified-reception.json").write_bytes((json.dumps(dict(frozen_commit="8e4f8d9668a13a8057ff2797f137d49b2fc88136",source=ancestors,native_sha256=sha(native),native_zip_crc_entries=entries,files={q.name:sha(q) for q in sorted(selected)},physical_PASS=False,actual_cuts=None,actual_fit=None),indent=1)+"\n").encode())
