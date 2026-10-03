"""Preserve clear R5 factory joints; stop HELU descent BEFORE TE exits.

R6/R7 lowered cages into existing input wires. Use the clear R5 factory
paths and reduce the extension's descent, turning west earlier in Y.
Terminal contacts are actual TE solids, not permission to remove wires.
Includes all three accepted FR output strap envelopes. Native casing/grips
remain open until constructed, all recorded intersections remain failures.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r5.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r5_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace("servo-fuse-output-returns-complete-r5'", "servo-fuse-output-returns-complete-r8'")
code=code.replace("    native=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r5.py')\n    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r6.py')\n    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r7.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r7/checks.json')\n    native=ROOT/",1)
code=code.replace("('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep','BodyTie'),", "('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep','BodyTie'),\n        ('servo-fuse-fr-output-station-native-r3','*Tie*_DESIGN.brep','FRNewTie'),")
assert code.count("('RL','W045',16.5,72,130,8,-51,82,130,123.5)")==1
assert code.count("('RR','W053',28.5,-86,121.5,14,-49,-91,121.5,115)")==1
code=code.replace("('RL','W045',16.5,72,130,8,-51,82,130,123.5)","('RL','W045',16.5,72,130,6,-51,82,130,123.5)")
code=code.replace("('RR','W053',28.5,-86,121.5,14,-49,-91,121.5,115)","('RR','W053',28.5,-86,121.5,7,-49,-91,121.5,115)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
