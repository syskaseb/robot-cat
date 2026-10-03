"""Complete front-port pair: FL R20 bend rises2mm above the head feeds.

R1's same-net cage permutation cleared FR but exposed three FL contacts.
Raise FL during its first quarter bend, then return to113.5mm at the same
cage with an R20 S-bend. No radius/reserve reduction or holder relocation.
Both front conductors are rechecked, unrelated rejected feeds remain open.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_front_source_ports_r1.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r1'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2'")
replace("f=Route([right,cy,cz]);f.arc(X,-Y,20)\n            f.shift(-Y,V(.5,0,-12.5),20);assert f.p.y>=11",
        """f=Route([right,cy,cz]);normal=-Y*math.sqrt(1-.1**2)+Z*.1
            f.arc(X,normal,20)
            f.arc(normal,-Y*.1-Z*math.sqrt(1-.1**2),20,math.asin(.1))
            f.shift(-Y,V(.5,0,113.5-f.p.z),20);assert f.p.y>=11""")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py');pin(ROOT/'tools/electronics/servo_fuse_front_source_ports_r1.py');pin(ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r1/checks.json')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
