"""Bounded first material check before detail. Check new load path and occupied front."""
import json
import math
from pathlib import Path
import FreeCAD as App
import Part

doc = App.ActiveDocument
out = Path(__file__).parent
V = App.Vector
assert Path(doc.FileName).resolve() == (out/"whole-front.FCStd").resolve()
frame = doc.FRONT18_LOWER_BEARING_FRAME.Shape
folder = out
checks = []
def bbox_gap(a,b):
    return math.sqrt(sum(max(0,getattr(a,k+"Min")-getattr(b,k+"Max"),getattr(b,k+"Min")-getattr(a,k+"Max"))**2 for k in "XYZ"))
def check(a,b,an,bn,pose=None):
    lower = bbox_gap(a.BoundBox,b.BoundBox)
    row = dict(a=an,b=bn,pose=pose,bbox_gap=lower)
    if lower<1.251:
        v=a.common(b)
        row.update(common=v.Volume,valid=v.isValid(),gap=0. if v.Volume>1e-6 else a.distToShape(b)[0])
    checks.append(row)
def persist():
    (out/"front-frame-check.json").write_bytes((json.dumps(checks,indent=1)+"\n").encode())
for n in ("D18C_P02_THREE_ROOT_THROUGH_VERSION","Yaw608_120","Yaw608_134","YAW_FIXED_OUTER_RACE_CAP","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX","MG92B_Head_yaw","YAW_REAL_REMOVABLE_SERVO_SADDLE","Monitor_MOD05015","Pi_components_and_cooling","Pi4B_actual_PCB"):
    check(frame,doc.getObject(n).Shape,"lower_frame",n)
persist()
for yaw in (-20,0,20):
    rot=App.Rotation(V(0,0,1),yaw)
    center=V(-130,0,127)
    T=App.Placement(center-rot.multVec(center),rot)
    for o in doc.Objects:
        if o.ViewObject.Visibility and o.Name.startswith(("YAW_SHAFT_FORK_POSITIVE_CROSSPIN","HEAD_YAW_FORK_FIXED","YAW_HORN_KEY","YAW_HORN_ROOF","YAW_HORN_CAP_","MG92B_Head_pitch")):
            shape=o.Shape.copy()
            shape.transformShape(T.toMatrix())
            check(frame,shape,"lower_frame",o.Name,yaw)
persist()
neighbors=["Speaker","MG92B_Tail","Pi_components_and_cooling","S0_body","OP_S1_PRIMARY_CASE_CONSERVATIVE","OP_S1_PRIMARY_STEM","OP_S1_LEVER_NOMINAL","BUS25514_installed","Battery_GEA223S30X6GT","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","F0_FHAC0002_30A","F2_COMMON_PI_BUS_PCA_RECEIVER","ReSpeakerLite_on_REMOVABLE_back"]
banks=[o for o in doc.Objects if o.Name.startswith("Motor_ATO4A_")]+[doc.getObject(n) for n in ("WAGO415_data__1_0","WAGO415_data__1_4")]
for i,o in enumerate(banks):
    for n in neighbors:
        check(o.Shape,doc.getObject(n).Shape,o.Name,n)
    for other in banks[i+1:]:
        check(o.Shape,other.Shape,o.Name,other.Name)
    persist()
# Secondary source holders are not simplified into an empty aisle.
for tag in ("NEG","POS"):
    bed=doc.getObject("FRONT18_BANK_BED_"+tag)
    for n in ("D18C_P02_THREE_ROOT_THROUGH_VERSION","P03_rear_deck_integrated_load_yoke","PBAY_P_REAR","Battery_GEA223S30X6GT","S0_body","NIGHT_INLINE_RR_W052","NIGHT_INLINE_RR_W053","OP_S1_LEVER_NOMINAL"):
        check(bed.Shape,doc.getObject(n).Shape,bed.Name,n)
persist()
hits=[(r["a"],r["b"],round(r.get("common",0),2)) for r in checks if r.get("common",0)>1e-4]
print("Whole front fixed/rotating checks",len(checks),"positive material or installation fields",hits)
