"""Bounded coupled source-corridor search, no native CAD trial variants.

Search named complete route families against all22 current centrelines, with
fixed ring bearings/minimum radii and a common receiving level. One best
candidate and its remaining conflicts are saved, never claimed selected.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, itertools, json, time
import open_prototype_source_group as B
import open_prototype_source_group_separated as S
from open_prototype_path_preflight import screen
from open_prototype_distribution_allocation import input_recipe

OUT=B.OUT;PLAN=OUT/'source-group-search-plan.json';PROOF=OUT/'source-group-distance-gate.json'
ROOT=B.ROOT;read=B.read;sha=B.sha

def shared_receiving_level(entry_z=135):
    p=S.build(True)
    station=next(r for r in p['stations'] if r['role']=='P_REAR');station['centre_mm'][2]=entry_z+11
    for key,port in p['ports'].items():
        if key.startswith('P_REAR.'):port['point_mm'][2]=entry_z
    # Raise all four receiving paths as a group. RL approaches above AUX,
    # not through the PWM board or by a kink at the last wire segment.
    for r in p['tails']:
        if r['wire']=='W044':
            start=r['segments'][0]['start'];prebend=[68.8,36.5,entry_z-15]
            parts=input_recipe(start,prebend,B.NORTH,6)['segments']
            q=B.quarter(prebend,B.NORTH,B.UP,6)
            r['segments']=parts+[q,B.line(q['end'],p['ports'][r['target']]['point_mm'])]
        elif r['wire']=='W052':r['segments'][-1]['end']=p['ports'][r['target']]['point_mm']
        r['centreline_mm']=B.check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=r['min_radius_mm'])
        r['required_blank_mm']=r['centreline_mm']+r['strip_allowance_mm'];assert r['required_blank_mm']<=100
    h=next(h for h in p['holders'] if h['role']=='F_AUX')
    h['input_segments'][-1]['end']=p['ports'][h['input_target']]['point_mm']
    h['input_blank_mm']=B.check_path(h['input_segments'],end=p['ports'][h['input_target']]['point_mm'],min_radius=6)+14
    assert h['input_blank_mm']<=50
    return p

def candidate(base,parameters):
    p=copy.deepcopy(base)
    down,roof,x,y,sysx,sysy,sysroof,sysdown=parameters
    for r in p['s1_routes']:
        if r['wire']=='W064':
            parts=B.compose(r['barrel_mm'],[('line',[120.2,33,50.877-down]),('half',B.DOWN,[-50.4,16,0])])
            parts+=input_recipe(parts[-1]['end'],[x,y,roof-25.2],B.UP,25.2)['segments']
            q=B.quarter(parts[-1]['end'],B.UP,B.WEST,25.2);parts.append(q)
            parts+=input_recipe(q['end'],p['ports'][r['target']]['point_mm'],B.WEST,25.2)['segments']
            r['source_restraint_plan']='At least9mm straight after lower U, not a clamp guessed inside ring/barrel'
        elif r['wire']=='W065':
            parts=B.compose(r['barrel_mm'],[('line',[132.2,33,50.877-sysdown]),('half',B.DOWN,[-50.4,6.3,0])])
            parts+=input_recipe(parts[-1]['end'],p['ports'][r['target']]['point_mm'],B.UP,25.2)['segments']
        elif r['wire']=='W067':
            extra=sysy-33
            parts=B.compose(r['barrel_mm'],[('line',[81.077,33,85]),('quarter',B.WEST,B.NORTH,25.2)])
            if extra>1e-8:parts.append(B.line(parts[-1]['end'],[55.877,58.2+extra,85]))
            q=B.quarter(parts[-1]['end'],B.NORTH,B.WEST,25.2);parts.append(q)
            parts+=B.compose(q['end'],[('line',[sysx+25.2,sysy+50.4,85]),('quarter',B.WEST,B.SOUTH,25.2),
                ('quarter',B.SOUTH,B.UP,25.2),('line',[sysx,sysy,sysroof-25.2]),('quarter',B.UP,B.EAST,25.2),
                ('half',B.EAST,[0,p['ports'][r['target']]['point_mm'][1]-sysy,0])])
            assert B.segment_geometry(parts[-1])[3]>=25.2
            end=p['ports'][r['target']]['point_mm']
            if abs(parts[-1]['end'][2]-end[2])<1e-8:parts.append(B.line(parts[-1]['end'],end))
            else:parts+=input_recipe(parts[-1]['end'],end,B.WEST,25.2)['segments']
        else:parts=r['segments']
        r['segments']=parts;r['centreline_mm']=B.check_path(parts,r['barrel_mm'],p['ports'][r['target']]['point_mm'],25.2)
        assert B.dot(B.segment_geometry(parts[-1])[2],p['ports'][r['target']]['departure'])<-1+1e-7
    return p

def build():
    """Reconstruct the one saved winning parameter set for the geometry gate."""
    saved=read(PLAN)
    return candidate(shared_receiving_level(),saved['search_parameters'])

def main():
    assert not PLAN.exists(),'Receive existing candidate; no unchanged search'
    tick=time.monotonic();base=shared_receiving_level();best=None;tested=invalid=0
    # 512 complete joint allocations; no on-disk variant per evaluation.
    values=itertools.product([3,6],[149.323,155],[75.3,81.8,88.3,94.8],[49,51.9],
        [-42,-14],[38,43],[143.323,149.323],[9,12])
    for parameters in values:
        tested+=1
        try:p=candidate(base,parameters)
        except (AssertionError,ValueError):invalid+=1;continue
        result=screen(p)
        conflicts=[r for r in result['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
        penalty=sum(r['centreline_minimum_mm']-r['sampled_distance_mm'] for r in conflicts)
        score=(len(conflicts),penalty,sum(r['centreline_mm'] for r in p['s1_routes']))
        if best is None or score<best[0]:best=(score,p,parameters,result)
        if not conflicts:break
    assert best is not None,'No path family satisfies endpoint/radius constraints'
    score,p,parameters,result=best
    p.update(status='JOINT_CENTRELINE_SCREEN_ONLY_BREP_OPEN' if not score[0] else 'BOUNDED_SEARCH_REJECTED_NO_CLEAR_CANDIDATE',
        search_parameters=parameters,mutual_path_preflight=result,
        search=dict(evaluated=tested,invalid_recipe_count=invalid,maximum_family_evaluations=512,
            score=score,worker_seconds=round(time.monotonic()-tick,6),
            caveat='Sampled centrelines only: retained material/torso/grips/service still OPEN; no partial credit'),
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (Path(__file__),Path(B.__file__),Path(S.__file__),
            OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',OUT/'obstacle-map-current.json')},
        finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],search=p['search'],parameters=parameters,
        conflicts=[r for r in result['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])),flush=True)

if __name__=='__main__':main()
