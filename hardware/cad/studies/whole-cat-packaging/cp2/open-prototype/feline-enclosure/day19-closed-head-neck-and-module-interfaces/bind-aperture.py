"""Only the one-piece optical mask changed after indexed mesh and STEP export."""
from pathlib import Path
import json,hashlib,zipfile
from xml.etree import ElementTree as E
import numpy as np
P=Path(__file__).parent;native=P/"whole-cat19C.FCStd";index=P/"material-index.json"
with zipfile.ZipFile(native) as z:
    pins={o.get("name"):hashlib.sha256(z.read(o.find("./Properties/Property[@name='Shape']/Part").get("file"))).hexdigest() for o in E.fromstring(z.read("Document.xml")).findall("./ObjectData/Object") if o.find("./Properties/Property[@name='Shape']/Part") is not None}
prev=json.loads((P/"pre-aperture-pins.json").read_bytes());changed=[n for n in pins if pins[n]!=prev.get(n)]
assert "C19_FaceAndEars" in changed and set(changed) <= {"C19_FaceAndEars","BR_COMMON_OPTICAL_MASK"},changed
x=json.loads(index.read_bytes());row=next(r for r in x["parts"] if r["part"]=="C19_FaceAndEars")
m=json.loads((P/"final-members.json").read_bytes())["C19_FaceAndEars"]
row.update(volume_total_mm3=m["volume"],envelope_with_allowance=(np.array(m["extents"])+[16,16,4]).tolist())
g=sum(r["volume_total_mm3"] for r in x["parts"])*.00127
x.update(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),geometric_P_g=g,delta_vs_19B_g=g-863.6858,whole_robot_known_range_g=[1853.4+g,2593.4+g],final_changed_breps=changed)
for row in x["parts"]:
    if row["stl"]:assert hashlib.sha256((P/row["stl"]).read_bytes()).hexdigest()==row["sha256"]
for st in x["steps"]:assert hashlib.sha256((P/st["path"]).read_bytes()).hexdigest()==st["sha256"]
index.write_bytes((json.dumps(x,indent=1)+"\n").encode());print(g,x["whole_robot_known_range_g"],x["native_sha256"])

