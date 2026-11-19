"""Locate the yaw-shell joint behind the pitch back instead of crossing its side wall."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,json,runpy
P=Path(__file__).parent
s=(P/"articulated-covers.py").read_text()
exec(s[:s.index("# Keyed saddle seat")])
# The existing saddle has continuous bearing material at x=-135/-129, y=14..17,
# z=130. Both cantilevers leave the pivot on the inside, run aft, then meet
# the slotted landing at x=-118..-108, beyond the moving back at this height.
def beam(x0,y0,x1,y1,z,w,h):
    dx=x1-x0;dy=y1-y0;l=(dx*dx+dy*dy)**.5;nx=-dy/l*w/2;ny=dx/l*w/2
    pts=[V(x0+nx,y0+ny,z),V(x1+nx,y1+ny,z),V(x1-nx,y1-ny,z),V(x0-nx,y0-ny,z)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
a=beam(-135.4,14.5,-116.8,37.5,128.8,4.2,3.1)
b=beam(-129.2,14.5,-110.6,37.5,128.8,4.2,3.1)
legs=[box(x-2,35.9,128.8,4.1,29.5,3.1) for x in [-116.8,-110.6]]
rail=box(-118.8,60,128.8,10.3,7.1,4.2).cut(box(-115.1,62.3,128,3.1,2.8,6.4))
saddle=fused([sh("BR_FINISHED_YAW_SADDLE"),rail,a,b]+legs)
update("D19D_YawSaddle",saddle)
tab=box(-118.8,60,133.2,10.3,30,3.1).common(skin_out).cut(box(-115.1,62.3,133,3.1,2.8,3.9))
new=join_valid(hood,tab);assert new.Volume!=hood.Volume
update("D19D_YawHood",new)
D.recompute();D.save();write("aft-attachment.json",dict(root_saddle_x=[-135.4,-129.2],tab_x=[-118.8,-108.5],bearing_z=[133,133.2],through_slot_x=[-115.1,-112],through_slot_y=[62.3,65.1],previous_witness="pinch-location.json"))
runpy.run_path(str(P/"views.py"))

