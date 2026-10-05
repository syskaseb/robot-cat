"""One outward-facing central family, retaining the received leg network.

No positional grid. Rotate both cage faces outward in their existing body
envelopes. Exchange G1 logical .1/.2 physical cages on the same ground block.
The bridge must be a complete new curved wire, never the old straight bar.
"""
from pathlib import Path
from itertools import product
import w5_central_space_solver_r2 as prior
from w5_path_length import recipe_length

ROOT=prior.base.ROOT
ends=dict(prior.base.ENDS,W061_A='G1.5',W061_B='G2.1')


def ports():
    p=prior.base.ports()
    p['G1.1'],p['G1.2']=p['G1.2'],p['G1.1']
    return p


def placements(targets):
    return [dict(g1_centre=[66,5.5],g2_centre=[111,5.5],floor=109,
        shift={'G1':[0,0,0],'G2':[0,0,0]},direction=-1,
        bridge_changed_to_curved=True,port_exchange='G1.1/G1.2 same ground block')]


source=prior.source
source=source.replace("received=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3/checks.json'", "received=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r3/checks.json'")
needle="        p=received.parent/(r['wire']+'_WORLD.brep');fixed[r['wire']]=Part.read(str(p));pins.append(p);reused.append(r['wire'])"
assert needle in source
source=source.replace(needle,"""        candidates=[ROOT/('hardware/electronics/full-cat/'+folder)/(r['wire']+'_WORLD.brep') for folder in ('w5-branch-joint-routes-r3','w5-branch-joint-routes-r2','w5-branch-joint-routes-r1','w5-coupled-corridors-r3')]
        p=next(p for p in candidates if p.exists())
        fixed[r['wire']]=Part.read(str(p));pins.append(p);reused.append(r['wire'])""")
source=source.replace('assert len(reused)==22','assert len(reused)==28')
source=source.replace("    targets.update(W001=[55.5,75,70],W060=[132.5,0,95])", "    targets.update(W001=[55.5,75,70],W060=[132.5,0,95],W061_A=[120.5,5.5,113.5],W061_B=[55,5.5,113.5])")
source=source.replace("        for option in ('up','down','left','right'):","        for option in (('up',) if w.startswith('W061_') else ('up','down','left','right')):")
lines=source.splitlines()
source='\n'.join(l for l in lines if not l.strip().startswith(('edge=Part.makeLine(A.Vector(x+c[','family[\'W061\']=')))+'\n'
source=source.replace('            def joint(i):\n                if i==len(ordered):return True',
    '            nodes=0\n            def joint(i):\n                nonlocal nodes\n                nodes+=1\n                if nodes>2048 or time.monotonic()-tic>240:return False\n                if i==len(ordered):return True')
source=source.replace('                path,whole=from_recipe(A,Part,recipe_full)',
    "                if recipe_length(recipe_full)+19>150:\n                    last_reasons.append('nominal_above150mm');continue\n                path,whole=from_recipe(A,Part,recipe_full)")
needle="            solution=dict(placement=c,whole_W001=full,ends="
assert needle in source
source=source.replace(needle,"""            aa=chosen['W061_A'][0];bb=chosen['W061_B'][0];bridge=None;bridge_reasons=[]
            for h in (160,180,200,220):
                middle=[aa['tip'],[aa['tip'][0],aa['tip'][1],h],[bb['tip'][0],bb['tip'][1],h],bb['tip']]
                try:corner_offsets(middle,21)
                except AssertionError:continue
                rr=dict(wire='W061',a=aa,b=bb,middle=middle,radius_mm=21)
                bp,bs=from_recipe(A,Part,rr)
                owner=hit(bs,{**fixed,**family,'W001_FULL':whole_shape,**{w:s for w,(q,s) in chosen.items() if not w.startswith('W061_') and w!='W001'}})
                if owner:bridge_reasons.append(owner);continue
                bridge=dict(recipe=rr,body_mm=bp.Length,strip_allowance_mm=25,stock_reconciliation_pending=True)
                bridge_shape=bs;bridge_path=bp;break
            if bridge is None:
                attempts.append(dict(placement=c,blocked='whole_bridge_not_qualified',reasons=bridge_reasons));continue
"""+needle)
source=source.replace('solution=dict(placement=c,whole_W001=full,ends=', 'solution=dict(placement=c,whole_W001=full,whole_W061=bridge,ends=')
source=source.replace('solution_shapes.update(W001_FULL=whole_shape,W001_CENTERLINE=whole_path)',
    'solution_shapes.update(W001_FULL=whole_shape,W001_CENTERLINE=whole_path,W061_FULL=bridge_shape,W061_CENTERLINE=bridge_path)')
source=source.replace('pins += [Path(__file__),RECEIVED', 'pins += [Path(__file__),WRAPPER,ROOT/"tools/electronics/w5_path_length.py",RECEIVED')
ctx=dict(__name__='outward_definition',__file__=prior.base.__file__,product=product,recipe_length=recipe_length,WRAPPER=Path(__file__))
exec(compile(source,prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=ends,ports=ports,placements=placements,
    prefix=lambda d,w,o:prior.base.prefix(d,'W061' if w.startswith('W061_') else w,o),
    spec=lambda w:prior.base.spec('W061' if w.startswith('W061_') else w),
    OUT=ROOT/'hardware/electronics/full-cat/w5-central-outward-plan-r1')
if __name__=='__main__':ctx['main']()
