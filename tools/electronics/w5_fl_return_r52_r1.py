"""Independent complete W025 lower route; existing FL_G orientation retained.

No further FR_G mouth search. Reuse sourced R21 downwards departure and
installed R52 cache. Both endpoints belong to the unchanged P0 G net.
This builder remains unselected until routes, current Deck passages and
restraints have all been finished.
"""
from pathlib import Path
import runpy

template = Path(__file__).with_name('w5_front_return_r52_r6.py')
code = runpy.run_path(str(template), run_name='route_definition')['code']
code = code.replace('w5-front-return-r52-r6', 'w5-fl-return-r52-r1')
code = code.replace('W036', 'W025')
code = code.replace('G1.4', 'G1.3').replace('FR_G.1', 'FL_G.1')
code = code.replace('a, b = [73.5, 11, 113.5]', 'a, b = [66, 11, 113.5]')
code = code.replace('b = [-33, -49.5, 113.5]', 'b = [-46.5, 30.5, 113.5]')
before = 'middle = rounded([pa, A.Vector(pa.x, 78, height), A.Vector(-108, 78, height), A.Vector(-108, -116, height), A.Vector(pb.x, -116, height), pb], 21)'
assert before in code
code = code.replace(before, 'middle = rounded([pa, A.Vector(pa.x, 78, height), A.Vector(-108, 78, height), A.Vector(-108, -35, height), A.Vector(pb.x, -35, height), pb], 21)')
code = code.replace('R5 west trunk clear, west mouth blocked by XB13/XS13/W040. R4 east mouth blocked by PWM shelf. Use south middle mouth between witnessed obstacles; all selected wires and body positions retained',
    'Independent FL_G return on complete lower corridor; no repeated FR_G trials. G1.3 exits+Y and FL_G.1 exits-Y in existing block positions; fixed TKD4mm2 R21, all selected head/Pi/source/bank wires retained')
code = code.replace('FR_G rotated180deg: south mouths Y-49.5, project labels west-to-east [.5,.4,.1,.2,.3], feed .1 X-33. Same body/seat/net; project labels not catalogue cavity numbers; three moving G routes open',
    'No block rotation or electrical relabelling. G1.3 X66,Y11 and FL_G.1 X-46.5,Y30.5 are existing project datums, not measured catalogue cavities')
code = code.replace('source_sha256={', 'source_sha256={ROUTE_TEMPLATE_PATH.relative_to(ROOT).as_posix(): sha(ROUTE_TEMPLATE_PATH),', 1)
needle = '    owners, receipt = cached()'
assert needle in code
code = code.replace(needle, needle + '''
    g1receipt = ROOT/'hardware/electronics/full-cat/w5-g1-saved-export-r1/checks.json'
    g1deck = ROOT/'hardware/cad/studies/w5-g1-passage-native-r2/Deck_WORLD.brep'
    g1proof = json.loads(g1receipt.read_text(encoding='utf-8'))
    assert g1proof['closed_STL'] and g1proof['relocated_reopen']
    assert sha(g1deck) == g1proof['files'][g1deck.relative_to(ROOT).as_posix()]
    owners['CandidateDeck'] = Part.read(str(g1deck))
''')
code = code.replace('source_sha256={', 'source_sha256={g1receipt.relative_to(ROOT).as_posix(): sha(g1receipt), g1deck.relative_to(ROOT).as_posix(): sha(g1deck),', 1)
exec(compile(code, str(Path(__file__).resolve()), 'exec'), dict(
    __file__=str(Path(__file__).resolve()), __name__=__name__, ROUTE_TEMPLATE_PATH=template,
    BASE_SCRIPT_PATH=template.with_name('w5_front_return_r52_r1.py'),
    ROUTE_PARENT_PATH=template.with_name('w5_front_return_r52_r4.py'),
    ROUTE_PREVIOUS_PATH=template.with_name('w5_front_return_r52_r5.py')))
