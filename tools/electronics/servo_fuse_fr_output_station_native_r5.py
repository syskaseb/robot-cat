"""Open the tangent upper tie passage instead of repairing a bad mesh.

R4 diagnosis: exactly one four-facet edge at X-99.5,Z116.378784, the
strap-slot roof tangent to the factory groove. Raise that CUT0.3mm so the
two openings really meet. This only removes material, preserves R3's
collision scope by proven subset, and must still pass native/mesh tests.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_output_station_native_r4.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("servo-fuse-fr-output-station-native-r4'","servo-fuse-fr-output-station-native-r5'")
code=code.replace("servo-fuse-fr-output-station-native-r3/FRGuardOutputStation.FCStd'", "servo-fuse-fr-output-station-native-r4/FRGuardOutputStation.FCStd'")
code=code.replace('    pins={}',"    pins={}\n    pins['tools/electronics/servo_fuse_fr_output_station_native_r4.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_output_station_native_r4.py')\n    pins['hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r4/tessellation.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r4/tessellation.json')")
code=code.replace('        f.Refine=True;d.recompute();s=f.Shape.copy();', "        assert abs(d.UpperTiePass.Height.Value-1.8)<1e-6\n        d.UpperTiePass.Height=2.1\n        f.Refine=True;d.recompute();s=f.Shape.copy();")
code=code.replace('        diff=before.cut(s).Volume+s.cut(before).Volume;assert diff<1e-5,diff', "        diff=before.cut(s).Volume;added=s.cut(before).Volume\n        assert diff>0 and added<1e-5,(diff,added)")
code=code.replace('symmetric_difference_mm3=diff','removed_slot_material_mm3=diff,added_material_mm3=added')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
