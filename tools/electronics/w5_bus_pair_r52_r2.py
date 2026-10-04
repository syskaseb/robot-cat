"""Whole upper-level BUS pair, replacing the rejected under-Deck routes.

Keep the G2/W061 restraint in the collision census: it must be redesigned
jointly, never silently omitted. No supplier plug dimensions are inferred.
"""
from pathlib import Path

SOURCE = Path(__file__).with_name('w5_bus_pair_r52_r1.py')
code = SOURCE.read_text(encoding='utf-8')
code = code.replace("w5-bus-pair-r52-r1", "w5-bus-pair-r52-r2")
first = code.index('        up,end=curves.elevated_start')
last = code.index('        assert route.isValid()', first)
code = code[:first] + '''        # Entire path above cooling/Deck; no lower endpoint transition.
        end=A.Vector(*dst)
        lane=-12 if wire=='W002' else 55
        route=rounded([src,A.Vector(src.x,src.y,113.5),
                       A.Vector(src.x,lane,113.5),
                       A.Vector(end.x,lane,113.5),end],10)
''' + code[last:]
code = code.replace("ROOT/'tools/electronics/body_ground_routes_r1.py',", "SOURCE, ROOT/'tools/electronics/body_ground_routes_r1.py',")
exec(compile(code, str(SOURCE), 'exec'), globals())
