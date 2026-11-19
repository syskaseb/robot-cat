"""Integrate the stationary lower collar, open the moving back, and form the detachable cowls."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,math,json
P=Path(__file__).parent
exec((P/"floor19b.py").read_text(encoding="utf8").split("old=[")[0])
def ellipse_xy(x,y,z,rx,ry):
    c=Part.Ellipse(V(x,y,z),max(rx,ry),min(rx,ry))
    w=Part.Wire([c.toShape()])
    if ry>rx:w.rotate(V(x,y,z),V(0,0,1),90)
    return w
def collar(d):
    return Part.makeLoft([ellipse_xy(-130,0,z,a-d,b-d) for z,a,b in [(47.4,28,30),(68,32,35),(92,36,39),(97,36.5,39.5)]],True,True)
fore=shape("B19_FrontFloor")
rear=shape("B19_RearFloor")
neck=collar(0).cut(collar(1.5))
# Printed on the fixed frame. The removable upper bearing, horn and head enter
# from above. A forward access gate permits inserting the yaw case and plug.
neck=neck.cut(box(-172,-9,46,25,18,28))
fore=fore.fuse(neck).removeSplitter()
D.D19_FIXED_INNER_NECK.ViewObject.Visibility=False
# Former full ellipsoid crossed the fixed yaw motor. The skirt now overlaps
# the open fixed collar at neutral and leaves room for the linked head axes.
headcut=Part.makeLoft([ellipse_xy(-132,0,z,a,b) for z,a,b in [(46,58,47),(95,47.5,45),(117,45,44)]],True,True)
back=shape("D19_BROAD_SKULL_BACK").cut(headcut)
D.D19_BROAD_SKULL_BACK.Shape=back
# Lower the short threading rungs only where they intruded into the battery.
# The two 18 mm-wide top saddles still bear at the full z=52 seating plane.
battery=shape("Battery_GEA223S30X6GT").BoundBox
window=box(battery.XMin-.1,battery.YMin-.15,battery.ZMin,battery.XLength+.2,battery.YLength+.3,4)
fore=fore.cut(window);rear=rear.cut(window)
mb=shape("B19_TailMatedPair").BoundBox
rear=rear.cut(box(mb.XMin-.2,mb.YMin-.2,mb.ZMin,mb.XLength+.4,mb.YLength+.4,mb.ZLength+.2))
# Bow the flanks away from the real low bank and mated JR. Taper to the rear
# operator panel; hips keep open cutouts and both permanent switches stay whole.
def ring(row,d):
    x,w,lo,hi=row
    z=(lo+hi)/2;h=(hi-lo)/2-d;w=w-d;k=.72
    poles=[[(0,h),(k*w,h),(w,k*h),(w,0)],[(w,0),(w,-k*h),(k*w,-h),(0,-h)],[(0,-h),(-k*w,-h),(-w,-k*h),(-w,0)],[(-w,0),(-w,k*h),(-k*w,h),(0,h)]]
    edges=[]
    for q in poles:
        c=Part.BezierCurve();c.setPoles([V(x,y,z+dz) for y,dz in q]);edges.append(c.toShape())
    return Part.Wire(edges)
rows=[(-149,45,45,127),(-121,91,14,150),(-96,104,-2,164),(-55,103,-2,169),(25,103,-2,170),(91,102,-2,171),(145,101,4,168),(174,94,15,163),(204,61,37,148),(213,38,55,133)]
body=Part.makeLoft([ring(q,0) for q in rows],True,True);inner=Part.makeLoft([ring(q,1.45) for q in rows],True,True)
skin=body.cut(inner)
def ell(c,r):
    m=A.Matrix();m.A11,m.A22,m.A33=r;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(*c));return s
skin=skin.cut(ell((-164,0,145),(82,104,76)))
for x in (-75,125):
    for y in (-120,38):skin=skin.cut(box(x-34,y,-12,68,82,54))
# The stem approaches its panel along its own axis.
skin=skin.cut(box(202,-12,72.8,15,25,25))
skin=skin.cut(box(161,-112,91,14,41,14))
skin=skin.cut(box(126,-13,143,50,35,38))
# High roof speaker grille plus separated Pi inlet/outlet slots.
for x in (25,37,49,61,73,85,97):
    skin=skin.cut(box(x,-14,159,3,27,22))
for x in (-91,-80,-69,-58,-47):
    skin=skin.cut(box(x,-56,141,3,21,37)).cut(box(x,35,141,3,21,37))
# Tool pilots are references used with cowls/electronics removed.
tool_shapes=[cylinder(x,y,48.52,2.65,38) for x in [-80,-70,112,122] for y in [-22.5,22.5]]
tools=publish("B19_ToolEightAnchors",Part.makeCompound(tool_shapes),"project straight driver R2.65 mm, open installation",(.87,.63,.29))
tools.ViewObject.Visibility=False
# A shaft driver along X is used before fitting the optical front.
cross=publish("B19_ToolYawPin",cylinder(-174,0,130,2.7,29,(1,0,0)),"project yaw pin driver, before fitting optical front",(.87,.63,.29))
cross.ViewObject.Visibility=False
for n,s in [("B19_FrontFloor",fore),("B19_RearFloor",rear),("D19_ROUNDED_FORE_COWL",skin.common(box(-160,-120,-10,180,240,200))),("D19_ROUNDED_REAR_COWL",skin.common(box(20,-120,-10,204,240,200)))]:
    D.getObject(n).Shape=s.removeSplitter()
D.recompute();D.save()
v=G.activeDocument().activeView()
def view(direction,n):
    axis=V(*direction);axis.normalize();right=V(0,0,1).cross(axis);right.normalize()
    v.setCameraOrientation(A.Rotation(right,axis.cross(right),axis,"ZXY").Q)
    v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/(n+".png")),1440,960,"White")
view((-1.4,-1,.55),"three-quarter")
view((-1,0,.03),"front");view((0,-1,.035),"side")
skins=["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","D19_BROAD_SKULL_BACK","BR_COMMON_OPTICAL_MASK","D19_SKULL_EARS"]
for n in skins:D.getObject(n).ViewObject.Visibility=False
for n in ("B19_TailJRUnderBank","B19_TailLaps"):D.getObject(n).ViewObject.Visibility=True
view((-1.15,-1,.95),"interior")
for n in skins:D.getObject(n).ViewObject.Visibility=True
for n in ("B19_TailJRUnderBank","B19_TailLaps"):D.getObject(n).ViewObject.Visibility=False
view((-1.4,-1,.55),"three-quarter")
D.recompute();D.save()
wr("closure-receipt.json",{"shell_profiles":rows,"fixed_collar":len(fore.Solids),"rear":len(rear.Solids),"physical_PASS":False})

