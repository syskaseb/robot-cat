"""One actual left mount pair and corrected two washers per bank axis."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_select_r5.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='selector_r5_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r10','servo-fuse-bank-stock-budget-r11').replace('servo-fuse-bank-assembly-r9','servo-fuse-bank-assembly-r10').replace('servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-bank-fixed-rr-lift-r15')
for a,b in [(
    "('Deck','electronics:DeckP10-cover-mount','servo-fuse-guard-fixed-deck-native-r1','DeckFixedGuardFinished','PETG',6)",
    "('Deck','electronics:DeckP10-cover-mount','servo-fuse-left-mount-service-native-r7','DeckLeftServiceMountFinished','PETG',6)"),(
    "('BankLeft','electronics:servo-fuse-bank-left','servo-fuse-output-rib-exits-native-r3','BankLeftOutputExitsFinished','PETG',10)",
    "('BankLeft','electronics:servo-fuse-bank-left','servo-fuse-left-mount-service-native-r7','BankLeftServiceMountFinished','PETG',10)"),(
    "('00125202',4,'bank:M2washers')","('00125202',8,'bank:M2washers')")]:
    assert a in code,a;code=code.replace(a,b)
exec(compile(code,str(Path(__file__).resolve()),'exec'))
