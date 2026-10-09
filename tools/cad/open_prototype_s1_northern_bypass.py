"""Change the blocked front-source topology, not another terminal offset.

W064 first leaves the whole AUX/PWM bay NORTH, then turns WEST before its
large-radius rising approach. Other3complete sources use exact biarcs.
Earlier cheap exclusions/producers are archived in11a999a, not overwritten.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import open_prototype_s1_biarc_plan as G
from open_prototype_distribution_allocation import input_recipe
B=G.B;ROOT=G.ROOT;OUT=G.OUT
PLAN=OUT/'s1-northern-bypass-plan.json';PROOF=OUT/'s1-northern-bypass-space.json';REUSE_PROOF=None

def connect(start,departure,end,arrival,d1):
    if abs(start[0]-120.2)<1e-6 and abs(start[1]-34.123)<1e-6:
        assert departure==B.NORTH and arrival==B.WEST
        straight=B.line(start,B.add(start,B.mul(B.NORTH,9)))
        turn=B.quarter(straight['end'],B.NORTH,B.WEST,25.2)
        return [straight,turn]+input_recipe(turn['end'],end,B.WEST,25.2)['segments']
    return G.A.connect(start,departure,end,arrival,d1)

def build():
    data=B.read(PLAN);assert data['family'] is not None
    for n,h in data['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return data['family']

if __name__=='__main__':
    assert not PLAN.exists(),'Receive the changed cause, no unchanged retry'
    tick=time.monotonic();choices,counts,rejections=G.search(connect);p=choices[0][1] if choices else None
    if p:p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,
        changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        status='ALL4S1_NORTHERN_BYPASS_REQUIRES_ACTUAL_AND_THICKNESS_GATE')
    files=[Path(__file__),Path(G.__file__),Path(G.A.__file__),Path(G.S.__file__),Path(G.F.__file__),
        G.F.PLAN,G.F.PROOF,OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    data=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_SOURCE_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY',
        previous_producers_snapshot='11a999a: first WEST barrel starts in PWM allowance; simple two-arc W064 hits AUX allowance. No CAD was run.',
        changed_root='NORTH bay exit then WEST S-rise, all other complete source routes/receiving family planned jointly',
        family=p,counts=counts,conservative_rejections=rejections,
        mutual_preflight=choices[0][2] if p else None,geometry_digest=G.S.R.geometry_digest(p) if p else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        samples_and_budget_exclusions_not_actual_contact=True,
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ('status','counts','conservative_rejections','worker_seconds')}),flush=True)
