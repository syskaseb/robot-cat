"""Shared release with segmented native Cover and49explicit tie releases.

Body/source/output loops are sacrificial service fasteners. Keep the four
lower input ties and all closed purchased bodies/wires on their supported
Deck positions. FR output cage MOVES with Guard, not a fixed Deck cage.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r8.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r8_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r8','servo-fuse-bank-fixed-rr-lift-r9')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-cover-rr-fixed-service-r1','servo-fuse-cover-main-service-r2')
marker='    assert len(parked)==24,parked'
replace(marker,"""    released_body_source=[k for k in owners if k.startswith(('FRTie/','RLTie/','RRTie/','PWagoTie/','BodyTie/'))]
    assert len(released_body_source)==80,released_body_source
    for k in released_body_source:omitted.append(k);del owners[k]
    assert len([k for k in owners if k.startswith('RetainedGrip/') and 'TIE' in k])==20
    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r8.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r8.py')
    assert len(parked)==24,parked""")
replace('total_service_ties_cut=33','total_service_ties_cut=49,body_source_PWAGO_ties_cut=16')
replace('P_WAGO_body_ties_stationary=4','P_WAGO_body_ties_stationary=0,P_WAGO_closed_bodies_stationary=4')
replace('extra_FR_source_ties_cut=0','extra_FR_source_ties_cut=2')
replace('Cut9FR/RL/RR output-cage/insulation ties, keep their closed splice bodies/wires seated on fixed saddles. FRsource grooves/2ties remain fixed onDeck;',
        'Cut9output,6source,6MTA-body and4P-WAGO-body straps after24TE straps. Keep closed purchased bodies and insulation on their Deck support surfaces; FR output housing requires hand support because its Guard cage moves;')
replace('ALL output wires/splice bodies stay seated on fixed Deck, released ties absent. Replace33TE/output ties after assembly. No WAGO opening or wire parking.',
        'Closed splice bodies/wires remain stationary, FR output splice hand-supported while its cage moves; all49released loops absent. Replace49ties after assembly. No WAGO opening or relocated wire route.')
replace("            for key,t in owners.items():", "            for key,t in sorted(owners.items(),key=lambda item:item[0]=='CandidateDeck'):")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
