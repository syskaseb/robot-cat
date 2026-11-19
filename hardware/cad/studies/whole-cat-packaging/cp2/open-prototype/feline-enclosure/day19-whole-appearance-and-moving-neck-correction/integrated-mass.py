"""Use adaptive volume integration for the thin trimmed spline lofts on both sides of the 19C delta."""
from pathlib import Path
import json,runpy
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces";path=P/"material-index.json"
x=json.loads(path.read_bytes());src=json.loads((C/"material-index.json").read_bytes())
D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](C/"whole-cat19C.FCStd")
m=json.loads((P/"form-members.json").read_bytes())
for r in x["parts"]:
    if r["part"] in m:
        r["native_default_integration_mm3"]=r["volume_total_mm3"];r["volume_total_mm3"]=r["adaptive_volume_mm3"];assert r["volume_total_mm3"]>0
base=src["geometric_P_g"];diffs={}
for r in src["parts"]:
    if r["part"] in x["retired"]:
        v=GProp_GProps();BRepGProp.VolumeProperties_s(D.shape(r["part"]),v,1e-8)
        delta=(v.Mass()-r["volume_total_mm3"])*.00127
        diffs[r["part"]]=delta;base+=delta
mass=sum(r["volume_total_mm3"] for r in x["parts"])*.00127
x.update(geometric_P_g=mass,delta_19C_g=mass-src["geometric_P_g"],comparable_19C_P_g=base,delta_comparable_19C_g=mass-base,whole_robot_known_range_g=[1853.4+mass,2593.4+mass],published_19C_P_g=src["geometric_P_g"],superseded_19C_integrator_difference_g=diffs,volume_method="New parts and superseded comparison use BRepGProp adaptive integration 1e-8. Retained material from the received single index; no meshes or components counted twice.")
path.write_bytes((json.dumps(x,indent=1)+"\n").encode())
print(mass,base,mass-base,x["whole_robot_known_range_g"])

