"""Rebind unchanged exact tests and measure the two old root failures on the saved correction."""
from pathlib import Path
import hashlib,zipfile,json,runpy,math
from xml.etree import ElementTree as E
P=Path(__file__).parent;native=P/"whole-cat19D.FCStd";D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](native)
before=json.loads((P/"pre-attachment-shapes.json").read_bytes());changed=[n for n,f in D.members.items() if before.get(n)!=hashlib.sha256(D.zip.read(f)).hexdigest()]
old=json.loads((P/"forward-tab-mounts.json").read_bytes())
assert old["native_sha256"]=="3b8e6257633aeb0ccf1d96ce4c43b09fce372840ad093c7ca5b900d2619821ff"
rows=[r for r in old["rows"] if r["a"] not in changed and r["b"] not in changed]
out=dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),source_test_sha256=old["native_sha256"],changed_brep_streams=changed,rows=rows)
# Both joint faces turn with yaw. In pitch coordinates the foremost possible
# X of the new tab is separated from the back by this interval even at ±10°.
# Bound uses independent cos/sin extrema over the complete pitch range.
lo=-159+(-118.8+159)*math.cos(math.radians(10))-(136.3-121)*math.sin(math.radians(10))
out["all_pitch_aft_tab_gap_lower_bound_x"]=lo-D.bounds("D19D_PitchBack")[3]
for a,b in [("D19D_PitchBack","D19D_Shoulder"),("D19D_YawSaddle","D19D_OpticsCarrier")]:
    rows.append(dict(a=a,b=b,**D.common(a,b)))
(P/"final-joints.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
print(out["changed_brep_streams"],out["all_pitch_aft_tab_gap_lower_bound_x"],rows[-2:])

