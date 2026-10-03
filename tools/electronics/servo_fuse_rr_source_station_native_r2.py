"""Two-sided RR grips with an explicit26mm sleeve clearance between them.

The bridge is NOT allowed to occupy the lower sleeve or solder. Cut a
continuous10mm nominal clearance channel between the separate grip lands;
retain3mm minimum floor below it and the proven16mm2 Deck foot.
"""
from pathlib import Path
src=Path(__file__).with_name('servo_fuse_rr_source_station_native_r1.py')
code=src.read_text(encoding='utf-8')
code=code.replace("servo-fuse-rr-source-station-native-r1'","servo-fuse-rr-source-station-native-r2'")
code=code.replace('        tools=[]\n', '''        tools=[]
        jointclear=d.addObject('Part::Cylinder','RRSourceSleeveClearance')
        jointclear.Radius=5; jointclear.Height=28
        jointclear.Placement=A.Placement(V(cx,-63,z),A.Rotation(V(0,0,1),V(0,1,0)))
        tools.append(jointclear)
''')
code=code.replace('    pins={};V=A.Vector', "    pins={};V=A.Vector\n    pins[src.relative_to(ROOT).as_posix()]=sha(src)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
