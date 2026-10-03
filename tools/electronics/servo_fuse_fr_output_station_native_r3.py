"""Complete lower tie vertical exit; keep R2 construction and its one fault.

Only the east vertical strap crosses the tray by4.5mm3. Its real1.8x2.8mm
through passage reaches ABOVE the tray, not merely the bottom tie band.
No change to accepted wire paths, stock mounting or housing/grip supports.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_output_station_native_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace("servo-fuse-fr-output-station-native-r2'","servo-fuse-fr-output-station-native-r3'")
code=code.replace("    tools=[s for _,_,_,s in grooves]", "    slots += [('LowerTieVerticalExit',[-95.7,-106.4,z0-2,-93.9,-103.6,z0+.3])]\n    tools=[s for _,_,_,s in grooves]")
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_fr_output_station_native_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_output_station_native_r2.py')\n    pins['hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r2/preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r2/preflight.json')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
