"""One bank-to-lower-layer W033 proposal; retained terminal, curved9mm grip.

Replaces only W033 bank kit. No selected route or supplier datum changes.
The old straight9 grip is explicitly retired, not silently retained.
"""
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
import feline_tangent_routes as ft
from receive_feline_W024_shared_body import solid
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_bank_selected_t18i import dimensions
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def build(first9=False):
    radius=12.4; start=np.array([-18.,-14.152,69.])
    tangent=np.array([0.,1.,0.]); bend=np.array([1.,0.,-1.])/math.sqrt(2)
    at=lambda length:start+radius*math.sin(length/radius)*tangent+radius*(1-math.cos(length/radius))*bend
    segment=lambda a,b:ft.arc(at(a),math.cos(a/radius)*tangent+math.sin(a/radius)*bend,at(b))
    arc=segment(0,radius*math.pi/2);arc['radius']=radius
    arc['length']=radius*arc['angle']
    wireparts=[ft.line([-18,-17.152,69],start),arc,ft.line(arc['end'],np.array(arc['end'])+9*bend)]
    grip=[wireparts[0],segment(0,6)] if first9 else [segment(0,9)]
    centre_length=1.5 if first9 else 4.5
    band=[segment(centre_length-1.25,centre_length+1.25)]
    cap=solid(grip,3).cut(solid(grip,1.15))
    strap=solid(band,4.2).cut(solid(band,3))
    # Head uses selected maximum dimensions in its actual strap frame.
    D,H,E=dimensions(); radial=np.array([1.,0.,1.])/math.sqrt(2)
    axis=math.cos(centre_length/radius)*tangent+math.sin(centre_length/radius)*bend
    transverse=np.cross(axis,radial);centre=at(centre_length)+(4.2+D/2)*radial
    matrix=A.Matrix()
    for i in range(3):
        for j,col in enumerate((radial,transverse,axis)):setattr(matrix,f'A{i+1}{j+1}',col[i])
    head=Part.makeBox(D,H,E,A.Vector(-D/2,-H/2,-E/2))
    head.Placement=A.Placement(A.Vector(*centre),A.Rotation(matrix))
    parts={'wire':solid(wireparts,1),'curved_saddle':cap,'band_budget':strap,'head_budget':head}
    assert all(s.isValid() and len(s.Solids)==1 for s in parts.values())
    return parts,wireparts,dict(grip_total_length_mm=9,grip_arc_length_mm=6 if first9 else 9,first9=first9,entry_project_mm=3,R_mm=radius,
        head_max_dimensions_mm=[D,H,E],old_straight9_retired=True,
        split_saddle_retention_root_and_installation_OPEN=True)


def run(scene,metadata,pins,first9=False):
    tick=time.monotonic();dest=OUT/('n01-W033-first9-curved-grip-kit-static.json' if first9 else 'n01-W033-curved-grip-common-kit-static.json')
    assert not dest.exists(),'Receive saved result'
    parts,recipe,contract=build(first9);queries=SolidQueries();checks={};errors={}
    retired=[n for n in scene if n.startswith('Station:Bank:W033/body/end:')]
    assert len(retired)==4
    for name,s in parts.items():
        for other,target in scene.items():
            if other in retired:continue
            reserve=metadata.get(other,{}).get('nominal_profile_radius_mm',0) if not target.Solids else 0
            if bbox_lower_bound(s.BoundBox,target.BoundBox)>=1.25+reserve+1e-6:continue
            try:
                t=solid_profile_target(target,metadata.get(other,{}));gap=queries.distance(s,t)
                own=name in ('wire','curved_saddle') and other=='Ref_Material_F_R2_CP2_OUT_0_0'
                wire=other.startswith('CurrentMiddle:') or ':wire:' in other
                minimum=0 if own else .2 if name=='wire' and wire else 1.25
                row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
                if own:row['common_mm3']=s.common(t).Volume;row['ok'] &= row['common_mm3']<1e-6
                checks[name+' / '+other]=row
            except Exception as exc:errors[name+' / '+other]=str(exc)
    result=dict(status='CONSTRUCTIVE_KIT_STATIC_SCREEN_NOT_RECEIVED',recipe=recipe,contract=contract,
        retired=retired,checks=checks,errors=errors,source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print('W033 KIT',[(k,v) for k,v in checks.items() if not v['ok']],errors,result['worker_seconds'],flush=True)
    return result,parts
