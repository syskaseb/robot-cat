"""Select only the matched nativeCover/sharedR12, not rejectedR11."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_select_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='selector_r2_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r7','servo-fuse-bank-stock-budget-r8').replace('servo-fuse-bank-assembly-r6','servo-fuse-bank-assembly-r7').replace('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r12')
code=code.replace('servo-fuse-cover-main-service-r6','servo-fuse-cover-fixed-guard-service-r1').replace('CoverWholeRearFeedServiceFinished','CoverFixedGuardServiceFinished')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
