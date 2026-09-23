"""Fresh-process checks of the installed R4 whole robot; never saves CAD.

geometry compares every component to its pinned predecessor/source.
relocation tests automatic link loading, coupled parameters and native motion.
"""
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import time
import pilot
import integrate_tail_cartridge as task


def files():
    return [task.TARGET, task.MODULE] + [p for p in task.old_files() if p != pilot.TARGET]


def hashes():
    return {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in files()}


def overlap(a, b):
    return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.


def equal(a, b):
    from inheritance30 import compare_text
    try:
        return compare_text(a.cleaned().exportBrepToString(), b.cleaned().exportBrepToString())
    except AssertionError:
        # Recompute can change OCCT serialization flags. This fallback requires
        # strict BOP and empty differences, and is used only on the new parts.
        from tail_module import compare_boolean_history
        return compare_boolean_history(a, b)


def start():
    import FreeCAD as A
    assert not A.GuiUp and not A.listDocuments()
    sys.path.insert(0, str(Path(A.getHomePath())/'Mod/Assembly'))
    sys.path.insert(0, str(pilot.ROOT/'tools/freecad/skorupa'))
    return A


def close_all(A):
    for n in list(A.listDocuments()): A.closeDocument(n)


def geometry():
    A = start()
    import Part
    from inheritance30 import compare_text
    original_hashes = hashes()
    migration = json.loads((task.OUT/'migration.json').read_text())
    baseline = pilot.document(A, pilot.TARGET)
    old_plan = json.loads((pilot.BASE/'assembly-plan.json').read_text())
    # Keep only serialization, not two large native documents in memory.
    expected = {r['name']: pilot.global_shape(baseline.getObject(r['name'])).cleaned().exportBrepToString()
                for r in old_plan['components'] if r['name'] not in task.REPLACEMENTS}
    old_frames = {r['name']: (str(baseline.getObject(r['name']).Placement1),
                             str(baseline.getObject(r['name']).Placement2)) for r in old_plan['joints']}
    close_all(A)
    print('Predecessor geometry serialized; closed before loading new robot', flush=True)
    r4 = pilot.document(A, task.SOURCE/'TailCartridgeClearance.FCStd')
    for n, src in {'TailRoot29': 'SupportedRoot34', **task.SOURCES}.items():
        expected[n] = pilot.global_shape(r4.getObject(src)).cleaned().exportBrepToString()
    close_all(A)
    lid = pilot.document(A, task.SOURCE/'TailBearingLidService.FCStd')
    expected['BearingCap34'] = pilot.global_shape(lid.getObject('BearingCap34')).cleaned().exportBrepToString()
    close_all(A)
    d = pilot.document(A, task.TARGET)
    d.recompute()
    plan = json.loads((task.OUT/'assembly-plan.json').read_text())
    assert set(expected) == {r['name'] for r in plan['components']}
    rows = []
    shapes = {}
    for n, text in expected.items():
        s = pilot.global_shape(d.getObject(n)); shapes[n] = s
        try:
            result = compare_text(text, s.cleaned().exportBrepToString())
        except AssertionError:
            from tail_module import compare_boolean_history, mappings
            # The seven inherited editable PETG histories have the same strict
            # fallback as the original migration audit. Never use it on shells.
            inherited_history = {name for name, (owner, _, _) in mappings().items() if owner == 'tail/TailSupport'}
            assert n in task.REPLACEMENTS or n in task.ADDED or n in inherited_history, n
            source_shape = Part.Shape(); source_shape.importBrepFromString(text)
            result = compare_boolean_history(source_shape, s)
        rows.append({'name': n, 'source': 'R4' if n in task.REPLACEMENTS or n in task.ADDED else 'predecessor', **result})
        if len(rows) % 50 == 0: print('Compared', len(rows), '/329', flush=True)
    assert all(old_frames[n] == (str(d.getObject(n).Placement1), str(d.getObject(n).Placement2)) for n in old_frames)
    print('All 329 physical geometries and 319 inherited joint frames preserved/intentional', flush=True)
    module = d.getObject('TailRoot29').LinkedObject.Document
    sketches = [o for o in module.Objects if o.TypeId == 'Sketcher::SketchObject']
    assert len(sketches) == 25 and all(o.FullyConstrained and o.solve() == 0 for o in sketches)
    changed = list(task.REPLACEMENTS) + task.ADDED
    valid = {}
    for n in changed:
        s = shapes[n]; s.check(True)
        assert s.isValid() and len(s.Solids) == 1
        valid[n] = {'strict_bop': True, 'solids': 1, 'volume_mm3': s.Volume,
                    'bbox_mm': [s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength]}
    static = []
    for n in changed:
        for m in shapes:
            if m == n or (m in changed and changed.index(m) < changed.index(n)): continue
            v = overlap(shapes[n], shapes[m])
            if v > .001: static.append({'parts': [n, m], 'mm3': v})
    from tail_housing_installation import descendants
    rotating = descendants(plan, 'TailRoot29')
    motion = []
    for angle in range(-30, 31, 5):
        frame = {}
        for n,s in shapes.items():
            frame[n] = s.copy()
            if n in rotating: frame[n].rotate(A.Vector(171,-6,0), A.Vector(0,0,1), angle)
        hits = []
        for n in changed:
            for m in frame:
                if m == n or (m in changed and changed.index(m) < changed.index(n)): continue
                v = overlap(frame[n], frame[m])
                if v > .001: hits.append({'parts': [n,m], 'mm3': v})
        motion.append({'angle_deg': angle, 'intersections': hits})
        print('Installed tail collision sample', angle, hits, flush=True)
    # An actual displaced assembly instance must not match the migration source.
    obj = d.getObject('TailLowerRetainer'); saved = obj.LinkPlacement
    try:
        obj.LinkPlacement = A.Placement(A.Vector(1, 0, 0), A.Rotation())*saved
        d.recompute()
        caught = False
        try: compare_text(expected[obj.Name], pilot.global_shape(obj).cleaned().exportBrepToString())
        except AssertionError: caught = True
        assert caught
    finally:
        obj.LinkPlacement = saved; d.recompute()
    report = {'file_sha256': original_hashes, 'tool_sha256': pilot.sha(Path(__file__)),
              'components': 329, 'unchanged_components': 318, 'replacements': task.REPLACEMENTS,
              'added': task.ADDED, 'geometry_comparison': rows, 'new_geometry': valid,
              'constrained_sketches': [o.Name for o in sketches], 'static_intersections': static,
              'tail_collision_samples': motion, 'co_rotated_parts': sorted(rotating),
              'inherited_joint_frames_unchanged': len(old_frames), 'misplacement_control_detected': caught,
              'print_ready': False, 'legacy_shell_bop_passed': False,
              'scope': 'Incremental R4 geometry and collisions only. Inherited shell defects remain; no global BOP approval.'}
    close_all(A)
    assert original_hashes == hashes()
    assert all(pilot.sha(pilot.ROOT/p) == h for p, h in migration['unchanged_predecessor_files'].items())
    task.write('geometry.json', report)
    assert not static, static
    assert all(not r['intersections'] for r in motion), motion
    print('Geometry PASS; unchanged files; no incremental rest intersections', flush=True)


def parameters(A, d):
    module = d.getObject('TailRoot29').LinkedObject.Document
    rows = []
    for varname, prop, value, names, signs in [
        ('BossInterface', 'BossRadius', 2.7, ['TailLowerRetainer', 'TailRoot29'], [1, -1]),
        ('CartridgeParameters', 'HoleRadius', 1.3, ['TailLowerRetainer', 'TailRoot29'], [-1, -1]),
        ('LidServiceParameters', 'AccessRadius', 3.4, ['BearingCap34'], [-1])]:
        control = d.getObject('Cartridge_'+varname).LinkedObject
        assert control.Document == module
        original = getattr(control, prop)
        before = {n: pilot.global_shape(d.getObject(n)) for n in names}
        try:
            setattr(control, prop, value); module.recompute(); d.recompute()
            deltas = {n: pilot.global_shape(d.getObject(n)).Volume-s.Volume for n,s in before.items()}
            assert all(deltas[n]*sign > .001 for n,sign in zip(names,signs)), deltas
            assert all(o.FullyConstrained and o.solve() == 0 for o in module.Objects if o.TypeId == 'Sketcher::SketchObject')
        finally:
            setattr(control, prop, original); module.recompute(); d.recompute()
        for n,s in before.items(): equal(s, pilot.global_shape(d.getObject(n)))
        rows.append({'parameter': varname+'.'+prop, 'test_value': value, 'volume_delta_mm3': deltas, 'restored': True})
    return rows


def native(A, d, plan):
    asm = d.getObject('RobotCatAssembly24')
    sim = d.getObject('RobotConnectionTest35')
    names = [r['name'] for r in plan['components']]
    wrappers = {n: d.getObject('Rigid_'+n) for n in names}
    initial = {n: o.Placement.copy() for n,o in wrappers.items()}
    landmarks = {}
    source_placements = {}
    for n in names:
        shape = pilot.global_shape(d.getObject(n))
        count = len(shape.Vertexes)
        indices = sorted({1, max(1,count//2), count})
        landmarks[n] = {i: shape.getElement('Vertex'+str(i)).Point for i in indices}
        source_placements[n] = shape.Placement
    # Calculate centres of the nine new pieces once. During pure rigid motion
    # their transformed centre follows from the verified global shape frame.
    centres = {n: pilot.solid_centroid(pilot.global_shape(d.getObject(n))) for n in task.ADDED}
    local = {n: d.getObject(n).Placement.copy() for n in names}
    assert len(names) == 329 and len(plan['joints']) == 328
    temp = sum('TEMP' in d.getObject(r['name']).DesignStatus.upper() for r in plan['joints'])
    assert temp == 29
    for r in plan['joints']:
        j = d.getObject(r['name'])
        assert j.Reference1[0].Name == 'Rigid_'+r['parent'] and j.Reference2[0].Name == 'Rigid_'+r['child']
        assert j.JointType == r['type']
    rows, peaks = [], {}
    excursions = {n: 0. for n in task.ADDED}
    try:
        asm.generateSimulation(sim)
        assert asm.numberOfFrames() == 22
        for i in range(asm.numberOfFrames()):
            tick = time.monotonic()
            asm.updateForFrame(i)
            print('Solver frame', i, 'updated', flush=True)
            gap = fixed = axis = 0.
            for r in plan['joints']:
                j = d.getObject(r['name']); p = j.Reference1[0].Placement*j.Placement1; q = j.Reference2[0].Placement*j.Placement2
                gap = max(gap, (p.Base-q.Base).Length)
                theta = (p.Rotation.inverted()*q.Rotation).Angle
                if r['type'] == 'Fixed': fixed = max(fixed, theta)
                else:
                    axis = max(axis, p.Rotation.multVec(A.Vector(0,0,1)).getAngle(q.Rotation.multVec(A.Vector(0,0,1))))
                    peaks[r['name']] = max(peaks.get(r['name'], 0), math.degrees(theta))
            error = 0.
            for n in names:
                assert d.getObject(n).Placement.isSame(local[n], 1e-6), n
                shape = pilot.global_shape(d.getObject(n))
                expected = wrappers[n].Placement*source_placements[n]
                assert shape.Placement.isSame(expected, 1e-5), n
                for index, point in landmarks[n].items():
                    actual = shape.getElement('Vertex'+str(index)).Point
                    error = max(error, (actual-wrappers[n].Placement.multVec(point)).Length)
                if n in excursions:
                    transform = shape.Placement*source_placements[n].inverse()
                    excursions[n] = max(excursions[n], (transform.multVec(centres[n])-centres[n]).Length)
            assert max(gap, fixed, axis, error) < 1e-5
            rows.append({'frame': i, 'gap_mm': gap, 'fixed_error_rad': fixed, 'axis_error_rad': axis, 'geometry_error_mm': error})
            print('Native frame', i, 'gap', gap, 'seconds', time.monotonic()-tick, flush=True)
        assert len(peaks) == 13 and abs(peaks['Rev_TailYaw29']-30) < 1e-5
        assert all(abs(p-3) < 1e-5 for n,p in peaks.items() if n != 'Rev_TailYaw29')
        assert all(v > .1 for v in excursions.values())
    finally:
        for n, pose in initial.items(): wrappers[n].Placement = pose
        d.recompute(); assert asm.solve() == 0
    assert all(o.Placement.isSame(initial[n], 1e-5) for n,o in wrappers.items())
    return {'frames': rows, 'peaks_deg': peaks, 'added_centroid_excursions_mm': excursions,
            'geometry_method': 'Global shape frame and first/middle/last vertex of each of 329 components; centres propagated by verified rigid transforms, not recalculated per frame.',
            'components': 329, 'fixed': 315, 'revolute': 13, 'temporary': temp, 'restored': True}


def relocation():
    A = start()
    original_hashes = hashes()
    plan = json.loads((task.OUT/'assembly-plan.json').read_text())
    with tempfile.TemporaryDirectory(prefix='robot-cat-r4-installed-') as tmp:
        root = Path(tmp).resolve()
        for p in files():
            dest = root/p.relative_to(pilot.CAD); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
        d = pilot.document(A, root/task.TARGET.relative_to(pilot.CAD))
        try:
            d.recompute()
            docs = list(A.listDocuments().values())
            assert len(docs) == 10, [(o.Name,o.FileName) for o in docs]
            assert all(Path(o.FileName).resolve().is_relative_to(root) for o in docs)
            assert not any('Invalid' in o.State for doc in docs for o in doc.Objects)
            links = []
            for row in plan['components']:
                o = d.getObject(row['name'])
                if o.TypeId == 'App::Link':
                    path = Path(o.LinkedObject.Document.FileName).resolve()
                    assert path.is_relative_to(root) and not o.Shape.isNull()
                    links.append({'component': o.Name, 'owner': path.relative_to(root).as_posix(), 'object': o.LinkedObject.Name})
            assert len(links) == 54
            report = {'file_sha256': original_hashes, 'tool_sha256': pilot.sha(Path(__file__)),
                      'fresh_process': True, 'documents': 10, 'links': links, 'outside_dependencies': False,
                      'parameters': parameters(A, d), 'native': native(A,d,plan),
                      'print_ready': False, 'servo_coupling_confirmed': False, 'cad_saved': False}
        finally: close_all(A)
    assert hashes() == original_hashes
    task.write('relocation-native.json', report)
    print('Relocation, parameter update and native whole-robot motion PASS', flush=True)


if __name__ == '__main__':
    {'geometry': geometry, 'relocation': relocation}[sys.argv[1]]()
