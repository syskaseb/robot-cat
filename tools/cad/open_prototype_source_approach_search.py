"""Treat9mm insulation grip as a minimum, not a fixed route datum.

One coherent early-bend/long-terminal approach family, sampled jointly with
all current22 routes. No native parts are generated during the bounded search.
"""
from datetime import datetime, timezone
from pathlib import Path
import itertools, json, time
import open_prototype_source_group as B
import open_prototype_source_search as S
from open_prototype_path_preflight import screen
from open_prototype_distribution_allocation import input_recipe

ROOT=B.ROOT;OUT=B.OUT;read=B.read;sha=B.sha
PLAN=OUT/'source-group-approach-plan.json';PROOF=OUT/'source-group-distance-gate.json'

def candidate(base,parameters,extra):
    p=S.candidate(base,parameters)
    r=next(r for r in p['s1_routes'] if r['wire']=='W064')
    i=max(i for i,q in enumerate(r['segments']) if 'radius_mm' in q)
    parts=r['segments'][:i+1];start=parts[-1]['end'];end=p['ports'][r['target']]['point_mm']
    target=B.add(end,[extra,0,0])
    parts+=input_recipe(start,target,B.WEST,25.2)['segments']
    if extra:parts.append(B.line(target,end))
    r.update(segments=parts,centreline_mm=B.check_path(parts,r['barrel_mm'],end,25.2),
        terminal_straight_mm=9+extra,
        approach_basis='Explicit early bend and longer final entry; independent grip9mm is a minimum')
    return p

def build():
    p=read(PLAN)
    return candidate(S.shared_receiving_level(),p['search_parameters'],p['terminal_approach_extra_mm'])

def main():
    assert not PLAN.exists(),'Receive existing result; no unchanged search'
    tick=time.monotonic();base=S.shared_receiving_level();best=None;count=invalid=0
    values=itertools.product([3,6],[149.323,155],[75.3,81.8,88.3,94.8],[49,51.9],
        [-42,-14],[38,43],[143.323,149.323],[9,12],[9,18,21,27])
    for valueset in values:
        count+=1;parameters=valueset[:-1];extra=valueset[-1]
        try:p=candidate(base,parameters,extra)
        except (ValueError,AssertionError):invalid+=1;continue
        report=screen(p);fail=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
        score=(len(fail),sum(r['centreline_minimum_mm']-r['sampled_distance_mm'] for r in fail),sum(r['centreline_mm'] for r in p['s1_routes']))
        if best is None or score<best[0]:best=(score,p,parameters,extra,report)
        if not fail:break
    assert best is not None,'No valid approach family'
    score,p,parameters,extra,report=best
    p.update(status='MUTUAL_CENTRELINE_SCREEN_ONLY_BREP_OPEN' if score[0]==0 else 'EARLY_APPROACH_FAMILY_REJECTED',
        search_parameters=parameters,terminal_approach_extra_mm=extra,mutual_path_preflight=report,
        search=dict(evaluated=count,invalid_recipe_count=invalid,maximum_family_evaluations=2048,
            score=score,worker_seconds=round(time.monotonic()-tick,6)),
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (Path(__file__),Path(S.__file__),Path(B.__file__),
            OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',OUT/'obstacle-map-current.json')},
        finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],search=p['search'],parameters=parameters,extra=extra,
        conflicts=score[0],near_pairs=report['near_pairs'])),flush=True)

if __name__=='__main__':main()
