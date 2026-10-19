"""Full 24-way receiving-material preflight before another whole robot run.

One complete bank selected jointly. Reuse exact whole-parent material pairs;
propagate identical failing component shapes across head-only choices.
No core/world/native/N01 claim is made by bank-only acceptance.
"""
import hashlib
import json
import time
import itertools
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_remaining_kits import candidates as original_candidates
from feline_remaining_receive import key
from feline_bank_receiving_grips import both_after_candidates
from feline_bank_zoned_layout import candidates,materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();groups,_=original_candidates();recipes=both_after_candidates(groups);recipes.update(candidates(groups))
    source=OUT/'n01-shared54-whole.json';parent=json.loads(source.read_text());prior=parent['mutual_cache']
    helper=Path(__file__).with_name('feline_bank_zoned_layout.py')
    assert parent['source_sha256'][helper.relative_to(ROOT).as_posix()]==sha(helper)
    choices=[(g,r) for g,rows in recipes.items() for r in rows];codes=[key(g,r) for g,r in choices]
    assert len(codes)==len(set(codes))
    parts=[materialise(g,r) for g,r in choices];signatures=[];cache=SolidQueries();component_cache={}
    for pp,kk in parts:
        signatures.append({n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in pp.items()})
    result=dict(status='RUNNING_FULL_BANK_PLAN',source_sha256={source.relative_to(ROOT).as_posix():sha(source),helper.relative_to(ROOT).as_posix():sha(helper),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        pairs={},cuts=[],iterations=[],errors=[],N01_complete=False,physical_pass=False)
    dest=OUT/'n01-bank-whole-preflight.json';cuts=set();bad=[]
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def mutual(i,j):
        code='|'.join(sorted((codes[i],codes[j])))
        if code in result['pairs']:return result['pairs'][code]['ok']
        if code in prior:
            result['pairs'][code]=dict(prior[code],reused_from_parent=True);return result['pairs'][code]['ok']
        aa,ak=parts[i];bb,bk=parts[j];record=dict(ok=True,pairs=[])
        for n,s in aa.items():
            for other,t in bb.items():
                minimum=pair_spacing('Current:'+n,dict(kind=ak[n]),'Current:'+other,dict(kind=bk[other]))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                sig=tuple(sorted((signatures[i][n],signatures[j][other])))
                if sig not in component_cache:component_cache[sig]=cache.distance(s,t)
                gap=component_cache[sig];record['pairs'].append(dict(part=n,other=other,gap_mm=gap,minimum_mm=minimum))
                if gap<minimum-1e-6:
                    record['ok']=False
                    # Only EXACT same world shapes inherit the failure.
                    left=[k for k,(g,r) in enumerate(choices) if g==choices[i][0] and signatures[k].get(n)==signatures[i][n]]
                    right=[k for k,(g,r) in enumerate(choices) if g==choices[j][0] and signatures[k].get(other)==signatures[j][other]]
                    for a,b in itertools.product(left,right):cuts.add(tuple(sorted((a,b))))
                    break
            if not record['ok']:break
        result['pairs'][code]=record;return record['ok']
    try:
        for iteration in range(80):
            if time.monotonic()-tick>180:raise TimeoutError('Bank preflight180s bound, not window stop')
            rr=[];cc=[];vv=[];lo=[];hi=[]
            def add(ii,l,h):
                row=len(lo);rr.extend([row]*len(ii));cc.extend(ii);vv.extend([1.]*len(ii));lo.append(l);hi.append(h)
            for group in recipes:add([i for i,(g,r) in enumerate(choices) if g==group],1,1)
            for i,j in cuts:add([i,j],-np.inf,1)
            # Preserve real static failures, but do not treat absent receipts as PASS.
            upper=np.ones(len(choices))
            for filename in ('n01-bank-both-after-static.json','n01-bank-zoned-static.json'):
                records=json.loads((OUT/filename).read_text())['units']
                for i,c in enumerate(codes):
                    if records.get(c,{}).get('failure'):upper[i]=0
            fit=milp(np.zeros(len(choices)),integrality=np.ones(len(choices)),bounds=Bounds(0,upper),
                constraints=LinearConstraint(coo_matrix((vv,(rr,cc)),shape=(len(lo),len(choices))).tocsc(),lo,hi),options={'time_limit':10})
            if fit.x is None:result['status']='BANK_PLAN_REJECTED_COMPLETE_MATERIAL_NOT_GLOBAL_IMPOSSIBILITY';break
            selected=[i for i,x in enumerate(fit.x) if x>.5];assert len(selected)==24
            result['iterations'].append([codes[i] for i in selected]);rejected=False
            for a,i in enumerate(selected):
                for j in selected[a+1:]:
                    if not mutual(i,j):
                        cuts.add(tuple(sorted((i,j))));rejected=True;save();break
                if rejected:break
            if not rejected:
                result.update(status='ALL24_BANK_FULL_MATERIAL_MUTUAL_CLEAR_CORE_WORLD_OPEN',chosen={choices[i][0]:dict(recipe=choices[i][1],key=codes[i]) for i in selected});break
        else:result['status']='PARTIAL_FULL_BANK_PLAN'
    except TimeoutError as exc:result.update(status='PARTIAL_FULL_BANK_PLAN',note=str(exc))
    result['cuts']=[[codes[i],codes[j]] for i,j in sorted(cuts)];save()
    print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],pairs=len(result['pairs']),cuts=len(cuts))),flush=True)
    for pair,rec in result['pairs'].items():
        if not rec['ok']:print('Rejected',pair,rec['pairs'][-1],flush=True)


if __name__=='__main__':main()
