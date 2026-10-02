"""R1 lift witness: expose bank bolt access, retain roof/head/mount history.

Independent cover lift crosses bank panels. Plan bank+cover removal as a
disconnected module; verify this order separately, do not waive collisions.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_cover_native_r1.py')
code=base.read_text(encoding='utf-8').replace('servo-fuse-cover-native-r1','servo-fuse-cover-native-r2')
code=code.replace('cuts.append([x-9.8,lo,103,x+9.8,hi,114.5])',
    'cuts.append([x-9.8,min(side*88.2,side*150),103,x+9.8,max(side*88.2,side*150),200])')
code=code.replace('Bank remains on Deck.', 'Bank no longer falsely assumed to remain on Deck during cover removal; disconnected module removal needs its own check.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
