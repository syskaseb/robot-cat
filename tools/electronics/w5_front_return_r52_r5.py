"""Lower corridor outside W038 and west of the tail/PWM terminal shelf.

R4 ruled out its east FR_G mouth and X-100 bend. Keep the south-facing
block and the complete lower architecture, change those two witnessed
obstacles together. No selected bank, head or Pi route is relocated.
"""
from pathlib import Path
import runpy

parent = Path(__file__).with_name('w5_front_return_r52_r4.py')
code = runpy.run_path(str(parent), run_name='route_definition')['code']
code = code.replace('w5-front-return-r52-r4', 'w5-front-return-r52-r5')
code = code.replace('b = [-19.5, -49.5, 113.5]', 'b = [-46.5, -49.5, 113.5]')
code = code.replace('A.Vector(-100, 78, height)', 'A.Vector(-108, 78, height)')
code = code.replace('A.Vector(-100, -116, height)', 'A.Vector(-108, -116, height)')
code = code.replace('R3 lower corridor only hit Deck and F_PI at north FR_G mouths. Rotate FR_G 180deg toward south, preserving common net/body/stock; one complete fixed below-Deck path, exact passages and restraints required',
    'R4 lower route hit W038 at west corner and PWM/tail shelf at east FR_G mouth. One west-mouth/south-facing FR_G route with X-108 trunk, preserving existing nets and all selected head/bank/Pi routes')
code = code.replace('FR_G 180deg: south mouths Y-49.5, project labels west-to-east [.5,.4,.3,.2,.1], feed .1 X-19.5. Electrical graph unchanged; three moving G ends open, no selected wire removed',
    'FR_G rotated180deg: south mouths Y-49.5, project labels west-to-east [.1,.2,.3,.4,.5], feed .1 X-46.5. Same body/seat/net; project labels not catalogue cavity numbers; three moving G routes open')
needle = 'source_sha256={BASE_SCRIPT_PATH.relative_to(ROOT).as_posix(): sha(BASE_SCRIPT_PATH),'
assert needle in code
code = code.replace(needle, 'source_sha256={ROUTE_PARENT_PATH.relative_to(ROOT).as_posix(): sha(ROUTE_PARENT_PATH), BASE_SCRIPT_PATH.relative_to(ROOT).as_posix(): sha(BASE_SCRIPT_PATH),')
exec(compile(code, str(Path(__file__).resolve()), 'exec'), dict(
    __file__=str(Path(__file__).resolve()), __name__=__name__,
    BASE_SCRIPT_PATH=parent.with_name('w5_front_return_r52_r1.py'), ROUTE_PARENT_PATH=parent))
