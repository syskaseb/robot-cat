"""Fully supported RL foot, located from the actual retained Deck aperture.

R1's rectangular foot has14.5 of16mm2 bearing. Place the complete4x4 foot
west of that precise missing-material witness; one small middle cross-arm
joins it to both source seats. No source route, connector or RR changes.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rl_source_station_native_r1.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rl-source-station-native-r1'","servo-fuse-rl-source-station-native-r2'")
needle='    # Exact small construction stock and both real bands first.'
assert needle in code
code=code.replace(needle,'''    original_foot=[cx+.5,j['centre_mm'][1]-2,108.8,cx+4.5,j['centre_mm'][1]+2,109]
    old_area=olddeck.common(box(original_foot)).Volume/.2
    missing=box(original_foot).cut(olddeck)
    assert abs(old_area-14.5)<1e-5 and missing.Volume>0
    fx=missing.BoundBox.XMin-.3-4
    supported_foot=[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,109]
    actual=olddeck.common(box(supported_foot)).Volume/.2
    save(OUT/'foot-land.json',dict(original_bearing_mm2=old_area,missing_bounds_mm=bounds(missing),
        shifted_foot_mm=supported_foot,new_bearing_mm2=actual,source_sha256=pins,selected=False,physical_pass=False))
    assert abs(actual-16)<1e-5,dict(foot=supported_foot,bearing_mm2=actual)
    # Exact small construction stock and both real bands first.''')
code=code.replace("foot=[cx+.5,j['centre_mm'][1]-2,108.8,cx+4.5,j['centre_mm'][1]+2,109]",
    "foot=[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,109]")
# Keep the original witness rectangle in the diagnostic, before fx exists.
code=code.replace("original_foot=[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,109]",
    "original_foot=[cx+.5,j['centre_mm'][1]-2,108.8,cx+4.5,j['centre_mm'][1]+2,109]")
code=code.replace("[cx+.5,j['centre_mm'][1]-2,108.8,cx+4.5,j['centre_mm'][1]+2,z]",
    "[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,z]")
code=code.replace('    cuttools=[Part.makeCylinder',
    "    prospective=prospective.fuse(box([fx,j['centre_mm'][1]-2,z-8,cx+4.5,j['centre_mm'][1]+2,z]))\n    cuttools=[Part.makeCylinder")
code=code.replace('        tools=[]\n',
    "        stocks.append(nativebox(d,'RLSourceFootCrossArm',[fx,j['centre_mm'][1]-2,z-8,cx+4.5,j['centre_mm'][1]+2,z]))\n        tools=[]\n")
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rl_source_station_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_rl_source_station_native_r1.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
