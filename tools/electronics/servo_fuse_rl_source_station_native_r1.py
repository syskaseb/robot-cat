"""Native RL station for the complete matched R2 source, retaining RR R4.

Two straight insulation seats share a single16mm2 Deck foot west of D_RL.
Full small-stock fit must pass before editing the inherited native Deck.
Old RR support, both complete source routes and the front remain retained.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_source_station_native_r4.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rr-source-station-native-r4'","servo-fuse-rl-source-station-native-r1'")
code=code.replace("folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8'",
    "folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-complete-r2'")
code=code.replace("startswith('W052')","startswith('W044')")
code=code.replace("x['id']=='W052'","x['id']=='W044'")
remove="    j['extension_grip_centre_mm'][1]=-34\n    assert j['extension_grip_centre_mm'][1]-2==j['centre_mm'][1]+13"
assert remove in code;code=code.replace(remove,'')
code=code.replace('RRSource','RLSource').replace("f'RR{role}","f'RL{role}").replace("'RR'+role","'RL'+role")
code=code.replace("'RRStock'","'RLStock'").replace('RRStock=prospective','RLStock=prospective')
code=code.replace("'RR_SMALL_STOCK_PREFLIGHT'","'RL_SMALL_STOCK_PREFLIGHT'").replace("'RR_NATIVE_DECK_RECOMPUTE'","'RL_NATIVE_DECK_RECOMPUTE'")
code=code.replace("'RR_DECK_COMPUTED'","'RL_DECK_COMPUTED'").replace("'RR_NATIVE_COVER_RECOMPUTE'","'RL_NATIVE_COVER_RECOMPUTE'")
code=code.replace("'RR_SOURCE_NATIVE_STATION_STATIC_CLEAR'","'RL_SOURCE_NATIVE_STATION_STATIC_CLEAR'")
code=code.replace("owners['RL_R3_CANDIDATE/'+p.stem]=load(p)","owners['RR_R8/'+p.stem]=load(p)")
code=code.replace("(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r3').glob('W044*_DESIGN.brep')",
    "(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8').glob('W052*_DESIGN.brep')")
code=code.replace("    source=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2'",'''    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-station-native-r4').glob('RR*Tie*_DESIGN.brep'):
        owners['RetainedRRTie/'+p.stem]=load(p)
    source=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2' ''')
code=code.replace('servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep','servo-fuse-rr-source-station-native-r4/Deck_WORLD.brep')
code=code.replace('servo-fuse-rolled-cradles-native-r7/DeckRolledCradles.FCStd','servo-fuse-rr-source-station-native-r4/DeckRRSourceStation.FCStd')
code=code.replace('servo-fuse-fr-joint-station-native-r1/CoverFRJointStation.FCStd','servo-fuse-rr-source-station-native-r4/CoverRRSourceStation.FCStd')
code=code.replace("getObject('RolledCantileversFinished')","getObject('RRSourceStationFinished')")
code=code.replace("getObject('FRJointCoverFinished')","getObject('RRSourceCoverFinished')")
# Single direct post; the RR external cross-arm is not needed west of D_RL.
code=code.replace('[130.5,-47,108.8,134.5,-43,109]', '[cx+.5,j[\'centre_mm\'][1]-2,108.8,cx+4.5,j[\'centre_mm\'][1]+2,109]')
code=code.replace('[130.5,-47,108.8,134.5,-43,z]', '[cx+.5,j[\'centre_mm\'][1]-2,108.8,cx+4.5,j[\'centre_mm\'][1]+2,z]')
code=code.replace('[cx-.7,-67,z-8,cx+4.5,-32,z]', "[cx-.7,j['extension_grip_centre_mm'][1]-2,z-8,cx+4.5,j['factory_grip_centre_mm'][1]+2,z]")
code=code.replace("    prospective=prospective.fuse(box([cx+.5,-47,z-8,134.5,-43,z]))\n",'')
code=code.replace("        stocks.append(nativebox(d,'RLSourceCrossArm',[cx+.5,-47,z-8,134.5,-43,z]))\n",'')
code=code.replace('Part.makeCylinder(5,27,V(cx,-63,z),V(0,1,0))',"Part.makeCylinder(5,28,V(cx,j['centre_mm'][1]-14,z),V(0,1,0))")
code=code.replace('jointclear.Height=27','jointclear.Height=28')
code=code.replace('V(cx,-63,z)',"V(cx,j['centre_mm'][1]-14,z)")
code=code.replace('AddedRRSourceGrips','AddedRLSourceGrips')
code=code.replace("'RL source remains rejected, unrelated output/WAGO grips/RR body clips/whole assembly-removal and final selection/stock/E3 open.'",
    "'Both complete rear source routes are retained; output/WAGO grips/RR body clips/whole assembly-removal and final selection/stock/E3 open.'")
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rr_source_station_native_r4.py']=sha(ROOT/'tools/electronics/servo_fuse_rr_source_station_native_r4.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
