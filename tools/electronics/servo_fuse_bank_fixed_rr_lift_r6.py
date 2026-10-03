"""Receive corrected primitive link placements; then whole module lift.

Use only finished native fixed-source R2 Deck/BankRight/Cover and retain all
stationary source loops. R1 origin-link failure is not an accepted export.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r5.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='lift_r5_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r5','servo-fuse-bank-fixed-rr-lift-r6')
code=code.replace('servo-fuse-fr-source-fixed-deck-native-r1','servo-fuse-fr-source-fixed-deck-native-r2')
code=code.replace("    assert len(parked)==24,parked", "    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r5.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r5.py')\n    assert len(parked)==24,parked")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
