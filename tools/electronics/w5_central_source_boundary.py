"""Place the whole source family beyond the measured saved obstacle bounds.

Saved CAD bound (not physical measurement): XA02 maxY=50.588873254751405,
RL_P maxY=49.5. G1 half-depth18.5 plus1mm planning clearance gives
ceil(50.588873254751405+18.5+1)=71. Material tests still decide acceptance.
"""
from pathlib import Path
import math
import w5_central_source_zone as prior


def placements(targets):
    y=math.ceil(50.588873254751405+18.5+1)
    return [dict(g1_centre=[60,y],g2_centre=[100,y],floor=109,
        shift={'G1':[-6,y-5.5,0],'G2':[-11,y-5.5,0]},direction=-1,
        bridge_changed_to_curved=True,port_exchange='G1.1/G1.2 same ground block',
        boundary_basis={'XA02_saved_maxY':50.588873254751405,'RL_P_saved_maxY':49.5,
                        'G1_half_depth':18.5,'planning_clearance':1})]


source=prior.source.replace('pins += [CURRENT_WRAPPER,','pins += [BOUNDARY_WRAPPER,CURRENT_WRAPPER,',1)
ctx=dict(prior.ctx,BOUNDARY_WRAPPER=Path(__file__))
exec(compile(source,prior.prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.prior.ends,ports=prior.prior.ports,placements=placements,
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.prior.ROOT/'hardware/electronics/full-cat/w5-central-source-boundary-r1')
if __name__=='__main__':ctx['main']()
