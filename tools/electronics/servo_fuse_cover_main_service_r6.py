"""Retain the intact R2 Cover; open the complete W053 extension footprint.

R3/R5 oversized all-feed radius envelopes damage three original mount
zones and are rejected. R2 retains ALL original zones/bearing rings. Its
one remaining W053 tube-corner conflict is corrected by the entire actual
extension footprint, below119mm and far from the four mounting axes.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_rr_fixed_service_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-cover-rr-fixed-service-r1','servo-fuse-cover-main-service-r6')
replace("fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r7/checks.json')", "fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r9/checks.json')")
replace("fail['hits'][0]['owner']=='CandidateDeck'", "fail['hits'][0]['owner']=='W053/extension'")
replace("    pre=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/preflight.json')\n    outline=next(b for name,b in pre['cover_tools'] if name=='RRStationOpenSide')", """    wirepath=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8/W053_extension_DESIGN.brep'
    pins[wirepath.relative_to(ROOT).as_posix()]=sha(wirepath);wire=Part.read(str(wirepath));wb=wire.BoundBox
    outline=[wb.XMin-.35,wb.YMin-.35,0,wb.XMax+.35,wb.YMax+.35,wb.ZMax+.35]""")
replace("native=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')", "native=read('hardware/electronics/full-cat/servo-fuse-cover-main-service-r2/checks.json')")
replace("dest=CAD/'CoverRRFixedService.FCStd'", "dest=CAD/'CoverWholeRearFeedService.FCStd'")
replace('FixedRRServiceParameters','WholeRearFeedServiceParameters')
replace('RRStationFullBottomServicePassage','WholeW053BottomServicePassage')
replace('CoverFixedRRServiceFinished','CoverWholeRearFeedServiceFinished')
replace('p.Allowance=.3','p.Allowance=.35')
replace('-.6','-.7')
replace('b[0]+.3','b[0]+.35');replace('b[1]+.3','b[1]+.35')
replace('p.Allowance=.4','p.Allowance=.45')
replace('parameter_mm=[.3,.4,.3]','parameter_mm=[.35,.45,.35]')
marker='        v=s.Volume;p.Allowance=.45;'
replace(marker,"""        removed=parent.Shape.cut(s);mounts=[]
        for x in (-84,106):
            for side in (-1,1):
                lo,hi=sorted((side*88,side*102));zone=Part.makeBox(12,hi-lo,12,A.Vector(x-6,lo,109))
                ring=Part.makeCylinder(2.5,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)).cut(Part.makeCylinder(1.2,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)))
                loss=removed.common(zone).Volume;ringloss=removed.common(ring).Volume
                assert loss<1e-5 and ringloss<1e-5,(x,side,loss,ringloss)
                mounts.append(dict(xy=[x,side*91],original_zone_removed_mm3=loss,bearing_removed_mm3=ringloss))
        v=s.Volume;p.Allowance=.45;""")
replace('assembly_ties_cut=33,','assembly_ties_cut=49,mounts=mounts,whole_W053_extension_service=True,')
replace("status='NATIVE_COVER_RR_FULL_BOTTOM_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN'", "status='NATIVE_INTACT_COVER_WHOLE_REAR_FEED_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
