"""Rotate the entire PI supply family into a central upper-layer allocation.

The rejected -60X placement is not retried. All five SYS datums, the PI
holder/input/both exits move together, with a NORTH output/joint topology
above the Pi allowance instead of dropping a covered joint through it.
"""
from datetime import datetime, timezone
from pathlib import Path
import json,time
import open_prototype_source_receiving_family as F
import open_prototype_rr_receiving_branch as R
import open_prototype_source_group as B

ROOT=F.ROOT;OUT=F.OUT
PLAN=OUT/'pi-family-plan.json';PROOF=OUT/'pi-family-space.json'
REUSE_PROOF=F.PROOF

def build():
    p=F.build();station=next(s for s in p['stations'] if s['role']=='P_SYS')
    centre=station['centre_mm'];goal=[20,0,148]
    def point(q):
        x,y,z=B.sub(q,centre)
        return B.add([-y,x,z],goal)
    def direction(q):return [-q[1],q[0],q[2]]
    station.update(centre_mm=goal,size_mm=[37,22,11],rotation='180')
    for n in range(1,6):
        port=p['ports'][f'P_SYS.{n}']
        port.update(point_mm=point(port['point_mm']),departure=direction(port['departure']))
    h=next(h for h in p['holders'] if h['role']=='F_PI')
    for k in ('input_mm','output_mm','centre_mm'):h[k]=point(h[k])
    h['size_mm']=[20.25,22,51];h['axis']=direction(h['axis'])
    h['input_segments']=[{k:point(v) if k in ('start','end','mid') else v for k,v in s.items()} for s in h['input_segments']]
    h['output_segments']=B.compose(h['output_mm'],[
        ('line',B.add(h['output_mm'],[0,0,-3])),('quarter',B.DOWN,B.NORTH,6),
        ('line',[33,50,67])])
    h['output_prefix_mm']=B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
    cut=h['output_segments'][-1]['end']
    h.update(sleeve_start_mm=B.sub(cut,B.mul(B.NORTH,17.25)),
        sleeve_end_mm=B.add(cut,B.mul(B.NORTH,9.25)),
        new_insulation_end_mm=B.add(cut,B.mul(B.NORTH,18.25)))
    assert h['output_prefix_mm']+17.25<=84.5 # project usable delivery assumption
    B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    p.update(changed_case_names=['P_SYS','F_PI'],
        changed_path_names=['F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        s1_geometry_changed=False,
        status='WHOLE_PI_FAMILY_ORIENTATION_AND_EXIT_REBOUND_NOT_COMPLETE_WIRING',
        reuse_geometry_basis='S1/P_AUX/threeFHACinputs unchanged versus source-receiving-family-space.json; prior producer archived in ce778be. Full routes remain OPEN.')
    return p

def compact():
    p=build();base=F.compact()
    base.update(status=p['status'],geometry_digest=R.geometry_digest(p),
        changed_cases=[s for s in p['stations']+p['holders'] if s['role'] in p['changed_case_names']],
        changed_holder_inputs=[dict(role=h['role'],target=h['input_target'],segments=h['input_segments'],
            blank_mm=h['input_blank_mm'],factory_limit_is_project_assumption=True)
            for h in p['holders'] if h['role']=='F_PI'],
        whole_PI=next(h for h in p['holders'] if h['role']=='F_PI'),
        reused_partial_proof='source-receiving-family-space.json',
        changed_cause='Whole pair Z+90, SYS20/0/148 with input and both PI exits rebound, output/joint NORTH above Pi allowance. Not another -60X scalar shift.',
        reused_partial_not_full_acceptance=True)
    for f in (Path(__file__),F.PLAN,F.PROOF):base['source_sha256'][f.relative_to(ROOT).as_posix()]=B.sha(f)
    return base

if __name__=='__main__':
    assert not PLAN.exists(),'No unchanged retry'
    tick=time.monotonic();p=compact()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],SYS=p['changed_cases'][0]['centre_mm'],
        PI_centre=p['whole_PI']['centre_mm'],PI_input_blank=p['whole_PI']['input_blank_mm'],
        PI_output_prefix=p['whole_PI']['output_prefix_mm'],seconds=p['worker_seconds'])),flush=True)
