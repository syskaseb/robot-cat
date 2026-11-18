"""Identify the first named installed surface on the low front and shoulder sight lines."""
from pathlib import Path
import json,runpy,sys
import numpy as np
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.gp import gp_Pnt,gp_Dir,gp_Lin
P=Path(__file__).parent
s=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
names=["OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_SKULL_BACK","INSERT_OPTICAL_FACE","Monitor_MOD05015","OPEN_SINGLE_FRONT_FLOOR","D18C_TRUE_PITCH_OPTICAL_RECEIVER",
       "MG92B_Head_yaw","MG92B_Head_pitch","HEAD_YAW_FORK_FIXED_PITCH_HOUSING","Camera3_NoIR_Wide","VL53L5CX",
       "Pi4B_actual_PCB","Pi_components_and_cooling","F2_COMMON_PI_BUS_PCA_RECEIVER"]
current="--current" in sys.argv
final="--final" in sys.argv or current
if final:
    names=[{"OPEN_FRONT_COWL":"FIT_FRONT_COWL","OPEN_AFT_COWL":"FIT_AFT_COWL","OPEN_SINGLE_FRONT_FLOOR":"FIT_FLOOR_AND_BATTERY_MONITOR" if current else "FIT_FRONT_FLOOR"}.get(n,n) for n in names]
queries=[(x,y,z) for x in [-300] for y in [-15,0,15] for z in [74,78,82,86,90,94,98]]
hits={p:[] for p in queries}
for n in names:
    shape=s.shape(n);bb=s.bounds(n)
    tester=IntCurvesFace_ShapeIntersector();tester.Load(shape,1e-6)
    for p in queries:
        if not (bb[1]-1e-6<=p[1]<=bb[4]+1e-6 and bb[2]-1e-6<=p[2]<=bb[5]+1e-6):continue
        tester.Perform(gp_Lin(gp_Pnt(*p),gp_Dir(1,0,0)),0,500)
        if tester.NbPnt():hits[p].append((min(tester.WParameter(i+1) for i in range(tester.NbPnt())),n))
result=[dict(origin=p,front_to_back=[n for _,n in sorted(group)[:4]]) for p,group in hits.items()]
file="current-front-sight.json" if current else "final-front-sight.json" if final else "low-front-sight.json"
(P/file).write_bytes((json.dumps(result,indent=1)+"\n").encode())
print([(r["origin"][1:],r["front_to_back"][:1]) for r in result])
