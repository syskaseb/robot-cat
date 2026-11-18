"""Make the two fixed stations and full unit fields on a shared, open body bracket."""
from pathlib import Path
import json,math
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve() and not D.getObject("BR_BODY_ROOT")
r=json.loads((P/"reception-layout.json").read_bytes())
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def add(n,s,col,visible):
    o=D.getObject(n) or D.addObject("PartDesign::Feature",n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=col
    o.ViewObject.DisplayMode="Shaded" if visible else "Wireframe";o.ViewObject.LineWidth=2;o.ViewObject.Visibility=visible;return o
def lines(n,arr,color):
    add(n,Part.makeCompound([Part.makePolygon([V(*a) for a in pts]) for pts in arr]),color,False)
def combine(parts):return parts[0].multiFuse(parts[1:]).removeSplitter()
def bounds(s):
    b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
bronze=(.73,.49,.14);teal=(.22,.40,.42)
neutral=next(q for q in r["pitch"] if q["yaw"]==0)
pair={}
for n,q in [("HY",r["yaw"]),("HP",neutral)]:
    x,y,z=q["key_tip"];s=box(x-15,y-7,z-5,30,14,10);pair[n]=s
    add("BR_PAIR_"+n,s,bronze,False)
# Low C_HY is supported at the front end so the complete, short F_AUX
# factory assembly and its upper face remain available on the rear side.
x,y,z=r["yaw"]["key_tip"]
base=box(-117,-27,72.5,22,8,3)
hy=[base,box(-106,-25,72.5,11,27,3),box(-106,y-9.5,75,11,2.1,5.8),
    box(-106,y+7.4,75,11,2.1,5.8)]
# Upper C_HP and the splice tray share an outside spine. The moving
# factory cable and both keyed ends enter the shelf from the open top.
x,y,z=neutral["key_tip"]
upper=[box(-115,24,101,6,16,5),box(-115,36,104,6,5,50),
       box(-114,36,123.5,47,5,3),box(-96,29,123.5,30,18,3),
       box(-96,28.5,126,30,2,5),box(-96,45.5,126,30,2,5)]
centers=[q["lap_center"] for q in r["extension"]["fans"]];zj=centers[0][2];yj=min(q[1] for q in centers)
xj=min(q[0] for q in centers)-13
upper+= [box(-115,36,zj-6.5,xj+116,5,3.5),box(xj,yj-3.6,zj-6.5,28,19.2,3.5),
         box(xj,36,zj-6.5,4,yj-35,3.5)]
joints=[box(c[0]-13,c[1]-3,c[2]-3,26,6,6) for c in centers]
add("BR_LAPS",Part.makeCompound(joints),(.82,.66,.21),False)
# Strap passages run under the housings in the two side saddles. The
# four-wire fixed grip shares the tall body spine above the rigid stations.
B=r["shared_grips"]["body"];S=r["shared_grips"]["pitch"]
upper+= [box(-115,36,150,5,5,29),box(-125,36,175,15,10,2.55),
         box(-125,36,177,7,3,4),box(-125,45,177,7,2.5,4)]
upperbr=combine(upper).cut(box(-123.8,35,175.45,4.6,13,1.35)).cut(box(-85,27,124.1,4.6,22,1.35))
low=combine(hy).cut(box(-102.5,-26,73.1,4.6,28,1.35))
bodybr=Part.makeCompound([upperbr,low]);add("BR_RECEIVER_HARD_MATERIAL",bodybr,(.23,.48,.45),False)
floor=D.FIT_FLOOR_AND_BATTERY_MONITOR.Shape
root=combine([floor,upperbr,low])
facts=dict(prior_root_contact=[floor.common(q).Volume for q in (upperbr,low)],new_floor_solids=len(root.Solids),root_valid=root.isValid(),
           fixed_station_common={name:root.common(s).Volume for name,s in pair.items()},
           splice_tray_contacts=[root.common(s).Volume for s in joints])
assert root.isValid() and len(root.Solids)==1,facts
add("BR_BODY_ROOT",root,teal,True);D.FIT_FLOOR_AND_BATTERY_MONITOR.ViewObject.Visibility=False
# The pitch-side landing connects directly to the printed optical receiver
# close to its measured positive-side extremity (-152,30,114).
arm=combine([box(-157.5,26,113,5.5,6,4),box(-157.5,29.5,112,5.5,18,4),
             box(-157.5,43,102,5.5,4.5,12),box(-157.5,42.7,100,10,8.6,2.55),
             box(-155,42,102,6,2.2,4),box(-155,50,102,6,2.2,4)])
recv=D.D18C_TRUE_PITCH_OPTICAL_RECEIVER
arm=arm.cut(box(-153.3,41,100.5,4.6,12,1.35))
armjoint=arm.common(recv.Shape).Volume;built=recv.Shape.fuse(arm).removeSplitter()
facts.update(pitch_arm_joint=armjoint,pitch_receiver_solids=len(built.Solids),pitch_receiver_valid=built.isValid())
if armjoint>0 and built.isValid() and len(built.Solids)==1:
    add("BR_PITCH_RECEIVER_AND_GRIP",built,teal,True);recv.ViewObject.Visibility=False
else:add("BR_PITCH_GRIP_TRIAL",arm,teal,True)
lines("BR_YAW_STATIC",[r["yaw"]["centreline"]],(.78,.42,.2))
lines("BR_PITCH_FLEX",[neutral["centreline"]],(.91,.49,.13))
lines("BR_EXT_STATIC",[r["extension"]["centreline"]]+[q["centreline"] for q in r["extension"]["fans"]],(.64,.36,.16))
lines("BR_TOF_FIELD",[next(q for q in r["ToF_move"] if q["yaw"]==q["pitch"]==0)["centreline"]]+[q["centreline"] for q in r["ToF_head"]+r["ToF_fixed"]],(.22,.63,.29))
# Evaluate both diagonal choices on the primary footprints. Retain the
# unchanged DATA500 boot and its qualified 500 mm allocation for this trial.
rear=D.CF17_PI_PRIMARY_USB_A_rear.Shape.BoundBox;front=D.CF17_PI_PRIMARY_USB_A_front.Shape.BoundBox
boot=D.Pi_USB_DATA_Delock_mating.Shape
def socket(y,z,w,h):return box(-20,y-w/2,z-h/2,26,w,h)
lo=104.1;hi=front.ZMin+.75*front.ZLength
old=D.INSERT_AUDIO_USB_A_FULL_MATE_FIELD
usb=socket(front.Center.y,hi,14,13)
altdata=socket(front.Center.y,hi,26,24);altaudio=socket(rear.Center.y,lo,14,13)
facts["USB"]=dict(lower_data_upper_audio=boot.common(usb).Volume,upper_data_lower_audio=altdata.common(altaudio).Volume,
      current_audio_center=[-7,front.Center.y,hi],fixed_DATA_source=bounds(boot),alternate_data_solid=bounds(altdata),
      selected="existing rear lower DATA and front upper AUDIO; keep complete data path and both boots. Upper height from upper half of full 16 mm primary stack; fitted plug bodies still unknown.",
      one_fit_condition="Both delivered plugs must seat and latch at the selected diagonal pair with free jackets; full project field overlap is a hold.")
# Work on world-space geometry; the inherited object has a translation.
old.Placement=A.Placement();old.Shape=usb
old_audio=json.loads((P.parent/"day18-open-front-assembly"/"audio-port-binding.json").read_bytes())["USB_AUDIO_illustrative_free_region"]
for p in old_audio[:4]:p[2]=hi
btl=json.loads((P.parent/"day18-open-front-assembly"/"audio-connections.json").read_bytes())["BTL"]["free_region"]
D.OPEN_AUDIO_CONNECTIONS.Shape=Part.makeCompound([Part.makePolygon([V(*p) for p in pts]) for pts in (old_audio,btl)])
facts["USB"].update(actual_audio_field=bounds(old.Shape),rectilinear_audio_mm=sum(sum(abs(a-b) for a,b in zip(q,t)) for q,t in zip(old_audio,old_audio[1:])),free_audio=old_audio)
facts["physical_PASS"]=False
(P/"station-facts.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
D.Label="Body-owned duplex reception - whole-unit trial";D.recompute();G.runCommand("Std_Save")
