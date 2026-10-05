"""One coarse-to-fine refinement driven by the complete battery-lead failure.

Refine only the jointly clear family neighborhoods found by r2. All eight
ends, both bodies, bridge and complete150mm W001 remain required. Do not
repeat any pose already rejected by the coarse search.
"""
from pathlib import Path
from itertools import product
import json,math
import w5_central_space_solver_r2 as prior

ROOT=prior.base.ROOT
PROOF=ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r2/checks.json'

def placements(targets):
    proof=json.loads(PROOF.read_text(encoding='utf-8'))
    assert not proof['errors'] and proof['solution'] is None
    seeds=[r['placement'] for r in proof['attempts'] if r.get('blocked')=='whole_W001_not_qualified']
    assert seeds,'No evidence-backed neighborhood to refine'
    key=lambda p:(tuple(p['g1_centre']),tuple(p['g2_centre']),p['floor'],p['direction'])
    visited={key(r['placement']) for r in proof['attempts']};result={};datum=prior.base.ports()
    for seed in seeds:
        for dx,dy,dz,dgap in product(range(-15,16,5),range(-15,16,5),range(-15,16,5),range(-10,11,5)):
            x=seed['g1_centre'][0]+dx;y=seed['g1_centre'][1]+dy;z=seed['floor']+dz
            direction=seed['direction'];gap=abs(seed['g2_centre'][0]-seed['g1_centre'][0])+dgap;gx=x+direction*gap
            if gx+9.5>140 or gx-9.5 < -98:continue
            shift={'G1':[x-66,y-5.5,z-109],'G2':[gx-111,y-5.5,z-109]};points={}
            for w,end in prior.base.ENDS.items():
                name=end.split('.')[0];p=list(datum[end]['point_mm'])
                if direction==-1:p[:2]=[2*(66 if name=='G1' else 111)-p[0],11-p[1]]
                points[w]=[v+d for v,d in zip(p,shift[name])]
            if math.dist(points['W001'],targets['W001'])+19>150:continue
            if math.dist(points['W003'],targets['W003'])+41>300:continue
            row=dict(g1_centre=[x,y],g2_centre=[gx,y],floor=z,shift=shift,direction=direction,
                lower_bound_cost_mm=sum(math.dist(points[w],targets[w]) for w in prior.base.ENDS),bridge_mm=gap-20.5,
                refinement_seed=seed,refinement_priority=math.dist(points['W001'],targets['W001'])+2*abs(dz)+.5*abs(dy)+.2*abs(dgap))
            if key(row) not in visited:result[key(row)]=row
    return sorted(result.values(),key=lambda p:(p['refinement_priority'],p['lower_bound_cost_mm']))

source=prior.source.replace("pins += [Path(__file__),", "pins += [ROOT/'tools/electronics/w5_central_space_solver_r3.py',ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r2/checks.json',Path(__file__),")
ctx=dict(__name__='central_space_r3_definition',__file__=prior.base.__file__,product=product)
exec(compile(source,prior.base.__file__,'exec'),ctx)
ctx['placements']=placements
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r3'
if __name__=='__main__':ctx['main']()
