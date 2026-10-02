"""Bound the solver fan; construct only the previously untested final pose.

R1's upper search bracket15mm exceeded a route precondition. Preserve that
interruption and midpoint files, without counting unpersisted midpoint checks.
"""
from pathlib import Path
parent = Path(__file__).with_name('servo_fuse_bank_connected_release_r1.py')
code = parent.read_text(encoding='utf-8')
code = code.replace("OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r1'",
                    "OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r2'")
code = code.replace('for fraction in (0.5, 1.0):', 'for fraction in (1.0,):')
code = code.replace('lo, hi = -5.0, 15.0', 'lo, hi = -5.0, 5.0')
code = code.replace('sampled_fractions=[0.5,1.0]', 'sampled_fractions=[1.0]')
code = code.replace('delay = 13 - 4 * int(pose[\'holder\'] and next', 'delay = 13 - 4 * int(next')
code = code.replace("hashes[source.relative_to(ROOT).as_posix()] = sha(source)",
                    "hashes[source.relative_to(ROOT).as_posix()] = sha(source)\n    hashes['tools/electronics/servo_fuse_bank_connected_release_r1.py'] = sha(ROOT/'tools/electronics/servo_fuse_bank_connected_release_r1.py')")
exec(compile(code, str(Path(__file__).resolve()), 'exec'))
