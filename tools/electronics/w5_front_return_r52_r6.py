"""South middle mouth between the witnessed head and PWM/ATO feed routes.

R5 fixed the west-corner conflict, but its west mouth crosses XB13/XS13 and
W040. R4 east mouth crossed the PWM shelf. Keep the complete lower route;
use the middle mouth in the same rotated FR_G block, with all three
moving-servo G legs still open. No displacement of a qualified wire.
"""
from pathlib import Path
import runpy

parent = Path(__file__).with_name('w5_front_return_r52_r5.py')
code = runpy.run_path(str(parent), run_name='route_definition')['code']
code = code.replace('w5-front-return-r52-r5', 'w5-front-return-r52-r6')
code = code.replace('b = [-46.5, -49.5, 113.5]', 'b = [-33, -49.5, 113.5]')
code = code.replace('R4 lower route hit W038 at west corner and PWM/tail shelf at east FR_G mouth. One west-mouth/south-facing FR_G route with X-108 trunk, preserving existing nets and all selected head/bank/Pi routes',
    'R5 west trunk clear, west mouth blocked by XB13/XS13/W040. R4 east mouth blocked by PWM shelf. Use south middle mouth between witnessed obstacles; all selected wires and body positions retained')
code = code.replace('FR_G rotated180deg: south mouths Y-49.5, project labels west-to-east [.1,.2,.3,.4,.5], feed .1 X-46.5. Same body/seat/net; project labels not catalogue cavity numbers; three moving G routes open',
    'FR_G rotated180deg: south mouths Y-49.5, project labels west-to-east [.5,.4,.1,.2,.3], feed .1 X-33. Same body/seat/net; project labels not catalogue cavity numbers; three moving G routes open')
needle = 'source_sha256={ROUTE_PARENT_PATH.relative_to(ROOT).as_posix(): sha(ROUTE_PARENT_PATH),'
assert needle in code
code = code.replace(needle, 'source_sha256={ROUTE_PREVIOUS_PATH.relative_to(ROOT).as_posix(): sha(ROUTE_PREVIOUS_PATH), ROUTE_PARENT_PATH.relative_to(ROOT).as_posix(): sha(ROUTE_PARENT_PATH),')
exec(compile(code, str(Path(__file__).resolve()), 'exec'), dict(
    __file__=str(Path(__file__).resolve()), __name__=__name__,
    BASE_SCRIPT_PATH=parent.with_name('w5_front_return_r52_r1.py'),
    ROUTE_PARENT_PATH=parent.with_name('w5_front_return_r52_r4.py'), ROUTE_PREVIOUS_PATH=parent))
