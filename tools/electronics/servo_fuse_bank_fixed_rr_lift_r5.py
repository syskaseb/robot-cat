"""Whole common module after BOTH source FR grips become stationary.

Preserve the same stationary wires and their two FR source ties. Guard and
its four fasteners still belong to the moving bank. Use all three accepted
native parts, not a preflight candidate or an old Cover.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='lift_r4_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-bank-fixed-rr-lift-r4','servo-fuse-bank-fixed-rr-lift-r5')
replace('servo-fuse-output-rib-exits-native-r3/checks.json','servo-fuse-fr-source-fixed-deck-native-r1/checks.json')
replace('servo-fuse-rr-mount-pair-native-r1/Deck_WORLD.brep','servo-fuse-fr-source-fixed-deck-native-r1/Deck_WORLD.brep')
replace('servo-fuse-output-rib-exits-native-r3/BankRight_WORLD.brep','servo-fuse-fr-source-fixed-deck-native-r1/BankRight_WORLD.brep')
replace("'Cover':owners.pop('ModifiableCover')", "'Cover':load('hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r1/Cover_WORLD.brep')")
replace('    owners.pop(right);owners.pop(left)', "    owners.pop(right);owners.pop(left);owners.pop('ModifiableCover')")
replace("        if key.startswith('FRTie/'):\n            omitted.append(key);del owners[key];continue", "        # FRTie source loops now remain stationary with their Deck seats.")
replace("    assert len([k for k in omitted if k.startswith('FRTie/')])==10", "    assert len([k for k in owners if k.startswith('FRTie/')])==10")
replace("assert len(proof['exports'])==2", "assert len(proof['exports'])==3")
replace("installed_changed_interfaces_source='servo-fuse-fr-source-fixed-deck-native-r1/checks.json'", "installed_changed_interfaces_source='servo-fuse-fr-source-fixed-deck-r3/checks.json'")
replace('extra_FR_source_ties_cut=2','extra_FR_source_ties_cut=0')
replace('Cut2FR source insulation ties; Guard/2M3screws/2nuts remain attached.', 'FRsource grooves/2ties remain fixed onDeck; Guard/2M3screws/2nuts remain attached.')
replace("    assert len(parked)==24,parked", "    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r4.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r4.py')\n    assert proof['unchanged_source_grips_and_wires']\n    assert len(parked)==24,parked")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
