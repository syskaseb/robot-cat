"""Continuous translation of a convex nominal case; explicit removal hypotheses."""
import time
import FreeCAD as A
import Part
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap


def sweep_convex_case(shape, delta):
    assert shape.isValid() and len(shape.Solids) == 1
    vector = A.Vector(*delta)
    # Sweeping every boundary face plus the original fills the translation
    # volume. No bounding-box collision approximation is used.
    pieces = [shape]
    for face in shape.Faces:
        normal = face.normalAt(0, 0)
        if abs(normal.dot(vector)) > 1e-8:
            pieces.append(face.extrude(vector))
    result = pieces[0].multiFuse(pieces[1:]).removeSplitter()
    assert result.isValid() and len(result.Solids) == 1
    return result


def check(scene, metadata, actors, excluded, bus, inverse, minimum=1.25):
    tick = time.monotonic()
    q = SolidQueries()
    checks, errors = {}, {}
    for name, actor in actors.items():
        for other, target in scene.items():
            margin = minimum(name, other) if callable(minimum) else minimum
            if other in excluded or bbox_lower_bound(actor.BoundBox, target.BoundBox) >= margin+1e-6:
                continue
            key = name+'|'+other
            try:
                a, b = actor, target
                if other == 'Ref_Material_BUSsupplier25_0_0':
                    a = actor.copy()
                    a.Placement = inverse*a.Placement
                    b = bus
                assert b.isValid(), 'invalid material cannot qualify a path'
                if b.Solids:
                    gap = q.distance(a, b)
                    checks[key] = dict(gap_mm=gap, minimum_mm=margin, ok=gap >= margin-1e-6)
                else:
                    m = metadata.get(other, {})
                    radius = m.get('nominal_profile_radius_mm') or m.get('radius_mm')
                    assert radius is not None, 'unknown wire radius'
                    checks[key] = profile_gap(a, b, radius, margin)
            except Exception as exc:
                errors[key] = str(exc)
    return dict(checks=checks, errors=errors,
                failures=[k for k,v in checks.items() if not v['ok']],
                removal_hypotheses=sorted(excluded),
                worker_seconds=round(time.monotonic()-tick, 3),
                complete_service_received=False, N01_complete=False, physical_pass=False)
