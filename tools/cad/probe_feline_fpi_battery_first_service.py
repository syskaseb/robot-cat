"""Different assembly sequence: battery out before downward F_PI cap access.

No shifted wires or smaller access volume. Necessary spatial test only;
battery extraction, cap clock/hinge fit and case retention remain explicit.
"""
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def probe(scene,metadata,pins):
    tick=time.monotonic();dest=OUT/'n01-FPI-battery-first-service-proposal.json'
    assert not dest.exists()
    # Same family24x23.75x20.5 central cap/finger budget, now below the case.
    # The nominal casing remains at its current pose, mouths on its X axis.
    access=box([-64.95,-10.25,6.975],[-40.95,10.25,30.725])
    assert access.isValid() and len(access.Solids)==1
    query=SolidQueries();checks={};errors={}
    excluded={'Ref_Material_F_PI_new_0_0':'own lid interface; delivered clock/hinge remains a fit gate',
              'BatterySelectedNominal':'battery must be unplugged and extracted BEFORE this step; extraction gate remains open'}
    for name,target in scene.items():
        if name in excluded:continue
        if bbox_lower_bound(access.BoundBox,target.BoundBox)>=.5+1e-6:continue
        try:
            if target.Solids:
                gap=query.distance(access,target);r=dict(ok=gap>=.5-1e-6,gap_mm=gap,minimum_mm=.5)
            else:
                radius=metadata.get(name,{}).get('nominal_profile_radius_mm') or metadata.get(name,{}).get('radius_mm')
                assert radius is not None,'missing profile radius'
                r=profile_gap(access,target,radius,.5)
            checks[name]=r
        except Exception as e:errors[name]=str(e)
    result=dict(status='BATTERY_FIRST_CAP_SPACE_HOLD' if errors or any(not r['ok'] for r in checks.values()) else 'BATTERY_FIRST_CAP_SPACE_POSITIVE_EXTRACTION_AND_RETENTION_OPEN',
        checks=checks,errors=errors,failures=[n for n,r in checks.items() if not r['ok']],
        service_budget_bounds_mm=[[-64.95,-10.25,6.975],[-40.95,10.25,30.725]],
        cap_direction=[0,0,-1],preserved_wire_paths_and_both_factory_mouths=True,
        excluded_parts_and_required_prior_operations=excluded,
        battery_extraction_NOT_received=True,case_clock_hinge_fit_NOT_supplier_guarantee=True,
        unaltered_straps_frame_roots_all_checked=True,case_retention_must_not_block_downward_access=True,
        N01_complete=False,physical_pass=False,selected=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['failures'],errors,result['worker_seconds'],flush=True)
    return result
