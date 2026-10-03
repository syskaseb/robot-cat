"""Complete lower RL source, preserving the full native RR station.

Move the whole factory approach below W061 and XA02 before its turn.
Both ends retain14mm straight insulation for sleeve/grip, not a bare-end
offset. RR R8 and its native R2 station remain unchanged. This is a
conditional construction candidate, not a selected bank or physical PASS.
"""
from pathlib import Path
src=Path(__file__).with_name('servo_fuse_rear_source_pair_r1.py')
code=src.read_text(encoding='utf-8')
code=code.replace("servo-fuse-rear-source-pair-r1'","servo-fuse-rl-source-complete-r1'")
code=code.replace("servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep", "servo-fuse-rr-source-station-native-r4/Deck_WORLD.brep")
code=code.replace("servo-fuse-fr-joint-station-native-r1/Cover_WORLD.brep", "servo-fuse-rr-source-station-native-r4/Cover_WORLD.brep")
code=code.replace("    affected=('W044','W052')", "    affected=('W044',)")
code=code.replace("if not p.stem.startswith(affected):owners['OtherFeed/'+p.stem]=load(p)",
    "if not p.stem.startswith(('W044','W052')):owners['OtherFeed/'+p.stem]=load(p)")
code=code.replace('    fixed={n:bounds(s)', '''    rr_station=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-station-native-r4'
    p=rr_station/'checks.json';pin(p);rr_native=json.loads(p.read_text(encoding='utf-8'))
    assert not rr_native['hits'] and not rr_native['errors']
    # Names have Factory/Extension before Tie; retain every real RR band/head.
    for p in rr_station.glob('RR*Tie*_DESIGN.brep'):owners['RRTie/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8').glob('W052*_DESIGN.brep'):
        owners['RR_R8/'+p.stem]=load(p)
    fixed={n:bounds(s)''')
code=code.replace("for leg,w,right,cy,cz,sy in [('RL','W044',51.5,72,130,-6.8),('RR','W052',63.5,-86,121.5,6.8)]:",
    "for leg,w,right,cy,cz,sy in [('RL','W044',51.5,72,130,-6.8)]:")
a=code.index('        normal=Y*.5+Z*math.sqrt(.75)')
b=code.index('        a=f.p;b=e.p;',a)
code=code[:a]+'''        f=Route([right,cy,cz])
        f.shift(X,V(0,4,-11),20)
        f.arc(X,-Y,20)
        jx=f.p.x;jz=f.p.z;factory_y=42
        assert abs(f.p.y-factory_y)>=14
        f.line([jx,factory_y,jz])
        e=Route([32,sy,129]);delta=Z*(jz-129)
        travel=math.sqrt(4*25.2*delta.Length-delta.Length**2)
        assert jx-25.2-32>=travel
        e.line([jx-25.2-travel,sy,129]);e.shift(X,delta,25.2)
        e.arc(X,Y,25.2);ext_y=factory_y-8
        assert ext_y-e.p.y>=14
        e.line([jx,ext_y,jz]);jy=(factory_y+ext_y)*.5
''' +code[b:]
code=code.replace('centre=(a+b)*.5;axis=-X;', 'centre=(a+b)*.5;axis=Y;')
code=code.replace('barestart+V(0,dy,0),axis', 'barestart+X*dy,axis')
code=code.replace('factory_grip_centre_mm=[fx+12,jy,jz],extension_grip_centre_mm=[fx-20,jy,jz]',
    'factory_grip_centre_mm=list(a+Y*12),extension_grip_centre_mm=list(b-Y*12)')
code=code.replace("    prior=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_rear_source_pair_r1.py');\n    prior=ROOT/")
code=code.replace("'Native joint supports/ties and cover passages after real shared fit; WAGO grips, RR clips, combined removal, stock/E3 and selection.'",
    "'Native RL supports/cover after shared route fit; existing RR native station/front retained. Whole output/WAGO/clip access/removal/stock/E3 selection OPEN.'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
