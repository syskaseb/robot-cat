"""Open solder-side frame, over-camera receiver and recessed stationary rail."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,json,runpy,math
P=Path(__file__).parent
src=(P/"head-and-shoulder.py").read_text()
exec(src[:src.index("# Both reception seats")])
floor=sh("B19_FrontFloor")
base=box(-71.4,21.5,41,6,18.3,4.8);pillar=box(-71.3,34.8,43.5,5.9,5.1,87.3)
arm=box(-71.3,15.6,128.5,19.8,24.2,3.1).cut(box(-65.5,22,128,8.6,11,4.2))
stand=box(-60.2,15.7,131.1,8.4,4.8,2.5)
fore=fused([floor,base,pillar,arm,stand,cheek_seat(-56,17,138)])
D.C19_ShoulderFloor.Shape=fore
# Retain the complete mounting-screw flange at y=-3.81, both bosses and the
# rear pitch root. Open the opposite length of the socket for the actual PTH row.
original=sh("D18C_TRUE_PITCH_OPTICAL_RECEIVER")
open_frame=original.cut(box(-204,1.2,91,17.5,15,24)).removeSplitter()
upright=box(-182.9,16.5,156.9,4.9,4.7,7.4)
bridge=box(-182.9,16.5,162,41.8,5.8,3)
guide=cheek_seat(-146,22,168)
carrier=fused([open_frame,upright,bridge,guide])
D.C19_MovingOpticsCarrier.Shape=carrier
# The complete mating rim retains both previous screw positions. The lateral
# flexible corridors have an open exit from the rear sides of the movable face.
back=sh("C19_OpenRearHelmet")
back=back.cut(box(-156.5,-86,95,14,172,79)).removeSplitter()
D.C19_OpenRearHelmet.Shape=back
# Shaped positive flank covers the full moving return; lower front has a
# fixed bridging lip from the shoulder to the legged floor, under the chin.
sections=[(-171,85,75,216),(-155,96,66,219),(-139,102,47,216),(-117,114,24,205),(-96,115,7,191),(-67,103,0,176),(-38,98,-2,158),(-15,98,-2,157),(8,102,-2,165),(20,103,-2,169.94)]
cow=skin(sections,1.45)
for y in (-120,38):cow=cow.cut(box(-109,y,-12,68,82,54))
for x in (-94,-82,-70,-58):cow=cow.cut(box(x,-55,140,3.3,19,80)).cut(box(x,32,140,3.3,17,80))
lip=skin([(-171.1,85.2,75,216),(-164.8,68,84,204),(-160.6,64,87,199)],1.5).common(box(-174,-96,68,20,192,36))
cow=cow.fuse(lip).removeSplitter();D.C19_FixedShoulderShell.Shape=cow
# Two sideways tongue seats on the shared forefloor/slats. Slot pairs accept
# temporary hand feed of a selected tie and keep the cow removable for assembly.
# The full tie length/slack remains an assembly condition.
frame_parts=[fore];cowl_parts=[cow]
for x in [-66,-19]:
    for sign in [-1,1]:
        y=sign*88
        # Short inward tab from the actual skin at slat height; intersect full
        # body to form the outer end without projecting material through skin.
        slab=box(x-4, min(sign*84,sign*111),72.0,8,27,2.7)
        outer=Part.makeLoft([ring(r,0) for r in sections],True,True)
        tab=slab.common(outer)
        tab=tab.cut(box(x-1.6,min(sign*91,sign*96),71.7,3.2,5,3.5))
        cowl_parts.append(tab)
        # Narrow outer slat is directly below each tab at the same station.
        frame_parts.append(box(x-4,min(sign*85,sign*90),69.5,8,5,4.5))
D.C19_FixedShoulderShell.Shape=fused(cowl_parts)
# Avoid bonding the detachable cowl tabs to floor material. Maintain an
# installation gap over the slat at each station.
for t in cowl_parts[1:]:frame_parts[0]=frame_parts[0].cut(t)
# Added pads touch frame and tabs only below the joint plane.
for i in range(1,len(frame_parts)):
    frame_parts[i]=frame_parts[i].common(box(-200,-125,40,320,250,31.7))
s=fused(frame_parts)
if len(s.Solids)==1 and s.isValid():D.C19_ShoulderFloor.Shape=s
else:D.C19_ShoulderFloor.Shape=fore
lay=json.loads((P/"side-return.json").read_bytes())
exec(src[src.index("def poly("):src.index("neutral=next")])
n=next(q for q in lay["motion"] if q["yaw"]==q["pitch"]==0)
D.C19_ToFLeadSet.Shape=Part.makeCompound([poly(q) for q in lay["head"]+[n["centreline"]]+[f["centreline"] for f in lay["fixed"]]])
D.recompute();G.runCommand("Std_Save")
names=[o.Name for o in D.Objects if o.Name.startswith("C19_") and len(o.Shape.Solids)]
write("final-members.json",{n:dict(valid=sh(n).isValid(),solids=len(sh(n).Solids),volume=sh(n).Volume,extents=[sh(n).BoundBox.XLength,sh(n).BoundBox.YLength,sh(n).BoundBox.ZLength]) for n in names})
runpy.run_path(str(P/"views.py"))

