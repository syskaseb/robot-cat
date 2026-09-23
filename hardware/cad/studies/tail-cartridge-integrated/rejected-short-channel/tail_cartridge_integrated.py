"""R3: MCP-authored integrated PETG upper/root; ownership migration and audits."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import pilot

OUT = pilot.CAD / 'studies/tail-cartridge-integrated'
TARGET = OUT / 'TailCartridgeIntegrated.FCStd'
PREVIOUS = pilot.CAD / 'studies/tail-cartridge-service/TailCartridgeService.FCStd'
PRINTS = ['LowerRetainerPETG', 'SupportedRoot34']
PARTS = PRINTS + [f'Cartridge{k}{i}' for k in ('Bolt', 'Nut') for i in range(4)]
HOLES = [(x, y) for x in (164.5, 177.5) for y in (-12.5, .5)]


def author():
    """Migrate explicit datum joints after MCP fusion, never rebuild CAD solids."""
    import FreeCAD as A
    assert A.GuiUp
    d = A.ActiveDocument
    assert Path(d.FileName).resolve() == TARGET.resolve()
    # MCP pocket autodirection selected upward; the intended service cut is down.
    d.getObject('IntegratedServiceChannel').Reversed = False
    # The consumed upper Body is construction history, no longer a separate part.
    d.removeObject('Fix_UpperCarrierPETG')
    asm = d.getObject('CartridgeBenchAssembly')
    if d.getObject('UpperCarrierPETG') in asm.Group:
        asm.removeObject(d.getObject('UpperCarrierPETG'))
    for i in range(4):
        b = d.getObject(f'CartridgeBolt{i}')
        assert abs(b.Placement.Base.z - 90.2) < 1e-6
        b.Placement.Base = A.Vector(b.Placement.Base.x, b.Placement.Base.y, 90)
        j = d.getObject('Fix_' + b.Name)
        datum = j.Reference1[0].Placement * j.Placement1
        j.Placement2 = b.Placement.inverse() * datum
    asm.DesignStatus = '10 physical parts, 9 Fixed; integrated upper/root; horn unjointed. BENCH ONLY.'
    for n in PRINTS:
        d.getObject(n).Label = ('Lower retainer PETG R3' if n == PRINTS[0]
                              else 'Integrated upper and root PETG R3')
    d.recompute()
    initial = {n: d.getObject(n).Placement for n in PARTS}
    assert asm.solve() == 0
    for n, p in initial.items():
        assert (d.getObject(n).Placement.Base-p.Base).Length < 1e-6
    for o in d.Objects:
        if hasattr(o, 'ViewObject'): o.Visibility = False
    asm.Visibility = True
    for n in PARTS + ['CommunityHornEnvelope']:
        d.getObject(n).Visibility = True
    d.Label = 'Tail cartridge R3 - integrated PETG - NOT INSTALLED'
    d.recompute()
    d.save()


def audit():
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    files = [pilot.PARAMS, pilot.TARGET] + [pilot.CAD/'modules'/(n+'.FCStd') for n in pilot.MODULES]
    hashes = {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in files}
    report = {'study_sha256': pilot.sha(TARGET), 'previous_sha256': pilot.sha(PREVIOUS),
              'tool_sha256': pilot.sha(Path(__file__)), 'unchanged_robot_files': hashes,
              'installed_in_robot': False, 'print_ready': False, 'cad_saved_by_audit': False}

    def overlap(a, b):
        return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.

    def same(a, b):
        return max(abs(a.cut(b).Volume), abs(b.cut(a).Volume)) < 1e-5

    def snapshot(doc, names):
        return {n: pilot.global_shape(doc.getObject(n)) for n in names}

    def descendants(plan, parent):
        result = {parent}
        while True:
            more = result | {j['child'] for j in plan['joints'] if j['parent'] in result}
            if more == result: return result
            result = more

    try:
        with tempfile.TemporaryDirectory(prefix='tail-integrated-r3-') as tmp:
            dst = Path(tmp)/TARGET.name
            shutil.copy2(TARGET, dst)
            d = pilot.document(A, dst); d.recompute()
            assert len(A.listDocuments()) == 1
            assert not any(o.TypeId == 'App::Link' for o in d.Objects)
            relocated = snapshot(d, PARTS)
            A.closeDocument(d.Name)
            assert pilot.sha(dst) == pilot.sha(TARGET)
        d = pilot.document(A, TARGET); d.recompute()
        old = pilot.document(A, PREVIOUS)
        shapes = snapshot(d, PRINTS)
        report['geometry'] = {}
        for n, s in shapes.items():
            s.check(True)
            assert s.isValid() and len(s.Solids) == 1
            assert same(s, relocated[n])
            bb = s.BoundBox
            report['geometry'][n] = {'strict_bop': True, 'solids': 1, 'volume_mm3': s.Volume,
                                    'bbox_mm': [bb.XLength, bb.YLength, bb.ZLength]}
            assert max(bb.XLength, bb.YLength, bb.ZLength) + 20 < 256
        sketches = [o for o in d.Objects if o.TypeId == 'Sketcher::SketchObject']
        assert len(sketches) == 22 and all(o.FullyConstrained and o.solve() == 0 for o in sketches)
        report['fully_constrained_sketches'] = [o.Name for o in sketches]
        report['relocation'] = {'documents_loaded': 1, 'external_links': 0}
        # Independent R2 geometry plus explicit intended solids, not current feature copies.
        upper = pilot.global_shape(old.getObject('UpperCarrierPETG'))
        added = Part.makeCylinder(13.5, 2.4, A.Vector(171, -6, 94)).fuse(
            Part.makeBox(8.2, 32, 2.4, A.Vector(166.9, -19, 94)))
        added = added.cut(Part.makeBox(5.3, 40, 45, A.Vector(154, -25, 85)))
        for x, y, r in [(171, -6, 4)] + [(x, y, 1.2) for x, y in HOLES]:
            added = added.cut(Part.makeCylinder(r, 3, A.Vector(x, y, 94)))
        expected_upper = upper.fuse(added)
        assert same(expected_upper, pilot.global_shape(d.getObject('UpperCarrierPETG')))
        channel = Part.makeBox(6.6, 14, 2.5, A.Vector(167.7, -6, 95.9))
        expected_root = pilot.global_shape(old.getObject('SupportedRoot34')).fuse(expected_upper).cut(channel)
        expected_lower = pilot.global_shape(old.getObject('LowerRetainerPETG'))
        for x, y in HOLES:
            plug = Part.makeCylinder(2.3, .2, A.Vector(x, y, 90)).cut(
                Part.makeCylinder(1.2, .2, A.Vector(x, y, 90)))
            expected_lower = expected_lower.fuse(plug)
        assert same(shapes[PRINTS[1]], expected_root)
        assert same(shapes[PRINTS[0]], expected_lower)
        report['independent_intent_comparison'] = True
        # These are local roof probes, NOT a global wall-thickness certificate.
        report['roof_probes'] = []
        for y, top in [(10, 96.4), (3, 95.9)]:
            line = Part.makeLine(A.Vector(171, y, 92.35), A.Vector(171, y, top))
            length = line.common(shapes['SupportedRoot34']).Length
            assert abs(length - (top-92.35)) < 1e-5
            report['roof_probes'].append({'x_mm': 171, 'y_mm': y, 'solid_length_mm': length})
        report['remaining_slot_divider_mm'] = .9
        var = d.getObject('CartridgeParameters'); radius = var.HoleRadius
        try:
            var.HoleRadius = 1.3; d.recompute()
            report['parameter_removed_mm3'] = {n: s.Volume-pilot.global_shape(d.getObject(n)).Volume for n, s in shapes.items()}
            assert all(v > 0 for v in report['parameter_removed_mm3'].values())
        finally:
            var.HoleRadius = radius; d.recompute()
        assert all(same(s, pilot.global_shape(d.getObject(n))) for n, s in shapes.items())
        candidate = snapshot(d, PARTS)
        horn = pilot.global_shape(d.getObject('CommunityHornEnvelope'))
        report['horn_intersections_mm3'] = {n: overlap(horn, s) for n, s in shapes.items()}
        assert max(report['horn_intersections_mm3'].values()) < .001
        report['internal_intersections'] = [{'parts': [n, m], 'mm3': v}
            for i, (n, s) in enumerate(candidate.items()) for m, t in list(candidate.items())[i+1:]
            if (v := overlap(s, t)) > .001]
        assert not report['internal_intersections'], report['internal_intersections']
        asm = d.getObject('CartridgeBenchAssembly')
        assert d.getObject('UpperCarrierPETG') not in asm.Group
        assert d.getObject('CommunityHornEnvelope') not in asm.Group
        assert not d.getObject('Fix_UpperCarrierPETG')
        joints = [o for o in d.getObject('Joints').Group if 'JointType' in o.PropertiesList]
        assert len(joints) == 9 and all(str(o.JointType) == 'Fixed' for o in joints)
        initial = {n: d.getObject(n).Placement for n in PARTS}
        report['solver_recovery'] = []
        for n in PARTS[1:]:
            d.getObject(n).Placement = A.Placement(A.Vector(.8, -.5, .6), A.Rotation(A.Vector(0, 0, 1), 3))*initial[n]
            d.recompute(); result = asm.solve()
            errors = [(d.getObject(m).Placement.Base-p.Base).Length for m, p in initial.items()]
            angles = [abs((d.getObject(m).Placement.Rotation*p.Rotation.inverted()).Angle) for m, p in initial.items()]
            assert result == 0 and max(errors) < 1e-5 and max(angles) < 1e-5
            report['solver_recovery'].append({'part': n, 'max_translation_mm': max(errors), 'max_rotation_rad': max(angles)})
        for j in joints:
            p = j.Reference1[0].Placement*j.Placement1
            q = j.Reference2[0].Placement*j.Placement2
            assert (p.Base-q.Base).Length < 1e-5
            assert abs((p.Rotation*q.Rotation.inverted()).Angle) < 1e-5
        assert all(same(s, pilot.global_shape(d.getObject(n))) for n, s in candidate.items())
        report['physical_parts'] = PARTS; report['fixed_joints'] = 9
        report['horn_jointed'] = False
        print('Geometry and native solver passed; loading robot...', flush=True)
        robot = pilot.document(A, pilot.TARGET)
        plan = json.loads((pilot.BASE/'assembly-plan.json').read_text())
        original = {r['name']: pilot.global_shape(robot.getObject(r['name'])) for r in plan['components']}
        rotating = descendants(plan, 'TailRoot29')
        report['co_rotated_existing_parts'] = sorted(rotating)
        report['motion_samples'] = []
        for angle in range(-30, 31, 5):
            def rotated(s):
                s = s.copy(); s.rotate(A.Vector(171, -6, 0), A.Vector(0, 0, 1), angle); return s
            frame = {n: rotated(s) if n in rotating else s for n, s in original.items() if n != 'TailRoot29'}
            hits = []
            for n, s in candidate.items():
                s = rotated(s)
                for m, t in frame.items():
                    if (v := overlap(s, t)) > .001: hits.append({'new': n, 'existing': m, 'mm3': v})
            report['motion_samples'].append({'angle_deg': angle, 'intersections': hits})
            print('Rotation', angle, hits, flush=True)
        absent = descendants(plan, 'UpperHousing34') - {'MG92BOutput29'}
        fixed = {n: s for n, s in original.items() if n not in absent}
        report['installation_absent'] = sorted(absent)
        report['installation_samples'] = []
        for height in range(36, -1, -3):
            hits = []
            for n, s in {**candidate, 'CommunityHornEnvelope': horn}.items():
                s = s.copy(); s.translate(A.Vector(0, 0, height))
                for m, t in fixed.items():
                    if n == 'CommunityHornEnvelope' and m == 'MG92BOutput29': continue
                    if (v := overlap(s, t)) > .001: hits.append({'new': n, 'existing': m, 'mm3': v})
            report['installation_samples'].append({'height_mm': height, 'intersections': hits})
            print('Insertion', height, hits, flush=True)
        installed = {n: s for n, s in original.items() if n != 'TailRoot29'} | candidate
        nut = original['SpindleNut34']; bolt = original['SpindleBolt34']
        report['nut_path'] = []
        for i in range(73):
            dy = 18-i*.25; s = nut.copy(); s.translate(A.Vector(0, dy, 0))
            hits = [{'part': n, 'mm3': v} for n, t in installed.items()
                    if n not in ('SpindleNut34', 'SpindleBolt34') and (v := overlap(s, t)) > .001]
            report['nut_path'].append({'dy_mm': dy, 'intersections': hits, 'retained_bolt_mm3': overlap(s, bolt)})
        def seat(s):
            def faces(t):
                return [f for f in t.Faces if isinstance(f.Surface, Part.Plane)
                        and abs(f.CenterOfMass.z-98.4) < 1e-6 and abs(f.normalAt(0, 0).z) > .9999]
            return sum(f.common(g).Area for f in faces(s) for g in faces(nut))
        report['nut_seat_mm2'] = {'r2': seat(pilot.global_shape(old.getObject('SupportedRoot34'))),
                                  'r3': seat(shapes['SupportedRoot34'])}
        assert abs(report['nut_seat_mm2']['r2']-report['nut_seat_mm2']['r3']) < 1e-5
        report['shaft_tools'] = []
        for diameter in (2.5, 3., 6.):
            probe = Part.makeCylinder(diameter/2, 90, A.Vector(171, -6, 93.05))
            hits = [{'part': n, 'mm3': v} for n, t in installed.items()
                    if n not in ('SpindleNut34', 'SpindleBolt34') and (v := overlap(probe, t)) > .001]
            report['shaft_tools'].append({'diameter_mm': diameter, 'intersections': hits})
        report['fastener_stack_mm'] = {'head_seat_z': 90, 'nut_bottom_z': 98,
                                      'nut_height': 1.6, 'nominal_M2_length': 10, 'protrusion': .4}
        report['conditional_checks_passed'] = all(not row['intersections'] for field in
            ('motion_samples', 'installation_samples', 'nut_path') for row in report[field])
        report['conditional_checks_passed'] &= all(not row['intersections'] for row in report['shaft_tools'][:2])
        assert report['shaft_tools'][2]['intersections']
        assert max(row['retained_bolt_mm3'] for row in report['nut_path']) > 1
        report['scope'] = ('Separate bench cartridge; native Fixed retention plus sampled rigid placements, '
            'NOT driven tail solver, continuous collision sweep, actual spline/screw fit, or physical PETG strength.')
    finally:
        for name in list(A.listDocuments()): A.closeDocument(name)
    assert all(pilot.sha(pilot.ROOT/p) == h for p, h in hashes.items())
    assert pilot.sha(TARGET) == report['study_sha256']
    (OUT/'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8', newline='\n')
    print('CONDITIONAL CHECKS:', report['conditional_checks_passed'], flush=True)


if __name__ == '__main__':
    {'author': author, 'audit': audit}[sys.argv[1]]()
