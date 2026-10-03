"""Retain the exact placements of linked primitive saddles and tie slots.

R1 App::Link default dropped Part::Box placement, putting both saddles at
origin. The explicit native LinkPlacement restores the pinned world datums;
final parent shapes have identity placement and are preserved unchanged.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_source_fixed_deck_native_r1.py')
code=parent.read_text(encoding='utf-8')
assert "q.setLink(target);return q" in code
code=code.replace('servo-fuse-fr-source-fixed-deck-native-r1','servo-fuse-fr-source-fixed-deck-native-r2')
code=code.replace('q.setLink(target);return q','q.setLink(target);q.LinkPlacement=target.Placement;return q')
code=code.replace('    pins={}',"    pins={}\n    pins['tools/electronics/servo_fuse_fr_source_fixed_deck_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_source_fixed_deck_native_r1.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
