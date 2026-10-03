"""Same fixedDeck assembly sequence, qualified by the matched CoverR12."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_assembly_r6.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-bank-assembly-r6','servo-fuse-bank-assembly-r7').replace('servo-fuse-bank-stock-budget-r7','servo-fuse-bank-stock-budget-r8').replace('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r12')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
