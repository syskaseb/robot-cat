"""One external RR post clears both closed G_AUX and D_RR bodies.

The full source and open insulation seats are unchanged. A single native
cross-arm from the east Deck strip carries both seats above the WAGO cases;
the sleeve passage continues through the arm. Exact small-stock preflight
must pass before the inherited Deck operation.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_source_station_native_r3.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rr-source-station-native-r3'","servo-fuse-rr-source-station-native-r4'")
code=code.replace('[cx+.5,-47,108.8,cx+4.5,-43,109]', '[130.5,-47,108.8,134.5,-43,109]')
code=code.replace('[cx+.5,-47,108.8,cx+4.5,-43,z]', '[130.5,-47,108.8,134.5,-43,z]')
needle="    cuttools=[Part.makeCylinder"
assert needle in code
code=code.replace(needle,"    prospective=prospective.fuse(box([cx+.5,-47,z-8,134.5,-43,z]))\n    cuttools=[Part.makeCylinder")
needle="        tools=[]\n"
assert needle in code
code=code.replace(needle,"        stocks.append(nativebox(d,'RRSourceCrossArm',[cx+.5,-47,z-8,134.5,-43,z]))\n        tools=[]\n")
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rr_source_station_native_r3.py']=sha(ROOT/'tools/electronics/servo_fuse_rr_source_station_native_r3.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
