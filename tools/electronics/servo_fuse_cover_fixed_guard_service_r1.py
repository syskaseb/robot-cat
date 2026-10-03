"""One bottom-open side passage for the now-stationary complete channel.

R11 found actual Cover/Guard contact at2mm. No wire movement, no fastener
change. Use the whole fixed channel footprint up to its top, preserve all
original Cover mount zones/bearing rings, require one intact native solid.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_main_service_r6.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='cover_r6_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(a,b):
    global code
    assert a in code,a[:140]
    code=code.replace(a,b)
replace('servo-fuse-cover-main-service-r6','servo-fuse-cover-fixed-guard-service-r1')
replace('servo-fuse-bank-fixed-rr-lift-r9/checks.json','servo-fuse-bank-fixed-rr-lift-r11/checks.json')
replace("fail['hits'][0]['owner']=='W053/extension'", "fail['hits'][0]['owner']=='FixedGuard'")
replace("wirepath=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8/W053_extension_DESIGN.brep'", "wirepath=ROOT/'hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Guard_WORLD.brep'")
replace('servo-fuse-cover-main-service-r2/checks.json','servo-fuse-cover-main-service-r6/checks.json')
replace('CoverWholeRearFeedService.FCStd','CoverFixedGuardPassage.FCStd')
replace('WholeRearFeedServiceParameters','FixedGuardServiceParameters')
replace('WholeW053BottomServicePassage','WholeFixedGuardBottomServicePassage')
replace('CoverWholeRearFeedServiceFinished','CoverFixedGuardServiceFinished')
replace('whole_W053_extension_service=True','whole_fixed_Guard_service=True')
replace('NATIVE_INTACT_COVER_WHOLE_REAR_FEED_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN','NATIVE_COVER_WHOLE_FIXED_GUARD_PASSAGE_COMPLETE_SHARED_REMOVAL_OPEN')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
