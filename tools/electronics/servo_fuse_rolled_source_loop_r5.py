"""One FR-source correction: clear F_PI below its south face and cross west.

Keep4MTA and all other R4 routes. Replace only W042: a minimumR20 factory
S-offset and an opposing lap atY-36; the HELU source turns west BEFORE its
rise, instead of crossing W041. Exterior west loop requires new cover
passages if the exact fit identifies them. No casing/stock selection here.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r4.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code, str(Path(__file__).resolve()), 'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rsplit(tail,1)[0],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r5'")
replace("prior_path=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3/checks.json'", "prior_path=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4/checks.json'")
replace("old=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3'/(n+'_DESIGN.brep')", "old=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'/(n+'_DESIGN.brep')")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r3.py')", "pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r3.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r4.py')")
old="""            north=V(0,1,0);south=-north
            f=Route([right,cy,cz]);f.arc(X,north,20,math.pi)
            f.line([-56.4,-32,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5])
            e.shift(north,Z*23.5,25.2)
            e.arc(north,-X,25.2);e.line([e.p.x-25.2,e.p.y,e.p.z])
            e.arc(-X,south,25.2)
            assert abs(e.p.x+99.6)<1e-6
            e.shift(south,-Z*11,25.2)
            assert e.p.y>=-6.8
            e.line([-99.6,-6.8,cz]);e.arc(south,X,25.2)
            e.line([-64.4,-32,cz]);lap(leg,in_id,f,e,-X,X,X)"""
new="""            north=V(0,1,0);south=-north
            f=Route([right,cy,cz]);f.arc(X,north,20,math.pi)
            f.shift(-X,south*4,20);assert f.p.x>=-62.1
            f.line([-62.1,-36,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5])
            e.arc(north,-X,25.2);e.shift(-X,Z*12.5,25.2)
            e.arc(-X,south,25.2)
            west_x=e.p.x;assert west_x < -107
            e.line([west_x,-10.8,cz]);e.arc(south,X,25.2)
            e.line([-70.1,-36,cz]);lap(leg,in_id,f,e,-X,X,X)"""
replace(old,new)
replace("cad=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r1/Deck_WORLD.brep'", "cad=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep'")
replace("cradle=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r1/checks.json'", "cradle=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7/checks.json'")
replace("(ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r1').glob", "(ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7').glob")
replace("    owners=retained_owners(pin,load,Part);owners['CandidateDeck']=load(cad)", """    owners=retained_owners(pin,load,Part);owners['CandidateDeck']=load(cad)
    owners['RetainedCover']=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Cover_WORLD.brep')
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/BankRight_WORLD.brep')
    relief_path=ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r6/checks.json';pin(relief_path)
    relief=json.loads(relief_path.read_text(encoding='utf-8'));assert all(p['changed_feed_contacts']==0 for p in relief['parts'])
    for p,h in relief['source_sha256'].items():assert sha(ROOT/p)==h,p
    # Discard old-cover/bank contacts only for byte-identical unchanged R4
    # feed parts covered by the exact R6 proof. The changed W042 is retested.
    cleared_owners=('RetainedCover','Bank/RightClipAccessFinished_WORLD')
""")
replace("if not r['part'].startswith('W042') and not r['owner'].startswith('W042')", "if not r['part'].startswith('W042') and not r['owner'].startswith('W042') and r['owner'] not in cleared_owners")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
