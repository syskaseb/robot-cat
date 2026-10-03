"""Whole bank/Cover release with channel and its hardware FIXED on Deck.

One new ownership interface; no wire relocations or collider exemptions.
Native R1 must be complete before starting. Keep49explicit strap releases
as the existing conservative service recipe. Check the complete shared
module against actual fixed owners at the six recorded poses.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r9.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r9_definition_only');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(a,b):
    global code
    assert a in code,a[:120]
    code=code.replace(a,b)
replace('servo-fuse-bank-fixed-rr-lift-r9','servo-fuse-bank-fixed-rr-lift-r11')
replace('servo-fuse-cover-main-service-r2','servo-fuse-cover-main-service-r6')
marker='    assert len(parked)==24,parked'
replace(marker,"""    gp=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json'
    pins[gp.relative_to(ROOT).as_posix()]=sha(gp);gn=json.loads(gp.read_text(encoding='utf-8'))
    assert gn['Guard_owner']=='FIXED_DECK' and len(gn['exports'])==2 and all(r['relocated_reopen'] for r in gn['exports'])
    assert gn['bank_unchanged']
    owners['CandidateDeck']=load('hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Deck_WORLD.brep')
    module.pop('FRReturnGuard');owners['FixedGuard']=load('hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Guard_WORLD.brep')
    for k in list(module):
        if k.startswith('FRHardware/'):del module[k]
    for role in ('Screw0','Screw1','Nut0','Nut1'):
        owners['FixedGuardHardware/'+role]=load('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r3/'+role+'_CANDIDATE.brep')
    assert set(module)=={'BankRight','BankLeft','Cover'}
    assert len(parked)==24,parked""")
replace("FR_guard_owner='MOVING_BANK_WITH_2SCREWS_2NUTS'", "FR_guard_owner='FIXED_DECK_WITH_2SCREWS_2NUTS'")
replace('FR output housing requires hand support because its Guard cage moves; Guard/2M3screws/2nuts remain attached.', 'ALL output cages and the Guard stay supported by Deck;2Guard M3 fasteners remain untouched.')
replace('Lift bank+Cover+Guard together while Closed splice bodies/wires remain stationary, FR output splice hand-supported while its cage moves;', 'Lift bank+Cover together while all closed splice bodies/wires AND Guard remain fixed on Deck;')
replace("installed_changed_interfaces_source='servo-fuse-cover-main-service-r6/checks.json'", "installed_changed_interfaces_source='servo-fuse-guard-fixed-deck-native-r1/checks.json'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
