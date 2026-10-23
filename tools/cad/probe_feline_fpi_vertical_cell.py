"""Necessary case/access gate for a whole vertical F_PI cell, not a new route."""
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from feline_source_restraint_plan import box
from feline_atomic_save import save_json


def probe(scene, metadata, pins, bus_original, inverse):
    tick = time.monotonic()
    dest = OUT/'n01-FPI-vertical-cell-necessary.json'
    assert not dest.exists()
    centre = A.Vector(-52.95, 0, 41.1)
    shift = A.Vector(40.95, 16, 29.9)
    case = scene['Ref_Material_F_PI_new_0_0'].copy()
    cap = box([-64.95,11.25,30.85],[-40.95,35,51.35])
    for s in (case, cap):
        s.rotate(centre,A.Vector(0,1,0),90)
        s.translate(shift)
        assert s.isValid() and len(s.Solids)==1
    excluded = {n for n in scene if n.startswith('FPIJoint:')}
    excluded.update(['Ref_Material_F_PI_new_0_0','W043','W077','SpliceClip','SpliceSleeve'])
    query=SolidQueries(); checks={}; errors={}
    for label, actor, minimum in [('case',case,1.25),('cap_access',cap,.5)]:
        for name,target in scene.items():
            if name in excluded or bbox_lower_bound(actor.BoundBox,target.BoundBox)>=minimum+1e-6:
                continue
            key=label+'|'+name
            try:
                a,b=actor,target
                if name=='Ref_Material_BUSsupplier25_0_0':
                    a=actor.copy(); a.Placement=inverse*a.Placement; b=bus_original
                if b.Solids:
                    assert b.isValid()
                    gap=query.distance(a,b)
                    checks[key]=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
                else:
                    m=metadata.get(name,{})
                    radius=m.get('nominal_profile_radius_mm') or m.get('radius_mm')
                    assert radius is not None
                    checks[key]=profile_gap(a,b,radius,minimum)
            except Exception as e: errors[key]=str(e)
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(status='VERTICAL_CELL_HOLD' if failures or errors else 'NECESSARY_CASE_ACCESS_ONLY',
                centre_mm=[-12,16,71],input_mm=[-12,16,45.5],output_mm=[-12,16,96.5],
                checks=checks,errors=errors,failures=failures,
                excluded_changed_cell_parts=sorted(excluded),
                unresolved=['Both full wires and all four grips/splice','Input50mm including strip',
                            'Output factory minimum84.5mm','Donor continuation','Roots/assembly/motion/outer'],
                selected=False,N01_complete=False,physical_pass=False,
                source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
                worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],failures,errors,result['worker_seconds'],flush=True)
    return result,case,cap
