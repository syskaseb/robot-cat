"""Classify the exact stored witnesses by cable station and by the installed terminal."""
from pathlib import Path
import ast,hashlib,json,math,runpy
from xml.etree import ElementTree as ET
import numpy as np
P=Path(__file__).parent;H=next(d for d in P.parents if d.name=="hardware")
f=H/"reference/adafruit815-2026-09-26/Adafruit PCA9685 rev C.brd"
brd=ET.parse(f).getroot();jp=brd.find(".//elements/element[@name='JP3']")
pkg=brd.find(f".//libraries/library[@name='{jp.get('library')}']/packages/package[@name='{jp.get('package')}']")
pads={int(v.get("name")):v for v in pkg.findall("pad")}
assert sorted(pads)==[1,2,3,4,5,6] and jp.get("rot")=="R90"
nets={int(c.get("pad")):s.get("name") for s in brd.findall(".//signals/signal") for c in s.findall("contactref") if c.get("element")=="JP3"}
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
gui=ET.fromstring(D.zip.read("GuiDocument.xml"))
visible={o.get("name"):o.find('./Properties/Property[@name="Visibility"]/Bool').get("value")=="true" for o in gui.iter("ViewProvider") if o.find('./Properties/Property[@name="Visibility"]/Bool') is not None}
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for fn in ast.parse(lib.read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in ("profile","unit"):exec(compile(ast.Module([fn],type_ignores=[]),str(lib),"exec"))
raw=json.loads((P/"flank-material.json").read_bytes())["rows"]
rows=[];board="PCA9685_Adafruit815_PCB"
for q in json.loads((P/"flank-reception.json").read_bytes())["ToF_fixed"]:
    name=q["wire"];idx=int(q["JP3"]);pad=pads[idx]
    assert float(pad.get("drill"))==1.016 and q["budget"]["ends_once"]==12
    path=np.array(q["centreline"]);end=path[-1];field=profile(path,2.1,2.1)
    hits=next(row["witness"] for row in raw if row["name"]==name);w=np.array(hits[board]);v=field[-1]
    assert np.min(np.linalg.norm(v[1:]-w,axis=1))<1e-7
    pre=field[:-1].reshape(-1,3);ix=D.inside(board,pre)
    rows.append(dict(wire=name,pad=f"JP3.{idx}",net=nets[idx],primary_xy_mm=[float(pad.get(k)) for k in ("x","y")],world_center=end.tolist(),world_witness=w.tolist(),
        corner_distance_mm=float(np.linalg.norm(end-w)),last_PVC_square_only=True,preterminal_PCB_sample=None if ix is None else pre[ix].tolist(),
        terminal="Center ends at the sourced plated through-hole. The corner belongs to the 2.1 mm insulated bounding square at the termination station. Fit of stripped conductor, solder and insulation setback remains measured on the delivered assembly.",
        other_active_witnesses={n:dict(point=p,distance_from_pad_mm=float(np.linalg.norm(np.asarray(p)-end))) for n,p in hits.items() if n not in (board,"WAGO415_data_1_0")},
        retired_proxy_witnesses=[n for n in hits if n=="WAGO415_data_1_0"],operand_binding="pa-aux-effectivity.json, constructor lines 59-64",both_ends_debit_mm=12,installed_strip_mm=None))
out=dict(board_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),library=jp.get("library"),package=jp.get("package"),orientation=jp.get("rot"),
         six_holes_mm=[float(pads[i].get("drill")) for i in sorted(pads)],pitch_mm=abs(float(pads[2].get("x"))-float(pads[1].get("x"))),rows=rows,
         physical_check="One unpowered four-core JP3 termination fit: delivered conductor entry, solder and insulation shoulder at adjacent pads, with the soldered E1/PCA in its actual fixture.",physical_PASS=False,actual_cut=None)
(P/"typed-jp3.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
print([(v["wire"],v["preterminal_PCB_sample"],v["other_active_witnesses"]) for v in rows])
