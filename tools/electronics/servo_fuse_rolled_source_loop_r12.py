"""One low east-offset source corridor; preserve R10 factory and lap.

The bounded dx-only fit had no solution: W041 blocks dx<=5 while XA02
blocks dx>=4 at the old137.5mm routing plane. This corridor rises only13mm
and offsets14mm east, below XA02's actual129.411mm minimum; the north
straight clears FL's75mm body before turning west. It rises to the lap
only outside the west carrier edge. Radii, strips and reserves unchanged.
Cover passages/protection and two-sided native grips remain OPEN.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r11.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r11'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r12'")
replace("e=Route([-24,11,113.5]);e.shift(north,V(6,0,24),25.2)",
        "e=Route([-24,11,113.5]);e.shift(north,V(14,0,13),25.2)\n            e.line([e.p.x,e.p.y+4,e.p.z])")
replace("e.line([-85.5,e.p.y,137.5])","e.line([-85.5,e.p.y,126.5])")
replace("e.shift(south,Z*(joint_z-137.5),25.2)","e.shift(south,Z*(joint_z-126.5),25.2)")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r10.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r10.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py');pin(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-corridor-solver-r1/checks.json')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
