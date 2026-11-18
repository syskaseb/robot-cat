"""Use the occupied cross sections to size three covered entries in the nested throat."""
from pathlib import Path
import json,ast,math
import numpy as np
P=Path(__file__).parent
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("unit","profile","transforms"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
r=json.loads((P/"flank-reception.json").read_bytes());j=json.loads((P/"yaw-laid-factory.json").read_bytes())["rows"]
ffc=json.loads((lib.parent/"occupied-layout.json").read_bytes())["FFC"]
cloud={k:{"fixed":[],"pitch":[]} for k in ("ribbon","tof","pitch250")}
for q in ffc:
    y,p=q["yaw"],q["pitch"];R,T=transforms(y,p)["pitch"]
    tof=next(v for v in r["ToF_move"] if v["yaw"]==y and v["pitch"]==p)
    jr=next(v for v in j if v["yaw"]==y)
    for tag,pts in [("ribbon",q["corners"]),("tof",profile(tof["centreline"],4.9,4.9)),("pitch250",profile(jr["centreline"],3.5,1.8))]:
        pts=np.array(pts).reshape(-1,3);cloud[tag]["fixed"].extend(pts);cloud[tag]["pitch"].extend((pts-T)@R)
out={}
for k,owners in cloud.items():
    out[k]={}
    for o,points in owners.items():
        pts=np.array(points);edges=np.array([-177.,-151.,-130.,-108.,-91.,-71.])
        bins=[]
        for a,b in zip(edges,edges[1:]):
            sel=pts[(pts[:,0]>=a-1)&(pts[:,0]<=b+1)]
            bins.append(None if not len(sel) else [sel[:,1:].min(0),sel[:,1:].max(0)])
        sections=[];pad=3.7 if k=="pitch250" else 1.6
        for i,x in enumerate(edges):
            adjacent=[q for q in bins[max(0,i-1):i+1] if q is not None]
            if adjacent:sections.append([x,*(np.min([v[0] for v in adjacent],axis=0)-pad),*(np.max([v[1] for v in adjacent],axis=0)+pad)])
        out[k][o]=sections
(P/"covered-passages.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
