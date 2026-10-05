"""Replace obsolete endpoint restraints with explicit reconstruction obligations.

G1BAT is the former W001 tie/seat. G1_input and Deck_input are the former
upstream W060 ties. Those wires are replaced as whole paths; their old bands
cannot be treated as immutable obstacles. Retain downstream MAIN ties and
all source fasteners, electrical insulation, purchased bodies and wires.
"""
from pathlib import Path
import w5_central_orientation_plan as prior

source=prior.source
needle="        if k in {'G1_NEW_BODY','G2_NEW_BODY'} or"
assert needle in source
source=source.replace(needle,"        if k.startswith(('Source/G1BAT_','Input/G1_input_tie_','Input/Deck_input_tie_')) or k in {'G1_NEW_BODY','G2_NEW_BODY'} or",1)
source=source.replace('pins += [ORIENTATION_WRAPPER,',
    'pins += [DEPENDENCY_WRAPPER,ROOT/"tools/electronics/battery_feed_return_finish_r2.py",ROOT/"tools/electronics/main_input_return_finish_r2.py",ORIENTATION_WRAPPER,',1)
source=source.replace("body_envelopes_and_cage_registration_provisional=True,", "obsolete_restraints_require_new_native_supports=True,body_envelopes_and_cage_registration_provisional=True,")
ctx=dict(prior.ctx,DEPENDENCY_WRAPPER=Path(__file__))
exec(compile(source,prior.prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.prior.ends,ports=prior.prior.ports,placements=prior.placements,
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.prior.ROOT/'hardware/electronics/full-cat/w5-central-restraint-dependencies-r1')
if __name__=='__main__':ctx['main']()
