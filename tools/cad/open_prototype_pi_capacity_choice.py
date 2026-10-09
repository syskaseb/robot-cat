"""Materialize ONE whole PI family from bounded capacity, no finer retry grid."""
from datetime import datetime,timezone
from pathlib import Path
import json,time
import open_prototype_source_receiving_family as F
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
import open_prototype_pi_capacity_plan as C

ROOT=F.ROOT;OUT=F.OUT;REUSE_PROOF=F.PROOF
PLAN=OUT/'pi-capacity-choice-plan.json';PROOF=OUT/'pi-capacity-choice-space.json'

def build():
    capacity=B.read(C.DEST)
    assert capacity['status']=='BOUNDED_CAPACITY_SHORTLIST_REQUIRES_ACTUAL_BREP'
    for n,h in capacity['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    choice=capacity['shortlist'][0];p=F.build()
    station=next(s for s in p['stations'] if s['role']=='P_SYS')
    station.update(choice['SYS'],rotation=str((90+90*choice['whole_pair_turns_z'])%360))
    for n,datum in choice['all_SYS_ports'].items():p['ports'][n].update(datum)
    h=next(h for h in p['holders'] if h['role']=='F_PI')
    h.update(choice['PI'])
    for key in ('input_segments','output_segments','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):h[key]=choice[key]
    h['input_mm']=h['input_segments'][0]['start'];h['output_mm']=h['output_segments'][0]['start']
    h['output_prefix_mm']=B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
    h['input_blank_mm']=B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)+14
    assert h['input_blank_mm']<=50 and h['output_prefix_mm']<=84.5
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,
        changed_path_names=['F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        status='ONE_CAPACITY_ALLOCATED_PI_FAMILY_NOT_FULL_WIRING',
        capacity_recipe=choice,
        capacity_basis='7176 rigid family coordinate allocations/1164 complete prefix choices, no native variants. Conservative boxes and sampled torso rejected candidates for search only, not actual collision proof.')
    return p

def compact():
    p=build();base=F.compact()
    base.update(status=p['status'],geometry_digest=R.geometry_digest(p),capacity_recipe=p['capacity_recipe'],
        changed_cases=[s for s in p['stations']+p['holders'] if s['role'] in p['changed_case_names']],
        changed_holder_inputs=[dict(role=h['role'],target=h['input_target'],segments=h['input_segments'],blank_mm=h['input_blank_mm'],factory_limit_is_project_assumption=True) for h in p['holders'] if h['role']=='F_PI'],
        whole_PI=next(h for h in p['holders'] if h['role']=='F_PI'),
        capacity_basis=p['capacity_basis'],reused_partial_proof='source-receiving-family-space.json',
        no_full_route_or_native_acceptance=True)
    for f in (Path(__file__),Path(C.__file__),C.DEST,F.PLAN,F.PROOF):base['source_sha256'][f.relative_to(ROOT).as_posix()]=B.sha(f)
    return base

if __name__=='__main__':
    assert not PLAN.exists(),'Receive existing one-choice candidate'
    tick=time.monotonic();p=compact()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],SYS=p['changed_cases'][0]['centre_mm'],PI=p['whole_PI']['centre_mm'],input_blank=p['whole_PI']['input_blank_mm'],seconds=p['worker_seconds'])),flush=True)
