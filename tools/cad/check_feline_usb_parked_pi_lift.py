"""Delta-only continuous Pi lift against an unplugged, stationary USB cable.

Does not qualify USB mating dimensions, its unplug stroke, or the old scene.
Caller supplies current pinned shapes; no archived scene rebuilding.
"""
import time
import FreeCAD as A
from feline_solid_distance import bbox_lower_bound, distance
from plan_feline_pi_root_access import profile_gap


def run(movers, curves, boot, fixed_parts, certify, stop=24.):
    tick = time.monotonic()
    checks, errors = {}, {}
    targets = {**{f'cable:{k}': (s, 2.5, 1.25) for k, s in curves.items()},
               'parked_boot': (boot, 0., .5),
               **{f'fixed:{k}': (s, 0., 1.25) for k, s in fixed_parts.items()}}
    for name, moving in movers.items():
        for other, (target, radius, margin) in targets.items():
            key = name + '|' + other
            box = moving.BoundBox
            box.ZMax += stop
            lower = bbox_lower_bound(box, target.BoundBox) - radius
            if lower > margin + 1e-6:
                checks[key] = dict(continuous_clear=True, method='whole_motion_bbox_separation',
                                   certified_lower_bound_mm=lower, minimum_required_mm=margin)
                continue
            try:
                moving.copy().check(True)
                target.copy().check(True)
                def gap(z):
                    actor = moving.copy()
                    actor.translate(A.Vector(0, 0, z))
                    if radius:
                        r = profile_gap(actor, target.copy(), radius, margin)
                        return -radius if r['first_point_inside_material'] else r['gap_lower_bound_mm']
                    return distance(actor, target.copy())
                checks[key] = certify(gap, stop=stop, minimum=margin)
            except Exception as exc:
                errors[key] = str(exc)
    return dict(checks=checks, errors=errors,
                failures=[k for k, v in checks.items() if not v['continuous_clear']],
                worker_seconds=round(time.monotonic()-tick, 3), lift_mm=stop,
                delta_only=True, whole_service_received=False, N01_complete=False,
                physical_pass=False)
