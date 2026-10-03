"""Whole RL post fits the real gap between RL_G and D_RL.

RL_G ends atX90 and D_RL begins atX96 in the retained models. A5.5mm
post occupies90.2..95.7, on22mm2 of Deck; the XA05 passage leaves2.4mm
spine. Stop the post at the3mm seat floor to avoid a thin upper side sliver.
Both source routes, source seats, all WAGO and the accepted RR stay fixed.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rl_source_station_native_r4.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rl-source-station-native-r4'","servo-fuse-rl-source-station-native-r5'")
assert 'fx=cx-1.5;fy=' in code
code=code.replace('fx=cx-1.5;fy=','fx=90.2;fy=')
code=code.replace('[fx,fy,108.8,fx+6,fy+4,109]', '[fx,fy,108.8,fx+5.5,fy+4,109]')
code=code.replace('[fx,fy,108.8,fx+6,fy+4,z]', '[fx,fy,108.8,fx+5.5,fy+4,z-5]')
code=code.replace('abs(actual-24)<1e-5','abs(actual-22)<1e-5')
code=code.replace('abs(area-24)<1e-5','abs(area-22)<1e-5')
code=code.replace('[92.4,33.9,111.8,96.8,38.4,115.3]','[92.6,33.9,111.8,96.8,38.4,115.3]')
code=code.replace('24mm2 foot and nominal3.3mm spine','22mm2 foot and nominal2.4mm spine')
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rl_source_station_native_r4.py']=sha(ROOT/'tools/electronics/servo_fuse_rl_source_station_native_r4.py')\n    pins['hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r4/support-preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r4/support-preflight.json')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
