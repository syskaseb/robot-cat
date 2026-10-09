"""Rebind all four REAR inputs to measured whole-case height capacity.

No scalar CAD trials: one case footprint and its four complete approaches.
Capacity and sampled proximity are preparation, never route acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, time
import open_prototype_source_group as B
import open_prototype_source_group_separated as D
import open_prototype_source_search as S
import open_prototype_source_approach_search as G
from open_prototype_path_preflight import screen

ROOT=B.ROOT;OUT=B.OUT;read=B.read;sha=B.sha
PLAN=OUT/'source-group-capacity-plan.json'
PROOF=OUT/'source-group-capacity-distance-gate.json'
CAPACITY=OUT/'rear-gallery-height-capacity.json'

def build():
    capacity=read(CAPACITY);previous=read(G.PLAN)
    assert capacity['proposed_outside_volume_mm3']==0
    assert capacity['source_sha256'][G.PLAN.relative_to(ROOT).as_posix()]==sha(G.PLAN)
    p=G.candidate(S.shared_receiving_level(capacity['proposed_entry_z_mm']),
        previous['search_parameters'],previous['terminal_approach_extra_mm'])
    for e in p['body_ends']:
        e['datum']=p['ports'].get(e['current_role'])
    for r in p['tails']+p['s1_routes']:
        assert r['segments'][-1]['end']==p['ports'][r['target']]['point_mm']
        assert B.dot(B.segment_geometry(r['segments'][-1])[2],p['ports'][r['target']]['departure'])<-1+1e-7
    p.update(status='MEASURED_CASE_CAPACITY_REBOUND_SOURCE_GROUP_NOT_ACCEPTED',
        receiving_height_basis='Whole footprint exact torso capacity,0.5mm project vertical margin; all four full inputs regenerated',
        capacity_result=CAPACITY.relative_to(ROOT).as_posix())
    return p

def main():
    assert not PLAN.exists(),'Receive existing result; no unchanged repeat'
    tick=time.monotonic();p=build();report=screen(p)
    p.update(mutual_path_preflight=report,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in
            (Path(__file__),Path(B.__file__),Path(D.__file__),Path(S.__file__),Path(G.__file__),G.PLAN,CAPACITY)},
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_seconds=round(time.monotonic()-tick,6))
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],seconds=p['worker_seconds'],
        rear_entry_z=capacity_entry(p),conflicts=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'],
        near_pair_count=len(report['near_pairs']),tails=[(r['wire'],round(r['required_blank_mm'],3)) for r in p['tails']],
        holder_inputs=[(r['role'],round(r['input_blank_mm'],3)) for r in p['holders']])),flush=True)

def capacity_entry(p):return p['ports']['P_REAR.1']['point_mm'][2]

if __name__=='__main__':main()
