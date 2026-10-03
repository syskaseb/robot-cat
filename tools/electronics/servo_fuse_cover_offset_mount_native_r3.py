"""Keep the complete M2 Deck bearing, clear the rear-left wire crossing.

R2 replacement bracket hit W066_4 at its rear-left base corner. Remove
that entire corner, outside the OD5 screw bearing and offset upright.
"""
from pathlib import Path
import runpy
parent=Path(__file__).with_name('servo_fuse_cover_offset_mount_native_r2.py')
code=runpy.run_path(str(parent),run_name='offset_definition')['code']
code=code.replace('servo-fuse-cover-offset-mount-native-r2','servo-fuse-cover-offset-mount-native-r3')
old="    bracket=cut('OffsetBracketFinished',joined,compound('OffsetBracketTools',[bolt,side,pocket]))"
new="""    corner=box('CompleteRearLeftWireCornerClearance',[-93,-90,108.5,-87,-87,112.1])
    bracket=cut('OffsetBracketFinished',joined,compound('OffsetBracketTools',[bolt,side,pocket,corner]))"""
assert old in code;code=code.replace(old,new)
marker='        overlap=cover.Shape.common(bracket.Shape).Volume;assert overlap<1e-5,overlap'
code=code.replace(marker,"""        deckring=Part.makeCylinder(2.5,3,A.Vector(-84,-91,109)).cut(Part.makeCylinder(1.21,3,A.Vector(-84,-91,109)))
        deck_bearing_missing=deckring.cut(bracket.Shape).Volume;assert deck_bearing_missing<1e-5,deck_bearing_missing
"""+marker)
code=code.replace('installed_pair_overlap_mm3=overlap,','installed_pair_overlap_mm3=overlap,Deck_OD5_bearing_missing_mm3=deck_bearing_missing,rear_left_corner_clearance_mm=[-93,-90,108.5,-87,-87,112.1],')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
