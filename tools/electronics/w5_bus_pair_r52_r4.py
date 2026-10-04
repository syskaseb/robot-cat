"""BUS with separate D passage and continuous G channel above source bridge.

G107/Y61 clears the fixed105mm bridge and the RL band atY53..56.5.
Native Deck channel and a snug existing-hole W061 band remain required.
This is one complete pair, not an endpoint-position search.
"""
from pathlib import Path
SOURCE = Path(__file__).with_name('w5_bus_pair_r52_r1.py')
code = SOURCE.read_text(encoding='utf-8')
code = code.replace('w5-bus-pair-r52-r1', 'w5-bus-pair-r52-r4')
code = code.replace("        up,end=curves.elevated_start", "        plane=103.5 if wire=='W002' else 107\n        up,end=curves.elevated_start")
code = code.replace('95.5', 'plane')
code = code.replace("lane=-12 if wire=='W002' else 55", "lane=-12 if wire=='W002' else 61")
code = code.replace("ROOT/'tools/electronics/body_ground_routes_r1.py',", "SOURCE, ROOT/'tools/electronics/body_ground_routes_r1.py',")
exec(compile(code, str(SOURCE), 'exec'), globals())
