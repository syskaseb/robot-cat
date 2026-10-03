"""Full shared release using the intact Cover with whole W053 passage.

Reuse only R9's fully checked2mm banks, not its rejected Cover or unchecked
Guard. All higher poses are new whole-owner checks. No collider exemptions.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r9.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r9_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r9','servo-fuse-bank-fixed-rr-lift-r10')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-cover-main-service-r2','servo-fuse-cover-main-service-r6')
marker='    assert len(parked)==24,parked'
replace(marker,"""    previouspath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r9/checks.json'
    pins[previouspath.relative_to(ROOT).as_posix()]=sha(previouspath)
    previous=json.loads(previouspath.read_text(encoding='utf-8'))
    assert len(previous['hits'])==1 and previous['hits'][0]['part']=='Cover' and previous['hits'][0]['owner']=='W053/extension' and not previous['errors']
    census=json.loads((previouspath.parent/'owner-census.json').read_text(encoding='utf-8'))
    assert census['fixed']==list(owners) and census['removed']==omitted and census['parked']==parked
    # The only geometry replacement is Cover. Verify identical pinned files
    # for the native banks, Deck, Guard, every retained/released wire and tie.
    for rel,h in previous['source_sha256'].items():
        if rel in pins and not 'servo-fuse-cover-main-service-r2' in rel:assert pins[rel]==h,rel
    assert len(parked)==24,parked""")
replace("        for name,s in module.items():", "        for name,s in module.items():\n            if lift==2 and name in ('BankRight','BankLeft'):continue")
replace("installed_changed_interfaces_source='servo-fuse-cover-main-service-r6/checks.json'", "installed_changed_interfaces_source='servo-fuse-cover-main-service-r6/checks.json',reused_R9_clear_at_2mm=['BankRight','BankLeft'],reused_scope='Identical owners/omissions/wires/nativebanks, fully checked before R9Cover conflict; not Guard or Cover'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
