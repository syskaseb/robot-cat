"""Whole FL lower corridor above the witnessed unchanged source bridge.

R1 has only two required Deck passages and one source-bridge contact.
Raise the complete lower route plane, not a succession of endpoint nudges.
Do not cut the P0 bridge or move any already selected wire.
"""
from pathlib import Path
import runpy

parent = Path(__file__).with_name('w5_fl_return_r52_r1.py')
code = runpy.run_path(str(parent), run_name='route_definition')['code']
code = code.replace('w5-fl-return-r52-r1', 'w5-fl-return-r52-r2')
assert 'height, lane = 75.5, 78' in code
code = code.replace('height, lane = 75.5, 78', 'height, lane = 85, 78')
code = code.replace('Independent FL_G return on complete lower corridor;',
                    'R1 source departure crossed the source bridge at Z72.6..82.45. Complete lower plane nowZ85; unchanged P0 bridge, existing wires and blocks;')
code = code.replace('source_sha256={',
                    'source_sha256={FL_PARENT_PATH.relative_to(ROOT).as_posix(): sha(FL_PARENT_PATH),', 1)
exec(compile(code, str(Path(__file__).resolve()), 'exec'), dict(
    __file__=str(Path(__file__).resolve()), __name__=__name__,
    FL_PARENT_PATH=parent, ROUTE_TEMPLATE_PATH=parent.with_name('w5_front_return_r52_r6.py'),
    BASE_SCRIPT_PATH=parent.with_name('w5_front_return_r52_r1.py'),
    ROUTE_PARENT_PATH=parent.with_name('w5_front_return_r52_r4.py'),
    ROUTE_PREVIOUS_PATH=parent.with_name('w5_front_return_r52_r5.py')))
