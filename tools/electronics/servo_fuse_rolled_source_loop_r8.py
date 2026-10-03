"""FR feed between FL holder row and fuse bank, with raised source lap.

R7's down-tilted factory cable entered FR cages and its145mm north loop
entered the actual bank atY>=89. Keep the complete factory/source loop but
tilt factory UP8.2mm, lift the source east16/up18 before crossing FL cages,
and turn west atY~79/Z131.5, above FL but below the bank's Yspan.
Retained cover may require native local passages; no exterior protection,
grip, stock, physical length or assembly acceptance is inferred here.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r7.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r7'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r8'")
replace("normal=north*math.cos(tilt)-Z*math.sin(tilt)","normal=north*math.cos(tilt)+Z*math.sin(tilt)")
replace("joint_z=117.8","joint_z=134.2")
replace("            # AtY30.5 the cable is above118mm, before entering FL_G's Xspan.\n            e=Route([-24,11,113.5]);e.shift(north,V(6,0,12.5),25.2)\n            e.shift(north,Z*19,25.2)\n            e.arc(north,-X,25.2);e.line([-88.3,e.p.y,145])\n            e.arc(-X,south,25.2);assert abs(e.p.x+113.5)<1e-6\n            e.shift(south,-Z*(145-joint_z),25.2)",
        """            # At the FL_G edge the wire is already above118mm; avoid XB22.
            e=Route([-24,11,113.5]);e.shift(north,V(16,0,18),25.2)
            e.arc(north,-X,25.2);assert e.p.y+2.1<89
            e.line([-88.3,e.p.y,131.5])
            e.arc(-X,south,25.2);assert abs(e.p.x+113.5)<1e-6
            e.shift(south,Z*(joint_z-131.5),25.2)""")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r6.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r6.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r7.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
