"""Complete bank + Cover + attached Guard with the accepted upper clamps.

Retain every stationary owner. Explicitly cut the twelve output ties and
twelve input ties; lower saddles are replaced, not wires relocated.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r3.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='lift_r3_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r3','servo-fuse-bank-fixed-rr-lift-r4')
code=code.replace('servo-fuse-output-rib-exits-native-r1','servo-fuse-output-rib-exits-native-r3')
old="    assert len(parked)==24,parked"
assert old in code
code=code.replace(old,"""    fitpath=ROOT/'hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1/checks.json'
    pins[fitpath.relative_to(ROOT).as_posix()]=sha(fitpath)
    fit=json.loads(fitpath.read_text(encoding='utf-8'))
    assert fit['checked_clamps']==12 and not fit['hits'] and not fit['errors']
    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r3.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r3.py')
    assert len(parked)==24,parked""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
