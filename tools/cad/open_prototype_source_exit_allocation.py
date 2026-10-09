"""One joint four-source allocation with actual current end-ledger binding.

Current NORTH barrels3/6 retained. Both SOUTH barrels2/5 turn together
to the eastern corridor: old9mm SOUTH grips point into D_RR's allocation.
All source circuits and receiving prefix family must pass the same screen.
No native variants; boxed budgets are not physical collision evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import open_prototype_s1_grip_capacity as H
B=H.B;G=H.G;ROOT=H.ROOT;OUT=H.OUT
PLAN=OUT/'source-exit-allocation.json';PROOF=OUT/'source-exit-space.json';REUSE_PROOF=None

def build_base():
    p=G.F.build();d=[math.sqrt(.5),-math.sqrt(.5),0]
    for r in p['s1_module']['rings']:
        if r['terminal'] not in (2,5):continue
        old=math.degrees(math.atan2(r['direction'][1],r['direction'][0]))
        r['ring_rotation_z_deg'] += -45-old
        r.update(direction=d[:],barrel_mm=B.add(r['eye_mm'],B.mul(d,22.123)))
    return p

def build():
    data=B.read(PLAN);assert data['family'] is not None
    for n,h in data['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return data['family']

if __name__=='__main__':
    assert not PLAN.exists(),'No unchanged layout retry'
    tick=time.monotonic();choices,counts,reasons=G.search(H.connector,build_base());p=choices[0][1] if choices else None
    if p:
        for r in p['s1_routes']:
            r['source_straight_mm']=B.segment_geometry(r['segments'][0])[0]
            r['end_straight_mm']=B.segment_geometry(r['segments'][-1])[0]
        p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,changed_ring_terminals=[2,5],
            changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
            status='FOUR_CURRENT_SOURCES_AND_WHOLE_RING_EXIT_CHANGE_REQUIRE_ACTUAL_GATE')
    files=[Path(__file__),Path(H.__file__),Path(G.__file__),Path(G.A.__file__),Path(G.S.__file__),
        Path(G.F.__file__),G.F.PLAN,G.F.PROOF,OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    data=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_EAST_EXIT_FAMILY_NOT_PHYSICAL_IMPOSSIBILITY',
        family=p,counts=counts,conservative_rejections=reasons,mutual_preflight=choices[0][2] if p else None,
        changed_cause='Both2/5 whole terminals leave EAST of D_RR before turning, all4correct-current-port circuits solved together',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        geometry_digest=G.S.R.geometry_digest(p) if p else None,
        source_ring_geometry_in_plan_and_pins_not_old_digest=True,
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ('status','counts','conservative_rejections','worker_seconds')}),flush=True)
