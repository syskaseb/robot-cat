"""One FR corridor around, not through, the actual Pi carrier.

Carrier isX[-94,136]/Y[-76,72]/Z[140,152.55]. R9 crossed itsfloor.
FactoryR20 bends south/up (normalY=-.5,Z=sqrt(.75)), leaves the carrier
Yspan before reaching140mm and finishes above the inner bank rail atY-92.
Source west/up S24 stays below the carrier (137.5+2.1<140), turns before
bankY89, then rises outside the west edge and returns to the same lap.
Factory10mm trim/8mm stripping and straight16/17mm ends are unchanged.
Native casing passages/protection and two-sided grips remain OPEN.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r9.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r9'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r10'")
replace("            tilt=math.asin(26/40)\n            normal=north*math.cos(tilt)+Z*math.sin(tilt)",
        "            normal=south*.5+Z*math.sqrt(.75)")
replace("joint_z=152","joint_z=cz+40*math.sqrt(.75)")
replace("e=Route([-24,11,113.5]);e.shift(north,V(12,0,32),25.2)",
        "e=Route([-24,11,113.5]);e.shift(north,V(-16,0,24),25.2)")
replace("e.line([-85.5,e.p.y,145.5])","e.line([-85.5,e.p.y,137.5])")
replace("e.shift(south,Z*(joint_z-145.5),25.2)","e.shift(south,Z*(joint_z-137.5),25.2)")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r8.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r8.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r9.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
