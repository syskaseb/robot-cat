"""Select matched fixed service Guard and R14, never rejected R13."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_select_r4.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='selector_r4_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r9','servo-fuse-bank-stock-budget-r10').replace('servo-fuse-bank-assembly-r8','servo-fuse-bank-assembly-r9').replace('servo-fuse-bank-fixed-rr-lift-r13','servo-fuse-bank-fixed-rr-lift-r14')
old="('Guard','electronics:FR-return-guard','servo-fuse-guard-fixed-deck-native-r1','GuardFixedFinished','PETG',10)"
assert old in code
code=code.replace(old,"('Guard','electronics:FR-return-guard','servo-fuse-guard-fixed-service-r1','GuardFixedServiceFinished','PETG',10)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
