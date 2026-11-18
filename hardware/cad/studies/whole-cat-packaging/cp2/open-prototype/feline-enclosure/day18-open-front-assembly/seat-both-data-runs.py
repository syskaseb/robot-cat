"""Seat the actual two runs, form the fixed skull well and close the full audio plug field."""
from pathlib import Path
import math,json
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("FIT_FRONT_FLOOR")
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def new(n,s,col):
    assert s.isValid() and not s.isNull(),n
    o=D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode="Shaded";return o
def loft(rows,d):
    sections=[]
    for x,w,low,high,e in rows:
        z=(low+high)/2;rz=(high-low)/2-d;pts=[]
        for i in range(28):
            ang=2*math.pi*i/28;c,s=math.cos(ang),math.sin(ang)
            pts.append(V(x,(w-d)*math.copysign(abs(c)**e,c),z+rz*math.copysign(abs(s)**e,s)))
        cur=Part.BSplineCurve();cur.interpolate(pts,PeriodicFlag=True);sections.append(Part.Wire([cur.toShape()]))
    return Part.makeLoft(sections,True,True)
def mesh(q):
    vs=[V(*p) for p in q["vertices"]]
    s=Part.makeSolid(Part.makeShell([Part.Face(Part.makePolygon([vs[a],vs[b],vs[c],vs[a]])) for a,b,c in q["faces"]])).removeSplitter()
    if s.Volume<0:s.reverse()
    return s
def ell(c,axes):
    m=A.Matrix();m.A11,m.A22,m.A33=axes
    s=Part.makeSphere(1).transformGeometry(m);s.translate(V(*c));return s
floor=D.OPEN_PORTAL_AND_FLOOR.Shape
panels=[D.getObject("FRONT18_FORE_"+tag+"_PANEL").Shape for tag in ("NEG","POS")]
seats=[]
for i,x in enumerate((-63,-31)):
    halves=[]
    for side in (-1,1):
        # Actual cable at these stations runs near Y=-60 and Y=+17.
        # No transverse rail runs through the moving ToF middle.
        y=54.4 if side==1 else -58
        post=box(x-1,y,126.5,6,3.6,39)
        lip=box(x,9 if side==1 else -65.5,162.5,4,49 if side==1 else 13.5,4.1)
        foot=box(x-2,y,126.1,8,3.6,3.6)
        half=post.fuse(lip).fuse(foot).removeSplitter();halves.append(half)
    sh=Part.makeCompound(halves)
    o=new("FIT_DATA_SEATS_"+str(i),sh,(.31,.45,.46));o.ViewObject.Visibility=False
    seats.extend(halves)
integrated=floor.multiFuse(panels+seats).removeSplitter()
assert integrated.isValid() and len(integrated.Solids)==1
new("FIT_FRONT_FLOOR",integrated,(.24,.40,.42));D.OPEN_SINGLE_FRONT_FLOOR.ViewObject.Visibility=False
# Replace the floating inner U with the outside of the head's motion socket.
# The body-adjacent side of the complete servo and the stepped floor stay open.
rows=json.loads((P/"closed-outline.json").read_bytes())["stations"]
outer=loft(rows,0);inside=loft(rows,2)
source=json.loads((P.parent/"day18-latest-whole-front"/"shoulder-volume.json").read_bytes())
a,b=mesh(source["small"]),mesh(source["large"])
well=b.cut(a).common(outer)
# Common rear entry for mechanism and moving groups, with continuous side cheeks.
rear=ell((-103,0,140),(58,65,60)).fuse(box(-119,-60,85,75,120,103))
throat=box(-157,-34,69,99,68,80)
well=well.cut(rear.fuse(throat)).common(box(-200,-110,8,220,220,228))
outer_front=max(D.OPEN_FRONT_COWL.Shape.Solids,key=lambda t:t.Volume)
front=outer_front.fuse(well).removeSplitter()
new("FIT_FRONT_COWL",front,(.15,.16,.18));D.OPEN_FRONT_COWL.ViewObject.Visibility=False
# Extend only the connector-side surface of the existing dorsal shoulder.
# Fuse a smoothly rounded shell around the entire mic cable plug approach.
outer_pod=ell((62,61,168),(20,23,17));inner_pod=ell((62,61,168),(18,21,15))
aft=D.OPEN_AFT_COWL.Shape.fuse(outer_pod.cut(inside)).cut(inner_pod).removeSplitter()
new("FIT_AFT_COWL",aft,(.15,.16,.18));D.OPEN_AFT_COWL.ViewObject.Visibility=False
facts=dict(floor_solids=len(integrated.Solids),front_solids=len(front.Solids),aft_solids=len(aft.Solids),
    well_volume=well.Volume,well_to_outer_join_mm3=outer_front.common(well).Volume,
    full_USB_C_field_vs_aft=aft.common(D.INSERT_AUDIO_USB_C_FULL_MATE_FIELD.Shape).Volume,
    phone_plug_field_status="Nominal unbound USB_AUDIO-C mating field, sample still required.",
    body_service_monitor="Original bay pending independent fit result",physical_PASS=False)
(P/"separate-layer-fit.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
