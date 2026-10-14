"""Continue independent body branches without repeating known failed sources.

Reuse received receiver allocation, actual eleven paths and original planner.
Keep every old obstacle/reservation; only the work queue is filtered. A failed
bounded branch is recorded once and other independent branches continue.
"""
import copy
import json
import math
import hashlib
import subprocess
import time
from datetime import datetime,timezone,timedelta
from pathlib import Path
import numpy as np
import plan_body_fanout_layout as R


def run():
    tick=time.monotonic();dest=R.OUT/'body-fanout-layout.json';prior=json.loads(dest.read_text())
    inherited_generator=None
    for n,h in prior['source_sha256'].items():
        if R.SHA(R.ROOT/n)==h:continue
        assert n=='tools/cad/plan_body_fanout_layout.py',n
        commits=subprocess.check_output(['git','log','--format=%H','--',n],cwd=R.ROOT).decode().splitlines()
        matched=None
        for commit in commits:
            blob=subprocess.check_output(['git','show',commit+':'+n],cwd=R.ROOT)
            variants=(blob,blob.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
            if any(hashlib.sha256(v).hexdigest()==h for v in variants):matched=commit;break
        assert matched,'Received generator snapshot cannot be verified in Git'
        baseline=json.loads(subprocess.check_output(['git','show','595d7f8:'+dest.relative_to(R.ROOT).as_posix()],cwd=R.ROOT))
        for name,row in prior['routes'].items():assert row['parts']==baseline['routes'][name]['parts'],(name,'Changed inherited curve')
        inherited_generator=dict(path=n,recorded_sha256=h,matching_git_commit=matched,
            prior_curve_parts_verified_against_commit='595d7f8',
            current_generator_only_used_for_new_candidates=True,
            new_candidates_require_actual_material_gate=True)
    assert prior['route_family']=='tangent_grid_R10_plus_spatial_completion'
    origin=R.SHA(dest);rows=copy.deepcopy(prior['rows']);routes=copy.deepcopy(prior['routes']);inherited=list(routes)
    cf=R.OUT/'body-fanout-work-contract.json';sf=R.OUT/'body-fanout-scene.json';receipt=json.loads(sf.read_text())
    archive=R.ROOT/receipt['scene'];assert R.SHA(archive)==receipt['sha256']
    scene=R.Scene(np.load(archive,allow_pickle=False))
    physical=R.prepared_rows(json.loads(cf.read_text()))
    for row in physical:
        scene.add_points('new/'+row['wire']+'/source',np.linspace(row['start'],row['free_start'],9))
        entry=R.add(row['receiver_point_mm'],R.mul(row['receiver_outward_axis'],3))
        scene.add_points('new/'+row['wire']+'/receiver',np.linspace(entry,row['receiver_point_mm'],6))
    for name,row in routes.items():scene.add_points('new/'+name,np.concatenate([R.part_points(p) for p in row['parts']]))
    excluded_looms={'FL1','FR1','RL1','RR1'};excluded_wires={'W071','W009'}
    excluded={r['wire'] for r in rows if r['loom'] in excluded_looms or r['wire'] in excluded_wires}
    pending=[r for r in rows if r['wire'] not in routes and r['wire'] not in excluded]
    pending.sort(key=lambda r:(r['capacity_before_terminal_mm']-r['terminal_allowance_project_mm']-math.dist(r['free_start'],r['free_end']),r['wire']))
    rejected=[];completed=[]
    pins=copy.deepcopy(prior['source_sha256']);pins[Path(__file__).relative_to(R.ROOT).as_posix()]=R.SHA(Path(__file__))
    pins['tools/cad/plan_body_fanout_layout.py']=R.SHA(Path(R.__file__))
    def save():
        result=copy.deepcopy(prior);result.update(status='PARTIAL_INDEPENDENT_BODY_ROUTES_ACTUAL_MATERIAL_GRIPS_OPEN',
            routes=routes,inherited_routes=inherited,inherited_candidate_sha256=origin,
            rejected=prior.get('rejected',[])+rejected,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            current_queue_completed=completed,explicitly_deferred_source_wires=sorted(excluded),
            inherited_generator_snapshot=inherited_generator or prior.get('inherited_generator_snapshot'),
            planning_scope='Only independent unchanged nonHip1 roots and cached receiver allocations. Hip1whole-source redesign, W071/W009 coupled-source conflicts, newgrips/material/wholeW5 remain OPEN.',
            selected=False,W5_complete=False,physical_pass=False)
        tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest);return result
    print('independent body queue',len(pending),'inherited',len(routes),flush=True)
    latest_start=datetime(2026,10,15,7,tzinfo=timezone.utc)-timedelta(seconds=125)
    for row in pending:
        if datetime.now(timezone.utc)>=latest_start:break
        result,points=R.corridor(scene,row,backward=True)
        completed.append(row['wire'])
        if points is None:
            rejected.append(dict(wire=row['wire'],**result));save()
            print('independent branch deferred',row['wire'],result,flush=True);continue
        assert math.dist(result['parts'][0]['start'],row['start'])<1e-6
        assert math.dist(result['parts'][-1]['end'],row['receiver_point_mm'])<1e-6
        routes[row['wire']]=result;scene.add_points('new/'+row['wire'],points);save()
        print('independent route received',row['wire'],'routes',len(routes),'guide',round(result['guide_mm'],2),flush=True)
    result=save();print(json.dumps(dict(routes=len(routes),added=len(routes)-len(inherited),deferred=len(rejected),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
