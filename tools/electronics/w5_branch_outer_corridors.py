"""Complete the five blocked branch flights through dedicated outer corridors.

Keep the joint 24-departure allocation and every received accepted full path.
Only new outer-X doglegs are attempted, not rejected direct flights.
"""
from pathlib import Path
import json, math
import w5_branch_joint_routes as base
from w5_rounded_path import corner_offsets

ROOT=base.ROOT
RECEIVED=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r1/checks.json'
received=json.loads(RECEIVED.read_text(encoding='utf-8'))
todo={r['wire'] for r in received['unresolved']}
assert todo=={'W007','W006','W010','W034','W014'}


def variants(row):
    w=row['wire'];r=row['radius_mm']
    aa=[base.plan['choices'][w]['prefix']] if w in base.plan['choices'] else [base.prior.base.prefix(row['a_datum'],w,o) for o in ('left','right','up')]
    bb=[base.prior.base.prefix(row['b_datum'],w,o) for o in ('left','right','up')] if 'b_datum' in row else [None]
    outward=row['a_datum']['outward_axis'][0]
    lanes=(-175,-195,-215) if outward<0 else (245,265,285)
    for a in aa:
        for b in bb:
            p=a['tip'];q=b['tip'] if b else row['target']
            for h in (214,226,238,250):
                for lane in lanes:
                    # Leave the common upright plane before changing Y.
                    # Return from outside to the distinct endpoint X.
                    points=[p,[p[0],p[1],h],[lane,p[1],h],[lane,q[1],h],[q[0],q[1],h],q]
                    clean=[]
                    for v in points:
                        if not clean or math.dist(v,clean[-1])>1e-6:clean.append(v)
                    try:corner_offsets(clean,r)
                    except AssertionError:continue
                    yield dict(row,a=a,b=b,middle=clean)


source=base.source
needle="        p=OLD.parent/(r['wire']+'_WORLD.brep');fixed[r['wire']]=Part.read(str(p));pins.append(p)"
assert needle in source
source=source.replace(needle,"""        p=OLD.parent/(r['wire']+'_WORLD.brep')
        if not p.exists():p=ORIGINAL.parent/(r['wire']+'_WORLD.brep')
        fixed[r['wire']]=Part.read(str(p));pins.append(p)""")
source=source.replace('    pins += [PLAN,OLD,WRAPPER]', '    pins += [PLAN,OLD,WRAPPER,ORIGINAL,PREVIOUS_WRAPPER]')
ctx=dict(base.ctx,ORIGINAL=base.OLD,PREVIOUS_WRAPPER=Path(base.__file__),OLD=RECEIVED,
    WRAPPER=Path(__file__),RETAINED=received['accepted'],TODO=todo,CHANGED_PREFIX=set())
exec(compile(source,base.prior.base.__file__,'exec'),ctx)
ctx['contract']=base.prior.contract
ctx['variants']=variants
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r2'
if __name__=='__main__':ctx['main']()
