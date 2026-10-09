"""Whole RR receiving interface above the bank, no third parking micro-cut.

Rebind all five RR_P ports and full factory output with a reverse approach.
Lower6 source is explicitly rejected/open and excluded from this independent
changed-branch gate. Store a compact recipe rather than another160-end copy.
"""
from datetime import datetime, timezone
from pathlib import Path
import json,hashlib,time
import open_prototype_source_group as B
import open_prototype_source_capacity_plan as C
import open_prototype_source_frame_corridor as F
from open_prototype_path_preflight import screen

ROOT=B.ROOT;OUT=B.OUT;read=B.read;sha=B.sha
PLAN=OUT/'rr-receiving-branch-plan.json';PROOF=OUT/'rr-receiving-branch-gate.json'
CAPACITY=C.CAPACITY;REUSE_CASES_FROM=C.PLAN

def geometry_digest(p):
    def normalize(v):
        if isinstance(v,bool):return v
        if isinstance(v,(int,float)):return round(float(v),6) if v else 0.0
        if isinstance(v,dict):return {k:normalize(x) for k,x in v.items()}
        if isinstance(v,list):return [normalize(x) for x in v]
        return v
    fields=('stations','mta','tails','holders','s1_routes','ports','permutation','body_ends')
    return hashlib.sha256(json.dumps(normalize({k:p[k] for k in fields}),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def build():
    p=F.build();s=next(s for s in p['stations'] if s['role']=='RR_P')
    s.update(centre_mm=[109,-42,132.5],size_mm=[19,30,9],rotation='90')
    for n in range(1,6):
        p['ports'][f'RR_P.{n}'].update(point_mm=[118.5,-42+(n-3)*4.75,132.5],departure=B.EAST)
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    r=next(r for r in p['tails'] if r['wire']=='W053');end=p['ports'][r['target']]['point_mm']
    q=B.quarter([94.8,-41.5,117],B.SOUTH,B.EAST,7.5)
    start_return=[end[0]+9,q['end'][1],117]
    parts=[B.line([94.8,-38.5,117],q['start']),q,B.line(q['end'],start_return),
        B.half_turn(start_return,B.EAST,[0,end[1]-start_return[1],end[2]-start_return[2]])]
    parts.append(B.line(parts[-1]['end'],end))
    length=B.check_path(parts,[94.8,-38.5,117],end,7.5)
    r.update(segments=parts,centreline_mm=length,required_blank_mm=length+11,terminal_straight_mm=9,
        independent_grip_plan='Final9mm WEST factory straight; receiving station and grip require new native support')
    assert r['required_blank_mm']<=100
    p.update(changed_path_names=['W053'],changed_case_names=['RR_P'],
        status='INDEPENDENT_RR_RECEIVING_BRANCH_NOT_SELECTION',
        open_blocker='W065 lower6 source route rejected; not retested or qualified by this branch')
    return p

if __name__=='__main__':
    assert not PLAN.exists(),'Receive existing candidate; no unchanged repeat'
    tick=time.monotonic();p=build();report=screen(p)
    fail=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    row=next(r for r in p['tails'] if r['wire']=='W053')
    result=dict(status=p['status'],recipe_compact=True,materialized_geometry_digest=geometry_digest(p),
        geometry_digest_rounding_mm=1e-6,station=next(s for s in p['stations'] if s['role']=='RR_P'),
        changed_path_names=p['changed_path_names'],factory_output=row,mutual_path_preflight=report,
        known_lower6_blocker_retained=True,selected=False,stage_completed=False,W5_complete=False,physical_pass=False,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in
            (Path(__file__),Path(F.__file__),Path(C.__file__),C.PLAN,C.CAPACITY,OUT/'source-group-frame-point-screen.json')},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],blank_mm=row['required_blank_mm'],conflicts=fail,
        seconds=result['worker_seconds'])),flush=True)
