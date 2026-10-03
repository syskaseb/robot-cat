"""Matched left foot/Deck and eight real bank washers, same single order."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_assembly_r9.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='assembly_r9_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-assembly-r9','servo-fuse-bank-assembly-r10').replace('servo-fuse-bank-stock-budget-r10','servo-fuse-bank-stock-budget-r11').replace('servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-bank-fixed-rr-lift-r15')
code=code.replace('4M2x12/4M2nuts/4washers','4M2x12/4M2nuts/8washers (one washer at each head and nut)')
code=code.replace("    clips=read(","    leftmount=read('hardware/electronics/full-cat/servo-fuse-left-mount-service-native-r7/checks.json')\n    assert leftmount['four_mount_hardware']['OD5washers']==8 and all(r['relocated_reopen'] for r in leftmount['exports'])\n    clips=read(")
code=code.replace("      part_ownership=dict(","      bank_mount_axes_xy_mm=[leftmount['changed_axis_mm']]+leftmount['unchanged_axes_mm'],bank_mount_hardware=leftmount['four_mount_hardware'],\n      part_ownership=dict(")
code=code.replace('retain all Cover mount hardware.', 'use the changed left axis(-51,92.5) from the current native pair, not the obsolete left hole(-63,92.5); retain all Cover mount hardware.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
