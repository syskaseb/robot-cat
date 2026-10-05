"""Correct whole-network search direction and reject blocked ends once.

R2 could explore the same obstructed central end repeatedly because four
return nets started at the leg block in the electrical graph. Orient those
recipes from the constrained central block. Cache exact endpoint checks;
do not spend full-route CAD on a candidate with a blocked end preparation.
"""
from pathlib import Path
import w5_coupled_corridors as base
import w5_coupled_corridors_r2 as row_plan

def contract():
    bodies,rows,preserved,pins=row_plan.contract()
    for r in rows:
        if r['wire'] in ('W025','W036','W062','W063') and r['b_end'].startswith(('G1.','G2.')):
            r['a_end'],r['b_end']=r['b_end'],r['a_end']
            r['a_datum'],r['b_datum']=r['b_datum'],r['a_datum']
    pins.append(Path(__file__))
    return bodies,rows,preserved,pins


source=Path(base.__file__).read_text(encoding='utf-8')
needle='    accepted=[]; unresolved=[]; errors=[]'
assert needle in source
source=source.replace(needle,'''    endpoint_cache={}
    def endpoint_hit(prefix,wire):
        if prefix is None:return None
        cache_key=(wire,json.dumps(prefix['edges'],sort_keys=True))
        if cache_key not in endpoint_cache:
            bits=[]
            for edge in prefix['edges']:
                e=Part.makeLine(A.Vector(*edge['start']),A.Vector(*edge['end'])) if edge['kind']=='line' else Part.Arc(A.Vector(*edge['start']),A.Vector(*edge['mid']),A.Vector(*edge['end'])).toShape()
                section=Part.Wire([Part.makeCircle(spec(wire)['OD_mm']/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
                bits.append(Part.Wire([e]).makePipeShell([section],True,False))
            endpoint_cache[cache_key]=contact(Part.makeCompound(bits))
        return endpoint_cache[cache_key]
    accepted=[]; unresolved=[]; errors=[]''')
needle='            attempted+=1\n            try:path,shape=sweep.from_recipe(A,Part,candidate)'
assert needle in source
source=source.replace(needle,'''            attempted+=1
            hit=endpoint_hit(candidate['a'],row['wire']) or endpoint_hit(candidate['b'],row['wire'])
            if hit:
                rejected['end:'+hit]+=1;continue
            try:path,shape=sweep.from_recipe(A,Part,candidate)''')
# Accepted routes change the occupied space; never reuse an earlier clearance
# result after adding one. Cache only within a single complete-net search.
source=source.replace("        rejected=Counter();attempted=0;winner=None", "        endpoint_cache.clear()\n        rejected=Counter();attempted=0;winner=None")
ctx=dict(__name__='coupled_r3_definition',__file__=base.__file__)
exec(compile(source,base.__file__,'exec'),ctx)
ctx['contract']=contract
ctx['OUT']=base.ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3'
if __name__=='__main__':ctx['main']()
