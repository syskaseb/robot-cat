"""FR source: low approach, compound rising west bend, high west return.

R12 low plane cleared XA02 but crossed FL output feeds and XB22_0. Move
the early offset to18mm east (outside XB22_0's actual X[-12.1,-10]),
retain the low13mm rise below XA02, then rise11mm during the west bend.
Flatten the tangent north of the carrier'sY72 edge before the west return.
The lap/factory, minimum radii and10mm reserve are unchanged; cover/grips
are still not qualified merely by a route result.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r12.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r12'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r13'")
replace("e.shift(north,V(14,0,13),25.2)","e.shift(north,V(18,0,13),25.2)")
replace("e.arc(north,-X,25.2);assert e.p.y+2.1<89\n            e.line([-85.5,e.p.y,126.5])",
        """alpha=math.asin(11/25.2)
            rising=-X*math.cos(alpha)+Z*math.sin(alpha)
            e.arc(north,rising,25.2);assert e.p.y+2.1<89
            e.arc(rising,-X*math.sin(alpha)-Z*math.cos(alpha),25.2,alpha)
            assert e.p.y-2.1>72
            e.line([-85.5,e.p.y,e.p.z])""")
replace("e.shift(south,Z*(joint_z-126.5),25.2)","e.shift(south,Z*(joint_z-e.p.z),25.2)")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r12.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
