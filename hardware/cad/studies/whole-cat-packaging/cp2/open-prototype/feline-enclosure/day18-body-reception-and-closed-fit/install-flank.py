"""Fit lower reception to the existing floor and put the two paint rings on worn faces."""
from pathlib import Path
import json,math
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
r=json.loads((P/"flank-reception.json").read_bytes())
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fuse(parts):return parts[0].multiFuse(parts[1:]).removeSplitter()
def obj(n,s,col,vis=True):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=col
    o.ViewObject.DisplayMode="Shaded";o.ViewObject.Visibility=vis;return o
def lines(n,pts,c):
    o=obj(n,Part.makeCompound([Part.makePolygon([V(*p) for p in row]) for row in pts]),c,False)
    o.ViewObject.DisplayMode="Wireframe";o.ViewObject.LineColor=c;o.ViewObject.LineWidth=3
# Existing low HY saddle. The HP arm roots in the same negative portal foot.
floor=D.FIT_FLOOR_AND_BATTERY_MONITOR.Shape
low=min(D.BR_RECEIVER_HARD_MATERIAL.Shape.Solids,key=lambda s:s.BoundBox.ZMax)
hp=box(-111,-58,75.5,30,14,10)
hps=fuse([box(-117,-32,72.5,20,13,3),box(-110,-60.5,72.5,8,37,3),box(-110,-60.5,72.5,27,19,3),
          box(-110,-61,75,27,2.4,5.8),box(-110,-43.4,75,27,2.4,5.8)])
hps=hps.cut(box(-99.3,-62,73.15,4.6,23,1.35))
fan=r["extension"]["fans"];c=[q["lap_center"] for q in fan];x=min(q[0] for q in c);y=min(q[1] for q in c);z=c[0][2]
joints=[box(q[0]-3,q[1]-13,z-3,6,26,6) for q in c]
# Carry the shelf on the existing positive static DATA support, below its lip.
tray=fuse([box(-64,54.4,151,6,3.6,4.5),box(-64,54.4,z-6,25,3.6,3),box(x-3.5,y-13.5,z-6,19,28,3)])
# Support the body grip from the positive floor ledge outside the crosspin.
grip=fuse([box(-116,24,101,7,16,5),box(-116,35,101,7,26,5),
           box(-116,56,102,6,5,72.5),box(-149,55.5,171,38.5,6,3.4),
           box(-150,52.5,171,10,11,3.4),box(-150,52.1,173.5,10,2,6.1),box(-150,61.8,173.5,10,2,6.1)])
grip=grip.cut(box(-147.3,51,171.65,4.6,14,1.35))
br=Part.makeCompound([low,hps,tray,grip]);root=fuse([floor,low,hps,tray,grip])
facts=dict(floor_solids=len(root.Solids),valid=root.isValid(),root_attachments=[floor.common(q).Volume for q in (low,hps,tray,grip)],
           pairs=[root.common(D.BR_PAIR_HY.Shape).Volume,root.common(hp).Volume],splice_common=[root.common(s).Volume for s in joints])
assert root.isValid()
obj("BR_FLANK_FLOOR",root,(.23,.40,.42));D.BR_BODY_ROOT.ViewObject.Visibility=False
obj("BR_FLANK_SUPPORT_SUBSET",br,(.22,.47,.45),False)
obj("BR_FLANK_HP_PAIR",hp,(.73,.49,.14),False);obj("BR_FLANK_THREE_LAPS",Part.makeCompound(joints),(.76,.51,.17),False)
neutral=next(q for q in r["pitch"] if q["yaw"]==0)
lines("BR_FLANK_PITCH",[neutral["centreline"]],(.98,.49,.10))
lines("BR_FLANK_300",[r["extension"]["centreline"]]+[q["centreline"] for q in fan],(.75,.43,.19))
lines("BR_FLANK_TOF",[next(q for q in r["ToF_move"] if q["yaw"]==q["pitch"]==0)["centreline"]]+[q["centreline"] for q in r["ToF_head"]+r["ToF_fixed"]],(.21,.69,.27))
# Use split faces of the same solid. There are no coincident overlay meshes.
s=Part.Shape();s.read(str(P/"cheek-painted-surface.brep"));mask=D.BR_COMMON_OPTICAL_MASK;mask.Shape=s
body=(.16,.17,.19,1.);colors=[];counts={str(i):dict(gold=0,dark=0) for i in (-1,1)}
for f in s.Faces:
    color=body;b=f.BoundBox
    if b.XMax<-174 and b.ZMin>139 and b.ZMax<181:
        vs,tri=f.tessellate(.12)
        if tri:
            a,k,c=max(tri,key=lambda t:(vs[t[1]]-vs[t[0]]).cross(vs[t[2]]-vs[t[0]]).Length)
            p=(vs[a]+vs[k]+vs[c])/3;side=1 if p.y>0 else -1
            rho=lambda w,h:((p.y-side*43)/w)**2+((p.z-160)/h)**2
            if rho(16,19)<1:
                dark=rho(13.4,16.4)<1;color=(.008,.009,.012,1.) if dark else (.72,.50,.16,1.);counts[str(side)]["dark" if dark else "gold"]+=1
    colors.append(color)
mask.ViewObject.DiffuseColor=colors;mask.ViewObject.Deviation=.07
facts.update(painted_faces=counts,fit=None,physical_PASS=False)
(P/"flank-native.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.Label="Body reception and joint cover - current parting trial";D.recompute();G.runCommand("Std_Save")
