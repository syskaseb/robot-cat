"""Necessary actual-case samples for a removable F_PI/MAIN harness unit.

Reject with real material witnesses. Positive samples are NOT a continuous
withdrawal proof and do not waive wire parking or retention release.
"""
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def probe(scene, metadata, pins, bus_original, inverse):
    tick = time.monotonic()
    dest = OUT / 'n01-FPI-removable-unit-negative-X-samples.json'
    assert not dest.exists(), 'Receive saved result instead of repeating'
    own = 'Ref_Material_F_PI_new_0_0'
    original = scene[own]
    assert original.isValid() and original.Solids
    exclusions = {own: 'moving case', 'W043': 'input disconnected from P_SYS; parking NOT yet received',
                  'W077': 'soldered output travels with unit; release/parking NOT yet received'}
    query = SolidQueries()
    checks, errors, visited = {}, {}, []
    poses = [(-x, 0, 0) for x in (5, 10, 20, 30)]
    poses += [(-30, 0, z) for z in (10, 30, 60)]
    for step, offset in enumerate(poses):
        actor = original.copy()
        actor.translate(A.Vector(*offset))
        visited.append(list(offset))
        for name, target in scene.items():
            if name in exclusions or bbox_lower_bound(actor.BoundBox, target.BoundBox) >= 1.25 + 1e-6:
                continue
            key = str(step) + '|' + name
            try:
                a, b = actor, target
                if name == 'Ref_Material_BUSsupplier25_0_0':
                    a = actor.copy()
                    a.Placement = inverse * a.Placement
                    b = bus_original
                if b.Solids:
                    assert b.isValid(), 'invalid material cannot qualify a path'
                    gap = query.distance(a, b)
                    checks[key] = dict(gap_mm=gap, minimum_mm=1.25, ok=gap >= 1.25-1e-6)
                else:
                    m = metadata.get(name, {})
                    radius = m.get('nominal_profile_radius_mm') or m.get('radius_mm')
                    assert radius is not None, 'unknown wire radius'
                    checks[key] = profile_gap(a, b, radius, 1.25)
            except Exception as exc:
                errors[key] = str(exc)
        if errors or any(not r['ok'] for r in checks.values()):
            break
    failures = [k for k, r in checks.items() if not r['ok']]
    result = dict(status='REMOVABLE_UNIT_PATH_HOLD' if failures or errors else 'SAMPLES_ONLY_CONTINUOUS_PATH_OPEN',
                  visited_offsets_mm=visited, checks=checks, errors=errors, failures=failures,
                  excluded_with_unresolved_release=exclusions,
                  sequence=['Disconnect battery', 'Disconnect current W043 P_SYS.5 / W060 G1.1 and Pi USB-C',
                            'Release F_PI/splice/MAIN restraints; keep soldered harness intact',
                            'Proposed F_PI -X then upward; MAIN withdrawal/parking still OPEN'],
                  continuous_sweep_received=False, whole_harness_extraction_received=False,
                  selected=False, N01_complete=False, physical_pass=False,
                  source_sha256={**pins, Path(__file__).relative_to(ROOT).as_posix(): sha(Path(__file__))},
                  worker_seconds=round(time.monotonic()-tick, 3))
    save_json(dest, result)
    print(result['status'], failures, errors, result['worker_seconds'], flush=True)
    return result
