"""Receive the NEW matched fourth mount and check whole-module withdrawal.

R1 zero-pose contacts are rejected/preserved. Do not repeat its geometry.
Installed changes are covered by mount-pairR2 and its exact native match;
check translated2/10/100mm whole bank+Cover against ALL fixed owners here.
Save the FIRST real conflict immediately, not minutes of doomed later poses.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-bank-fixed-rr-lift-r1','servo-fuse-bank-fixed-rr-lift-r2')
replace('servo-fuse-rr-fixed-station-native-r1/checks.json','servo-fuse-rr-mount-pair-native-r1/checks.json')
replace('servo-fuse-rr-fixed-station-native-r1/Deck_WORLD.brep','servo-fuse-rr-mount-pair-native-r1/Deck_WORLD.brep')
replace('servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep','servo-fuse-rr-mount-pair-native-r1/BankRight_WORLD.brep')
replace("    assert len(parked)==24,parked", "    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r1.py')\n    assert len(proof['exports'])==2 and all(r['relocated_reopen'] for r in proof['exports'])\n    assert len(parked)==24,parked")
replace("        pairs+=1\n        try:", "        pairs+=1\n        if key=='CandidateDeck':print('WHOLE_LIFT_DECK_PAIR',phase,name,flush=True)\n        try:")
replace("                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))", "                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))\n                print('WHOLE_LIFT_FIRST_CONFLICT',phase,name,key,c.Volume,flush=True)")
replace("    lifts=[0,2,5,10,30,60,100]", "    lifts=[2,10,100];completed=[]")
replace("            for key,t in owners.items():check('sampled_lift_'+str(lift),name,q,key,t)\n        print('FIXED_RR_BANK_LIFT_SAMPLE',lift,len(hits),len(errors),flush=True)", """            for key,t in owners.items():
                check('sampled_lift_'+str(lift),name,q,key,t)
                if hits or errors:break
            if hits or errors:break
        print('FIXED_RR_BANK_LIFT_SAMPLE',lift,len(hits),len(errors),flush=True)
        if hits or errors:break
        completed.append(lift)""")
replace("sampled_lifts_mm=lifts,hits=hits", "requested_lifts_mm=lifts,completed_clear_lifts_mm=completed,early_rejection=bool(hits or errors),installed_changed_interfaces_source='servo-fuse-rr-mount-pair-r2/checks.json',sampled_lifts_mm=lifts,hits=hits")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
