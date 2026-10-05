"""Use a complete analytical W001 path, not mandatory 90-degree end elbows."""
from pathlib import Path
import w5_central_joint_clearance as prior

source=prior.source
begin=source.index('            # Qualify the complete battery path')
end=source.index("            aa=chosen['W061_A']",begin)
source=source[:begin]+'''            from w5_battery_parallel_s import route
            from w5_ground_network_r1 import from_recipe
            from w5_rounded_path import corner_offsets
            start=chosen['W001'][0]['edges'][0]['start']
            rr=route(start,targets['W001'])
            edges=[];bits=[]
            for edge in rr['edges']:
                e=Part.makeLine(A.Vector(*edge['start']),A.Vector(*edge['end'])) if edge['kind']=='line' else Part.Arc(A.Vector(*edge['start']),A.Vector(*edge['mid']),A.Vector(*edge['end'])).toShape()
                edges.append(e)
                bits.append(Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(1.55,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False))
            whole_path=Part.Wire(edges);whole_shape=Part.makeCompound(bits)
            assert whole_path.isValid() and all(s.isValid() and len(s.Solids)==1 for s in bits)
            assert abs(whole_path.Length-rr['body_mm'])<1e-7
            owner=hit(whole_shape,{**fixed,**family,**{w:s for w,(q,s) in chosen.items() if w!='W001'}})
            if owner or whole_path.Length+19>150:
                attempts.append(dict(placement=c,blocked='whole_W001_S_not_qualified',owner=owner,nominal_mm=whole_path.Length+19));continue
            full=dict(recipe=rr,body_mm=whole_path.Length,nominal_mm=whole_path.Length+19,
                source_straight_prototype_mm=6,source_outward_axis=[0,-1,0])
            chosen['W001']=(dict(rr,whole_path=True),whole_shape)
'''+source[end:]
source=source.replace('pins += [JOINT_WRAPPER,','pins += [S_WRAPPER,ROOT/"tools/electronics/w5_battery_parallel_s.py",JOINT_WRAPPER,',1)
ctx=dict(prior.ctx,S_WRAPPER=Path(__file__))
exec(compile(source,prior.prior.prior.prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.ctx['ENDS'],ports=prior.ctx['ports'],placements=prior.placements,
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.prior.prior.prior.ROOT/'hardware/electronics/full-cat/w5-central-battery-s-plan-r1')
if __name__=='__main__':ctx['main']()
