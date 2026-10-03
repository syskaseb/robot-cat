"""Same ledger; receive completed R13, not the withdrawn distance worker."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r8.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='stock_r8_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r8','servo-fuse-bank-stock-budget-r9').replace('servo-fuse-bank-fixed-rr-lift-r12','servo-fuse-bank-fixed-rr-lift-r13')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
