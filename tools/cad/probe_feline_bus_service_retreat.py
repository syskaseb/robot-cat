"""Necessary end-pose check of BUS retreat from the stationary USB plug.

Reuses saved geometry; a positive sample never qualifies a service sequence.
No cable parking, fastener access or missing actor is silently approved.
"""
import time
import FreeCAD as A
from feline_solid_distance import bbox_lower_bound
from receive_feline_pi_split_service_space import independent
from feline_atomic_save import save_json
from plan_feline_layout import OUT


def probe(scene, core):
    tick = time.monotonic()
    dest = OUT / 'n01-BUS-module-service-retreat-sample.json'
    assert not dest.exists(), 'Receive saved result, do not repeat'
    moving = {r['name'] for r in core['geometry']
              if r['name'].startswith('Ref_Material_BUSsupplier')}
    # Disconnect the BUS-owned mating connections before moving the module.
    # These are hypotheses, NOT a validated disconnect/parking operation.
    released = {'CurrentBUS:H5MatingReserve', 'CurrentBUS:BUS.D',
                'CurrentBUS:BUS.G'}
    retired = set(core['recipe'].get('fixed_replaced_names', []))
    obstacles = {n:s for n,s in scene.items() if n not in moving | released | retired}
    pairs, errors = {}, {}
    invalid = []
    for name in sorted(moving):
        actor = independent(scene[name])
        if not actor.Solids or not actor.isValid():
            invalid.append(name)
            continue
        actor.translate(A.Vector(12, 0, 0))
        for other, target in obstacles.items():
            if bbox_lower_bound(actor.BoundBox, target.BoundBox) > 1e-6:
                continue
            if not target.Solids:
                continue  # Explicitly not a complete wire-clearance test.
            key = name + '|' + other
            try:
                assert target.isValid(), 'Invalid obstacle'
                b = independent(target)
                gap = actor.distToShape(b)[0]
                if gap > 1e-6:
                    continue
                common = independent(actor).common(b)
                assert common.isNull() or common.isValid()
                volume = common.Volume
                pairs[key] = {'gap_mm': gap, 'common_mm3': volume,
                              'hard_intersection': volume > 1e-5}
            except Exception as exc:
                errors[key] = str(exc)
        # One positive material witness suffices to reject this end pose.
        if any(r['hard_intersection'] for r in pairs.values()):
            break
    failures = [k for k,r in pairs.items() if r['hard_intersection']]
    result = dict(status='BUS_RETREAT_END_POSE_REJECTED' if failures else
                  'BUS_RETREAT_SAMPLE_INCOMPLETE_NOT_RECEIVED',
                  translation_mm=[12,0,0], stroke_is_project_assumption=True,
                  moving_names=sorted(moving), released_hypotheses=sorted(released),
                  retired_aliases_excluded=sorted(retired),
                  checks=pairs, failures=failures, errors=errors, invalid=invalid,
                  scene_actor_count=len(scene),
                  wire_clearances_and_missing_actors_not_qualified=True,
                  fastener_access_and_parking_not_qualified=True,
                  continuous_motion_not_qualified=True,
                  N01_complete=False, physical_pass=False,
                  worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'], failures, errors, result['worker_seconds'],flush=True)
    return result
