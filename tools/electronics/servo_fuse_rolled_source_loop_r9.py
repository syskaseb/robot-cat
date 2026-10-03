"""FR feed rises above XS23/XA04 and crosses below the bank's Yspan.

R8 hits locate factory collisions atZ128..135 and source atZ128..135.
Tilt the factory half-turn UP26mm (R20) to clear that actual wiring,
with a152mm high lap and16mm/17mm straight factory/extension ends.
Restore the original10mm trim reserve: the factory total is below100mm.
Rise source12mm east/32mm up (R25.2), turn west before bankY89 and
return beside the casing. Extra housing passages/protection and native
two-sided insulation grips remain required, not an implied physicalPASS.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r8.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r8'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r9'")
replace("tilt=math.asin(8.2/40)","tilt=math.asin(26/40)")
replace("joint_z=134.2","joint_z=152")
replace("            f.shift(-X,south*(f.p.y+36),20)\n            f.line([-69.5,-36,joint_z])",
        "            joint_y=f.p.y\n            f.line([-60.5,joint_y,joint_z])")
replace("e=Route([-24,11,113.5]);e.shift(north,V(16,0,18),25.2)",
        "e=Route([-24,11,113.5]);e.shift(north,V(12,0,32),25.2)")
replace("e.line([-88.3,e.p.y,131.5])","e.line([-85.5,e.p.y,145.5])")
replace("e.arc(-X,south,25.2);assert abs(e.p.x+113.5)<1e-6",
        "e.arc(-X,south,25.2);assert abs(e.p.x+110.7)<1e-6")
replace("e.shift(south,Z*(joint_z-131.5),25.2)","e.shift(south,Z*(joint_z-145.5),25.2)")
replace("            assert e.p.y > -10.8\n            e.line([-113.5,-10.8,joint_z]);e.arc(south,X,25.2)\n            e.line([-77.5,-36,joint_z])",
        """            assert e.p.y > joint_y+25.2
            e.line([-110.7,joint_y+25.2,joint_z]);e.arc(south,X,25.2)
            e.line([-68.5,joint_y,joint_z])""")
replace("reserve=2 if name=='W042_factory' else 10","reserve=10")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r7.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r7.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r8.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
