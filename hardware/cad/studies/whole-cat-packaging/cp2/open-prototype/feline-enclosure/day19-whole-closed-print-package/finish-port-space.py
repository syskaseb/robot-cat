"""Complete the same shared port allocation and expose per-unit occupied reserve budgets."""
from pathlib import Path
import json,math,datetime,traceback,ast
import FreeCAD as A,FreeCADGui as G,Part
from PySide import QtCore
P=Path(__file__).parent;D=A.getDocument("cat19");V=A.Vector
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=1)+"\n").encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def pref(*ps):return [o.Name for o in D.Objects if o.Name.startswith(ps)]
moves=[]
def move(names,target,rotation=None):
    os=[D.getObject(n) for n in names if D.getObject(n)]
    if rotation:
        t=A.Placement(V(),rotation)
        for o in os:o.Placement=t.multiply(o.Placement)
    b=os[0].Shape.BoundBox;v=V(*target)-V(b.XMin,b.YMin,b.ZMin)
    for o in os:o.Placement.Base+=v
    moves.append(dict(primary=os[0].Name,members=[o.Name for o in os],target_primary_min=target))
def add(n,s,note,color=(.76,.48,.16)):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.DisplayMode="Shaded"
    if "EvidenceKind" not in o.PropertiesList:o.addProperty("App::PropertyString","EvidenceKind")
    o.EvidenceKind=note;return o
# Point BUS USB longitudinally into the open work area rather than into the side wall.
move(["BUS25514_installed","D18C_DATA_BUS_FULL26_PROJECT_BOOT"]+pref("CB_BUS_","CF17_BUS_CSK"),[-4,24,125],A.Rotation(V(0,0,1),-90))
# Keep the negative vertical cable layer clear with complete paired power units.
move(["MAIN_Pololu4853"]+pref("CB_MAIN_","F3_MAIN_"),[86,-16,92])
move(["AUX_Pololu4092"]+pref("CB_AUX_","F3_AUX_"),[86,16,90])
move(["MAX98357A_amp"]+pref("CB_AMP_"),[79,-50,128])
for n in ("PBAY_P_SYS","PBAY_F_PI"):D.getObject(n).Placement.Base+=V(78,65,0)
move(["PBAY_POST_F0"]+pref("CB_POST_"),[105,-12,52])
# One complete DATA500. Reserve and both port approaches are separate occupied fields.
# The 216 mm open racetrack uses centre R33.4 for the 6.8mm jacket, preserving inner R30.
r=33.4;L=(216-r*math.radians(330))/2;z=78.7;y=-32;xl=70;xr=xl+L
p=[V(xl,y,z+r),V(xr,y,z+r)]
p += [V(xr+r*math.cos(a),y,z+r*math.sin(a)) for a in [math.pi/2-math.pi*i/96 for i in range(1,97)]]
p += [V(xl,y,z-r)]
p += [V(xl+r*math.cos(a),y,z+r*math.sin(a)) for a in [-math.pi/2-math.radians(150)*i/80 for i in range(1,81)]]
add("D19_DATA216_OPEN_RESERVE",Part.makePolygon(p),"ILLUSTRATIVE_FREE_SPAN_IN_OCCUPIED_REGION_NOT_RIGID_PART")
field=D.D19_DATA_STORAGE_LAYER;field.Shape=box(32,-40,41,91,16,76);field.OccupancyNote="Whole500=26+76 Pi approach+216 open reserve+156 BUS approach+26. R30/OD6.8. Transport values are regional planned upper allocations; exact final endpoint/slack qualification pending."
field.ViewObject.Visibility=False
jr=[]
for role,x,transport,reserve in [("yaw",-40,120,126),("pitch",44,180,66),("tail",128,145,101)]:
    o=add("D19_JR300_"+role.upper()+"_RESERVE",box(x-26,-84,128,52,52,10),"ONE_SEPARATE_300_UNIT_OCCUPIED_ALLOCATION_PENDING")
    o.ViewObject.Transparency=75;o.ViewObject.Visibility=False
    jr.append(dict(unit="JR300_"+role,raw=300,plug=12,transport_plan=transport,laid_reserve=reserve,fan=25,insulated_land=9,proper_lap=8,
                   profile=[3.5,1.8],inner_R=22,region=[x-26,-84,128,52,52,10],qualified=False))
# Update full populated reserves after the complete module moves.
b=D.AUX_Pololu4092.Shape.BoundBox;D.D19_AUX_POPULATED_9P5_RESERVE.Shape=box(b.XMin,b.YMin,b.ZMin,b.XLength,b.YLength,9.5)
# Native head/neck load-path contacts are facts, not a print-release assertion.
n=D.D19_FIXED_INNER_NECK.Shape;portal=D.D19_OPEN_GIMBAL_LOAD_PORTAL.Shape
feet=[]
for side in (-1,1):feet.append(box(-141,side*35-4,42.52,10,8,22))
bridge=feet[0].fuse(feet[1])
j1=portal.common(bridge).Volume;j2=n.common(bridge).Volume
if j1>.1 and j2>.1:
    whole=portal.fuse(bridge).fuse(n).removeSplitter()
    if whole.isValid() and len(whole.Solids)==1:
        D.D19_OPEN_GIMBAL_LOAD_PORTAL.Shape=whole;D.D19_FIXED_INNER_NECK.ViewObject.Visibility=False
wr("whole-unit-space-plan.json",dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),moves=moves,
    DATA500=dict(raw=500,boots=[26,26],pi_approach_plan=76,reserve=216,bus_approach_plan=156,OD=6.8,inner_R=30,
                 region=[32,-40,41,91,16,76],qualification="Open reserve has both approaches assigned. Curvature/physical port/coallocation of those approaches still requires the named port-layer gate.",accepted=False),
    JR300=jr,FFC200=dict(raw=200,proper_ends_once=10,free=190,head_and_Pi_identity_unchanged=True,changed_shell_neighbors_pending=True),
    MG_factory_units=[dict(role=q,raw=250,case_exit="PROJECT actual sample",qualified=False) for q in ("yaw","pitch","tail")],
    ToF=dict(cores=4,jacket_OD=2.1,moving_inner_R=31.5,JP3=[2,6,3,4],changed_rear_board_ends="fixed fan and blank lengths must be rebound to the moved whole PCA-E1"),
    E2=dict(independent_contact_wire_units=4,available_each=220,both_ends_retained=True,changed_body_station_plan="pending"),
    MTA0100335=dict(qty=4,whole_profile=None,outer_OD=None,condition="One complete delivered unit; adjustable open tray, no140mm orFHAC84.5 length credit."),
    load_path=dict(inner_neck_to_bridge_mm3=j2,bridge_to_source_portal_mm3=j1,qualified=(j1>.1 and j2>.1)),
    physical_PASS=False,actual_fit=None,actual_cut=None,installed_slack=None,whole_accepted=False))
records=[]
for o in D.Objects:
    if hasattr(o,"Shape") and not o.Shape.isNull():
        b=o.Shape.BoundBox;records.append(dict(name=o.Name,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume=o.Shape.Volume,kind=getattr(o,"EvidenceKind","source")))
wr("corrected-low-actors.json",records)
known=[o for o in D.Objects if o.Name.startswith(("D19_LOW_","D19_ROUNDED_","D19_BROAD_","D19_FIXED_INNER_","D19_SKULL_EARS","D19_OPEN_GIMBAL"))]
v=sum(o.Shape.Volume for o in known if o.ViewObject.Visibility)
wr("mass-budget.json",dict(base_and_bought_g=[1853.4,2593.4],density_g_cm3=1.27,known_new_selected_prints_full_material_g=v*.00127,
    known_print_names=[o.Name for o in known if o.ViewObject.Visibility],P_scope="Add retained leg prints, optical front, complete head/tail mechanism and necessary remaining mounts once. Chassis/metal already in the source allowance.",
    P_actual=None,whole_actual=None,physical_payload_PASS=False))
D.recompute();D.save()
skins=["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","D19_BROAD_SKULL_BACK","BR_COMMON_OPTICAL_MASK","D19_SKULL_EARS"]
if D.D19_FIXED_INNER_NECK.ViewObject.Visibility:skins.append("D19_FIXED_INNER_NECK")
views=[("front",(-1,0,.03),False),("side",(0,-1,.035),False),("three-quarter",(-1.4,-1,.55),False),("interior",(-1.1,-1,1.15),True)]
captures=[]
for f in ast.parse((P/"correct-whole-allocation.py").read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("cam","step"):exec(compile(ast.Module([f],type_ignores=[]),str(P), "exec"))
step(0)
