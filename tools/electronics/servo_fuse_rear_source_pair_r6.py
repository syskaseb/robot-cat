"""RR complete outward-offset low plane; RL R5 remains explicitly rejected.

R5 RR had only an XS23 approach contact plus the replaceable cover. Move
the complete factory approach4mm outward while rising12mm; extend the
straight lap land. Full source remains below carrier; all lengths rechecked.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_source_pair_r5.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rear-source-pair-r5'","servo-fuse-rear-source-pair-r6'")
code=code.replace('f.shift(X,Z*13,20);factory_y=-49', 'f.shift(X,V(0,-4,12),20);factory_y=-53')
code=code.replace("    pin(parent);pin(src);", "    pin(parent);pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r5/checks.json');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
