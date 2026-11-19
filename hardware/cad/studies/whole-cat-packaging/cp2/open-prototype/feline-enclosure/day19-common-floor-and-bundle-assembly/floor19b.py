"""Rebuild the two independently mounted carriers in the received 19B FreeCAD copy (mm)."""
from pathlib import Path
import json, math
import FreeCAD as A, FreeCADGui as G, Part
P = Path(__file__).parent
D = A.ActiveDocument
assert Path(D.FileName).resolve() == (P / "whole-cat19B.FCStd").resolve()
V = A.Vector
def box(x,y,z,dx,dy,dz):
    return Part.makeBox(dx,dy,dz,V(x,y,z))
def unite(shapes):
    return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes)>1 else shapes[0]
def rib(points, y, thickness):
    vertices = [V(x,y,z) for x,z in points]
    return Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(V(0,thickness,0))
def cylinder(x,y,z,r,h,d=(0,0,1)):
    return Part.makeCylinder(r,h,V(x,y,z),V(*d))
def publish(n,s,kind,color):
    o=D.getObject(n) or D.addObject("Part::Feature",n)
    o.Shape=s
    if "EvidenceKind" not in o.PropertiesList: o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=kind
    o.ViewObject.ShapeColor=color
    o.ViewObject.DisplayMode="Shaded"
    return o
def shape(n):return D.getObject(n).Shape
def contact(a,b):
    return max(0.0,a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
def wr(n,obj):
    (P/n).write_text(json.dumps(obj,indent=2)+"\n",encoding="utf8")
old=["D19_OPEN_GIMBAL_LOAD_PORTAL","P01_load_rail","P01_load_rail_instance2","D19_LOW_FORE_CARRIER","D19_LOW_REAR_CARRIER"]
base_z=shape("P01_load_rail").BoundBox.ZMin
head_z=shape("H01_source_M2p5x16_flat_0").BoundBox.ZMax
# Each half has two paired, countersunk anchor landings. The remaining floor
# clears the bought chassis. Install its four screws before filling the decks.
def floor(x0,x1,first_anchor):
    xs=[first_anchor,first_anchor+10]
    parts=[]
    for y in (-22.5,22.5):
        parts.append(box(first_anchor-5,y-4.7,base_z,20,9.4,head_z-base_z))
    parts += [box(x0,-24.8,40.4,x1-x0,4.6,5),box(x0,20.2,40.4,x1-x0,4.6,5)]
    for x in [first_anchor-3,x0+2,x1-6]:
        parts.append(box(x,-89,40.4,4.5,178,3.8))
    for y in [-89,85]:
        parts.append(box(x0,y,40.4,x1-x0,4,4.6))
    return parts
def anchor_bores(s,axes):
    for x in axes:
        for y in [-22.5,22.5]:
            s=s.cut(cylinder(x,y,base_z-1,1.40,12))
            s=s.cut(Part.makeCone(1.40,2.70,1.30,V(x,y,head_z-1.22)))
    return s.removeSplitter()
fore=floor(-106,19.6,-80)
rear=floor(20.4,166,112)
# Cross-section above the servo landing retains the source saddle, upper
# bearing bores and cap-nut seats. All lower portal and rail material is replaced.
upper=shape(old[0]).common(box(-151,-35,66.5,46,70,56))
fore.append(upper)
for y in [-26.5,21.4]:
    fore.append(rib([(-121,65),(-117,74),(-108,73),(-75,45),(-65,45),(-65,41),(-108,41)],y,5.1))
# Open fuse banks rest on narrow slats at the true z=77 lower face. Slots
# between slats provide access from below for straps before the banks fill.
for parts,x0,x1,posts in [(fore,-105,19.6,[-103,-73,15]),(rear,20.4,148,[23,77,141])]:
    for ymin,ymax in [(-95,-43),(44,90)]:
        for y in [ymin+3,ymax-7]:
            parts.append(box(x0,y,74,x1-x0,4,3))
        for x in posts:
            parts.append(box(x,ymin+2,73.4,3.6,ymax-ymin-4,3.6))
        # Two transverse supports transfer each bank to the base by the outer rim.
        for x in [posts[0],posts[-1]]:
            y=-88.5 if ymin<0 else 85.5
            parts.append(box(x,y,43.4,3.6,3.4,32.5))
# Under-bank tail JR storage is open from above before installing the fuses.
# A flat U with 24 mm centre radius retains its minimum 22 mm inner bend for
# a 3.5 mm-wide flat lead. The tail factory lead stays separate.
tray=box(75,-91,60,75,54,2.8)
for x in [76,144]:
    tray=tray.cut(box(x,-89,59,3,11,5)).cut(box(x,-55,59,3,11,5))
rear += [tray,box(144,-87,43.7,4,4,17),box(76,-87,43.7,4,4,17)]
# Tail saddle and bearing use the retained two pairs of transverse steel
# fittings. Flat lands occupy only the original washer-to-part grip.
def tail_upright(y,seats,lo,hi,spine_x):
    items=[box(spine_x,y,43.5,4.2,3,hi-43.5)]
    for z in seats:
        items.append(box(min(spine_x,136),y,z-3.3,max(spine_x+4.2,144)-min(spine_x,136),3,6.6))
    return unite(items)
# A low crossbar carries both uprights to the four rear axes.
rear.append(box(125,-54,41.4,6,78,4))
rear.append(box(126,-54,41.4,21,46,3.2))
for y,seats,spine in [(-50.5,[120,140],125),(-13,[110,150],160)]:
    # Keep a bypass outside the case/race ring at its full section.
    rear.append(box(min(126,spine),y,41.4,abs(spine-126)+5,3.2,4.5))
    seat=tail_upright(y,seats,43.5,max(seats)+3.3,spine)
    for z in seats:seat=seat.cut(cylinder(140,y-.2,z,1.15,3.6,(0,1,0)))
    rear.append(seat)
fore_shape=anchor_bores(unite(fore),[-80,-70])
rear_shape=anchor_bores(unite(rear),[112,122])
# The lower neck cover is stationary. Retain its source surface while checking
# contact with the new direct side ribs and the removable servo as separate facts.
for n,s in [("B19_FrontFloor",fore_shape),("B19_RearFloor",rear_shape)]:
    publish(n,s,"19B common floor engineering candidate",(.25,.45,.45))
for n in old:D.getObject(n).ViewObject.Visibility=False
# A single continuous duct follows the U and its through-path tangencies.
r=24;xc=102;yc=-64;z=66.2
v0=V(147,yc-r,z);v1=V(xc,yc-r,z);v2=V(xc,yc+r,z);v3=V(139,yc+r,z)
arc=Part.Arc(v1,V(xc-r,yc,z),v2).toShape()
path=Part.Wire([Part.makeLine(v0,v1),arc,Part.makeLine(v2,v3)])
# Profile includes assembly allowance. Cross section stays normal around bend.
p=[v0+V(0,y,h) for y,h in [(-3,-2),(3,-2),(3,2),(-3,2),(-3,-2)]]
duct=path.makePipeShell([Part.Wire(Part.makePolygon(p).Edges)],True,True)
region=publish("B19_TailJRUnderBank",duct,"JR300 tail occupied U duct 6 x 4 in accessible open tray",(.88,.55,.14))
region.ViewObject.Transparency=65;region.ViewObject.Visibility=False
D.D19_JR300_TAIL_RESERVE.ViewObject.Visibility=False
D.recompute();D.save()
both=[("front",fore_shape),("rear",rear_shape)]
receipt={"physical_PASS":False,"actual_fit":None,"actual_cut":None,"actual_slack":None,
 "floor":{},"tail_JR":{"occupied_centerline":path.Length,"ends":[list(v0),list(v3)],"inner_radius_mm":22.25,"remaining_of_246":246-path.Length,"tray_z":62.8,"contacts":{}},
 "neck_skin_common_front":contact(fore_shape,shape("D19_FIXED_INNER_NECK"))}
for label,s in both:
    names=[o.Name for o in D.Objects if o.Name.startswith(("H01_source_","YAW_SHAFT_FORK_POSITIVE","TAIL_CARTRIDGE_CAP_ROOT","TAIL_SADDLE_ROOT"))]+["MG92B_Head_yaw","MG92B_Tail","TAIL_FIXED_BEARING_CARTRIDGE","TAIL_REAL_REMOVABLE_SERVO_SADDLE","YAW_REAL_REMOVABLE_SERVO_SADDLE","Yaw608_120","Yaw608_134","MAX98357A_amp","D19_DATA_STORAGE_LAYER","BR_PAIR_HY","BR_FLANK_HP_PAIR","WAVEGO_complete_126_source_solids"]
    # Chassis has 126 solids; only the physically adjacent solids need booleans.
    hits={}
    for n in names:
        t=shape(n)
        if n.startswith("WAVEGO"): hits[n]=sum(contact(s,k) for k in t.Solids if k.BoundBox.intersect(s.BoundBox))
        else:hits[n]=contact(s,t)
    receipt["floor"][label]={"solids":len(s.Solids),"valid":s.isValid(),"volume":s.Volume,
        "bounds":list([s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength]),"contact_mm3":hits}
for n in ["MG92B_Tail","MAX98357A_amp","B19_RearFloor","D19_DATA_STORAGE_LAYER","D19_ROUNDED_REAR_COWL","OP_S1_PRIMARY_CASE_CONSERVATIVE","TAIL_ROTATING_HOLLOW_REAL_ROOT"]:
    receipt["tail_JR"]["contacts"][n]=contact(duct,shape(n))
wr("root-and-underbank.json",receipt)

