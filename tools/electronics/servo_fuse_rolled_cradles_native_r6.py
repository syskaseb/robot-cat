"""RR Y loops pass outside both stop lips, with nominal0.5mm allowance.

R5's inner leg is at the body face and therefore crosses the stop/web.
Use the lips' actual outer bounds, not the body bounds, for both vertical
legs. Keep shoulders/front supports/body datums. Receive R5 before running.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_cradles_native_r5.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r5'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r6'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r5'", "CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r6'")
replace("    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r4.py')", "    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r5.py')\n    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r4.py')")
replace("z0=b[2]-1.5-1.2;z1=b[5]+1.2;outer=-98.5", "z0=b[2]-1.5-1.2;z1=b[5]+1.2;outer=-99;inner=b[4]+2")
replace("(x-1.25,b[4],z0,x+1.25,b[4]+1.2,z1)", "(x-1.25,inner,z0,x+1.25,inner+1.2,z1)")
replace("(x-1.25,outer,z0,x+1.25,b[4],b[2]-1.5)", "(x-1.25,outer,z0,x+1.25,inner,b[2]-1.5)")
replace("(x-1.25,outer,b[5],x+1.25,b[4],z1)", "(x-1.25,outer,b[5],x+1.25,inner,z1)")
replace("length=2*((b[4]-outer)+1.2+(z1-z0)-1.2)", "length=2*((inner-outer)+1.2+(z1-z0)-1.2)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
