"""Shared removal with the matched native locator passage in fixed Guard.

Reuse R11 two bank2mm checks only by proven subtractive Guard replacement;
all other fixed shapes remain unchanged. Recheck Cover and all higher poses.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r13.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r13_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r13','servo-fuse-bank-fixed-rr-lift-r14')
old="    module.pop('FRReturnGuard');owners['FixedGuard']=load('hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Guard_WORLD.brep')"
assert old in code
code=code.replace(old,"""    module.pop('FRReturnGuard')
    originalguard=load('hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Guard_WORLD.brep')
    owners['FixedGuard']=load('hardware/cad/studies/servo-fuse-guard-fixed-service-r1/Guard_WORLD.brep')
    servicepath=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1/checks.json'
    pins[servicepath.relative_to(ROOT).as_posix()]=sha(servicepath);service=json.loads(servicepath.read_text(encoding='utf-8'))
    assert service['exports'][0]['relocated_reopen'] and service['exports'][0]['closed_STL']
    assert owners['FixedGuard'].cut(originalguard).Volume<1e-5
    assert originalguard.cut(owners['FixedGuard']).Volume>0""")
code=code.replace('reused_R11_clear_at_2mm=["BankRight","BankLeft"],','reused_R11_clear_at_2mm=["BankRight","BankLeft"],Guard_reuse_basis="Native subtractive replacement, no added volume; all other fixed owners unchanged",')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
