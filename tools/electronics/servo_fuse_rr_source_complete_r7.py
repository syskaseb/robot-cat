"""Finish RR against the unchanged inherited RL, not rejected RL R5.

Lift RR's full low source plane0.6mm to clear W078 by0.5mm nominal; retain
factory100mm stock/strip/reserve and4mm grip lands. RL is inherited by SHA
with its known failures, not regenerated or falsely credited as complete.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_source_pair_r6.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rear-source-pair-r6'","servo-fuse-rr-source-complete-r7'")
code=code.replace("affected=('W044','W052')", "affected=('W052',)")
code=code.replace("[('RL','W044',51.5,72,130,-6.8),('RR','W052',63.5,-86,121.5,6.8)]", "[('RR','W052',63.5,-86,121.5,6.8)]")
code=code.replace('f.shift(X,V(0,-4,12),20)', 'f.shift(X,V(0,-4,12.6),20)')
code=code.replace("    pin(parent);pin(src);", "    pin(parent);pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r6/checks.json');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
