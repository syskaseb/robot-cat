"""Check a recut left/down groove within an unchanged saddle and tie envelope."""
import math
import numpy as np
import FreeCAD as A
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_solid_distance import bbox_lower_bound


def check(wire,cap,oldcap,whole,scene,metadata,mouth,terminal):
    owner='Station:Bank:'+wire+'/body/end:';checks={}
    assert cap.isValid() and len(cap.Solids)==1
    assert cap.cut(oldcap).Volume<1e-7 and cap.common(whole).Volume<1e-7
    assert cap.distToShape(whole)[0]>=.15-1e-6
    for name,target in scene.items():
        if name in (owner+'split_cap_exterior',owner+'wire:'+wire+'/body/end','CurrentWhole:'+wire):continue
        if name in (owner+'band_budget',owner+'head_budget'):
            oldgap=oldcap.distToShape(target)[0];gap=cap.distToShape(target)[0]
            oldcommon=oldcap.common(target).Volume;common=cap.common(target).Volume
            checks[name]=dict(gap_mm=gap,old_gap_mm=oldgap,common_mm3=common,old_common_mm3=oldcommon,
                retained_owned_tie_interface=True,ok=gap>=oldgap-1e-6 and common<=oldcommon+1e-7)
            wg=whole.distToShape(target)[0]
            checks['wire / '+name]=dict(gap_mm=wg,minimum_mm=.2,ok=wg>=.2-1e-6)
            continue
        if bbox_lower_bound(cap.BoundBox,target.BoundBox)>=1.25+(metadata.get(name,{}).get('nominal_profile_radius_mm') or 0)+1e-6:continue
        t=solid_profile_target(target,metadata.get(name,{}));gap=cap.distToShape(t)[0]
        minimum=0 if name==terminal else 1.25
        row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
        if name==terminal:row['common_mm3']=cap.common(t).Volume;row['ok'] &= row['common_mm3']<1e-7
        checks[name]=row
    b=np.array([-1.,0.,-1.])/math.sqrt(2);side=np.array([1.,0.,-1.])/math.sqrt(2);probes=[]
    for length in np.linspace(.25,8.75,35):
        centre=np.array(mouth)+[0,min(length,3),0]
        if length>3:
            angle=(length-3)/12.4;centre+=np.array([0,12.4*math.sin(angle),0])+12.4*(1-math.cos(angle))*b
        for sign in (-1,1):
            for radial in (1.2,1.8,2.4):probes.append(cap.isInside(A.Vector(*(centre+sign*radial*side)),1e-7,True))
    assert all(probes) and len(probes)==210
    assert all(r['ok'] for r in checks.values()),{k:v for k,v in checks.items() if not v['ok']}
    return dict(checks=checks,probe_count=len(probes),probes_inside=True,cap_valid_one_solid=True,
        old_envelope_subset=True,root_and_compression_not_qualified=True)
