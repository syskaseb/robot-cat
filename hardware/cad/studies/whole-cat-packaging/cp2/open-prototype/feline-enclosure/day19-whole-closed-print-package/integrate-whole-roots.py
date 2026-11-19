"""Join the source load interfaces and opaque inner neck into the two low carrier prints."""
from pathlib import Path
import json,ast,datetime,traceback
import FreeCAD as A,FreeCADGui as G,Part
from PySide import QtCore
P=Path(__file__).parent;D=A.getDocument("cat19");V=A.Vector
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=1)+"\n").encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
portal=D.D19_OPEN_GIMBAL_LOAD_PORTAL.Shape;neck=D.D19_FIXED_INNER_NECK.Shape
feet=box(-141,10,42.52,10,8,22).fuse(box(-141,-18,42.52,10,8,22))
pjoin=portal.common(feet).Volume;njoin=neck.common(feet).Volume
actual_mg=feet.common(D.MG92B_Head_yaw.Shape).Volume
proposed=portal.multiFuse([D.D19_LOW_FORE_CARRIER.Shape,D.D19_LOW_REAR_CARRIER.Shape,neck,feet,D.P01_load_rail.Shape,D.P01_load_rail_instance2.Shape]).removeSplitter()
for x in (-80,-70,112,122):
    for y in (-22.5,22.5):proposed=proposed.cut(Part.makeCylinder(1.4,18,V(x,y,35)))
fore=proposed.common(box(-160,-120,30,180,240,170)).removeSplitter()
rear=proposed.common(box(20,-120,30,210,240,170)).removeSplitter()
ok=pjoin>.1 and njoin>.1 and actual_mg<.001 and fore.isValid() and rear.isValid() and len(fore.Solids)==len(rear.Solids)==1
res=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),portal_to_feet_mm3=pjoin,neck_to_feet_mm3=njoin,
    feet_actual_MG_case_common_mm3=actual_mg,fore_solids=len(fore.Solids),rear_solids=len(rear.Solids),active=ok,
    root_binding="Source eight X=-80,-70,112,122 / Y=+/-22.5 M2.5 axes and full H01 source bolts. P01 printed rails become integral material in the common carrier.",
    prototype_unknown="Actual base/threads, parting joint between fore/rear, all changed neighboring occupied cable fields and full motion still require qualification.",physical_PASS=False)
if ok:
    D.D19_LOW_FORE_CARRIER.Shape=fore;D.D19_LOW_REAR_CARRIER.Shape=rear
    for n in ("D19_FIXED_INNER_NECK","D19_OPEN_GIMBAL_LOAD_PORTAL","P01_load_rail","P01_load_rail_instance2"):D.getObject(n).ViewObject.Visibility=False
wr("whole-root-assembly.json",res)
records=[]
for o in D.Objects:
    if hasattr(o,"Shape") and not o.Shape.isNull():
        b=o.Shape.BoundBox;records.append(dict(name=o.Name,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume=o.Shape.Volume,kind=getattr(o,"EvidenceKind","source")))
wr("corrected-low-actors.json",records)
known=[o for o in D.Objects if o.Name.startswith(("D19_LOW_","D19_ROUNDED_","D19_BROAD_","D19_FIXED_INNER_","D19_SKULL_EARS","D19_OPEN_GIMBAL")) and o.ViewObject.Visibility]
wr("mass-budget.json",dict(base_and_bought_g=[1853.4,2593.4],density_g_cm3=1.27,known_new_selected_prints_full_material_g=sum(o.Shape.Volume for o in known)*.00127,
    known_print_names=[o.Name for o in known],P_scope="Add retained leg prints, optical front, full remaining head/tail mechanism and essential mounts once. P01 integral in carriers if root assembly active. Source chassis/metal is already in180..400 allowance.",
    P_actual=None,whole_actual=None,physical_payload_PASS=False))
D.recompute();D.save()
skins=["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","D19_BROAD_SKULL_BACK","BR_COMMON_OPTICAL_MASK","D19_SKULL_EARS"]
if D.D19_FIXED_INNER_NECK.ViewObject.Visibility:skins.append("D19_FIXED_INNER_NECK")
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
captures=[]
for f in ast.parse((P/"correct-whole-allocation.py").read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("cam","step"):exec(compile(ast.Module([f],type_ignores=[]),str(P),"exec"))
step(0)
