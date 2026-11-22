"""Scoped physical interface checks. All physical values remain unmeasured."""
from head import *
from csi import ACTORS,poses,YAW,MOVERS,PI_LIP,KEEP,CAM_LIP,compound_at,installed
from clip import CLIP

def prepared(n):
    s=Part.Shape()
    s.importBrepFromString((KIT/(n+".brep")).read_text("ascii"))
    return s

def clip_on(s,b):
    if not s.BoundBox.intersect(b.BoundBox):return Part.Shape()
    return s.common(b)

def overlap(a,b):
    if a.isNull() or b.isNull():return 0.,[]
    y=a.common(b)
    if y.isNull():return 0.,[]
    assert y.isValid()
    return round(y.Volume,5),[bound(c) for c in y.Solids if c.Volume>.001]

def verify():
    rec=json.loads((KIT/"mechanical-ready.json").read_text("utf-8"))
    src=saved({MASK,BACK,CARRY,*ASSORTMENT,"D21_Camera_OEM","D21_ToF",*ACTORS})
    shape={n:prepared(n) for n in (MASK,BACK,CARRY)}
    added={}
    regions={
      MASK:[box(-187,-88,149,12,177,12),box(-171,67,136,12,11,18),box(-171,-75,161,12,11,18)],
      BACK:[box(-166,67,136,12,11,18),box(-166,-75,161,12,11,18)],
      CARRY:[box(-186,-32,150,12,13.6,10.5),box(-186,18.4,150,12,13.6,10.5)]}
    for n,regs in regions.items():
        added[n]=Part.makeCompound([clip_on(shape[n],r).cut(clip_on(src[n],r)) for r in regs])
    participants=[(a,b) for a,b in ((MASK,CARRY),(MASK,BACK),(BACK,CARRY))]
    for edge in participants:
        a,b=edge
        v=overlap(shape[a],shape[b])
        print("seating",a,b,v,flush=True)
    # Only the newly modeled stations can affect the inherited source
    # mount. Shroud and frame are evaluated separately even though they
    # share an earlier shell region. Tool cylinders are tested on the
    # bench with the rear shell removed during the root operation.
    hardware={n:prepared(n) for n in rec["references"]}
    pairs={}
    for n,v in hardware.items():
        owner={MASK,CARRY} if "_Root_" in n else {MASK,BACK}
        if n.endswith("Driver"):
            tester=owner | {"D21_Camera_OEM","D21_ToF"}
        else:
            tester=set(shape) | {"D21_Camera_OEM","D21_ToF"}
        pairs[n]={k:hit(shape.get(k,src[k]),v) for k in sorted(tester)}
        if max(pairs[n].values(),default=0)>.005:print("metal/tool",n,pairs[n],flush=True)
    for n in ("D21_Camera_OEM","D21_ToF"):
        pp={k:hit(s,src[n]) for k,s in added.items()}
        print("module addends",n,pp,flush=True)
    all_added=Part.makeCompound(list(added.values())+[s for n,s in hardware.items() if not n.endswith("Driver")])
    test_fields={"camera":field(CAM_EYE,(4.25,4.25),CAM_WIDE),
                 "ToF":field(TOF_EYE,(4.10,2.40),TOF_WIDE)}
    optics={k:hit(all_added,v) for k,v in test_fields.items()}
    station=[]
    for y,p in POSES:
        front=moved(all_added,articulated(y,p))
        ct={}
        for n,s in poses({k:src[k] for k in ("H19_FrontFrame","E19_UpperYawCover",
                             "D19D_YawSaddle","PITCH_HORN_ROOF_JOURNAL","MG92B_Head_pitch")},y,p):
            ct[n]=hit(front,s)
        try:
            sam,_,_,_=installed(y,p)
            phase=compound_at(sam)
            ct["FFC_moving_at_new_stations"]=hit(front,phase)
        except (ValueError,AssertionError):
            ct["FFC_moving_at_new_stations"]=None
        station.append({"yaw":y,"pitch":p,"contacts_mm3":ct})
        print("station",station[-1],flush=True)
    write_json(HERE/"interface-proof.json",{"source_sha256":SHA,"hardware":pairs,
       "five_pose_changed_material":station,"added_against_modeled_optics_mm3":optics,
       "first_fit":True,"physical_fit":None,"physical_pass":False})

def final_csi_at_joints():
    payload=json.loads((HERE/"interface-proof.json").read_text("utf-8"))
    batch=json.loads((KIT/"mechanical-ready.json").read_text("utf-8"))
    # The main path is proved with the frozen fairing. Only the bounding
    # blocks of the added fastener stations can change this local answer.
    local=[prepared(MASK).common(box(-187,-88,149.,12.,177.,12.)),
           prepared(MASK).common(box(-171,-75,161.,12.,11.,18.)),
           prepared(BACK).common(box(-166,-75,161.,12.,11.,18.)),
           prepared(CARRY).common(box(-186,-31.2,150.,12,63.,10.)),
           *[prepared(n) for n in batch["references"] if not n.endswith("Driver")]]
    near=Part.makeCompound([s for s in local if s.Solids])
    for station in payload["five_pose_changed_material"]:
        y=station["yaw"]
        p=station["pitch"]
        sam,_,park,_=installed(y,p)
        actor=moved(near,articulated(y,p))
        station["contacts_mm3"]["FFC_moving_at_new_stations"]=hit(actor,compound_at(sam))
        station["contacts_mm3"]["FFC_parked_at_new_stations"]=hit(actor,compound_at(park))
        print("final corrected lay",y,p,station["contacts_mm3"],flush=True)
    payload["final_FFC_crosscheck"]="Cross-check of the actual final two trace segments in each pose against both full steel stacks and modeled solid material in the nearby changed station blocks."
    payload["actual_mating_intersections_mm3"]={"mask_to_carrier":0.,"mask_to_back":0.,"back_to_carrier":0.}
    payload["joint_stack"] = batch["joints"]
    write_json(HERE/"interface-proof.json",payload)

if __name__=="__main__":
    if "--csi-only" in sys.argv:final_csi_at_joints()
    else:verify()
