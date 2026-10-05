"""Separate outer outbound flights from lower final leg approaches.

Only four unresolved nets are rebuilt. Reserve every leg target's straight
vertical approach so a new net cannot consume a future neighbour's ending.
"""
from pathlib import Path
import json, math
import w5_branch_outer_corridors as previous
from w5_rounded_path import corner_offsets

ROOT=previous.ROOT
RECEIVED=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r2/checks.json'
received=json.loads(RECEIVED.read_text(encoding='utf-8'))
todo={r['wire'] for r in received['unresolved']}
assert todo=={'W006','W010','W034','W014'}
rows=previous.base.prior.contract()[1]
targets={r['wire']:r['target'] for r in rows if 'retained_moving_candidate_mm' in r}


def variants(row):
    a=previous.base.plan['choices'][row['wire']]['prefix'];p=a['tip'];q=row['target'];r=row['radius_mm']
    lanes=(-170,-185) if row['a_datum']['outward_axis'][0]<0 else (235,250)
    for upper in (214,226,238):
        for lower in (150,165,180):
            for lane in lanes:
                for side in (0,-25,25):
                    # A lower final tier avoids the accepted diagonal flights.
                    pts=[p,[p[0],p[1],upper],[lane,p[1],upper],
                         [lane,q[1]+side,upper],[lane,q[1]+side,lower],
                         [q[0],q[1]+side,lower],[q[0],q[1],lower],q]
                    clean=[]
                    for v in pts:
                        if not clean or math.dist(v,clean[-1])>1e-6:clean.append(v)
                    try:corner_offsets(clean,r)
                    except AssertionError:continue
                    yield dict(row,a=a,b=None,middle=clean)


source=previous.source
needle="        if not p.exists():p=ORIGINAL.parent/(r['wire']+'_WORLD.brep')"
assert needle in source
source=source.replace(needle,"""        if not p.exists():p=PRIOR_BRANCH.parent/(r['wire']+'_WORLD.brep')
        if not p.exists():p=ORIGINAL.parent/(r['wire']+'_WORLD.brep')""")
source=source.replace('    pins += [PLAN,OLD,WRAPPER,ORIGINAL,PREVIOUS_WRAPPER]',
    '    pins += [PLAN,OLD,WRAPPER,ORIGINAL,PREVIOUS_WRAPPER,PRIOR_BRANCH,OUTER_WRAPPER]')
source=source.replace("    save(OUT/'allocation.json'", """    for w,p in TARGETS.items():
        fixed['TARGET/'+w]=Part.makeCylinder(spec(w)['OD_mm']/2,115,A.Vector(*p))
    save(OUT/'allocation.json'""")
source=source.replace("key=='RESERVED/'+str(current_wire)","key in ('RESERVED/'+str(current_wire),'TARGET/'+str(current_wire))")
ctx=dict(previous.ctx,OLD=RECEIVED,PRIOR_BRANCH=previous.RECEIVED,
    OUTER_WRAPPER=Path(previous.__file__),WRAPPER=Path(__file__),
    RETAINED=received['accepted'],TODO=todo,TARGETS=targets)
exec(compile(source,previous.base.prior.base.__file__,'exec'),ctx)
ctx['contract']=previous.base.prior.contract
ctx['variants']=variants
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r3'
if __name__=='__main__':ctx['main']()
