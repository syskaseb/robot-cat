"""Allocate the outward pair in one source-adjacent zone, not a global grid.

The old unchanged envelopes cannot provide six departures. Four source-side
G1 anchors and two G2 anchors are checked jointly with all eight ends, both
bridge ends, a complete <=150mm W001 and a complete R21 bridge.
"""
from pathlib import Path
import math
import w5_central_outward_plan as prior


def placements(targets):
    candidates=[]
    for x in (40,60):
        for z in (109,129):
            for gx in (100,120):
                c=dict(g1_centre=[x,60],g2_centre=[gx,60],floor=z,
                    shift={'G1':[x-66,54.5,z-109],'G2':[gx-111,54.5,z-109]},direction=-1,
                    bridge_changed_to_curved=True,port_exchange='G1.1/G1.2 same ground block')
                # Rotated physical G1.1 cage is on the source-facing Y edge.
                endpoint=[x-11,75,z+4.5]
                c['battery_straight_lower_bound_plus19']=math.dist(endpoint,targets['W001'])+19
                if c['battery_straight_lower_bound_plus19']<=150:candidates.append(c)
    return sorted(candidates,key=lambda c:c['battery_straight_lower_bound_plus19'])


source=prior.source
needle='pins += [Path(__file__),'
assert needle in source
source=source.replace(needle,'pins += [CURRENT_WRAPPER,OUTWARD_WRAPPER,ROOT/"tools/electronics/w5_path_length.py",Path(__file__),',1)
ctx=dict(prior.ctx,CURRENT_WRAPPER=Path(__file__),OUTWARD_WRAPPER=Path(prior.__file__))
exec(compile(source,prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.ends,ports=prior.ports,placements=placements,
    prefix=lambda d,w,o:prior.prior.base.prefix(d,'W061' if w.startswith('W061_') else w,o),
    spec=lambda w:prior.prior.base.spec('W061' if w.startswith('W061_') else w),
    OUT=prior.ROOT/'hardware/electronics/full-cat/w5-central-source-zone-r1')
if __name__=='__main__':ctx['main']()
