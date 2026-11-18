"""Check the installed body lane, both receivers and three insulated splice fields."""
import ast,json,math,runpy,sys
from pathlib import Path
from xml.etree import ElementTree as ET
from scipy.spatial import cKDTree
import numpy as np
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
assert "BR_RECESSED_CHEST" in D.members
gui=ET.fromstring(D.zip.read("GuiDocument.xml"))
active={o.get("name") for o in gui.iter("ViewProvider") if o.find('./Properties/Property[@name="Visibility"]/Bool[@value="true"]') is not None}
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("profile","transforms","unit"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
shared="--shared" in sys.argv
r=json.loads((P/"flank-reception.json").read_bytes());rows=json.loads((P/("jp3-shared-fan.json" if shared else "jp3-body-lane.json")).read_bytes())["rows"]
parts=["F2_COMMON_PI_BUS_PCA_RECEIVER","Pi4B_actual_PCB","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","OPEN_PORTAL_MATERIAL_SUBSET","BR_FLANK_SUPPORT_SUBSET","PBAY_F_HP","PBAY_F_HY","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX"]
parts += [n for n in active if n.startswith(("CB_PCA_","Motor_ATO4A_","YAW_SHAFT_FORK_POSITIVE_CROSSPIN","HEAD_YAW_FORK","MG92B_Head"))]
parts += json.loads((P/"pa-aux-effectivity.json").read_bytes())["selected_415"]
parts=sorted(set(parts))
out=dict(stations=[],leads=[],intercore=[],physical_PASS=False)
def save():(P/("shared-fan-material.json" if shared else "installed-reception.json")).write_bytes((json.dumps(out,indent=1)+"\n").encode())
for n in (() if shared else ("BR_PAIR_HY","BR_FLANK_HP_PAIR","BR_FLANK_THREE_LAPS")):
    hits=[]
    for k in parts:
        v=D.common(n,k)
        if v.get("common_mm3",0)>.001 or "error" in v:hits.append([k,v])
    out["stations"].append(dict(name=n,neutral_exact=hits));save()
def check(tag,path,w,h,terminal=None):
    plane=profile(path,w,h);p=plane.reshape(-1,3);last=5*(len(plane)-1);hits={}
    for n in parts:
        i=D.inside(n,p)
        if i is not None:hits[n]=dict(point=p[i].tolist(),station=i//5,last=i>=last,mm_from_end=float(np.linalg.norm(p[i]-p[last])),termination=terminal if i>=last else None)
    out["leads"].append(dict(name=tag,profile_mm=[w,h],hits=hits));save()
if not shared:
    check("JR300",r["extension"]["centreline"],3.5,1.8)
    for q in r["extension"]["fans"]:check("JR300 individual fan",q["centreline"],1.8,1.8)
for q in rows:check(q["wire"],q["centreline"],2.1,2.1,q["JP3"])
for i,a in enumerate(rows):
    for b in rows[i+1:]:
        pa,pb=(np.array(q["centreline"]) for q in (a,b));d,j=cKDTree(pb).query(pa);idx=d.argmin()
        out["intercore"].append(dict(a=a["wire"],b=b["wire"],sampled_center_distance_mm=float(d[idx]),OD=2.1,point_a=pa[idx].tolist(),point_b=pb[j[idx]].tolist()))
save()
