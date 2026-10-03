"""Current unchanged materials, requires completed matched whole lift R15."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r10.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='stock_r10_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r10','servo-fuse-bank-stock-budget-r11').replace('servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-bank-fixed-rr-lift-r15')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
