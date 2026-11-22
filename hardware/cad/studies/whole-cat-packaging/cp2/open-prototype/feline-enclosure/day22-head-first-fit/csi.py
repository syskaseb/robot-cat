"""Full Standard–Standard CSI trace, split at the fixed slack keeper."""
from math import acos, cos, sin, radians
from pathlib import Path
import json
import numpy as np
import FreeCAD as App
import Part
from head import (HERE,KIT,POSES,MASK,BACK,CARRY,saved,hit,bound,inject,moved,articulated,V,write_json)
import cables as c

CAM_LIP=V(-208.895,40,151.092)
PI_LIP=np.array([-62.5,-16.5,105.1])
KEEP=np.array([-128.,-16.5,160.])
PHYSICAL_NOMINAL=300.
END_DEBITS=10.
FREE=PHYSICAL_NOMINAL-END_DEBITS
ALLOWANCES={(0,0):142.5,(-20,-10):145.,(-20,10):139.5,(20,-10):143.,(20,10):138.5}
MOVING=ALLOWANCES[(0,0)]
FIXED=FREE-MOVING
BEND_LIMIT=12.5
WIDTH=16.8
DEPTH=1.8
EU="https://pip-assets.raspberrypi.com/categories/907-approvals/documents/RP-005152-CF-1-Std_-_Std_EU_DoC_Cam_Display.pdf"
DOCS="https://www.raspberrypi.com/documentation/accessories/camera.html"

def bisect(f,l,h):
    a,b=f(l),f(h)
    assert a<=0 and b>=0,(a,b,l,h)
    for _ in range(38):
        m=(l+h)*.5
        if f(m)>0:h=m
        else:l=m
    return (l+h)*.5

def stationary(target):
    r=14.5
    initial=3.0
    def spans(a):
        across=(PI_LIP[0]-KEEP[0]-2*r*(1-cos(a)))/sin(a)
        final=KEEP[2]-initial-PI_LIP[2]-2*r*sin(a)-across*cos(a)
        return across,final,initial+2*r*a+across+final
    theta=bisect(lambda a:spans(a)[2]-target,radians(134),radians(155))
    across,final,length=spans(theta)
    assert min(across,final)>0 and r-DEPTH/2>BEND_LIMIT
    down=np.array([0.,0.,-1.])
    w=np.array([0.,1.,0.])
    position=KEEP.copy()
    points=[(position,down,w)]
    position=position+down*initial
    points.append((position,down,w))
    base=position
    for a in np.linspace(0.,theta,23)[1:]:
        position=base+np.array([r*(1-cos(a)),0.,-r*sin(a)])
        tangent=np.array([sin(a),0.,-cos(a)])
        points.append((position,tangent,w))
    position=position+across*tangent
    points.append((position,tangent,w))
    base=position
    for a in np.linspace(theta,0.,23)[1:]:
        position=base+np.array([r*(cos(a)-cos(theta)),0.,r*(sin(a)-sin(theta))])
        points.append((position,np.array([sin(a),0.,-cos(a)]),w))
    position=position+down*final
    assert np.linalg.norm(position-PI_LIP)<.000001
    points.append((PI_LIP,down,w))
    return points,{"inside_radius_mm":r-DEPTH/2,"rounding_arc_deg":theta*180/np.pi,
        "length_mm":length,"terminal_straight_mm":final,"near_keeper_straight_mm":initial}

def moving(y,p,r):
    c.FIXED=KEEP
    c.R=r
    return c.make_fan(CAM_LIP,y,p)

def choose(y,p,length):
    # All five lay positions spend the same moving allowance by opening
    # or closing the arch. Arc choice follows a measured path length,
    # with no change of topology or fixed stop.
    best=None
    brackets=[]
    for r in (20.1,24.,28.,32.,36.,39.,41.,42.,42.5,43.,43.5,44.):
        try:
            sam,details=moving(y,p,r)
        except (ValueError,AssertionError,np.linalg.LinAlgError):
            continue
        delta=details["free_path_mm"]-length
        if best is None or abs(delta)<best[0]:
            best=(abs(delta),sam,details)
        if delta>=0 and brackets:
            lo,hi=brackets[-1],r
            for _ in range(18):
                mid=(lo+hi)*.5
                try:
                    sam,details=moving(y,p,mid)
                except (ValueError,AssertionError,np.linalg.LinAlgError):
                    hi=mid
                    continue
                error=details["free_path_mm"]-length
                if abs(error)<best[0]:best=(abs(error),sam,details)
                if error<0:lo=mid
                else:hi=mid
            break
        if delta<0:brackets.append(r)
    assert best and best[0]<2.0,(y,p,length,None if best is None else best[0])
    return best[1:]

def installed(y,p):
    samples,detail=choose(y,p,ALLOWANCES[y,p])
    st,metrics=stationary(FREE-detail["free_path_mm"])
    return samples,detail,st,metrics

def compound_at(samples,step=3):
    j=[0,*range(step,len(samples)-1,step),len(samples)-1]
    return Part.makeCompound(c.occupied([samples[i] for i in j]))

def occupied_exact_compound(samples):
    return Part.makeCompound(c.occupied(samples))

def reference_shape(samples):
    return Part.makePolygon([V(*q[0]) for q in samples])

MOVERS={MASK,BACK,CARRY,"D21_Camera_OEM","PITCH_HORN_ROOF_JOURNAL",
        "PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw"}
YAW={"E19_UpperYawCover","D19D_YawSaddle","MG92B_Head_pitch",
     "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw"}
FIXTURES={"H19_FrontFrame","F19_ForeCap","Pi4B_actual_PCB","Pi_components_and_cooling",
          "CF17_PI_PRIMARY_CSI","PBAY_POST_F0","D20_POST_Aft_Slotted","YAW_FIXED_OUTER_RACE_CAP",
          "YAW_FIXED_CAP__1_full_screw","MG92B_Head_yaw"}
ACTORS=MOVERS|YAW|FIXTURES

def poses(src,y,p):
    for n,s in src.items():
        yield n,moved(s,articulated(y,p)) if n in MOVERS else (
                moved(s,articulated(y,0)) if n in YAW else s)

def test_cable():
    src=saved(ACTORS)
    report=[]
    for y,p in POSES:
        sam,fit,fixed,st=installed(y,p)
        length=fit["free_path_mm"]
        solid=compound_at(fixed)
        fixed_hits={n:hit(solid,s) for n,s in src.items() if n not in
                    (MOVERS|YAW|{"CF17_PI_PRIMARY_CSI","Pi_components_and_cooling"})}
        reserve=solid.common(src["Pi_components_and_cooling"])
        print("fixed slot",y,p,bound(solid),st,"rigid",fixed_hits,flush=True)
        small,minimum=moving(y,p,20.1)
        print("arch",y,p,fit,flush=True)
        now=compound_at(sam)
        readings={}
        park={}
        for n,s in poses(src,y,p):
            if n in ("D21_Camera_OEM","CF17_PI_PRIMARY_CSI","Pi_components_and_cooling"):
                continue
            v=hit(now,s)
            if v>.005:
                readings[n]=v
            if n in MOVERS|YAW:
                v=hit(solid,s)
                if v>.005:park[n]=v
        print("result",y,p,readings,park,flush=True)
        report.append({"yaw":y,"pitch":p,"long_occupied_bounds_mm":bound(now),
          "upper_graph_short_path_mm":minimum["free_path_mm"],
          "moving_allowance_minus_short_path_mm":round(length-minimum["free_path_mm"],4),
          "length_of_laid_sample_mm":fit["free_path_mm"],
          "min_inside_bend_mm":fit["min_inner_radius_mm"],"roll_deg":fit["wire_roll_deg"],
          "moving_occupied_hits_mm3":readings,"parked_occupied_hits_at_pose_mm3":park,
          "parked_stationary_hits_mm3":fixed_hits,"parked":st,
          "pi_cooling_air_reservation_contact_only_mm3":reserve.Volume,
          "pi_exit_clear_access_strip_mm":bound(reserve) if not reserve.isNull() else None})
        if y==p==0:
            inject({"D22_FFC_Moving":now,"D22_FFC_Parked":solid},
                   {"D22_FFC_Moving_Trace":reference_shape(sam),"D22_FFC_Parked_Trace":reference_shape(fixed)})
            neutral_st,neutral_band,neutral_moving=st,bound(solid),length
            reference={"moving_stations":[q[0].tolist() for q in sam],
                       "fixed_stations":[q[0].tolist() for q in fixed]}
    report={"standard":"Raspberry Pi Camera and Display Cable Standard–Standard 300mm; 15↔15, 1 mm pitch",
             "manufacturer_declaration":EU,"connector_families_source":DOCS,
             "camera_lip_xyz":[*CAM_LIP],"pi4_lip_xyz":PI_LIP.tolist(),"fixed_keeper_xyz":KEEP.tolist(),
             "nominal_total_mm":PHYSICAL_NOMINAL,"total_end_insertions_allowance_mm":END_DEBITS,
             "free_total_mm":FREE,"neutral_moving_free_mm":neutral_moving,"neutral_stationary_free_mm":FREE-neutral_moving,
             "fixed_slip_guide_max_axial_redistribution_mm":max(q["length_of_laid_sample_mm"] for q in report)-min(q["length_of_laid_sample_mm"] for q in report),
             "stationary_neutral":neutral_st,"width_depth_screen_mm":[WIDTH,DEPTH],
             "stationary_neutral_occupied_bounds_mm":neutral_band,"project_inside_bend_min_mm":BEND_LIMIT,
             "supplier_dynamic_bend_limit":None,"five_poses":report,"neutral_trace":reference,
             "physical_usable_length":None,"actual_slack":None,"supplier_contact_clock_and_available_length_trial":True}
    write_json(HERE/"csi-layout.json",report)

if __name__=="__main__":
    test_cable()
