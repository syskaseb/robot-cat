"""One wider RL post with an open passage for the retained XA05 wire.

Keep the measured north-of-slot land and both source seats/routes. Widen
the post westward to6mm, then cut the actual XA05 contact envelope plus
clearance from its east side, leaving a3.3mm load-carrying spine. No wire
reroute, additional print, SKU or independent support variant is selected.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rl_source_station_native_r3.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rl-source-station-native-r3'","servo-fuse-rl-source-station-native-r4'")
code=code.replace('fx=cx+.5;fy=', 'fx=cx-1.5;fy=')
code=code.replace('[fx,fy,108.8,fx+4,fy+4,109]', '[fx,fy,108.8,fx+6,fy+4,109]')
code=code.replace('[fx,fy,108.8,fx+4,fy+4,z]', '[fx,fy,108.8,fx+6,fy+4,z]')
code=code.replace('abs(actual-16)<1e-5','abs(actual-24)<1e-5')
code=code.replace('abs(area-16)<1e-5','abs(area-24)<1e-5')
needle='    for t in cuttools:prospective=prospective.cut(t)'
assert needle in code
code=code.replace(needle, '    cuttools.append(box([92.4,33.9,111.8,96.8,38.4,115.3]))\n'+needle)
needle='        tools=[]\n'
assert needle in code
code=code.replace(needle,"        tools=[nativebox(d,'RLSourceXA05OpenPassage',[92.4,33.9,111.8,96.8,38.4,115.3])]\n")
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rl_source_station_native_r3.py']=sha(ROOT/'tools/electronics/servo_fuse_rl_source_station_native_r3.py')\n    pins['hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r3/support-preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r3/support-preflight.json')")
code=code.replace("recipe=['Removed unpowered Deck:","recipe=['Lay unchanged XA05 through the open east/south passage before source/body wiring;24mm2 foot and nominal3.3mm spine, prototype pull/creep in phase2.', 'Removed unpowered Deck:")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
