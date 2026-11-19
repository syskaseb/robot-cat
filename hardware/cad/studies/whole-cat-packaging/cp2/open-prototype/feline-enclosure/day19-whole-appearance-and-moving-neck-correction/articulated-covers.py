"""Complete two separate covers to the envelopes of their respective moving neighbours."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,json,runpy
P=Path(__file__).parent
code=(P/"close-moving-interface.py").read_text();exec(code[:code.index("S=lay")])
data=json.loads((P/"articulated-sections.json").read_bytes());rows=data["yaw"]
def section(r,key):
    pts=[V(r["x"],y,z) for y,z in r[key]]
    c=Part.BSplineCurve();c.interpolate(pts,PeriodicFlag=True)
    return Part.Wire([c.toShape()])
skin_out=Part.makeLoft([section(r,"outer") for r in rows],True,True)
skin_in=Part.makeLoft([section(r,"inner") for r in rows],True,True)
hood=skin_out.cut(skin_in).common(box(-173,-120,98.2,91,240,140)).removeSplitter()
# Keyed saddle seat is accessible with the forebody off; same through-slot
# as the bracket proven in the axial sample. It stays on the yaw member.
tab=box(-136,67.2,133.2,10.2,29,3.1).common(skin_out).cut(box(-132.8,68.6,133,2.8,3.2,4))
hood=join_valid(hood,tab);update("D19D_YawHood",hood)
fl=sh("D19D_FrontFloor");bodyrows=[(-110,91,38,220),(-98,99,27,220),(-77,104,18,211),(-54,101,17,189),(-31,99,21,172),(-5,98,23,164),(20,102,23,167)]
out=outer(bodyrows);skin=split_skin(bodyrows,1.45)
for y in [-120,38]:skin=skin.cut(box(-109,y,-12,68,82,54))
for x in [-89,-77,-65,-53]:skin=skin.cut(box(x,-55,140,3.3,20,82)).cut(box(x,33,140,3.3,18,82))
for x in [-64,-20]:
    for sg in [-1,1]:
        tab=box(x-4,min(sg*84,sg*110),77.3,8,26,2.3).common(out).cut(box(x-1.8,min(sg*90,sg*95),77,3.6,5,3))
        skin=join_valid(skin,tab)
skin=diag("fixed",-110,bodyrows,skin)
low=list(zip(data["chin_x"],[30,40,48,55,64,74,88],[45,42,40,39,39,38,35],data["chin_roof"]))
shield=split_skin(low,1.45,True)
for x in [-116,-110]:
    for sign in [-1,1]:
        skin=join_valid(skin,box(x,min(sign*50,sign*92),58,10,42,3.5).common(out))
shell=skin.fuse(shield).removeSplitter()
if len(shell.Solids)!=1:
    # Reach the lower rim below the new roof, behind the protected optical band.
    for sg in [-1,1]:
        rib=box(-110,min(sg*58,sg*90),57,10,32,2.7).common(out)
        skin=join_valid(skin,rib)
    shell=skin.fuse(shield).removeSplitter()
update("D19D_Shoulder",shell.cut(fl))
D.recompute();D.save();write("articulated-covers.json",dict(roof=data["chin_roof"],chin_joint_single=len(sh("D19D_Shoulder").Solids),yaw_joint_single=len(hood.Solids),via="full pitch hull at yaw front + fixed low shield beneath swept head"))
runpy.run_path(str(P/"views.py"))

