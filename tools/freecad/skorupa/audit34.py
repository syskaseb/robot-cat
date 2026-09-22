"""Read-only, fail-closed fit audit of v34 support against signed v33 geometry.

Run in FreeCAD Python. No old CAD is modified. Sampled rigid tail rotation,
not continuous collision, physical fit, bearing internal design or full gait.
"""
import hashlib
import itertools
import json
import math
import FreeCAD as A
import Part
from support34 import (OUT, SOURCE, SOURCE_SHA, MASTER, TARGET, PIVOT,
                       CAP_HOLES, FOOT_HOLES, HOUSING_HOLES, ADDITIONS, REPLACEMENTS, instance)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def common_volume(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.
    v = abs(a.common(b).Volume)
    assert v <= min(abs(a.Volume), abs(b.Volume)) + .001, 'Impossible Boolean volume'
    return v


def horizontal_contact_area(a, b):
    # A solid/solid common often returns no surface for a touching-only pair.
    # Compare coplanar horizontal faces explicitly; nominal race envelopes only.
    def faces(s):
        return [f for f in s.Faces if isinstance(f.Surface, Part.Plane)
                and abs(f.normalAt(0, 0).z) > .999999]
    return sum(f.common(g).Area for f in faces(a) for g in faces(b)
               if abs(f.CenterOfMass.z - g.CenterOfMass.z) < 1e-6
               and f.BoundBox.intersect(g.BoundBox))


def servo_insertion_path(servo, support):
    """Sampled cable-end-first path. Case only; loose cable/plug not supplied.

    Rotate about the ear-plane centre, shift Y to centre the section passing
    the 3mm deck; straighten after the cable boss passes it. These are CAD
    assembly poses, not actuator commands or a continuous swept-volume proof.
    """
    slab = Part.makeBox(100, 100, 3, A.Vector(120, -50, 74))
    poses = [(40., i, 1.2*i/12) for i in range(13)]
    poses += [(float(z), 12., 1.2) for z in range(39, 22, -1)]
    for step in range(41):
        dz = 22 - step*.1
        angle = min(12., max(0., 6*(dz-18)))
        s = servo.copy()
        p = A.Placement(A.Vector(0, 0, dz), A.Rotation(A.Vector(1, 0, 0), angle), A.Vector(171, -.75, 77))
        s.Placement = p * s.Placement
        section = s.common(slab).BoundBox
        assert section.YLength <= 23.3, (dz, angle, section.YLength)
        dy = -.75 - (section.YMin + section.YMax)/2
        poses.append((dz, angle, dy))
    poses += [(float(z), 0., 0.) for z in range(17, -1, -1)]
    result = []
    for dz, angle, dy in poses:
        s = servo.copy()
        p = A.Placement(A.Vector(0, dy, dz), A.Rotation(A.Vector(1, 0, 0), angle), A.Vector(171, -.75, 77))
        s.Placement = p * s.Placement
        v = common_volume(s, support)
        result.append(dict(lift_mm=dz, tilt_x_deg=angle, shift_y_mm=dy, volume_mm3=v))
    return result


def main():
    old_plan = json.loads((SOURCE / 'assembly-plan.json').read_text())
    assert digest(SOURCE / old_plan['cad_filename']) == SOURCE_SHA
    assert json.loads((SOURCE / 'shape-cache/index.json').read_text())['source_sha256'] == SOURCE_SHA
    master_sha = digest(MASTER)
    master = A.openDocument(str(MASTER))
    shapes = {}
    for row in old_plan['components']:
        shape = Part.Shape()
        shape.read(str(SOURCE / 'shape-cache' / (row['name'] + '.brep')))
        shapes[row['name']] = shape
    for name, (src, xyz) in REPLACEMENTS.items():
        shapes[name] = instance(master, src, xyz)
    for name, (src, _, _, _, xyz) in ADDITIONS.items():
        shapes[name] = instance(master, src, xyz)
    changed = set(ADDITIONS) | set(REPLACEMENTS)
    sketches = [dict(name=o.Name, fully_constrained=o.FullyConstrained,
                     constraints=len(o.Constraints)) for o in master.Objects
                if o.TypeId == 'Sketcher::SketchObject']
    parts = []
    for o in master.Objects:
        if o.TypeId != 'PartDesign::Body':
            continue
        s = o.Shape
        errors = []
        try:
            s.check(True)
        except Exception as exc:
            errors.append(str(exc))
        b = s.BoundBox
        parts.append(dict(name=o.Name, valid=s.isValid(), status=o.getStatusString(), solids=len(s.Solids),
                          bop_errors=errors, volume_mm3=s.Volume,
                          envelope_mm=[b.XLength, b.YLength, b.ZLength],
                          fits_256=max(b.XLength, b.YLength, b.ZLength) <= 256))
    hits = []
    pairs = 0
    for an, bn in itertools.combinations(sorted(shapes), 2):
        if not ({an, bn} & changed):
            continue
        if not shapes[an].BoundBox.intersect(shapes[bn].BoundBox):
            continue
        pairs += 1
        v = common_volume(shapes[an], shapes[bn])
        if v > .01:
            hits.append(dict(parts=[an, bn], volume_mm3=v))
    print('REST', pairs, 'pairs', hits, flush=True)
    moving = {r['name'] for r in old_plan['components'] if r['stage'] == 'Motion_Tail_Yaw'}
    moving |= {n for n, r in ADDITIONS.items() if r[2]}
    static = set(shapes) - moving
    sweep = []
    for deg in range(-30, 31, 5):
        pose = A.Placement(A.Vector(), A.Rotation(A.Vector(0, 0, 1), deg), A.Vector(*PIVOT))
        clashes = []
        for an in sorted(moving):
            a = shapes[an].copy()
            a.Placement = pose * a.Placement
            for bn in sorted(static):
                b = shapes[bn]
                if not a.BoundBox.intersect(b.BoundBox):
                    continue
                v = common_volume(a, b)
                if v > .01:
                    clashes.append(dict(parts=[an, bn], volume_mm3=v))
        sweep.append(dict(yaw_deg=deg, interferences=clashes))
        print('YAW', deg, clashes, flush=True)
    tools = []
    module = {n for n in shapes if n.startswith(('Tail', 'MG92B'))} | set(ADDITIONS)
    for i, (x, y) in enumerate(FOOT_HOLES):
        # Revised design: bolts inserted upwards, nuts captured in foot.
        probe = Part.makeCylinder(3., 40, A.Vector(x, y, 38.), A.Vector(0, 0, -1))
        test_names = set(shapes) - {f'TailMountBolt29_{i}'}
        collisions = {n: common_volume(probe, shapes[n]) for n in test_names
                      if probe.BoundBox.intersect(shapes[n].BoundBox)}
        tools.append(dict(check=f'foot driver {i}, from below, fully assembled', diameter_mm=6,
                          required_for_bench_assembly=False,
                          hits={n: v for n, v in collisions.items() if v > .01}))
        tools.append(dict(check=f'foot driver {i}, detached tail/bridge module', diameter_mm=6,
                          required_for_bench_assembly=True,
                          hits={n: v for n, v in collisions.items() if v > .01 and n in module}))
    for i, (x, y) in enumerate(CAP_HOLES):
        probe = Part.makeCylinder(3., 18.2, A.Vector(x, y, 101.))
        # Probe contains its own nut: exclude it, but not the stationary body.
        collisions = {n: common_volume(probe, s) for n, s in shapes.items()
                      if n not in {f'BearingCapNut34_{i}', f'BearingCapBolt34_{i}'}
                      and probe.BoundBox.intersect(s.BoundBox)}
        tools.append(dict(check=f'cap nut socket {i}, OD <=6 mm',
                          required_for_bench_assembly=True,
                          hits={n: v for n, v in collisions.items() if v > .01}))
    for i, (x, y) in enumerate(HOUSING_HOLES):
        probe = Part.makeCylinder(3., 40, A.Vector(x, y, 108.))
        excluded = {f'HousingJointBolt34_{i}', 'BearingCap34',
                    'BearingCapBolt34_0', 'BearingCapBolt34_1'}
        collisions = {n: common_volume(probe, shapes[n]) for n in module - excluded
                      if probe.BoundBox.intersect(shapes[n].BoundBox)}
        tools.append(dict(check=f'housing driver {i}, before cap installation', diameter_mm=6,
                          required_for_bench_assembly=True,
                          hits={n: v for n, v in collisions.items() if v > .01}))
    # Only the removable upper housing is lowered over the root. The lower
    # support and original servo mount are ONE print, not assembled around it.
    insertion = []
    present = {'MG92BMount29', 'MG92BCase29', 'MG92BOutput29', 'TailRoot29',
               'TailBridge29', 'TailEarBolt29_0', 'TailEarBolt29_1',
               'TailEarNut29_0', 'TailEarNut29_1'}
    for dz in range(24, -1, -2):
        a = shapes['UpperHousing34'].copy()
        a.translate(A.Vector(0, 0, dz))
        collisions = {n: common_volume(a, shapes[n]) for n in present
                      if a.BoundBox.intersect(shapes[n].BoundBox)}
        insertion.append(dict(lift_mm=dz, hits={n: v for n, v in collisions.items() if v > .01}))
    contacts = []
    servo_straight_insertion = []
    for dz in range(40, -1, -2):
        a = shapes['MG92BCase29'].copy()
        a.translate(A.Vector(0, 0, dz))
        v = common_volume(a, shapes['MG92BMount29'])
        servo_straight_insertion.append(dict(lift_mm=dz, volume_mm3=v))
    servo_insertion = servo_insertion_path(shapes['MG92BCase29'], shapes['MG92BMount29'])
    for an, bn in [('BearingLower34', 'UpperHousing34'),
                   ('BearingLower34', 'OuterSpacer34'), ('OuterSpacer34', 'BearingUpper34'),
                   ('BearingLower34', 'TailRoot29'), ('BearingLower34', 'InnerSpacer34'),
                   ('InnerSpacer34', 'BearingUpper34'), ('BearingUpper34', 'SpindleCap34'),
                   ('UpperHousing34', 'MG92BMount29'), ('UpperHousing34', 'BearingCap34')]:
        a, b = shapes[an], shapes[bn]
        contacts.append(dict(parts=[an, bn], minimum_gap_mm=a.distToShape(b)[0],
                             horizontal_contact_area_mm2=horizontal_contact_area(a, b)))
    tool_hits = [x for x in tools if x['hits'] and x['required_for_bench_assembly']]
    ok = not hits and not any(x['interferences'] for x in sweep) and not tool_hits
    ok &= not any(x['hits'] for x in insertion)
    ok &= not any(x['volume_mm3'] > .01 for x in servo_insertion)
    ok &= all(c['minimum_gap_mm'] < 1e-6 and c['horizontal_contact_area_mm2'] > .01 for c in contacts)
    ok &= all(s['fully_constrained'] for s in sketches)
    ok &= all(p['valid'] and p['status']=='Valid' and p['solids'] == 1 and not p['bop_errors'] and p['fits_256'] for p in parts)
    assert digest(MASTER) == master_sha, 'Master changed during audit; discard this run'
    report = dict(source_checkpoint_sha256=SOURCE_SHA, master_sha256=master_sha,
                  target_sha256=digest(TARGET) if TARGET.exists() else None,
                  changed_parts=sorted(changed), sketches=sketches, native_parts=parts,
                  rest_pairs=pairs, rest_interferences=hits, yaw_samples=sweep,
                  tool_corridors=tools, upper_housing_insertion_samples=insertion,
                  servo_insertion_samples=servo_insertion, nominal_contacts=contacts,
                  rejected_straight_servo_insertion=servo_straight_insertion,
                  servo_insertion_path_scope=servo_insertion_path.__doc__,
                  assembly_requires_detached_tail_bridge=True, in_situ_foot_service_verified=False,
                  geometric_checks_passed=bool(ok), print_release=False,
                  horn_interface_verified=False, physical_bearing_fit_verified=False,
                  scope=__doc__)
    (OUT / 'fit-audit.json').write_text(json.dumps(report, indent=2), encoding='utf8', newline='\n')
    print('GEOMETRIC_CHECKS_PASS', bool(ok), 'TOOLS', tool_hits, flush=True)
    assert ok, 'Geometric audit failed; do not promote the candidate'


if __name__ == '__main__':
    main()
