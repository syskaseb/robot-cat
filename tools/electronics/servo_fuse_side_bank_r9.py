"""Single remaining R8 contact: move FL3/cutout6mm in X, keep other11."""
from pathlib import Path

base=Path(__file__).with_name('servo_fuse_side_bank_r8.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-side-bank-r8','servo-fuse-side-bank-r9')
code=code.replace("if side==1 and base==-69 and i==1:cx-=3",
    "if side==1 and base==-69 and i==1:cx-=3\n                if side==1 and base==-69 and i==2:cx+=6")
code=code.replace("if leg=='FL' and index==2:cx-=3",
    "if leg=='FL' and index==2:cx-=3\n        if leg=='FL' and index==3:cx+=6")
code=code.replace("source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger)}",
    "source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger),'tools/electronics/servo_fuse_side_bank_r8.py':sha(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py')}")
code=code.replace('R6/R7 located upper feeds, S0foot and PWM shelf.',
    'R8 fixed all contacts except W029/XB11. Shift FL3/cutout6mm in+X; other11 unchanged.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
