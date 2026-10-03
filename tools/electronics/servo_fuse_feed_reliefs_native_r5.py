"""Keep the lip rib clear of the retained front-left cover bracket.

R4 found4mm3 of bracket interference. Move only the rib5mm towards+X;
preserve slots, full-feed geometry, bank clearance and failed-fit evidence.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_feed_reliefs_native_r4.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r4'", "OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r5'")
replace("CAD = ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r4'", "CAD = ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r5'")
replace("rib.Placement.Base=A.Vector(-85,96.5,118)", "rib.Placement.Base=A.Vector(-80,96.5,118)")
replace("    pins = {'tools/electronics/servo_fuse_feed_reliefs_native_r3.py'", """    pins = {'tools/electronics/servo_fuse_feed_reliefs_native_r4.py':sha(ROOT/'tools/electronics/servo_fuse_feed_reliefs_native_r4.py'),
            'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r4/bridge-fit.json':sha(ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r4/bridge-fit.json'),
            'tools/electronics/servo_fuse_feed_reliefs_native_r3.py'""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
