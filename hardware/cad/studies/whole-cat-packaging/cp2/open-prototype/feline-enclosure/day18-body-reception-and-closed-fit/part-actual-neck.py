"""Fit the moving back to the fixed chest and install the typed four-core body lane."""
from pathlib import Path
import json,ast,math
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
lib=P.parent/"day18-open-front-assembly"/"seat-both-data-runs.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("mesh","loft","box"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
def feature(n,s,c):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.DisplayMode="Shaded";return o
q=json.loads((P/"joint-portal.json").read_bytes());old=D.BR_OVERLAP_SKULL_BACK.Shape
cut=old.copy()
for p in q["pieces"]:cut=cut.cut(mesh(p))
cut=cut.removeSplitter()
measured=dict(solid_count=len(cut.Solids),valid=cut.isValid(),source_volume=old.Volume,remaining_mm3=cut.Volume,bosses=[])
for y in (-73,73):
    land=Part.makeCylinder(4.1,12,V(-165,y,145),V(1,0,0))
    measured["bosses"].append(dict(y=y,source=old.common(land).Volume,remaining=cut.common(land).Volume))
usable=cut.isValid() and len(cut.Solids)==1 and all(abs(k["source"]-k["remaining"])<.03 for k in measured["bosses"])
measured["use_moving_back"]=usable
if usable:
    feature("BR_PARTED_SKULL_BACK",cut,(.16,.17,.19));D.BR_OVERLAP_SKULL_BACK.ViewObject.Visibility=False
# The opaque cross wall spans the cut at the anterior lip. It ends ahead of
# the fixed MG case and below the complete yaw fork. All source parts remain.
lip=loft(q["rows"],0).common(box(-159,-68,52,4,136,44.3))
chest=D.BR_RECESSED_CHEST.Shape;joined=chest.fuse(lip).removeSplitter()
measured["lip"]=dict(old_join_mm3=chest.common(lip).Volume,solids=len(joined.Solids),valid=joined.isValid(),case_common=lip.common(D.MG92B_Head_yaw.Shape).Volume,
                     fork_z_gap=D.HEAD_YAW_FORK_FIXED_PITCH_HOUSING.Shape.BoundBox.ZMin-lip.BoundBox.ZMax)
if joined.isValid() and len(joined.Solids)==1 and measured["lip"]["old_join_mm3"]>.1:
    feature("BR_CLOSED_CHEST_LIP",joined,(.15,.16,.18));D.BR_RECESSED_CHEST.ViewObject.Visibility=False
# Keep neutral moving ToF and the header fields, replace just the fixed lane.
r=json.loads((P/"flank-reception.json").read_bytes());fan=json.loads((P/"jp3-shared-fan.json").read_bytes())["rows"]
paths=[next(j for j in r["ToF_move"] if j["yaw"]==j["pitch"]==0)]+r["ToF_head"]+fan
o=D.BR_FLANK_TOF;o.Shape=Part.makeCompound([Part.makePolygon([V(*p) for p in j["centreline"]]) for j in paths])
measured["physical_PASS"]=False
(P/"part-actual-neck.json").write_bytes((json.dumps(measured,indent=1)+"\n").encode())
D.Label="Body reception - typed solder lane and nested neck";D.recompute();G.runCommand("Std_Save")
