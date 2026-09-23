"""Sample bench insertion into the existing upper housing, outside the robot."""
import json
from pathlib import Path
import sys
import pilot
from tail_cartridge_clearance import OUT
import tail_module


def main():
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    mapping = tail_module.mappings()
    sys.path.insert(0, str(pilot.ROOT/'tools/freecad/skorupa'))
    from support34 import instance
    sources = [pilot.PARAMS] + [pilot.CAD/'modules'/(n+'.FCStd') for n in tail_module.MODULES]
    hashes = {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in sources}
    helpers = [pilot.ROOT/'tools/cad/pilot.py', pilot.ROOT/'tools/cad/tail_module.py',
               pilot.ROOT/'tools/freecad/skorupa/support34.py']
    report = {'tool_sha256': pilot.sha(Path(__file__)), 'source_sha256': hashes,
              'helper_sha256': {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in helpers},
              'cad_saved': False, 'print_ready': False, 'robot_obstacles_included': False,
              'scope': 'Bench-only nominal axial insertion; not press fit, tools, hands or retention before final cap.',
              'stages': []}
    try:
        docs = {n: pilot.document(A, pilot.CAD/'modules'/(n+'.FCStd')) for n in tail_module.MODULES}
        names = ['UpperHousing34', 'BearingCapNut34_0', 'BearingCapNut34_1',
                 'BearingLower34', 'InnerSpacer34', 'OuterSpacer34', 'BearingUpper34',
                 'BearingCap34', 'BearingCapBolt34_0', 'BearingCapBolt34_1']
        shapes = {}
        for n in names:
            owner, source, xyz = mapping[n]
            shapes[n] = instance(docs[owner], source, xyz)
            shapes[n].check(True); assert shapes[n].isValid()
        lid_path = OUT/'TailBearingLidService.FCStd'
        lid_doc = pilot.document(A, lid_path)
        shapes['BearingCap34'] = pilot.global_shape(lid_doc.getObject('BearingCap34'))
        shapes['BearingCap34'].check(True)
        report['lid_sha256'] = pilot.sha(lid_path)
        def overlap(a, b):
            return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
        fixed = {'UpperHousing34': shapes['UpperHousing34']}
        groups = [['BearingLower34'], ['InnerSpacer34'], ['OuterSpacer34'], ['BearingUpper34'],
                  ['BearingCap34'], ['BearingCapBolt34_0', 'BearingCapBolt34_1'],
                  ['BearingCapNut34_0', 'BearingCapNut34_1']]
        for names in groups:
            rows = []
            heights = range(-24, 1, 2) if names[0].startswith('BearingCapNut') else range(24, -1, -2)
            for height in heights:
                hits = []
                for n in names:
                    s = shapes[n].copy(); s.translate(A.Vector(0, 0, height))
                    for m, t in fixed.items():
                        if (v := overlap(s, t)) > .001: hits.append({'moving': n, 'fixed': m, 'mm3': v})
                rows.append({'height_mm': height, 'intersections': hits})
            report['stages'].append({'moving': names, 'samples': rows,
                                    'clear': all(not r['intersections'] for r in rows)})
            print(names, report['stages'][-1]['clear'], [r for r in rows if r['intersections']], flush=True)
            fixed.update({n: shapes[n] for n in names})
        # Positive control: off-centre bearing must clip the housing at its seat.
        control = shapes['BearingLower34'].copy(); control.translate(A.Vector(1, 0, 0))
        report['misaligned_bearing_control_mm3'] = overlap(control, shapes['UpperHousing34'])
        assert report['misaligned_bearing_control_mm3'] > 1
        report['all_sampled_stages_clear'] = all(r['clear'] for r in report['stages'])
        report['nut_counterhold_envelopes'] = []
        for i in range(2):
            name = f'BearingCapNut34_{i}'
            bb = shapes[name].BoundBox
            probe = Part.makeCylinder(3, 60, A.Vector(bb.Center.x, bb.Center.y, bb.ZMax-60))
            ignored = [name, f'BearingCapBolt34_{i}']
            hits = [{'part': n, 'mm3': v} for n, s in fixed.items()
                    if n not in ignored and (v := overlap(probe, s)) > .001]
            report['nut_counterhold_envelopes'].append({'diameter_mm': 6, 'intersections': hits,
                'ignored_intended_fasteners': ignored, 'socket_tip_fit_proven': False})
        report['counterhold_envelopes_clear'] = all(not r['intersections'] for r in report['nut_counterhold_envelopes'])
        report['components'] = {n: {'bbox_mm': [s.BoundBox.XMin, s.BoundBox.YMin, s.BoundBox.ZMin,
                                s.BoundBox.XMax, s.BoundBox.YMax, s.BoundBox.ZMax], 'volume_mm3': s.Volume}
                                for n, s in shapes.items()}
    finally:
        for name in list(A.listDocuments()): A.closeDocument(name)
    assert all(pilot.sha(pilot.ROOT/p) == h for p, h in hashes.items())
    assert pilot.sha(lid_path) == report['lid_sha256']
    (OUT/'bearing-preassembly.json').write_text(json.dumps(report, indent=2), encoding='utf-8', newline='\n')
    print('BENCH STAGES CLEAR:', report['all_sampled_stages_clear'], flush=True)


if __name__ == '__main__': main()
