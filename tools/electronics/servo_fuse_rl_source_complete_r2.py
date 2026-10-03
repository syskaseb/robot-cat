"""Complete RL source above closed WAGO cases and below retained W061.

R1 is rejected: its119mm lap enters D_RL and its extension enters G1/G2.
Use one126.2mm corridor: the entire factory approach, opposing lap and
extension move together, maintaining the14mm straight sleeve/grip lands.
RR stationR4, all four MTA and the accepted front remain untouched.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rl_source_complete_r1.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rl-source-complete-r1'","servo-fuse-rl-source-complete-r2'")
assert 'f.shift(X,V(0,4,-11),20)' in code and 'factory_y=42' in code
code=code.replace('f.shift(X,V(0,4,-11),20)','f.shift(X,V(0,3,-3.8),20)')
code=code.replace('factory_y=42','factory_y=41')
code=code.replace('    prior=ROOT/',"    pin(ROOT/'tools/electronics/servo_fuse_rl_source_complete_r1.py');\n    prior=ROOT/")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
