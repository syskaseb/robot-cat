"""Keep R10's clear factory corridor; source approaches on W041's east.

R10 witnesses place W041 atX[-32.6,-22.7]/Y22..36/Z112..125,
and the FL tie head atX[-49.3,-44.5]/Y66.75..71.25/Z135.2..138.7.
Replace the source's west16/up24 S-offset with east6/up24: it rises away
from W041, stays below the140mm carrier and turns west only north of FL.
No factory dimensions/reserves, body mounts or other feeds are changed.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r10.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r10'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r11'")
replace("e=Route([-24,11,113.5]);e.shift(north,V(-16,0,24),25.2)",
        "e=Route([-24,11,113.5]);e.shift(north,V(6,0,24),25.2)")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r9.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r9.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r10.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
