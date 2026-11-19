"""Establish sockets, positive inlay capture and a removable face on the saved head."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,json,runpy
P=Path(__file__).parent
src=(P/"head-and-shoulder.py").read_text()
exec(src[:src.index("# Both reception seats")])
mask=sh("C19_FaceAndEars");back=sh("C19_OpenRearHelmet");receipts=[]
def assign(name,s):
    s=s.removeSplitter()
    if s.isNull() or not s.isValid() or len(s.Solids)!=1:
        receipts.append([name,"rejected",len(s.Solids)])
        return
    D.getObject(name).Shape=s;receipts.append([name,"installed",s.Volume])
for sign,side in [(1,"L"),(-1,"R")]:
    axis=V(-.843,.516*sign,.150);axis.normalize()
    c=V(-210.14,sign*43,160);orient=A.Rotation(V(0,0,1),axis)
    def loc(s):
        s.Placement=A.Placement(c,orient).multiply(s.Placement)
        return s
    iris=sh("C19_Iris_"+side)
    # Split post with a tapered shoulder behind the mask. The black through-pin
    # spreads the split after the amber insert has been seated from outside.
    locking=Part.makeCone(2.98,3.45,1.4,V(0,0,-4.7),V(0,0,1)).cut(cyl((0,0,-5),1.45,5,(0,0,1)))
    iris=iris.fuse(loc(locking)).cut(loc(box(-.37,-4,-5,.74,8,4))).removeSplitter()
    assign("C19_Iris_"+side,iris)
    # Capture the black through-pin in the split iris once pressed from the front.
    black=sh("C19_Pupil_"+side)
    barb=Part.makeCone(1.18,1.61,.75,V(0,0,-5.55),V(0,0,1))
    barb=barb.fuse(cyl((0,0,-4.81),1.38,1,(0,0,1)))
    assign("C19_Pupil_"+side,black.fuse(loc(barb)))
    # Relieve the edge of the mask where the dome lands, leaving the post bore.
    mask=mask.cut(sh("C19_Iris_"+side).common(loc(box(-13,-14,-.3,26,28,6))))
mask=mask.cut(sh("C19_Nose"))
assign("C19_FaceAndEars",mask)
# Divide two rigid moving housings at their mating skins. Keep original ears
# accessible from above. The mask is removed frontward after the helmet screws.
back=back.cut(sh("C19_FaceAndEars"))
assign("C19_OpenRearHelmet",back)
for i in [1,2]:
    name="C19_Ear_"+str(i);ear=sh(name)
    ear=ear.cut(sh("C19_OpenRearHelmet")).cut(sh("C19_FaceAndEars"))
    if len(ear.Solids)>1:
        ribs=sorted(ear.Solids,key=lambda q:q.Volume,reverse=True)
        receipts.append([name,"loose fragments omitted mm3",[q.Volume for q in ribs[1:]]]);ear=ribs[0]
    assign(name,ear)
D.recompute();G.runCommand("Std_Save")
names=[o.Name for o in D.Objects if o.Name.startswith("C19_") and len(o.Shape.Solids)]
write("face-inserts.json",receipts)
write("final-members.json",{n:dict(valid=sh(n).isValid(),solids=len(sh(n).Solids),volume=sh(n).Volume,extents=[sh(n).BoundBox.XLength,sh(n).BoundBox.YLength,sh(n).BoundBox.ZLength]) for n in names})
runpy.run_path(str(P/"views.py"))

