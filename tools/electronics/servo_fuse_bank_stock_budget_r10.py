"""Unchanged counts, actual matched locator-service lift R14."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r9.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='stock_r9_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r9','servo-fuse-bank-stock-budget-r10').replace('servo-fuse-bank-fixed-rr-lift-r13','servo-fuse-bank-fixed-rr-lift-r14')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
