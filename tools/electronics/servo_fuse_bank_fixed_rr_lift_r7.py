"""Shared service after releasing the nine fixed output-cage insulation ties.

No new print or route. Disconnect power, cut24TE ties and the three ties at
each FR/RL/RR output splice before unbolting. Keep splice bodies/wires seated
on their fixed Deck saddles; no WAGO lever operation or wire/cage parking.
The6source ties and6MTA body ties remain installed. Replace33ties afterwards.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r6.py')
ns=dict(__file__=str(parent),__name__='lift_r6_definition_only')
exec(compile(parent.read_text(encoding='utf-8'),str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r6','servo-fuse-bank-fixed-rr-lift-r7')
marker="    assert len(parked)==24,parked"
assert marker in code
code=code.replace(marker,"""    # Explicit service release of9physical straps, represented by45pieces.
    output_ties=[k for k in owners if k.startswith(('FRNewTie/','CurrentRear/')) and 'Tie' in k]
    assert len(output_ties)==45,output_ties
    for k in output_ties:omitted.append(k);del owners[k]
    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r6.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r6.py')
    assert len(parked)==24,parked""")
code=code.replace("RR_cages_opened=False,", "RR_cages_opened=False, output_cage_and_insulation_ties_cut=9, total_service_ties_cut=33, output_splice_bodies_and_wires_stationary=True,")
old='FRsource grooves/2ties remain fixed onDeck; Guard/2M3screws/2nuts remain attached.'
assert old in code
code=code.replace(old,'Cut9FR/RL/RR output-cage/insulation ties, keep their closed splice bodies/wires seated on fixed saddles. FRsource grooves/2ties remain fixed onDeck; Guard/2M3screws/2nuts remain attached.')
code=code.replace('ALL RR output wires/cage/3ties stay fixed.','ALL output wires/splice bodies stay seated on fixed Deck, released ties absent. Replace33TE/output ties after assembly. No WAGO opening or wire parking.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
