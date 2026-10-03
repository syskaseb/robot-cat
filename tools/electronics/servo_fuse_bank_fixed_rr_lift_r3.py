"""Whole withdrawal after ALL twelve bottom-open native output exits.

R2's closed-rib conflict is preserved. Guard stays attached to the moving
bank; its two screws/nuts move with it. Two bank-mounted FR source strain
ties are explicitly cut before lifting. No stationary wire is waived.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r2.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='lift_r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-bank-fixed-rr-lift-r2','servo-fuse-bank-fixed-rr-lift-r3')
replace('servo-fuse-rr-mount-pair-native-r1/checks.json','servo-fuse-output-rib-exits-native-r1/checks.json')
replace('servo-fuse-rr-mount-pair-native-r1/BankRight_WORLD.brep','servo-fuse-output-rib-exits-native-r1/BankRight_WORLD.brep')
replace("'BankLeft':owners.pop(left)","'BankLeft':load('hardware/cad/studies/servo-fuse-output-rib-exits-native-r1/BankLeft_WORLD.brep')")
replace("    owners.pop(right)","""    owners.pop(right);owners.pop(left)
    module['FRReturnGuard']=owners.pop('FRReturnGuard')
    attached=[k for k in owners if k.startswith('FRHardware/')]
    assert len(attached)==4,attached
    for k in attached:module[k]=owners.pop(k)
    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r2.py')""")
replace("        # Only explicit released physical parts, not arbitrary collisions.","""        # Exactly two FR source ties belong to moving BankRight seats.
        if key.startswith('FRTie/'):
            omitted.append(key);del owners[key];continue
        # Only explicit released physical parts, not arbitrary collisions.""")
replace("    assert len(parked)==24,parked","    assert len([k for k in omitted if k.startswith('FRTie/')])==10\n    assert len(parked)==24,parked")
replace("    lifts=[2,10,100];completed=[]","    lifts=[2,10,100];completed=[]")
replace("installed_changed_interfaces_source='servo-fuse-rr-mount-pair-r2/checks.json'","installed_changed_interfaces_source='servo-fuse-output-rib-exits-native-r1/checks.json',FR_guard_owner='MOVING_BANK_WITH_2SCREWS_2NUTS',extra_FR_source_ties_cut=2")
replace("Unbolt4bank+4Cover mounts. Lift bank+Cover together", "Cut2FR source insulation ties; Guard/2M3screws/2nuts remain attached. Unbolt4bank+4Cover mounts. Lift bank+Cover+Guard together")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
