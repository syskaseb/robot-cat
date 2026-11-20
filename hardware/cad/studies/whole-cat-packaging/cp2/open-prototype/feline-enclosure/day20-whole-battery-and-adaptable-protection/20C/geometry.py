"""20C structural battery opening and independent fuse support solids (mm)."""
from pathlib import Path
import math
import FreeCAD as App
import Part

V = App.Vector

def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0,y0,z0))

def fuse(*shapes):
    return shapes[0].multiFuse(list(shapes[1:])).removeSplitter() if len(shapes)>1 else shapes[0]

def bore(x,y,z,r,h):
    return Part.makeCylinder(r,h,V(x,y,z),V(0,0,1))

def bbox(shape):
    b=shape.BoundBox
    return [round(q,4) for q in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]]

def overlap(a,b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.
    return abs(a.common(b).Volume)

def peg_end(x,y):
    return box(x-3.16,y-4.35,76.15,x+3.16,y+4.0,78.98)

def connector_shelf():
    return fuse(
        box(27,37,130,36.5,49.8,132.25),
        box(18,32.3,129.25,33.5,41.5,132.25),
        box(14.1,27.5,129.25,22,41.5,132.25),
        box(13.0,28,131.9,14.12,40,136.05),
        box(36.25,28,131.9,37.45,40,135.55),
        box(31.8,30.8,129.25,37.45,34.3,132.25),
    ).cut(box(15.5,30.4,129.6,19,34.1,132.5)).removeSplitter()

def door_parts(rear):
    # Only the outer ends of the transverse bank webs move with this upper bridge.
    opening = box(70.6,94.5,73.65,101.5,104.2,104.2)
    taken = rear.common(opening)
    base = rear.cut(opening)
    fixed_roots = [
        box(64.6,94.7,74.15,70.6,101.4,82),
        box(101.5,94.7,74.15,107.7,103,82),
    ]
    base = fuse(base,*fixed_roots)
    # Reliefs around the two top-inserted keys. Their undersides seat at Z82.
    left_relief=box(64.75,95.05,82,70.6,102.87,87.15)
    right_relief=box(101.5,95.05,82,107.32,102.87,87.15)
    base=base.cut(left_relief).cut(right_relief)
    ear = box(65.0,95.3,82,107.05,102.6,86.8)
    # The original corner strips key into the parent shell. Cut only at
    # the actual partition planes to leave assembly clearance.
    taken=taken.common(box(70.82,94.7,73.65,101.28,103.6,104.2))
    tongue_shapes=[]
    ribs=[(77,80.2),(94,97.2)]
    for x0,x1 in ribs:
        ledge=box(x0-.16,89.8,71.8,x1+.16,96.8,74.25)
        web=box(x0-.16,94.76,72.0,x1+.16,96.8,83.0)
        tongue_shapes.extend([ledge,web])
    bridge=fuse(ear,taken,*tongue_shapes)
    hardware=[]
    for x in (67.8,104.2):
        y=99.1
        base=base.cut(bore(x,y,73.5,1.64,17)).cut(peg_end(x,y))
        bridge=bridge.cut(bore(x,y,81.9,1.68,9))
        shank=bore(x,y,74.8,1.5,12)
        head=bore(x,y,86.8,2.75,3)
        hardware.append(fuse(shank,head))
    # Full bearing surfaces on both ends and under both retained ribs.
    support = {
        "root_common_mm3":[round(overlap(rear.cut(opening),q),4) for q in fixed_roots],
        "end_bearing_plane_z":82.0,
        "ribs":[[77,80.2,89.8,94.5,74.25],[94,97.2,89.8,94.5,74.25]],
        "support_foot_original_common_mm3":[
            round(overlap(rear,box(x0,89.8,74.25,x1,94.5,75.0)),4) for x0,x1 in ribs
        ],
    }
    return base.removeSplitter(),bridge.cut(base).removeSplitter(),hardware,support

def mta_plate(bx,by,z):
    # Open ends and an unbroken central bearing. There are two independent
    # tie lanes so the actual body can be centered after the sample arrives.
    plate=box(bx-1.1,by-1,z-2.4,bx+33.5,by+19,z)
    rails=[box(bx-1.05,by-1,z-.2,bx+33.45,by+.45,z+1.9),
           box(bx-1.05,by+17.6,z-.2,bx+33.45,by+19,z+1.9)]
    plate=fuse(plate,*rails)
    for x in (bx+4,bx+21):
        for y in (by+1.1,by+13.3):
            plate=plate.cut(box(x,y,z-2.55,x+7.5,y+3.5,z+.3))
    return plate.removeSplitter()

def mta_shapes(doc):
    specs = {
        "FL":(-41,-98,141,"E19_WagoForeNeg",(-38,-14,-80.25,-77)),
        "FR":(-62.5,69,144,"E19_WagoForePos",(-59,-36,77,81)),
        "RL":(106,-97,141,"E19_WagoRearNeg",(110,136,-80.25,-76.0)),
        "RR":(142.5,61.5,140,"E19_RearBase",(141.0,143.0,79.9,84.5))
    }
    result={}
    for name,(x,y,z,actor,site) in specs.items():
        src=doc.getObject(actor).Shape
        x0,x1,y0,y1=site
        b=src.common(box(x0,y0,109,x1,y1,z-2.42))
        if b.isNull() or b.Volume<.1:
            raise RuntimeError("No structural bearing at MTA "+name)
        high=b.BoundBox.ZMax
        # MTA sample carrier stays separate. The shoe bears top-down on a
        # coarse land which is checked against the saved source below.
        if x1-x0 > 12:
            left=box(x0,y0,high,x0+4,y1,z-1.8)
            right=box(x1-4,y0,high,x1,y1,z-1.8)
            neck=Part.makeCompound([left,right])
        else:
            neck=box(x0,y0,high,x1,y1,z-1.8)
        top=box(x0-.15,min(y0,y+16),z-2.4,x1+.15,max(y1,y+17.9),z-.2)
        shim=fuse(mta_plate(x,y,z),*neck.Solids,top)
        # One long slot for a tie around the source land. RR uses the short
        # transverse stem with tie shoulders in Y.
        if x1-x0>5:
            slit=box(x0+1.05,y0-.8,high+2.5,x0+5.0,y1+.75,high+6.3)
        else:
            slit=box(x0-.4,y0+1.05,high+1.0,x1+.5,y0+4,high+3.8)
        shim=shim.cut(slit)
        # Seat on the retained structures. Remove only pads that would
        # occupy rigid source material inside this small footprint.
        for ident in ('H19_FrontFrame','E19_RearBase',actor):
            real=doc.getObject(ident).Shape
            if overlap(shim,real)>.001:
                shim=shim.cut(real)
        shim=shim.removeSplitter()
        result["MTA_"+name]=(shim,actor,round(high,4),bbox(b),[x,y,z,x+32,y+18,z+18])
    return result

def collect(doc):
    rear=doc.E19_RearBase.Shape
    fixed,bridge,bolts,seat=door_parts(rear)
    dock=connector_shelf()
    dock_join=overlap(fixed,dock)
    fixed=fuse(fixed,dock)
    other=mta_shapes(doc)
    return {"rear":fixed,"bridge":bridge,"bolts":bolts,"seats":seat,
            "dock":dock,"dock_root_common_mm3":dock_join,"mta":other}