"""Finish the two anchor landings, jaw and open bank over the battery."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,math,json
P=Path(__file__).parent
exec((P/"floor19b.py").read_text(encoding="utf8").split("old=[")[0])
fore=shape("B19_FrontFloor");rear=shape("B19_RearFloor")
# Central battery bay opens from above once removable operator modules are off.
# Swap the forward slat above the cell for a slat under the outboard half of
# the 44..65.8 positive bank. Keep the entire battery and the two strap saddles.
opening=box(-12.4,18.7,72.9,107.3,37.6,32)
def battery_clear(s,x,dx):
    s=s.cut(opening)
    rail=box(x,57.3,74,dx,4.2,3)
    return s.fuse(rail).removeSplitter()
fore=battery_clear(fore,-104,123.6)
rear=battery_clear(rear,20.4,126.6)
# Countersinks follow the actual source head cones. New material encroaches
# only into the previous oversized cone. Keep shank clearance and driver throat.
for frame,axes in [(0,[-80,-70]),(1,[112,122])]:
    s=[fore,rear][frame]
    rings=[]
    for x in axes:
        for y in (-22.5,22.5):
            ix=([-80,-70,112,122].index(x)*2)+(1 if y>0 else 0)
            screw=shape("H01_source_M2p5x16_flat_"+str(ix))
            h=screw.BoundBox.ZMax
            ring=cylinder(x,y,h-1.6,3.2,1.6).cut(screw).cut(cylinder(x,y,h-1.7,1.4,1.9))
            rings.append(ring)
            s=s.cut(cylinder(x,y,h,3.05,39))
    s=unite([s]+rings)
    if frame==0:fore=s
    else:rear=s
# The saddle is now moulded into the jaw; its original two servo ear bolts,
# headwashers and nutwashers stay separate. The servo enters the open jaw.
saddle=shape("YAW_REAL_REMOVABLE_SERVO_SADDLE")
joined=fore.fuse(saddle).removeSplitter()
if len(joined.Solids)==1 and joined.isValid():
    fore=joined;D.YAW_REAL_REMOVABLE_SERVO_SADDLE.ViewObject.Visibility=False
else:raise RuntimeError("Yaw landing and saddle are not connected")
# The corner trim is restricted to material outside the new body profile.
# Avoid shrinking the actual underbank connector cradle or its strap slots.
closure=(P/"close-shared-interface.py").read_text(encoding="utf8")
exec(closure[closure.index("def ring("):closure.index("skin=body.cut")])
edge=Part.makeLoft([ring(q,2.15) for q in rows],True,True)
aft=rear.common(box(142,-110,36,28,220,26))
rear=rear.cut(aft.cut(edge)).removeSplitter()
fc=shape("D19_ROUNDED_FORE_COWL").cut(box(-151,-28,45,5,58,7.2))
D.D19_ROUNDED_FORE_COWL.Shape=fc
D.B19_FrontFloor.Shape=fore;D.B19_RearFloor.Shape=rear
D.recompute();D.save()
# Local ring of integral teal frame is now exterior-visible fixed neck.
# Current skin has clearance for lifting; the next test covers retaining the
# two body cowls and the complete head movement, independent of the anchor seat.
exec(closure[closure.index("v=G.activeDocument()"):closure.index('wr("closure-receipt')])
wr("seat-receipt.json",{"front_solids":len(fore.Solids),"rear_solids":len(rear.Solids),"front_valid":fore.isValid(),"rear_valid":rear.isValid(),"moulded_saddle":True,"print_release":False})

