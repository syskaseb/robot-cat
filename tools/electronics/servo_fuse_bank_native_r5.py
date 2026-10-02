"""R4 missing bearing witness: center OD5 washers on side rail Y92.5."""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_bank_native_r4.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-bank-native-r4','servo-fuse-bank-native-r5')
code=code.replace('hy=side*92','hy=side*92.5')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
