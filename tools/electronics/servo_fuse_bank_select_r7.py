"""One R52, not an extra variant; requires actual whole module R17."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_select_r6.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='selector_r6_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r11','servo-fuse-bank-stock-budget-r12').replace('servo-fuse-bank-assembly-r10','servo-fuse-bank-assembly-r11').replace('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-fixed-rr-lift-r17')
for old,new in [
    ("('BankRight','electronics:servo-fuse-bank-right','servo-fuse-fr-source-fixed-deck-native-r2','BankRightFixedSourceFinished','PETG',10)",
     "('BankRight','electronics:servo-fuse-bank-right','servo-fuse-bank-inner-feed-service-r1','BankRightInnerFeedServiceFinished','PETG',10)"),
    ("('Cover','body:raised-upper-cover-mount','servo-fuse-cover-fixed-guard-service-r1','CoverFixedGuardServiceFinished','PETG',10)",
     "('Cover','body:raised-upper-cover-mount','servo-fuse-cover-deck-edge-service-r2','CoverDeckEdgeServiceFinished','PETG',10)")]:
    assert old in code,old
    code=code.replace(old,new)
exec(compile(code,str(Path(__file__).resolve()),'exec'))
