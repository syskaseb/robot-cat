"""Receive the matched Cover/fixedGuard shared result, not rejectedR11."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r7.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-bank-stock-budget-r7','servo-fuse-bank-stock-budget-r8').replace('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r12')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
