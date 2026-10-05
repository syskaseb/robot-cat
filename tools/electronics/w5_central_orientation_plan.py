"""Joint cardinal orientation plan in the original central mounting zone.

Retain body centres and all received branch paths. Check the remaining
cardinal face combinations as complete families, not one-wire nudges.
"""
from pathlib import Path
from itertools import product
import math
import w5_central_outward_plan as prior


def placements(targets):
    return [dict(g1_centre=[66,5.5],g2_centre=[111,5.5],floor=109,
                 shift={'G1':[0,0,0],'G2':[0,0,0]},direction=-1,
                 angles={'G1':a,'G2':b},bridge_changed_to_curved=True,
                 port_exchange='G1.1/G1.2 same ground block')
            for a,b in product((0,90,180,270),repeat=2) if (a,b) not in ((0,0),(180,180))]


source=prior.source
needle="        blocked=None"
assert needle in source
source=source.replace(needle,"""        for name,shape in family.items():
            shape.rotate(A.Vector(66 if name=='G1' else 111,5.5,109),A.Vector(0,0,1),c['angles'][name])
        blocked=None""",1)
start=source.index("                    if c['direction']==-1:")
end=source.index('                    moved.translate(A.Vector(*delta))',start)
source=source[:start]+'''                    name=ENDS[w].split('.')[0];angle=c['angles'][name]
                    cx=66 if name=='G1' else 111
                    moved.rotate(A.Vector(cx,5.5,113.5),A.Vector(0,0,1),angle)
                    co=math.cos(math.radians(angle));si=math.sin(math.radians(angle))
                    def xy(p):return [cx+co*(p[0]-cx)-si*(p[1]-5.5),5.5+si*(p[0]-cx)+co*(p[1]-5.5),p[2]]
                    for e in q['edges']:
                        for field in ('start','mid','end'):
                            if field in e:e[field]=xy(e[field])
                    q['tip']=xy(q['tip']);tx,ty,tz=q['tangent']
                    q['tangent']=[co*tx-si*ty,si*tx+co*ty,tz]
'''+source[end:]
source=source.replace('pins += [Path(__file__),','pins += [ORIENTATION_WRAPPER,OUTWARD_WRAPPER,ROOT/"tools/electronics/w5_path_length.py",Path(__file__),',1)
ctx=dict(prior.ctx,ORIENTATION_WRAPPER=Path(__file__),OUTWARD_WRAPPER=Path(prior.__file__))
exec(compile(source,prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.ends,ports=prior.ports,placements=placements,
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.ROOT/'hardware/electronics/full-cat/w5-central-orientation-plan-r1')
if __name__=='__main__':ctx['main']()
