"""Check the two repaired walls, the physical optics and the changed moving interface."""
from pathlib import Path
from tempfile import gettempdir
import json
import math
import sys

import FreeCAD as A
import Part

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from layout import (CAM_EYE,CAM_WIDE,TOF_EYE,TOF_WIDE,V,Y,Z,REFERENCE,CAMERA_URL,SOURCE,
                    articulated,bounds,box,field,load_saved,moved,sha,solid_hit,write_json)
from cables import make_fan

KIT=Path(gettempdir())/"robot-cat21-camera-oem/native-kit"
items=json.loads((KIT/"objects.json").read_bytes())
def load(name):
    s=Part.Shape()
    s.importBrepFromString((KIT/(name+".brep")).read_text("ascii"))
    return s
def ray_length(s,y,z):
    ray=Part.makeLine(V(-273,y,z),V(-210,y,z))
    return round(s.common(ray).Length,4)

shell=load("D21_Face")
regions={"forehead":range(164,192,4),"above_nose":range(124,137,3)}
wall={k:[{"yz_mm":[y,z],"axial_material_mm":ray_length(shell,y,z)}
         for z in zz for y in (-12,-6,0,6,12)] for k,zz in regions.items()}
print("walls", {k:(min(r["axial_material_mm"] for r in rr),max(r["axial_material_mm"] for r in rr))
                for k,rr in wall.items()},flush=True)

named=["D21_Face","D21_Nose","D21_Carrier","D21_Insert_Cam","D21_Insert_ToF","D21_Rim_Cam",
       "D21_Rim_ToF","D21_Ear_L","D21_Ear_R","D21_Ear_Inset_L","D21_Ear_Inset_R"]
changed={k:load(k) for k in named}
optics={"camera":field(CAM_EYE,(4.25,4.25),CAM_WIDE),
        "ToF":field(TOF_EYE,(4.10,2.40),TOF_WIDE)}
fields={key:{n:solid_hit(s,o) for n,s in changed.items()} for key,o in optics.items()}
print("optics",fields,flush=True)
physical={"cam":load("D21_Camera_OEM"),"ToF":load("D21_ToF")}
contacts={}
for key,part in physical.items():
    major=[q for q in part.Solids if q.Volume>5.]
    for n in ("D21_Face","D21_Carrier","D21_Insert_Cam","D21_Insert_ToF"):
        hits=[v for q in major if q.BoundBox.intersect(changed[n].BoundBox)
              and (v:=solid_hit(q,changed[n]))>.001]
        contacts[key+"/"+n]=hits
print("module contacts",contacts,flush=True)

fixed=load_saved(["E19_FrontShroud","D19D_PitchBack","E19_UpperYawCover","H19_FrontFrame",
                  "PITCH_HORN_ROOF_JOURNAL","D19D_YawSaddle"])
# The altered shell's rear sector is the only area close enough to collide
# with the retained body and yaw hood in the specified sampled positions.
rear=Part.makeCompound([shell.common(box(-189,-106,66,30,212,191)),changed["D21_Ear_L"],changed["D21_Ear_R"]])
motions=[]
for y,p in [(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]:
    station=moved(rear,articulated(y,p))
    motion={n:solid_hit(station,fixed[n]) for n in ("E19_FrontShroud","H19_FrontFrame")}
    yaw_local=moved(rear,articulated(0,p))
    motion["E19_UpperYawCover"]=solid_hit(yaw_local,fixed["E19_UpperYawCover"])
    motions.append({"yaw":y,"pitch":p,"common_mm3":motion})
    print("motion",motions[-1],flush=True)

seat={n:solid_hit(changed[n],shell) for n in ("D21_Nose","D21_Rim_Cam","D21_Rim_ToF","D21_Insert_Cam","D21_Insert_ToF")}
seat["retained_pitch_rear_shell"]=solid_hit(shell,fixed["D19D_PitchBack"])
seat["carrier"]=solid_hit(shell,changed["D21_Carrier"])
seat["separate_ear_L_in_seat"]=solid_hit(shell,changed["D21_Ear_L"])
seat["separate_ear_R_in_seat"]=solid_hit(shell,changed["D21_Ear_R"])
seat["ear_shell_mirror_common_mm3"]=solid_hit(changed["D21_Ear_L"].mirror(V(),Y),changed["D21_Ear_R"])
for name in ("D21_Mask_M2_reference_L","D21_Mask_M2_reference_R"):
    fastener=load(name)
    seat[name]={"mask_common_mm3":solid_hit(fastener,shell),
                "carrier_common_mm3":solid_hit(fastener,changed["D21_Carrier"])}
print("seat",seat,flush=True)
ears=[load("D21_Ear_Inset_"+n) for n in ("L","R")]
reflection_common=solid_hit(ears[0].mirror(V(),Y),ears[1])

old=load_saved(["D19D_Face","D19D_Ear_L","D19D_Ear_R","D19D_Nose","D19D_OpticsCarrier",
    "D19D_Iris_L","D19D_Iris_R","D19D_Pupil_L","D19D_Pupil_R"])
a=sum(q.Volume for q in old.values())
b=sum(changed[n].Volume for n in named)

# Reuse confirmed neutral hit of the low FFC alternative with the original
# fixed frame. This scoping calculation uses only the named local obstacle.
from cables import occupied
candidate_lengths=json.loads((HERE/"cable-gate.json").read_bytes())
alternates={}
for mode,xyz,axis,w,indices in [
        ("alternative_180deg_lower_exit",(-208.895,40,132.908),-Z,Y,(41,42,43)),
        ("alternative_clock_90deg_inside",(-208.895,30.908,142),-Y,Z,(39,40,41,42,43))]:
    path,_=make_fan(V(*xyz),0,0,axis,w)
    c=occupied(path)
    actor="H19_FrontFrame" if "lower" in mode else "PITCH_HORN_ROOF_JOURNAL"
    chosen=indices if "lower" in mode else (37,38,39)
    vals=[(i,solid_hit(c[i],fixed[actor])) for i in chosen]
    alternates[mode]={"actor":actor,"neutral_section_intersections_mm3":[[i,v] for i,v in vals if v>.001]}
    print("alternative",mode,alternates[mode],flush=True)

result={"disposition":"Edit candidate only. Physical fitting, FFC200 and retention remain open.",
  "source_native_sha256":sha(SOURCE),"approved_look_sha256":sha(REFERENCE),"camera_oem_step":CAMERA_URL,
  "bridge_provenance":"The first inner loft reached through the outer forehead and above the nose. The corrected full interior uses the same corresponding sections shifted 2.65 mm aft and inset 2.65 mm before subtracting. Optical fields were preserved.",
  "bridge_section_probes":wall,"field_intersections_mm3":fields,
  "module_contacts_scope":"Exact OCC common of parts over 5 mm3 each. Smaller electronic SMD components and the complete screw/connector install sequence remain open.","module_contacts_mm3":contacts,"changed_motion_sample":motions,"seating_contacts_mm3":seat,
  "ear_inset_mirror_volume_mm3":[round(e.Volume,5) for e in ears],"ear_inset_mirror_common_mm3":reflection_common,
  "moving_print_model_volume_change_mm3":{"old":round(a,2),"new":round(b,2),"delta":round(b-a,2),
      "mass_torque_test":None},
  "physical_optics":"OEM Wide assembly geometry and actual Pololu board/package geometry. Modelled rectangular cones from published axis angles; physical entrance pupils, TX/RX clipping, reflections and crosstalk require comparison on hardware.",
  "nominal_ear_retention":"Both ear hulls match real seats cut in the mask and use mirrored geometry. Fastener or adhesive retention and clearance are open before print.",
  "nominal_mask_fastener":"Geometric M2 x 12 seat reference on two inherited holes. Driver access, axial engagement, nut/locking arrangement and coupon fit remain open.",
  "ToF_four_wire":candidate_lengths["ToF"],"alternate_FFC_contacts":alternates,
  "physical_fit":None,"physical_wire_slack":None,"physical_PASS":False,"stl_release":False}
write_json(HERE/"fit-proof.json",result)
