"""Whole BUS pair in the cooling/Deck interspace; unchanged tie contacts count.

R1 intersects cooling; R2 intersects installed distribution/input loops.
103.5mm is above the saved99mm cooling top and below109mm distribution
base. Through-Deck entries and the G2 restraint must subsequently be native.
"""
from pathlib import Path
SOURCE = Path(__file__).with_name('w5_bus_pair_r52_r1.py')
code = SOURCE.read_text(encoding='utf-8')
code = code.replace('w5-bus-pair-r52-r1', 'w5-bus-pair-r52-r3')
code = code.replace('95.5', '103.5')
code = code.replace("ROOT/'tools/electronics/body_ground_routes_r1.py',", "SOURCE, ROOT/'tools/electronics/body_ground_routes_r1.py',")
exec(compile(code, str(SOURCE), 'exec'), globals())
