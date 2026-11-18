"""Route the yaw reaction behind the bearing and support each complete bank by its flange."""
from pathlib import Path
import json
import FreeCAD as A
import Part

D=A.ActiveDocument
P=Path(__file__).parent
V=A.Vector
assert Path(D.FileName).resolve()==(P/"whole-front.FCStd").resolve()
assert not D.getObject("FRONT18_FORE_POS_PANEL")
def box(x,y,z,a,b,c): return Part.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,r,h): return Part.makeCylinder(r,h,V(x,y,z))
def feature(n,s):
    obj=D.addObject("PartDesign::Feature",n)
    obj.Shape=s
    obj.ViewObject.ShapeColor=(.23,.42,.44)
    obj.ViewObject.DisplayMode="Shaded"
    return obj
cx=-130
seat=cyl(cx,0,98,15.5,23)
for sy in (-1,1): seat=seat.fuse(cyl(cx,sy*14.5,110,3.5,11))
seat=seat.cut(cyl(cx,0,97,9,26)).cut(cyl(cx,0,100,11.1,22))
for sy in (-1,1):
    seat=seat.cut(cyl(cx,sy*14.5,109.5,1.1,13))
    seat=seat.cut(box(cx-2.42,12.1 if sy==1 else -22,111.9,4.84,9.9,1.8))
# Central rear column carries the outer races. No transverse member under the
# front-left moving fork. The removable servo saddle uses the real two M2 sets.
members=[seat,box(-112.5,-12,49,3.5,24,58),box(-119,-10,102,10,20,5),
         box(-118,-14,49,8,28,30),box(-118,-34,46.5,9,68,6)]
for sy in (-1,1):
    y0=28 if sy==1 else -34
    members.append(box(-140,y0,46.5,67,6,6))
    ledge=box(-140,sy*11.5-3.2,66.5,30,6.4,3)
    members.append(ledge.cut(cyl(-134,sy*11.5,64,1.15,9)))
frame=members[0].multiFuse(members[1:]).removeSplitter()
D.FRONT18_LOWER_BEARING_FRAME.Shape=frame
facts={"frame_valid":frame.isValid(),"frame_solids":len(frame.Solids),"banks":[],"floor_attachment":[]}
floors={"FORE":D.D18C_P02_THREE_ROOT_THROUGH_VERSION,"REAR":D.P03_rear_deck_integrated_load_yoke}
fore=floors["FORE"].Shape
facts["frame_to_floor_common"]=fore.common(frame).Volume
integrated=fore.fuse(frame).removeSplitter()
if integrated.isValid() and len(integrated.Solids)==1 and facts["frame_to_floor_common"]>0:
    fore_obj=feature("FRONT18_FLOOR_AND_YAW_ROOT",integrated)
    floors["FORE"].ViewObject.Visibility=False
    D.FRONT18_LOWER_BEARING_FRAME.ViewObject.Visibility=False
    floors["FORE"]=fore_obj
facts["front_floor_solid_count"]=len(integrated.Solids)
# Fuse is accessible from the top. Each supplied TE female is initially
# fitted from below after seating the holder. The present four-solid MTA
# compound carries an installation box for the unmodeled PA66 clips.
for side,tag in ((-1,"NEG"),(1,"POS")):
    D.getObject("FRONT18_BANK_BED_"+tag).ViewObject.Visibility=False
    for region,indices in (("FORE",range(3)),("REAR",range(3,6))):
        xmin,xmax=(-69,28) if region=="FORE" else (28,127)
        panel=box(xmin,side*70-15,125.915,xmax-xmin,30,2)
        support=[]
        for slot in indices:
            i=slot//2+(3 if side==-1 else 0)
            obj=D.getObject(("Motor_ATO4A_1_" if slot%2==0 else "Motor_ATO4A__1_")+str(i))
            center=obj.Shape.BoundBox.Center
            rot=A.Rotation(V(0,1,0),180)
            obj.Placement=A.Placement(center-rot.multVec(center),rot).multiply(obj.Placement)
            housing=obj.Shape.Solids[0]
            bb=housing.BoundBox
            edge=max(housing.Edges,key=lambda e: e.Length if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)<.01 else 0)
            direction=edge.Vertexes[-1].Point-edge.Vertexes[0].Point
            import math
            angle=math.degrees(math.atan2(direction.y,direction.x))
            root=bb.Center
            cut=box(-11.1,-5.65,-2,22.2,11.3,5)
            cut.rotate(V(),V(0,0,1),angle)
            cut.translate(V(root.x,root.y,126.915))
            panel=panel.cut(cut)
            facts["banks"].append({"holder":obj.Name,"panel":region+tag,"reference_flange_top":bb.ZMax,"printed_panel_z":[125.915,127.915],"window":[22.2,11.3],"case_clock":angle,"source_assembly_members":len(obj.Shape.Solids),"clip_fit":"one actual sample"})
        # Posts on the outside edge leave the inside face and TE connections
        # accessible. Each floor owns three positions. Integral floor feet
        # leave the deck splice and the opposite half independently installable.
        for x in ((-53,12) if region=="FORE" else (44.5,109.5)):
            y=80.5 if side==1 else -84.5
            foot=box(x-4,66 if side==1 else -84.5,46.5,8,18.5,4)
            post=box(x-3,y,49.5,6,4,77.9)
            support.extend((foot,post))
        united=panel.multiFuse(support).removeSplitter()
        n="FRONT18_"+region+"_"+tag+"_PANEL"
        feature(n,united)
        floor=floors[region].Shape
        facts["floor_attachment"].append(dict(panel=n,common=floor.common(united).Volume,valid=united.isValid(),solids=len(united.Solids)))
# Keep separate clear ownership for an engineering review. These panels are
# intended integral floor features on initial assembly, subject to actual
# floor intersection and useful bearing, never loose printable releases.
(P/"frame-and-panels.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.recompute()
D.save()
print("FRAME AND PANELS",facts["frame_to_floor_common"],facts["front_floor_solid_count"],facts["floor_attachment"])
