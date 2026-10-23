"""Whole F_PI service hypothesis: clock the case, keep both wire mouths.

Not another translation search. Test the changed casing in the assembled robot
and a diagonal lid/finger reservation after explicitly removing the isolator key.
Key removal and delivered hinge travel remain independent gates, never waived.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def probe(scene, metadata, bus_original, inverse, source_pins):
    tick=time.monotonic(); name='Ref_Material_F_PI_new_0_0'
    dest=OUT/'n01-FPI-diagonal-clock-service-proposal.json'
    assert not dest.exists(), 'Receive the saved proposal, never repeat'
    case=scene[name].copy(); centre=A.Vector(-52.95,0,41.1)
    case.rotate(centre,A.Vector(1,0,0),-45)
    # Reuse the same nominal central24 x23.75 x20.5 access budget.
    # Negative Y side rotates upwards, leaving the positive bank heads alone.
    access=box([-64.95,-35,30.85],[-40.95,-11.25,51.35])
    access.rotate(centre,A.Vector(1,0,0),-45)
    assert case.isValid() and access.isValid()
    query=SolidQueries(); checks={}; errors={}
    for label,actor in [('clocked_case',case),('diagonal_access',access)]:
        minimum=1.25 if label=='clocked_case' else .5
        for other,target in scene.items():
            if other==name: continue
            # Service starts assembled; the one required removal is explicit.
            if label=='diagonal_access' and other=='Ref_Material_S0_key_CP2_0_0': continue
            if label=='clocked_case' and other in ('W043','W077'): continue
            if bbox_lower_bound(actor.BoundBox,target.BoundBox)>=minimum+1e-6: continue
            a=actor;t=target
            if other=='Ref_Material_BUSsupplier25_0_0':
                a=actor.copy();a.Placement=inverse*a.Placement;t=bus_original
            try:
                if t.Solids:
                    gap=query.distance(a,t);row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
                else:
                    radius=metadata.get(other,{}).get('nominal_profile_radius_mm') or metadata.get(other,{}).get('radius_mm')
                    assert radius is not None, 'Profile without radius'
                    row=profile_gap(a,t,radius,minimum)
                checks[label+'|'+other]=row
            except Exception as exc: errors[label+'|'+other]=str(exc)
    result=dict(status='DIAGONAL_CLOCK_HOLD' if errors or any(not r['ok'] for r in checks.values()) else 'DIAGONAL_CLOCK_NECESSARY_SCREEN_POSITIVE_NOT_RECEIVED',
        checks=checks,errors=errors,failures=[k for k,r in checks.items() if not r['ok']],
        case_clock_degrees=-45,case_centre_mm=list(centre),factory_mouths_and_wire_paths_not_translated=True,
        intentional_case_wire_mates_not_requalified=['W043','W077'],
        proposed_service_sequence=['Isolate and unplug source; no energized work','Remove S0 key using separately verified extraction','Open diagonal F_PI cap with case and wires retained'],
        key_extraction_NOT_verified=True,actual_hinge_and_finger_budget_provisional_delivery_gate=True,
        all_case_retention_roots_tools_motion_and_mates_OPEN=True,
        source_sha256={**source_pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        N01_complete=False,physical_pass=False,selected=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],result['failures'],errors,result['worker_seconds'],flush=True)
    return result
