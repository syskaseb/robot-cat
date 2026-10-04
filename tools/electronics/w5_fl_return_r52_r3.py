"""R21 source dogleg goes around, not through, the retained P0 bridge.

R1/R2 downward sources intersected the bridge (Xmax67,Zmax105). A smooth
6mm lateral source shift stays above it, then descends at X72. The complete
lower corridor follows Y106. No bridge cut, block move or selected-wire move.
"""
from pathlib import Path
import runpy

parent = Path(__file__).with_name('w5_fl_return_r52_r1.py')
code = runpy.run_path(str(parent), run_name='route_definition')['code']
code = code.replace('w5-fl-return-r52-r1', 'w5-fl-return-r52-r3')
code = code.replace('height, lane = 75.5, 78', 'height, lane = 75.5, 106')
code = code.replace('A.Vector(pa.x, 78, height)', 'A.Vector(pa.x, 106, height)')
code = code.replace('A.Vector(-108, 78, height)', 'A.Vector(-108, 106, height)')
needle = '    ea, pa = departure(a, 1)'
assert needle in code
code = code.replace(needle, '''    # Map the existing R21 two-arc S from its Y/Z plane to Y/X.
    source_edges, source_end = geometry.elevated_start([a[0], a[1], 0], 1, 6)
    def lateral(v):
        return A.Vector(a[0]+v.z, v.y, a[2])
    prefix = []
    for edge in source_edges:
        p, q = lateral(edge.valueAt(edge.FirstParameter)), lateral(edge.valueAt(edge.LastParameter))
        prefix.append(Part.Arc(p, lateral(edge.valueAt((edge.FirstParameter+edge.LastParameter)/2)), q).toShape()
                      if hasattr(edge.Curve, 'Radius') else Part.makeLine(p, q))
    shifted = lateral(source_end)
    ea, pa = departure(list(shifted), 1)
    ea = prefix+ea
''')
code = code.replace('    save(out / "intent.json", intent)', '''    intent.update(reason='Whole source R21 lateral S at Z113.5 shifts X66→72 above retained bridge, then descends east of Xmax67; full lower corridor Y106/Z75.5. No repeated height search or P0 cut',
                  source_lateral_offset_mm=6, source_bend_radius_mm=21,
                  bridge_original_geometry_preserved=True)
    save(out / "intent.json", intent)''')
code = code.replace('source_sha256={',
                    'source_sha256={FL_PARENT_PATH.relative_to(ROOT).as_posix(): sha(FL_PARENT_PATH),', 1)
exec(compile(code, str(Path(__file__).resolve()), 'exec'), dict(
    __file__=str(Path(__file__).resolve()), __name__=__name__,
    FL_PARENT_PATH=parent, ROUTE_TEMPLATE_PATH=parent.with_name('w5_front_return_r52_r6.py'),
    BASE_SCRIPT_PATH=parent.with_name('w5_front_return_r52_r1.py'),
    ROUTE_PARENT_PATH=parent.with_name('w5_front_return_r52_r4.py'),
    ROUTE_PREVIOUS_PATH=parent.with_name('w5_front_return_r52_r5.py')))
