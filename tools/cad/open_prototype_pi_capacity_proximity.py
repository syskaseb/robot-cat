"""One cheap mutual screen including the covered PI joint's outer profile."""
from pathlib import Path
import json,time
import open_prototype_pi_capacity_choice as G
import open_prototype_source_group as B
from open_prototype_path_preflight import screen

DEST=G.OUT/'pi-capacity-choice-proximity.json'

if __name__=='__main__':
    assert not DEST.exists(),'No unchanged screen'
    p=G.build();h=next(h for h in p['holders'] if h['role']=='F_PI')
    p['tails'] += [dict(wire='F_PI/sleeve',OD_mm=6,segments=[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])]),
        dict(wire='F_PI/new_insulation',OD_mm=2.1,segments=[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])])]
    result=screen(p)
    join_names={'F_PI/output','F_PI/sleeve','F_PI/new_insulation'}
    result['intentional_same_conductor_covered_profiles']=[r for r in result['near_pairs'] if r['a'] in join_names and r['b'] in join_names]
    result['near_pairs']=[r for r in result['near_pairs'] if not (r['a'] in join_names and r['b'] in join_names)]
    result['status']='REJECTED_MUTUAL_PATH_RESERVATION' if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in result['near_pairs']) else 'CURRENT_PREFIXES_PROXIMITY_ONLY_COMPLETE_SOURCE_OPEN'
    result.update(source_sha256={f.relative_to(G.ROOT).as_posix():B.sha(f) for f in (Path(__file__),Path(G.__file__),G.PLAN,G.PROOF)},
        four_S1_paths_invalidated_not_screened=True,covered_joint_recipe_not_new_selection=True)
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],paths=result['paths'],samples=result['samples'],
        near=[{k:r[k] for k in ('a','b','sampled_distance_mm','status')} for r in result['near_pairs']],seconds=result['worker_seconds'])),flush=True)
