"""Reject a whole functional slot only through shared ACTUAL cap material.

One tiny common bottom-wall witness replaces label permutations when the
same fixed owner blocks the unchanged PETG wall. Bounds only propose a
solid; cut(subset, every actual cap) proves containment before use.
"""
import numpy as np
import FreeCAD as A
import Part
from feline_t18i_two_lane import unit


def common_bottom_wall(stations, slot, lane):
    models = [unit(st, slot, lane) for st in stations]
    caps = [m['parts']['split_common_comb'] for m in models]
    bounds = [s.BoundBox for s in caps]
    lo = np.array([max(b.XMin for b in bounds), max(b.YMin for b in bounds),
                   max(b.ZMin for b in bounds)])
    hi = np.array([min(b.XMax for b in bounds), min(b.YMax for b in bounds),
                   min(w['point_mm'][2]-w['radius_mm']-.15
                       for m in models for w in m['wires'])])
    assert np.all(hi-lo > 1e-5), (lo, hi)
    witness = Part.makeBox(*(hi-lo), A.Vector(*lo))
    receipts = []
    for st, cap in zip(stations, caps):
        outside = witness.copy().cut(cap.copy())
        assert outside.isNull() or outside.isValid()
        assert outside.Volume < 1e-7, (st['ref'], outside.Volume)
        receipts.append(dict(ref=st['ref'], outside_mm3=outside.Volume))
    return witness, receipts


def receive_common_failures(result, longdata, stations):
    """Exact one-way exclusions only; a clear witness never accepts a slot."""
    from feline_two_lane_receive import world_context
    from feline_fore_power_pair import SolidQueries
    candidates = {}
    for rec in longdata['units'].values():
        fail = rec.get('failure')
        if (rec['slot']['profile'] == 'standard' and isinstance(fail, str)
                and fail.startswith('split_common_comb|fixed:')):
            key = str(rec['slot']['id'])+':1'
            candidates.setdefault(key, (rec['slot'], fail.split('|fixed:', 1)[1]))
    done = result.setdefault('common_bottom_wall_receipts', {})
    pending = {k: v for k, v in candidates.items() if k not in done}
    if pending:
        world, fixed = world_context()
        oldpins = result.get('common_wall_world_source_sha256')
        assert oldpins is None or oldpins == world.pins
        result['common_wall_world_source_sha256'] = world.pins
        family = [st for st in stations.values()
                  if st['flat_dimensions_pitch_departure_thickness_mm'][2] < 10]
        query = SolidQueries()
        for key, (slot, owner) in pending.items():
            wall, subsets = common_bottom_wall(family, slot, 1)
            target = fixed[owner]
            if owner == world.bus['name']:
                wall = wall.copy()
                wall.Placement = world.bus['inverse']*wall.Placement
                target = world.bus['original']
            gap = query.distance(wall, target)
            done[key] = dict(slot_id=slot['id'], lane=1, fixed_owner=owner,
                common_actual_PETG_volume_mm3=wall.Volume, subset_proofs=subsets,
                actual_gap_mm=gap, required_mm=1.25,
                exclude_all_standard_profiles=gap < 1.25-1e-6,
                clear_witness_is_NOT_acceptance=True)
            print('Common cap wall', key, owner, gap,
                  'all profiles excluded' if gap < 1.25-1e-6 else 'no exclusion', flush=True)
    return {(r['slot_id'], r['lane']) for r in done.values()
            if r['exclude_all_standard_profiles']}
