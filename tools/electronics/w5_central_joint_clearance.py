"""One coupled clearance layout, with explicit replaced PETG subfeatures.

G1 turns90 and shifts6mm so the W060 departing centre is beyond RL_P X54
with its OD3. G2 turns180 and shifts6mm inward to create bending room before
the retained W078 positive portal. Actual solid tests remain mandatory.
"""
from pathlib import Path
import w5_central_restraint_dependencies as prior


def placements(targets):
    return [dict(g1_centre=[72,5.5],g2_centre=[105,5.5],floor=109,
        shift={'G1':[6,0,0],'G2':[-6,0,0]},direction=-1,
        angles={'G1':90,'G2':180},bridge_changed_to_curved=True,
        port_exchange='G1.1/G1.2 same ground block',
        boundary_basis='RL_P Xmax54; W060 departing X57 OD3; G2 extra6mm bend distance before retained positive portal')]


source=prior.source
source=source.replace("shape.rotate(A.Vector(66 if name=='G1' else 111,5.5,109),A.Vector(0,0,1),c['angles'][name])",
    "shape.rotate(A.Vector(*(c['g1_centre'] if name=='G1' else c['g2_centre']),c['floor']),A.Vector(0,0,1),c['angles'][name])")
source=source.replace("printed={k:fixed.pop(k) for k in PRINTED if k in fixed}",
    "printed={k:fixed.pop(k) for k in PRINTED|{'main-positive-complete-r8/positive_portal_seat_DESIGN','main-positive-complete-r8/splice_seat_DESIGN'} if k in fixed}")
source=source.replace('pins += [DEPENDENCY_WRAPPER,','pins += [JOINT_WRAPPER,ROOT/"tools/electronics/main_positive_complete_r8.py",DEPENDENCY_WRAPPER,',1)
source=source.replace('time.monotonic()-tic>240','time.monotonic()-tic>60')
ctx=dict(prior.ctx,JOINT_WRAPPER=Path(__file__))
exec(compile(source,prior.prior.prior.prior.base.__file__,'exec'),ctx)
ctx.update(ENDS=prior.ctx['ENDS'],ports=prior.ctx['ports'],placements=placements,
    prefix=prior.ctx['prefix'],spec=prior.ctx['spec'],
    OUT=prior.prior.prior.ROOT/'hardware/electronics/full-cat/w5-central-joint-clearance-r1')
if __name__=='__main__':ctx['main']()
