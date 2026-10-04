"""Same whole passage, recompute only touched native objects.

R1 was stopped after >5 CPU minutes without a completed result. Its saved
draft remains; no geometry rejection or CAD PASS inferred. Do not force
all source-link objects during each parameter change.
"""
from pathlib import Path

parent = Path(__file__).with_name('w5_g1_passage_native_r1.py')
code = parent.read_text(encoding='utf-8').replace('w5-g1-passage-native-r1', 'w5-g1-passage-native-r2')
code = code.replace('d.recompute(None, True, True)', 'd.recompute()')
code = code.replace('reopened.recompute(None, True, True)', 'reopened.recompute()')
code = code.replace('    shape = final.Shape.copy()', "    print('G1_NEW_CUT_RECOMPUTED', flush=True)\n    shape = final.Shape.copy()")
code = code.replace('    nominal = shape.Volume', "    print('G1_NEW_CUT_BOP_CHECKED', flush=True)\n    nominal = shape.Volume")
code = code.replace('    # Check only the changed cable departure', "    print('G1_PARAMETER_RESTORED', flush=True)\n    d.save()\n    # Check only the changed cable departure")
# Subtraction cannot create a contact on an unchanged previously clear route.
# Check the one witnessed changed departure, not all distant same-Deck pairs.
code = code.replace('    intersections = [s.common(shape).Volume for s in pieces]',
                    '    intersections = [pieces[r["segment"]].common(shape).Volume for r in deck_hits]')
code = code.replace('    original = link.Shape.copy()', "    print('G1_CHANGED_DEPARTURE_CLEAR', flush=True)\n    original = link.Shape.copy()")
code = code.replace('    for name in list(A.listDocuments()): A.closeDocument(name)\n    with tempfile',
                    "    print('G1_CLOSED_EXPORT_COMPLETE', flush=True)\n    for name in list(A.listDocuments()): A.closeDocument(name)\n    with tempfile")
code = code.replace('    pins = {q.relative_to(ROOT).as_posix(): sha(q) for q in [source, fit, routefile, Path(__file__)] + external}',
                    '    pins = {q.relative_to(ROOT).as_posix(): sha(q) for q in [source, fit, routefile, Path(__file__), BASE_SCRIPT_PATH] + external}')
exec(compile(code, str(Path(__file__).resolve()), 'exec'),
     dict(__file__=str(Path(__file__).resolve()), __name__=__name__, BASE_SCRIPT_PATH=parent))
