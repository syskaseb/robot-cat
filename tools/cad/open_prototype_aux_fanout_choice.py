"""ONE integrated FHAC/PI allocation, with complete protected approaches."""
from pathlib import Path
from datetime import datetime,timezone
import json,time
import open_prototype_aux_fanout_plan as F
import open_prototype_aux_fanout_capacity as C
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R

ROOT=F.ROOT;OUT=F.OUT;REUSE_PROOF=None
PLAN=OUT/'aux-fanout-choice-plan.json';PROOF=OUT/'aux-fanout-choice-space.json'

def build():
    data=B.read(C.DEST)
    assert data['status']=='SHARED_FANOUT_CAPACITY_REQUIRES_ONE_ACTUAL_GATE'
    for n,h in data['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    p=F.build();choice=data['choice'];s=next(s for s in p['stations'] if s['role']=='P_SYS')
    s.update(choice['SYS'],rotation=str((int(s['rotation'])+90*choice['whole_pair_turns_z'])%360))
    for n,datum in choice['all_SYS_ports'].items():p['ports'][n].update(datum)
    h=next(h for h in p['holders'] if h['role']=='F_PI');h.update(choice['PI'])
    for k in ('input_segments','output_segments','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):h[k]=choice[k]
    h['input_mm']=h['input_segments'][0]['start'];h['output_mm']=h['output_segments'][0]['start']
    h['input_blank_mm']=B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)+14
    h['output_prefix_mm']=B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
    assert h['input_blank_mm']<=50
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    p['changed_case_names']=['F_HY','F_HP','P_SYS','F_PI']
    p['changed_path_names'] += ['F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation']
    p.update(s1_geometry_changed=False,status='ONE_SHARED_FHAC_PI_FAMILY_NOT_FULL_SOURCE_OR_NATIVE_ACCEPTANCE')
    return p

def compact():
    p=build();report=F.proximity(p)
    assert not any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']),'No expensive gate on a known shared crossing'
    files=(Path(__file__),Path(F.__file__),Path(C.__file__),C.DEST,F.PLAN,
        OUT/'pi-capacity-choice-space.json',OUT/'obstacle-map-current.json')
    return dict(status=p['status'],geometry_digest=R.geometry_digest(p),
        changed_holders=[h for h in p['holders'] if h['role'] in ('F_PI','F_HY','F_HP','F_TY')],
        SYS=next(s for s in p['stations'] if s['role']=='P_SYS'),
        protected_receiving_rows=p['protected_receiving_rows'],
        mutual_path_preflight=report,retained_S1_and_AUX_space_not_full_source=True,
        head_exit_scope='Only existing last HY WEST segment to -112/-57.85/84.59378 leaves torso. Recorded unchanged body/head transition, NOT full tube/bridge/moving acceptance.',
        invalidated=p['invalidated'],remaining=['All4S1 source routes/old920mm','W045/tail receiving endpoint',
            'Head exit/moving continuation','All native grips/full remaining wiring/stock/selected exports'],
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False)

if __name__=='__main__':
    assert not PLAN.exists(),'Receive one chosen family'
    tick=time.monotonic();p=compact()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],SYS=p['SYS']['centre_mm'],
        blanks=[(h['role'],h['input_blank_mm']) for h in p['changed_holders']],
        known_crossings=0,near_pairs=len(p['mutual_path_preflight']['near_pairs']),seconds=p['worker_seconds'])),flush=True)
