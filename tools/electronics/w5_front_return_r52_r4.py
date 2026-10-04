"""Whole under-Deck return with FR_G turned toward the free south side.

R3 proved the lower corridor clear except Deck and the blocked north FR_G
mouth. Rotate only the same FR_G block 180deg in its rectangular seat;
all four connected G labels/nets remain, three leg G routes are still open.
Keep the G1 mouth and selected source/head/servo-bank construction unchanged.
"""
from pathlib import Path
import sys

parent = Path(__file__).with_name('w5_front_return_r52_r1.py')
code = parent.read_text(encoding='utf-8')
code = code.replace('w5-front-return-r52-r3', 'w5-front-return-r52-r4')
code = code.replace('b = [-33, -30.5, 113.5]', 'b = [-19.5, -49.5, 113.5]')
code = code.replace('def departure(point):', 'def departure(point, direction):')
code = code.replace('geometry.elevated_start(point, 1,', 'geometry.elevated_start(point, direction,')
code = code.replace('departure(a)', 'departure(a, 1)').replace('departure(b)', 'departure(b, -1)')
before = 'middle = rounded([pa, A.Vector(pa.x, lane, height), A.Vector(pb.x, lane, height), pb], 21)'
assert before in code
code = code.replace(before, 'middle = rounded([pa, A.Vector(pa.x, 78, height), A.Vector(-100, 78, height), A.Vector(-100, -116, height), A.Vector(pb.x, -116, height), pb], 21)')
code = code.replace('Both upper corridors blocked by selected MTA/head/source wires. One whole below-Deck corridor avoids those fixed owners; exact Deck passages must be constructed, not waived',
    'R3 lower corridor only hit Deck and F_PI at north FR_G mouths. Rotate FR_G 180deg toward south, preserving common net/body/stock; one complete fixed below-Deck path, exact passages and restraints required')
code = code.replace('FR_G project .1/feed uses middle mouth X-33; swap physical labels .1/.3 only; proposed west-to-east [.3,.2,.1,.4,.5]. Three moving G ends are still open and uncut',
    'FR_G 180deg: south mouths Y-49.5, project labels west-to-east [.5,.4,.3,.2,.1], feed .1 X-19.5. Electrical graph unchanged; three moving G ends open, no selected wire removed')
needle = 'source_sha256={"hardware/electronics/full-cat/w5-installed-r52/owners.json"'
assert needle in code
code = code.replace(needle, 'source_sha256={BASE_SCRIPT_PATH.relative_to(ROOT).as_posix(): sha(BASE_SCRIPT_PATH), "tools/electronics/body_ground_routes_r1.py": sha(ROOT / "tools/electronics/body_ground_routes_r1.py"), "tools/electronics/xb11_upstream_route.py": sha(ROOT / "tools/electronics/xb11_upstream_route.py"), "hardware/electronics/full-cat/w5-installed-r52/owners.json"')
if '--under-deck' not in sys.argv:
    sys.argv.append('--under-deck')
exec(compile(code, str(Path(__file__).resolve()), 'exec'),
     dict(__file__=str(Path(__file__).resolve()), __name__=__name__, BASE_SCRIPT_PATH=parent))
