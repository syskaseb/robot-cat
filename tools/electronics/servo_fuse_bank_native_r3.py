"""Native bank for R9: same mounts; shifted matching FL2/FL3 apertures."""
from pathlib import Path

base=Path(__file__).with_name('servo_fuse_bank_native.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-bank-native-r1','servo-fuse-bank-native-r3')
code=code.replace('servo_fuse_side_bank_r7','servo_fuse_side_bank_r9')
code=code.replace('side*130','side*136').replace('cx=base+26*i;cy=side*110',
    "cx=base+26*i;cy=side*116\n                if side==1 and base==-69 and i==1:cx-=3\n                if side==1 and base==-69 and i==2:cx+=6")
code=code.replace("sources={route_checks.relative_to(ROOT).as_posix():sha(route_checks),",
    "sources={'tools/electronics/servo_fuse_bank_native.py':sha(ROOT/'tools/electronics/servo_fuse_bank_native.py'),'tools/electronics/servo_fuse_side_bank_r8.py':sha(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py'),route_checks.relative_to(ROOT).as_posix():sha(route_checks),")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
