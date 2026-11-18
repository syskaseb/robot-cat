"""Keep the full bank and carry the front insert around the typed cable entries."""
from pathlib import Path
import math,json
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fuse(*s):
    q=s[0].multiFuse(s[1:])
    try:return q.removeSplitter()
    except Part.OCCError:return q
def show(n,s,old,c):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.DisplayMode="Shaded";o.ViewObject.Visibility=True
    if old:D.getObject(old).ViewObject.Visibility=False
    return o
def write():(P/"integrated-fit.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
facts={};teal=(.23,.40,.42);char=(.15,.16,.18)
jr=json.loads((P/"yaw-laid-factory.json").read_bytes())
pts=[V(*v) for v in jr["neutral_arc"]];s=pts[0];clock=math.asin((131.5-129.35)/(25*(1-math.cos(5*math.pi/6))))
out=V(math.cos(clock),0,-math.sin(clock));neg=V(0,-1,0);center=s+25*out
def polar(rad,u):return center+rad*(-out*math.cos(u)+neg*math.sin(u))+V(0,0,-4.95)
start=math.radians(22);end=math.radians(154)
angles=[start+(end-start)*i/24 for i in range(25)]
perimeter=[polar(29,u) for u in angles]+[polar(21,u) for u in reversed(angles)]
ring=Part.Face(Part.makePolygon(perimeter+[perimeter[0]])).extrude(V(0,0,2.75))
foot=box(-140,-68.1,126.1,10,22.8,3)
t=V(*jr["neutral_tangent"]);flat=V(t.x,t.y,0);flat.normalize();lateral=V(-flat.y,flat.x,0)
def local(a,b,z,length,width,height):
    base=pts[-1]+a*flat+b*lateral+V(0,0,z)
    poly=[base,base+length*flat,base+length*flat+width*lateral,base+width*lateral]
    return Part.Face(Part.makePolygon(poly+[poly[0]])).extrude(V(0,0,height))
saddle=fuse(ring,foot,local(-8,-5,-5,11,10,2.8),local(-7,-5,-2.8,9,1.4,4.5),local(-7,3.6,-2.8,9,1.4,4.5))
saddle=saddle.cut(local(-5.8,-6,-4.4,4.6,12,1.35))
fork=D.HEAD_YAW_FORK_FIXED_PITCH_HOUSING.Shape;held=fuse(fork,saddle)
facts["yaw_saddle"]=dict(attachment=fork.common(saddle).Volume,solids=len(held.Solids),valid=held.isValid(),laid_length=jr["rows"][2]["case_to_yaw_grip"],moving_length=jr["rows"][2]["yaw_grip_to_body"])
if held.isValid() and len(held.Solids)==1:
    show("BR_YAW_FORK_WITH_SADDLE",held,"HEAD_YAW_FORK_FIXED_PITCH_HOUSING",teal)
else:show("BR_YAW_SADDLE_TRIAL",saddle,None,teal)
D.BR_FLANK_PITCH.Shape=Part.makePolygon([V(*p) for p in jr["rows"][2]["centreline"]]);write()
# Bypass the cable on the NEG side of the Pi carrier. The original four
# Pi pads at Y ±24.5 and all four PCA lands are outside this opening.
old=D.F2_COMMON_PI_BUS_PCA_RECEIVER.Shape
relief=box(-61,-61,77.8,36,31,43)
rib=fuse(box(-65,-32.5,90.5,5,9,4.4),box(-65,-52.5,90.5,5,23,4.4),
         box(-65,-55.5,90.5,5,5,48.5),box(-65,-55.5,135.5,49,5,3.5),box(-20,-55.5,92,4,5,46.5))
new=old.cut(relief).fuse(rib).removeSplitter()
facts["Pi_carrier"]=dict(removed=old.common(relief).Volume,connected_to_old=old.common(rib).Volume,solids=len(new.Solids),valid=new.isValid(),
                         contacts={n:rib.common(D.getObject(n).Shape).Volume for n in ("PBAY_P_REAR","PBAY_F_AUX","PBAY_F_HY","Motor_ATO4A_1_3","Motor_ATO4A__1_3","Motor_ATO4A_1_4","Pi4B_actual_PCB")})
if new.isValid() and len(new.Solids)==1 and max(facts["Pi_carrier"]["contacts"].values())<.001:
    show("BR_PI_CARRIER_AROUND_LANE",new,"F2_COMMON_PI_BUS_PCA_RECEIVER",(.18,.24,.28))
write()
# Keep the two lower stations and the joint shelf. Transfer the positive
# ToF body support below the moving bight and put its upright outboard.
base=D.FIT_FLOOR_AND_BATTERY_MONITOR.Shape
pieces=sorted(D.BR_FLANK_SUPPORT_SUBSET.Shape.Solids,key=lambda v:v.BoundBox.ZMax)
newtower=fuse(box(-116,23.8,92,7,13,5),box(-116,32,92,7,36,5),box(-116,64,93,6,5,81),
              box(-149,63.8,170.8,39,5,3.6),box(-150,51.5,170.8,10,16,3.6),
              box(-150,51.2,173.5,10,2.6,6.1),box(-150,62.1,173.5,10,2.4,6.1))
newtower=newtower.cut(box(-147.3,50.4,171.3,4.6,18,1.35))
body=fuse(base,*pieces[:-1],newtower)
facts["tower"]=dict(attachment=base.common(newtower).Volume,solids=len(body.Solids),valid=body.isValid())
if len(body.Solids)==1 and body.isValid():
    show("BR_BODY_FLOOR_OUTER_TOWER",body,"BR_FLANK_FLOOR",teal)
    ref=show("BR_CURRENT_RECEPTION_SUBSET",Part.makeCompound(pieces[:-1]+[newtower]),None,teal);ref.ViewObject.Visibility=False
write()
# Open the dynamic end toward +X. The pitch-side anchor stays in the same
# world position and uses the same selected tie over the four-core pack.
arm=fuse(box(-163,26,113,11,6,4),box(-163,29.5,112,5.5,16,4),box(-163,41,98.6,5.5,5,16),
         box(-162,41,98.6,15,12.1,2.8),box(-156,41,101,8,2,4.8),box(-156,51,101,8,2.2,4.8))
arm=arm.cut(box(-154.5,40,99.1,4.6,14.3,1.35))
oldrec=D.D18C_TRUE_PITCH_OPTICAL_RECEIVER.Shape;rec=fuse(oldrec,arm)
facts["pitch_grip"]=dict(join=oldrec.common(arm).Volume,solids=len(rec.Solids),valid=rec.isValid())
if len(rec.Solids)==1 and rec.isValid():show("BR_PITCH_RECEIVER_OPEN_ENTRY",rec,"BR_PITCH_RECEIVER_AND_GRIP",teal)
write()
def passage(rows):
    wires=[]
    for x,y0,z0,y1,z1 in rows:
        pts=[V(x,y0,z0),V(x,y1,z0),V(x,y1,z1),V(x,y0,z1)]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    return Part.makeLoft(wires,True,True)
regions=json.loads((P/"covered-passages.json").read_bytes())
for owner,src,name in [("fixed","BR_CLOSED_CHEST_LIP","BR_CHEST_WITH_COVERED_ENTRIES"),("pitch","BR_PARTED_SKULL_BACK","BR_BACK_WITH_COVERED_ENTRIES")]:
    orig=D.getObject(src).Shape;result=orig
    for region in regions.values():result=result.cut(passage(region[owner]))
    result=result.removeSplitter()
    bosses=[]
    if owner=="pitch":
        for y in (-73,73):
            land=Part.makeCylinder(4.1,12,V(-165,y,145),V(1,0,0))
            bosses.append(abs(orig.common(land).Volume-result.common(land).Volume))
    facts[owner+"_cover"]=dict(solids=len(result.Solids),valid=result.isValid(),removed=orig.Volume-result.Volume,boss_loss=bosses)
    if len(result.Solids)==1 and result.isValid() and max(bosses or [0])<.03:show(name,result,src,char)
    write()
facts["physical_PASS"]=False;write()
D.Label="Body-fixed receptions - covered entrances and yaw-laid factory reserve";D.recompute();G.runCommand("Std_Save")
