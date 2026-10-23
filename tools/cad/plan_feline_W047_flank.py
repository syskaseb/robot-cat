"""Replace both self-crossing graph loops by one flank descent and return."""
import json
import time
import feline_tangent_routes as ft
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT,sha
from pathlib import Path
from feline_atomic_save import save_json


def recipe():
    old=json.loads((OUT/'joint-corridor-space-20261021/current-curved-path-preflight.json').read_text())['paths']['W047/body']['parts']
    return old[:2]+[ft.line([96,14,66],[96,-6,66]),
        ft.arc([96,-6,66],[0,-1,0],[96,-22,50])]+ft.biarc(
        [96,-22,50],[0,0,-1],[32,-22,38],[0,0,1])+old[-2:]


def screen(scene,metadata,pins,parts=None,destination='n01-W047-flank-screen.json'):
    from receive_feline_W024_shared_body import solid
    from receive_feline_jpwm_whole_pose import solid_profile_target
    from feline_solid_distance import bbox_lower_bound
    from feline_fore_power_pair import SolidQueries
    assert not (OUT/destination).exists(), 'Receive saved result instead of repeating it'
    tick=time.monotonic();parts=recipe() if parts is None else parts;shape=solid(parts,1)
    assert ft.min_radius(parts)>=12.4
    q=SolidQueries();checks={};errors={}
    for name,target in scene.items():
        reserve=metadata.get(name,{}).get('nominal_profile_radius_mm',0) if not target.Solids else 0
        if bbox_lower_bound(shape.BoundBox,target.BoundBox)>=1.25+reserve+1e-6:continue
        try:
            other=solid_profile_target(target,metadata.get(name,{}))
            gap=q.distance(shape,other)
            checks[name]=dict(gap_mm=gap,contact=gap<1e-6)
        except Exception as exc:errors[name]=str(exc)
    result=dict(status='NECESSARY_STATIC_SCREEN_NOT_RECEIVED',parts=parts,
        length_mm=ft.length(parts),minimum_R_mm=ft.min_radius(parts),radius_mm=1,
        checks=checks,errors=errors,source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/destination,result)
    print('W047 FLANK',[(k,v) for k,v in checks.items() if v['contact']],errors,result['worker_seconds'],flush=True)
    return result,shape
