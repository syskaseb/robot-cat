"""Bind the sixteen selected 415 housings to the constructor and reclassify one alias."""
from pathlib import Path
from xml.etree import ElementTree as ET
import ast,hashlib,json,math,runpy
import numpy as np
P=Path(__file__).parent;C=P.parent/"day16-night-compact-whole-core"/"build-one-compact-whole-organization.py"
source=C.read_bytes()
assert b"if n=='WAGO415_data_1_0':n='PBAY_P_AUX'" in source and b"if n=='PBAY_P_AUX':continue" in source and b"move('PBAY_P_AUX'," in source
Saved=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"]
frozen=P.parent/"day18-open-front-assembly"/"open-front.FCStd";D=Saved(frozen);current=Saved(P/"body-reception.FCStd")
alias="WAGO415_data_1_0";actual="PBAY_P_AUX"
selected=[(actual if n==alias else n) for n in [p+str(i) for p in ("WAGO415_data_1_","WAGO415_data__1_") for i in range(8)]]
assert len(set(selected))==16
ref=ET.fromstring(D.zip.read("GuiDocument.xml"))
def visible(n):return ref.find(f".//ViewProvider[@name='{n}']/Properties/Property[@name='Visibility']/Bool").get("value")=="true"
assert not visible(alias) and all(visible(n) for n in selected)
def digest(d,n):return hashlib.sha256(d.zip.read(d.members[n])).hexdigest()
assert digest(D,actual)==digest(current,actual)
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("unit","profile"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
r=json.loads((P/"flank-reception.json").read_bytes());raw=json.loads((P/"flank-material.json").read_bytes())["rows"]
paths=[("existing_extension_static",r["extension"]["centreline"],3.5,1.8)]+[("extension_fan",q["centreline"],1.8,1.8) for q in r["extension"]["fans"]]+[(q["wire"],q["centreline"],2.1,2.1) for q in r["ToF_fixed"]]
rows=[]
for row,(label,path,w,h) in zip([q for q in raw if q["name"] in {p[0] for p in paths}],paths):
    assert label==row["name"];pt=profile(path,w,h).reshape(-1,3);ix=current.inside(actual,pt)
    rows.append(dict(group=label,archived_alias_witness=row["witness"].get(alias),selected_operand=actual,actual_P_AUX_witness=pt[ix].tolist() if ix is not None else None,
                     other_raw_witnesses={n:v for n,v in row["witness"].items() if n!=alias}))
out=dict(frozen_commit="8e4f8d9668a13a8057ff2797f137d49b2fc88136",source_constructor=C.name,source_lines=[59,64],sha256=hashlib.sha256(source).hexdigest(),
    retired=alias,replacement=actual,selected_415=selected,source_placement_bounds=current.bounds(actual).tolist(),actual_pose_BRep_SHA=digest(current,actual),rows=rows,physical_PASS=False)
(P/"pa-aux-effectivity.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
