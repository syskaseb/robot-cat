"""Conditional, staged vertical assembly of existing tail bearing block over R4.

No model is modified/saved. Collision samples are not thread engagement,
press-fit force, hand/tool access or a complete robot assembly proof.
"""
import json
from pathlib import Path
import shutil
import tempfile
import pilot
from tail_cartridge_clearance import OUT, TARGET, PARTS


def descendants(plan, parent):
    result = {parent}
    while True:
        updated = result | {j['child'] for j in plan['joints'] if j['parent'] in result}
        if updated == result: return result
        result = updated


LID = OUT/'TailBearingLidService.FCStd'


def stages(A, original, candidate, horn, plan, old_lid):
    import Part
    def overlap(a, b):
        return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.

    absent = descendants(plan, 'UpperHousing34') - {'MG92BOutput29'}
    # Preserve stationary shaft and preloaded support nuts. Axial M3 nut is
    # inserted through the verified R4 side channel before lowering the block.
    fixed = {n: s for n, s in original.items() if n not in absent}
    fixed.update(candidate)
    fixed['CommunityHornEnvelope'] = horn
    fixed['SpindleNut34'] = original['SpindleNut34']
    groups = [
        ('closed_bearing_block', ['UpperHousing34', 'BearingLower34', 'BearingUpper34',
                           'OuterSpacer34', 'InnerSpacer34', 'BearingCapNut34_0', 'BearingCapNut34_1',
                           'BearingCap34', 'BearingCapBolt34_0', 'BearingCapBolt34_1'], 32, 2),
        ('housing_screws', ['HousingJointBolt34_0', 'HousingJointBolt34_1'], 20, 2),
        ('spindle_cap', ['SpindleCap34'], 20, 2),
        ('axial_screw', ['SpindleBolt34'], 32, 2),
    ]
    report = {'initially_absent': sorted(absent), 'initially_present': sorted(fixed),
              'preloaded_support_nuts': ['HousingJointNut34_0', 'HousingJointNut34_1'],
              'preloaded_axial_nut': 'SpindleNut34', 'stages': [],
              'final_tail_segments_installed': False, 'physical_assembly_proven': False}
    assert all(n in fixed for n in report['preloaded_support_nuts'])
    used = set()
    for label, names, start, step in groups:
        assert not any(n in fixed or n in used for n in names)
        moving = {n: original[n] for n in names}
        used.update(names)
        for s in moving.values():
            s.check(True); assert s.isValid()
        internal = [{'parts': [n, m], 'mm3': v} for i, (n, s) in enumerate(moving.items())
                    for m, t in list(moving.items())[i+1:] if (v := overlap(s, t)) > .001]
        rows = []
        for height in range(start, -1, -step):
            hits = []
            for n, shape in moving.items():
                s = shape.copy(); s.translate(A.Vector(0, 0, height))
                for m, t in fixed.items():
                    if (v := overlap(s, t)) > .001:
                        hits.append({'moving': n, 'fixed': m, 'mm3': v})
            rows.append({'height_mm': height, 'intersections': hits})
            print(label, height, hits, flush=True)
        clear = not internal and all(not r['intersections'] for r in rows)
        report['stages'].append({'name': label, 'moving': names, 'fixed_count': len(fixed),
                                'samples': rows, 'internal_intersections': internal, 'clear': clear})
        # Later checks are hypothetical if an earlier step fails; no blanket pass.
        fixed.update(moving)
    report['all_sampled_stages_clear'] = all(s['clear'] for s in report['stages'])
    report['housing_driver_paths'] = []
    for i, y in enumerate((-10, 0)):
        bolt = original[f'HousingJointBolt34_{i}']
        probe = Part.makeCylinder(3, 100, A.Vector(153, y, bolt.BoundBox.ZMax+.05))
        hits = [{'part': n, 'mm3': v} for n, s in fixed.items() if (v := overlap(probe, s)) > .001]
        control = overlap(probe, old_lid)
        assert control > 1
        report['housing_driver_paths'].append({'diameter_mm': 6, 'intersections': hits,
                                               'old_lid_control_mm3': control})
    report['housing_driver_paths_clear'] = all(not r['intersections'] for r in report['housing_driver_paths'])
    report['not_checked'] = ['Physical press fit and retention during bench preassembly (nominal paths tested separately)',
        'Initial insertion of support M3 nuts', 'Hands, tools, cable and shell removal access',
        'Real bearing press-fit, axial preload, screw rotation and engagement',
        'Attachment of tail segments and full assembly/revolute solver',
        'Continuous swept volume between sampled heights']
    return report


def main():
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    files = [pilot.PARAMS, pilot.TARGET] + [pilot.CAD/'modules'/(n+'.FCStd') for n in pilot.MODULES]
    hashes = {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in files}
    report = {'study_sha256': pilot.sha(TARGET), 'lid_sha256': pilot.sha(LID), 'tool_sha256': pilot.sha(Path(__file__)),
              'unchanged_robot_files': hashes, 'cad_saved': False, 'print_ready': False}
    try:
        with tempfile.TemporaryDirectory(prefix='tail-lid-r4-') as tmp:
            dst = Path(tmp)/LID.name; shutil.copy2(LID, dst)
            ld = pilot.document(A, dst); ld.recompute()
            assert len(A.listDocuments()) == 1
            relocated = pilot.global_shape(ld.getObject('BearingCap34'))
            A.closeDocument(ld.Name)
        ld = pilot.document(A, LID); ld.recompute()
        lid = pilot.global_shape(ld.getObject('BearingCap34'))
        lid.check(True); assert lid.isValid() and len(lid.Solids) == 1
        assert lid.cut(relocated).Volume < 1e-5 and relocated.cut(lid).Volume < 1e-5
        sketches = [o for o in ld.Objects if o.TypeId == 'Sketcher::SketchObject']
        assert len(sketches) == 3 and all(o.FullyConstrained and o.solve() == 0 for o in sketches)
        var = ld.getObject('LidServiceParameters')
        try:
            var.AccessRadius = 3.4; ld.recompute()
            removed = lid.Volume-pilot.global_shape(ld.getObject('BearingCap34')).Volume
            assert removed > 0
        finally:
            var.AccessRadius = 3.3; ld.recompute()
        restored = pilot.global_shape(ld.getObject('BearingCap34'))
        assert lid.cut(restored).Volume < 1e-5 and restored.cut(lid).Volume < 1e-5
        report['lid_geometry'] = {'strict_bop': True, 'solids': 1, 'sketches': [o.Name for o in sketches],
             'relocated_documents': 1, 'parameter_removed_mm3': removed, 'volume_mm3': lid.Volume,
             'bbox_mm': [lid.BoundBox.XLength, lid.BoundBox.YLength, lid.BoundBox.ZLength]}
        d = pilot.document(A, TARGET)
        candidate = {n: pilot.global_shape(d.getObject(n)) for n in PARTS}
        horn = pilot.global_shape(d.getObject('CommunityHornEnvelope'))
        print('Loading canonical robot for staged housing assembly...', flush=True)
        robot = pilot.document(A, pilot.TARGET)
        plan = json.loads((pilot.BASE/'assembly-plan.json').read_text())
        original = {r['name']: pilot.global_shape(robot.getObject(r['name'])) for r in plan['components']}
        old_lid = original['BearingCap34']
        expected = old_lid
        for y in (-10, 0): expected = expected.cut(Part.makeCylinder(3.3, 5, A.Vector(153, y, 123.2)))
        assert lid.cut(expected).Volume < 1e-5 and expected.cut(lid).Volume < 1e-5
        report['lid_geometry']['independent_intent_comparison'] = True
        report['lid_geometry']['removed_mm3'] = old_lid.Volume-lid.Volume
        original['BearingCap34'] = lid
        report.update(stages(A, original, candidate, horn, plan, old_lid))
    finally:
        for name in list(A.listDocuments()): A.closeDocument(name)
    assert all(pilot.sha(pilot.ROOT/p) == h for p, h in hashes.items())
    assert pilot.sha(TARGET) == report['study_sha256']
    assert pilot.sha(LID) == report['lid_sha256']
    (OUT/'housing-installation.json').write_text(json.dumps(report, indent=2), encoding='utf-8', newline='\n')
    print('ALL SAMPLED HOUSING STAGES CLEAR:', report['all_sampled_stages_clear'], flush=True)


if __name__ == '__main__': main()
