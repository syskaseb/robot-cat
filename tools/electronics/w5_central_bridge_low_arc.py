"""Start the bridge bend immediately, below the blocking high Pi crossing.

The former coarse160/180mm levels missed the exact lower feasible fillet
height. Preserve received W001/end geometry even if the bridge is rejected.
"""
from pathlib import Path
import w5_central_battery_s_plan as prior

source=prior.source
needle="            for h in (160,180,200,220):"
assert needle in source
source=source.replace(needle,"            for h in (math.ceil(max(aa['tip'][2],bb['tip'][2])+21+.5),):")
needle="            aa=chosen['W061_A'][0];bb=chosen['W061_B'][0];bridge=None;bridge_reasons=[]"
assert needle in source
source=source.replace(needle,"""            received_files=[]
            for name,shape in {'W001_FULL':whole_shape,'W001_CENTERLINE':whole_path,**{w:s for w,(q,s) in chosen.items() if w!='W001'}}.items():
                p=OUT/(name+'_RECEIVED.brep');shape.exportBrep(str(p));received_files.append(p)
            received_info=dict(whole_W001=full,ends={w:q for w,(q,s) in chosen.items()},placement=c,
                full_central_routes_complete=False,bridge_pending=True,selected=False,physical_pass=False,
                files={p.relative_to(ROOT).as_posix():sha(p) for p in received_files})
            save(OUT/'received-family.json',received_info)
"""+needle)
source=source.replace('pins += [S_WRAPPER,','pins += [BRIDGE_WRAPPER,S_WRAPPER,',1)
ctx=dict(prior.ctx,BRIDGE_WRAPPER=Path(__file__))
exec(compile(source,prior.prior.prior.prior.prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.ctx['ENDS'],ports=prior.ctx['ports'],placements=prior.ctx['placements'],
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.prior.prior.prior.prior.ROOT/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1')
if __name__=='__main__':ctx['main']()
