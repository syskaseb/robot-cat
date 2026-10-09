"""Current source trial blanks from retained termination process, not stock selection."""
from datetime import datetime, timezone
from pathlib import Path
import json, math, time
import open_prototype_source_group as B
import open_prototype_source_capacity_plan as C

OUTPUT=B.OUT/'source-group-trial-lengths.json'
TOOLS=B.ROOT/'hardware/electronics/full-cat/termination-tools-k3-r1/tools.json'
HISTORY=B.ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r2/intent.json'

def build():
    tick=time.monotonic();p=C.read(C.PLAN);tools=C.read(TOOLS);history=C.read(HISTORY)
    process=next(r for r in tools['processes'] if r.get('terminal')=='130171')
    maximum_strip=process['strip_mm'][1]
    rows=[]
    for r in p['s1_routes']:
        saved=next(q for q in history['routes'] if q['wire']==r['wire'])['end_allowance_mm']
        assert saved['TE130171_max_strip']==maximum_strip
        path=B.check_path(r['segments'],r['barrel_mm'],p['ports'][r['target']]['point_mm'],25.2)
        allowances=dict(saved)
        unrounded=path+sum(allowances.values())
        rows.append(dict(wire=r['wire'],sku='HELU23802',centreline_mm=path,
            allowance_mm=allowances,unrounded_trial_blank_mm=unrounded,
            nominal_unpowered_trial_blank_mm=10*math.ceil(unrounded/10),actual_cut_mm=None,
            route_status='UNSELECTED_CURRENT_CANDIDATE_GEOMETRY_PENDING'))
    return dict(status='NOMINAL_SOURCE_TRIAL_LENGTHS_NOT_SELECTED_STOCK',rows=rows,
        candidate_nominal_total_mm=sum(r['nominal_unpowered_trial_blank_mm'] for r in rows),
        legacy920mm_source_not_closed_or_deducted=True,
        stock_selection=False,W5_complete=False,stage_completed=False,physical_pass=False,
        basis='Existing terminal process maximum-strip additions and retained30mm unpowered trial reserve;10mm project round-up. Not measured hardware cuts or geometry acceptance.',
        source_sha256={f.relative_to(B.ROOT).as_posix():B.sha(f) for f in (C.PLAN,TOOLS,HISTORY,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())

if __name__=='__main__':
    assert not OUTPUT.exists(),'Receive existing result; no unchanged repeat'
    p=build();OUTPUT.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],total=p['candidate_nominal_total_mm'],
        rows=[(r['wire'],r['nominal_unpowered_trial_blank_mm']) for r in p['rows']])),flush=True)
