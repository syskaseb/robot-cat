"""Move the complete monitor, original keeper and both full screw stacks to a fixed service shelf."""
from pathlib import Path
import json
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("FIT_FLOOR_AND_BATTERY_MONITOR")
assert not json.loads((P/"service-bay-fit.json").read_bytes())["positive_or_unresolved"]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
# The cantilever rises outside the forward end of the purchased battery;
# the opening above the positive-side battery door remains available.
parts=[box(-20,20,46.5,6.5,31,5),box(-19,21,49,4.5,28.5,27.5),box(-19,21,74.75,67,29.5,1.75),
       box(-19,21,75.8,67,2.1,5),box(-19,48.9,75.8,67,1.6,5)]
for x in (-6,44):
    # Real existing washer is supported from underneath at z83.6. The
    # open-sided upright leaves access under the ledge to the actual nut.
    left=x-3.5
    parts.extend([box(left,48.6,75.8,7,2.4,12.7),
                  box(left,41.5,83.6,7,9,4.9).cut(cyl(x,45,83,1.2,6))])
shelf=parts[0].multiFuse(parts[1:]).removeSplitter();assert shelf.isValid() and len(shelf.Solids)==1
floor=D.FIT_FRONT_FLOOR.Shape;join=floor.common(shelf).Volume
full=floor.fuse(shelf).removeSplitter()
assert join>0 and full.isValid() and len(full.Solids)==1,(join,len(full.Solids))
bounds=json.loads((P/"service-bay-fit.json").read_bytes())["parts"]
r=A.Rotation(V(0,0,1),90).multiply(A.Rotation(V(0,1,0),90))
monitor=D.Monitor_MOD05015
pl=A.Placement(V(19,36,82.5)-r.multVec(monitor.Shape.BoundBox.Center),r)
keeper=A.Placement(V(19-128.5,45+90.5,89.5-134),A.Rotation())
source_names=[o.Name for o in D.Objects if o.Name.startswith("OP_MONITOR_")]
T=lambda o,p:p.multiply(o.Placement)
shifted={monitor.Name:pl}
for n in source_names:shifted[n]=keeper
# Verify the new support against the full battery, purchased display and
# complete retained keeper assemblies before changing the component placements.
candidate={n:D.getObject(n).Shape.copy() for n in shifted}
for n,s in candidate.items():s.Placement=shifted[n].multiply(s.Placement)
hits={n:shelf.common(s).Volume for n,s in candidate.items()}
neighbors=["Battery_GEA223S30X6GT","F2_COMMON_PI_BUS_PCA_RECEIVER","F0_FHAC0002_30A","BUS25514_installed","FIT_FRONT_COWL","FIT_AFT_COWL"]
for n in neighbors:hits[n]=shelf.common(D.getObject(n).Shape).Volume
facts=dict(shelf_to_floor=join,combined_solids=len(full.Solids),positive_mm3=hits,stroke="Battery side extraction and balance connector insertion are conditional on delivered harness reach and swollen pack size.",display_read="Lift back/upper covers. Service opening gives pack access. No conductor changes.",physical_PASS=False)
valid=all(abs(v)<.001 for v in hits.values())
facts["placed"]=valid
if valid:
    for n,p in shifted.items():D.getObject(n).Placement=T(D.getObject(n),p)
    part=D.addObject("PartDesign::Feature","FIT_FLOOR_AND_BATTERY_MONITOR");part.Shape=full;part.ViewObject.ShapeColor=(.24,.40,.42);part.ViewObject.DisplayMode="Shaded"
    D.FIT_FRONT_FLOOR.ViewObject.Visibility=False
(P/"battery-monitor-seat.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
