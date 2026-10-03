"""Preserve three free cavities; place RR below PWM and away from XA06 upright.

Full body/exit geometry changes, not bolt nudging. Input/source routes and
native supports remain required; no installed/module selection is inferred.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_main_joint_layout_r1.py')
code=base.read_text(encoding='utf-8').replace('servo-fuse-main-joint-layout-r1','servo-fuse-main-joint-layout-r2')
old='RR=[74,-66,126]'
assert code.count(old)==1
code=code.replace(old,'RR=[46,-77,121.5]')
old="    code=ns['code'];owner_code="
assert code.count(old)==1
code=code.replace(old,"    pin(ROOT/'tools/electronics/servo_fuse_main_joint_layout_r1.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r1/checks.json')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-witness-tessellation-r1/checks.json')\n    code=ns['code'];owner_code=")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
