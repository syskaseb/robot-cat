"""One complete upright-terminal S1 packet, not another old-plane clock grid.

Actual source body/control/hardware retained. Four outward jacket lands feed
concentric bends derived from the actual stud pitch. No native selection.
"""
import itertools
import json
import math
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_current_candidate_scene import current
from plan_feline_joint_fore_domains import cloud
from feline_flat_station_templates import box_points, shared_rail_bounds, to_box
from check_feline_shared_space import tube_prefix
from feline_solid_distance import distance


def main():
    tick = time.monotonic()
    scene, meta, _, pins, *_ = current()
    datumfile = OUT / 'n01-s1-current-source-datums.json'
    source = json.loads(datumfile.read_text())
    body = scene['Ref_Material_current_S1_body_CP2_0_0']
    # Position tied to the received protected Pi fore edge, not a blind offset.
    pi_fore_x = -78.45
    x_limit = pi_fore_x - body.BoundBox.XLength / 2 - 1.25
    target_x = math.floor(x_limit / 12) * 12
    target = A.Vector(target_x, -6, 50)
    rot = A.Rotation(A.Vector(1, 0, 0), -90) * A.Rotation(A.Vector(0, 1, 0), 180)
    tf = A.Placement(target - rot.multVec(body.BoundBox.Center), rot)
    moved = {}
    for row in source['source_parts']:
        name = row['name']
        s = scene[name].copy()
        s.Placement = tf * s.Placement
        assert s.isValid() and len(s.Solids) == 1, name
        moved[name] = s
    ends = []
    for receipt in source['receipts']:
        name = receipt['matching_nominal_source_planes'][0]['part']
        number = int(name.split('_ring_')[1].split('_')[0])
        screw = scene[f'Ref_Material_current_S1_screw_{number}_0_0']
        qold, dold = (A.Vector(*receipt[k]) for k in ('source_point_mm', 'source_departure'))
        eye = A.Vector(screw.BoundBox.Center.x, qold.y, screw.BoundBox.Center.z)
        e = tf.multVec(eye)
        assert abs(abs(e.y) - 6) < 1e-5
        d = A.Vector(0, 1 if e.y > 0 else -1, 0)
        original_target = rot.inverted().multVec(d)
        delta = math.degrees(math.atan2(dold.z, dold.x) - math.atan2(original_target.z, original_target.x))
        cr = A.Rotation(A.Vector(0, 1, 0), delta)
        assert cr.multVec(dold).isEqual(original_target, 1e-6)
        clock = A.Placement(eye - cr.multVec(eye), cr)
        ring = scene[name].copy()
        ring.Placement = tf * clock * ring.Placement
        moved[name] = ring
        q = tf.multVec(clock.multVec(qold))
        assert (q - e - 22.123 * d).Length < 1e-5
        ends.append(dict(ref=receipt['endpoint'], ring=name, eye=e, q=q, d=d))
    max_x = max(r['eye'].x for r in ends)
    new = {}
    clouds = []
    for n, s in moved.items():
        p = cloud(s)
        clouds.append((n, p, np.zeros(len(p)), np.full(len(p), 9)))
    recipes = []
    for r in ends:
        q, d = r['q'], r['d']
        b = A.Vector(1, 0, 0)
        R = 25.2 + max_x - r['eye'].x
        first, grip_start = 12, 3
        wire = tube_prefix(list(q), list(d), 2.1, list(b), R, first)
        end = q + (first + R) * d + R * b
        wire = wire.fuse(Part.makeCylinder(2.1, 9, end, b))
        assert wire.isValid() and len(wire.Solids) == 1
        angles = np.linspace(0, math.pi / 2, 61)
        a = np.array(list(q + first * d))
        dv, bv = np.array(list(d)), np.array(list(b))
        wp = np.vstack((np.linspace(list(q), a, 13),
                        a + R * np.sin(angles)[:, None] * dv + R * (1 - np.cos(angles))[:, None] * bv,
                        np.linspace(list(end), list(end + 9 * b), 10)))
        capq = q + grip_start * d
        cap = Part.makeCylinder(5.3, 9, capq, d).cut(Part.makeCylinder(2.1, 9, capq, d))
        h = capq + 4.5 * d + A.Vector(0, 0, -8.3)
        head = Part.makeBox(6, 6, 6, h - A.Vector(3, 3, 3))
        for label, s in (('wire', wire), ('full_cap_band_reservation', cap), ('head_reservation', head)):
            new[r['ref'] + ':' + label] = s
        clouds.append((r['ref'] + ':wire', wp, np.full(len(wp), 2.1), np.ones(len(wp), int)))
        for label, s in (('full_cap_band_reservation', cap), ('head_reservation', head)):
            p = cloud(s)
            clouds.append((r['ref'] + ':' + label, p, np.zeros(len(p)), np.full(len(p), 2)))
        recipes.append(dict(ref=r['ref'], point_mm=list(q), departure_axis=list(d), R_mm=R,
                            first_mm=first, grip_start_after_barrel_mm=grip_start, full_grip_mm=9,
                            after_arc_mm=9, end_mm=list(end + 9 * b)))
    fieldproof = OUT / 'n01-flat20-field-modulejoint.json'
    proof = json.loads(fieldproof.read_text())
    fieldpath = ROOT / proof['field']
    assert sha(fieldpath) == proof['field_sha256']
    f = np.load(fieldpath, allow_pickle=False)
    axes = [f[k] for k in ('x', 'y', 'z')]
    fields = {k: RegularGridInterpolator(axes, f[k + '_distance'], bounds_error=False, fill_value=0)
              for k in ('material', 'reservation', 'curve_hold', 'motion36', 'outer')}
    grid = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1)
    for k in ('P_SYS', 'W043', 'BankTerm', 'P0Rail'):
        dd = cKDTree(f[k + '_context']).query(grid.reshape(-1, 3), workers=1)[0].reshape(grid.shape[:3])
        fields[k] = RegularGridInterpolator(axes, dd, bounds_error=False, fill_value=0)
    inside = RegularGridInterpolator(axes, f['inside'].astype(float), bounds_error=False, fill_value=0)
    service = RegularGridInterpolator(axes, f['service'].astype(float), method='nearest', bounds_error=False, fill_value=1)
    holds = []
    for name, p, rr, tt in clouds:
        if inside(p).min() < .999:
            k = int(np.argmin(inside(p)))
            holds.append(dict(part=name, layer='outside', margin_mm=-1e6, point=p[k].tolist()))
        for label, interp in fields.items():
            req = 1 if label == 'outer' else 3.35 if label == 'curve_hold' else .2
            values = interp(p) - rr - req
            if values.min() < 0:
                k = int(np.argmin(values))
                holds.append(dict(part=name, layer=label, margin_mm=float(values[k]), point=p[k].tolist()))
        if service(p).max() > .5:
            holds.append(dict(part=name, layer='ATO_access', margin_mm=-.01))
        for rail in shared_rail_bounds():
            v = to_box(p, rail) - rr - .2
            if v.min() < 0:
                holds.append(dict(part=name, layer='common_low_rail', margin_mm=float(v.min())))
    ringpairs = []
    for a, b in itertools.combinations([r['ring'] for r in ends], 2):
        gap = distance(moved[a], moved[b])
        ringpairs.append(dict(a=a, b=b, exact_gap_mm=gap))
    selfpairs = []
    for a, b in itertools.combinations(new, 2):
        if a.split(':')[0] == b.split(':')[0]:
            continue
        gap = distance(new[a], new[b])
        req = .2 if a.endswith(':wire') and b.endswith(':wire') else 1.25
        if gap < req - 1e-6:
            selfpairs.append(dict(a=a, b=b, exact_gap_mm=gap, required_mm=req))
    result = dict(selected=False, N01_complete=False, physical_pass=False, worker_seconds=round(time.monotonic()-tick, 3),
                  whole_source_parts=len(moved), new_full_parts=len(new), centre_mm=list(target),
                  rotation_quaternion=list(rot.Q), recipes=recipes, world_numeric_holds=holds,
                  exact_ring_pairs=ringpairs, exact_new_cross_endpoint_failures=selfpairs,
                  old_S1_context_replaced_as_whole_not_an_exemption=True,
                  new_body_must_be_seen_by_all51_other_domains=True,
                  full_roots_and_tools_and_exact_external_world_OPEN=True,
                  source_sha256={**pins, **{p.relative_to(ROOT).as_posix():sha(p) for p in
                      (datumfile, fieldproof, fieldpath, Path(__file__))}})
    dest = OUT / 'n01-upright-s1-packet.json'
    dest.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(seconds=result['worker_seconds'], parts=len(moved)+len(new), holds=holds,
                         ringpairs=ringpairs, self_failures=selfpairs)), flush=True)


if __name__ == '__main__':
    main()
