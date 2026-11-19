"""Complete the shared bearing, JR tray and PCB/battery support interfaces."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,math,json
P=Path(__file__).parent
code=(P/"floor19b.py").read_text(encoding="utf8")
exec(code[:code.index("old=[")])
fore=shape("B19_FrontFloor");rear=shape("B19_RearFloor")
# Actual 608 OD is 22, both concentric bearing lands retain their source axial shoulders.
fore=fore.cut(cylinder(-130,0,99.99,11.06,7.02))
# Support the pitch pair at its seating face and keep a straight open keyed exit.
pbox=shape("BR_FLANK_HP_PAIR").BoundBox
seat=box(-106,-60,72.7,29,18,2.8)
fore=fore.cut(box(-112,-59,75.49,32,16,11)).fuse(seat)
# Open slotted textile saddles. Each strap winds around the 35 x 21.5 battery
# and under its own saddle. Lower rungs keep the threading aperture clear.
def strap_saddle(x):
    bridge=box(x-9,15,49,18,45,3)
    for y in (17,56):bridge=bridge.cut(box(x-8.1,y,48.8,16.2,2.4,3.5))
    return unite([bridge,box(x-9,20.3,44,2.4,4,6),box(x+6.6,20.3,44,2.4,4,6)])
fore=fore.fuse(strap_saddle(-2))
rear=rear.fuse(strap_saddle(84))
# The DATA216 cable bottom crosses the frame in one longitudinal window.
# Narrow its occupied layer to 9.8 around the OD6.8 and retain the complete original loop.
data=box(31,-36.9,40.3,92,9.8,77)
D.D19_DATA_STORAGE_LAYER.Shape=data
D.D19_DATA_STORAGE_LAYER.OccupancyNote="216 mm reserve; 6.8 jacket plus 1.5 mm on each side. Both approach paths remain separate."
rear=rear.cut(box(30.5,-37.3,39.9,93,10.6,11))
# Extend the storage floor for a U which also transports the tail JR unit.
# Both ends face the open rear. The installed factory mate and three insulated
# laps seat on different sides; the MG's own 250 mm is never debited to JR.
z=66.2; r=24.; y=-65.; start=115.;end=154.
cx=(start+end+math.pi*r-246)/2
a=V(start,y-r,z);b=V(cx,y-r,z);c=V(cx,y+r,z);e=V(end,y+r,z)
wire=Part.Wire([Part.makeLine(a,b),Part.Arc(b,V(cx-r,y,z),c).toShape(),Part.makeLine(c,e)])
def sweep_rect(path,point):
    p=[point+V(0,i,j) for i,j in [(-3,-2),(3,-2),(3,2),(-3,2),(-3,-2)]]
    return path.makePipeShell([Part.Wire(Part.makePolygon(p).Edges)],True,True)
duct=sweep_rect(wire,a)
D.B19_TailJRUnderBank.Shape=duct
# Thin slotted shelf is carried on the outer rim. Inside cutout keeps access
# to the DATA layer and avoids a broad unsupported horizontal plate.
shelf=box(cx-r-4,-92.5,60.2,158-(cx-r-4),55,2.6)
shelf=shelf.cut(box(cx+1,-82,60,149-cx,32,3.3))
for x in (cx-14,67,112,140):
    for yslot in (-85,-49):
        shelf=shelf.cut(box(x,yslot,59.9,3,5.6,3.4))
rear=rear.fuse(shelf).fuse(box(29,-88,43.8,4,4,17.2))
# Occupied mated pair cloned from the selected equivalent two-piece JR pair.
mated=shape("BR_PAIR_HY").copy()
mb=mated.BoundBox;mated.translate(V(start-mb.XMin,-89-mb.Center.y,z-mb.Center.z))
pair=publish("B19_TailMatedPair",mated,"tail servo/JR full project mate; same keyed envelope as head pair",(.37,.32,.26))
# Three individual lap positions 25 fan + 9 insulated + 8 lap within 20 sleeves.
# This is occupied space; the continuations are soldered with the cover open.
laps=unite([box(end,-44,64.2,25,6,4),box(end+24,-47,64.2,18,12,4)])
lap=publish("B19_TailLaps",laps,"XB32 F_TY.out, XB33 G_TAIL.5, XS33 R3.2; separate continuations",(.88,.6,.27))
lap.ViewObject.Visibility=False
# Upstanding tray supports are outside the lays and full plug. Remove material
# only from the 2 named connector/duct entrances, leaving the adjacent pillar.
rear=rear.cut(box(113,-96.7,61.1,33,15.4,11)).cut(box(76,-92.2,64.1,77,6.4,4.3))
# Keyed mated pair rests on a separate shallow ledge, restrained by a tie.
pb=mated.BoundBox
cradle=box(pb.XMin-1,pb.YMin-.8,pb.ZMin-2.3,pb.XLength+2,pb.YLength+1.6,2.3)
for x in [pb.XMin+5,pb.XMax-8]:cradle=cradle.cut(box(x,pb.YMin+1,pb.ZMin-2.5,2.7,pb.YLength-2,3))
rear=rear.fuse(cradle).fuse(box(116,-91,59.5,25,4,2))
# A common rear bridge takes the four PCA steel sets at their actual through axes;
# y=41.6 is the back of the PCB and y=47.6 seats the rear washer. Keep E1 soldered.
pca=[]
for i in range(4):
    bb=shape("CB_PCA_%s_backwasher"%i).BoundBox
    x=bb.Center.x; zz=bb.Center.z
    pca.append(cylinder(x,41.6,zz,3.45,6,(0,1,0)).cut(cylinder(x,41.5,zz,1.15,6.2,(0,1,0))))
# Rearward rails touch the edge of each boss, leaving the full screw bore free.
for zz in (121.17,140.17):pca.append(box(78,44.3,zz+1.8,58,3.1,2.3))
for x in (80.5,135.5):pca.append(box(x,44.3,110.2,3.2,3.1,32))
pca.append(box(80.5,44.3,109.5,82.5,3.1,3.4))
pca.append(box(160,-12.6,106.8,3.2,60,4.1))
rear=unite([rear]+pca)
# Free lower cable passage between structural ribs, carrier stays in one piece.
for n,s in [("B19_FrontFloor",fore),("B19_RearFloor",rear)]:
    D.getObject(n).Shape=s.removeSplitter()
D.recompute();D.save()
tested={"changes":{},"tail_JR":{"transport_and_reserve":wire.Length,"plug":12,"fan":25,"insulated":9,"lap":8,"radius_inside":22.25,"mate_mm":[start,-89,z],"fan_origin":[end,-41,z],"contacts":{}}}
for obj in ["B19_TailJRUnderBank","B19_TailMatedPair","B19_TailLaps"]:
    tested["tail_JR"]["contacts"][obj]={n:contact(shape(obj),shape(n)) for n in ["B19_RearFloor","MG92B_Tail","MAX98357A_amp","D19_DATA_STORAGE_LAYER","OP_S1_PRIMARY_CASE_CONSERVATIVE","D19_ROUNDED_REAR_COWL","S0_body","Motor_ATO4A__1_2"]}
for n in ["B19_FrontFloor","B19_RearFloor"]:
    s=shape(n)
    tested["changes"][n]={"valid":s.isValid(),"solids":len(s.Solids),"volume":s.Volume,"contacts":{}}
    names=["BR_FLANK_HP_PAIR","MG92B_Head_yaw","MG92B_Tail","Yaw608_120","Yaw608_134","D19_DATA_STORAGE_LAYER","Battery_GEA223S30X6GT","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","D19_FIXED_INNER_NECK","D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","TAIL_FIXED_BEARING_CARTRIDGE","TAIL_REAL_REMOVABLE_SERVO_SADDLE","YAW_REAL_REMOVABLE_SERVO_SADDLE"]
    names.extend(o.Name for o in D.Objects if o.Name.startswith(("H01_source","CB_PCA","TAIL_SADDLE_ROOT","YAW_SHAFT_FORK_POSITIVE","TAIL_CARTRIDGE_CAP_ROOT")))
    for k in names:tested["changes"][n]["contacts"][k]=contact(s,shape(k))
wr("bearing-and-connected-units.json",tested)

