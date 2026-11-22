"""Fixed slip keeper. The fitted shoe uses the existing POST rail lip."""
from head import *
from csi import stationary,FIXED,compound_at,poses,installed,KEEP

FOOT="D20_POST_Aft_Slotted"
CLIP="D22_CSI_ParkingClip"

def build_clip():
    src=saved({FOOT,"PBAY_POST_F0","H19_FrontFrame","E19_UpperYawCover","D19D_YawSaddle",
               "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw","F19_ForeCap",
               "D21_Face","D19D_PitchBack","D21_Carrier"})
    down=box(-117.9,-23.2,134.4,9.7,7.2,2.40)
    top=box(-117.9,-23.2,140.10,9.7,7.2,1.22)
    bridge=box(-117.9,-17.75,134.4,9.7,2.8,6.92)
    foot=push(down,[top,bridge],"POST rail shoe")
    # Short riser and lateral arm follow the side opposite the WAGO
    # access. The body, WAGO lever and existing mounting steel stay intact.
    pieces=[
       box(-117.1,-28.2,139.95,5.5,6.05,1.35),
       box(-117.1,-28.2,140.1,4.15,2.48,20.8),
       box(-128.7,-27.9,157.0,13.1,2.8,4.2),
       box(-126.18,-27.9,157.5,1.9,23.3,4.5),
       box(-130.2,-27.9,157.6,5.5,2.5,4.6),
       box(-130.2,-7.60,157.6,5.5,2.5,4.6)]
    keeper=push(foot,pieces,"rail shoe and free-slide keeper")
    for y in (-28.15,-7.85):
        tool=box(-129.7,y,158.4,2.0,3.20,2.2)
        keeper=solid(keeper.cut(tool),"through fore-aft retaining strap eye")
    # Break all build edges at the mouth. Keep the part separated across
    # the slip channel; the two soft strap anchors do not clamp the tape.
    nominal_mount=src[FOOT]
    bonded=hit(moved(top,App.Placement(V(0,0,-.50),App.Rotation())),nominal_mount)
    assert bonded>10,bonded
    inject({CLIP:keeper},{})
    trials={}
    for y,p in POSES:
        occ={}
        moving,_,fixed,_=installed(y,p)
        station=compound_at(fixed)
        lay=compound_at(moving)
        for n,s in poses(src,y,p):
            occ[n]=hit(keeper,s)
        occ["fixed_ribbon_occupied"]=hit(keeper,station)
        occ["moving_ribbon_occupied"]=hit(keeper,lay)
        if occ["fixed_ribbon_occupied"]>.01:
            print("fixed clip point",bound(keeper.common(station)),flush=True)
        print("keeper",y,p,occ,flush=True)
        trials[f"{y}/{p}"]=occ
    inject({CLIP:keeper},{})
    write_json(KIT/"keeper-ready.json",{"name":CLIP,"contact_slide_probe_mm3":bonded,
        "rail_thickness_mm":2.9,"slot_height_mm":3.3,"seat_kind":"keyed shoe on top/bottom of unchanged POST rail",
        "slide_axis":"-Y from inboard","seat_area_proxy_mm2":bonded/.30,
        "bounds_mm":bound(keeper),"volume_mm3":keeper.Volume,"five_pose_checks_mm3":trials,
        "required_operations":["Remove print burrs and break both lip edges by hand.","Keep at least 7 mm FFC tip-to-guide sliding travel. Loosely close guide with soft textile tie.","Bond only inside keyed shoe with adhesive compatible with actual rail and clip material. Keep POST tie slots and release lever clear."]})
    return keeper

if __name__=="__main__":
    build_clip()
