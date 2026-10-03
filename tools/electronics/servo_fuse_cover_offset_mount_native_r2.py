"""Remove the complete obsolete right-hand front-left cover tab.

R1 removed the stationary-seat sweep but left an isolated old tab to its
right. The new offset mount/arch is retained; the old tab is not a part.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_offset_mount_native_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-cover-offset-mount-native-r1','servo-fuse-cover-offset-mount-native-r2')
code=code.replace('[-83.85,-102.35,103.9,-79.15,-88.65,160.99101615137753]','[-83.85,-102.35,103.9,-66.45,-88.65,160.99101615137753]')
code=code.replace("[('Length',4),('Width',13)","[('Length',16.7),('Width',13)")
code=code.replace("passage_to_cover_bottom=True,","passage_to_cover_bottom=True,obsolete_front_left_tab_removed=True,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
