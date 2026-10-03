"""Matched FR station: three real tie passages, heads outside the spine.

R1 found only casing edge and strap/support contacts, no wire contacts.
Retain the full tray/spine and independent six-mm insulation seats. Cut
actual tie paths through the spine and avoid the cover edge; the lower tie
is separated from the upper seat. Whole construction, not contact waivers.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_output_station_native_r1.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("servo-fuse-fr-output-station-native-r1'","servo-fuse-fr-output-station-native-r2'")
code=code.replace('    pins={};V=A.Vector', "    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_fr_output_station_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_output_station_native_r1.py')\n    pins['hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r1/preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r1/preflight.json')")
code=code.replace("('LowerTiePass',[-110,-105.4,z0-3,-93,-102.6,z0-1.5])", "('LowerTiePass',[-112,-106.4,z0-3,-93,-103.6,z0-1.5])")
code=code.replace("    tools=[s for _,_,_,s in grooves]", "    slots += [('CoverEdgeClearance',[-94.2,-101.7,z0-2.5,-92.5,-94.7,z0+.1]),\n        ('HousingTieTopPass',[-112,-121.4,z0+12.8,-91.4,-118.6,z0+14.4]),\n        ('LowerTieTopPass',[-112,-106.4,ez+1.9,-93,-103.6,ez+3.5]),\n        ('UpperTieTopPass',[-112,-101.4,fz+2.3,-93,-98.6,fz+3.9])]\n    tools=[s for _,_,_,s in grooves]")
code=code.replace("tie('HousingTie',-120,-107.1,-91.75,z0-4,z0+13,-111.9)", "tie('HousingTie',-120,-111,-91.75,z0-4,z0+13,-115.8)")
code=code.replace("tie('ExtensionTie',-104,-108.7,-93.8,z0-2.7,ez+2.1,-113.5)", "tie('ExtensionTie',-105,-111,-94.2,z0-2.7,ez+2.1,-115.8)")
code=code.replace("tie('FactoryTie',-100,-108.7,-93.8,ez+2.3,fz+2.5,-113.5)", "tie('FactoryTie',-100,-111,-94.2,ez+2.3,fz+2.5,-115.8)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
