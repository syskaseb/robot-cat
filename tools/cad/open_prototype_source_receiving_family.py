"""One coupled source/receiving family, not another single-wire offset.

S1 changes its complete bearing plane; P_AUX and all three FHAC inputs
move together. P_SYS travels with the entire PI holder and both prefixes.
This preparation intentionally invalidates all affected downstream routes.
It never serializes stale source wires as if they belonged to this family.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, json, time
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_distribution_allocation import input_recipe
from open_prototype_entry_chambers import occupancy

ROOT=B.ROOT; OUT=B.OUT
PLAN=OUT/'source-receiving-family-plan.json'
PROOF=OUT/'source-receiving-family-space.json'

def build():
    p=R.build()
    before=R.geometry_digest(p)
    for role,delta in [('P_AUX',[0,-29,0]),('P_SYS',[-60,0,0])]:
        case=next(s for s in p['stations'] if s['role']==role)
        case['centre_mm']=B.add(case['centre_mm'],delta)
        for n in range(1,6):
            port=p['ports'][f'{role}.{n}']
            port['point_mm']=B.add(port['point_mm'],delta)
    for h in p['holders']:
        if h['role']=='F_PI':
            delta=[-60,0,0]
            for k in ('input_mm','output_mm','centre_mm','sleeve_start_mm',
                      'sleeve_end_mm','new_insulation_end_mm'):
                h[k]=B.add(h[k],delta)
            for k in ('input_segments','output_segments'):
                h[k]=[{field:B.add(value,delta) if field in ('start','mid','end') else value
                       for field,value in seg.items()} for seg in h[k]]
        elif h['role'] in ('F_HY','F_HP','F_TY'):
            h['input_segments']=input_recipe(h['input_mm'],
                p['ports'][h['input_target']]['point_mm'],B.EAST,6)['segments']
            h['input_blank_mm']=B.check_path(h['input_segments'],min_radius=6)+11
            assert h['input_blank_mm']<=h['factory_minimum_mm'],h['role']
    for h in p['holders']:
        B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)
        B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
    for e in p['body_ends']: e['datum']=p['ports'].get(e['current_role'])
    loads=occupancy(B.read(OUT/'routing-scope-plan.json'),p['permutation'])
    assert len(p['ports'])==100 and sum(bool(loads[n]) for n in p['ports'])==86
    assert all(len(loads[n])<=1 for n in p['ports'])
    # Remove invalidated geometry rather than checking or selecting it.
    p['s1_routes']=[]
    p.update(s1_module=dict(whole_rotation_deg=90,axis=[1,0,0],
        pivot_mm=[126.2,55.5,85],translation_mm=[0,-55.5,22.5],
        bearing_plane='XY, normal Z',external_control=True,
        external_control_basis='whole_cat_interior.py S1_control_CP2 require_internal_shell=False; manual operator reservation, not measured delivered geometry',
        rings=[dict(terminal=t,eye_mm=[x,y,85],barrel_mm=[x,b,85],
                    direction=d,ring_rotation_z_deg=a)
            for t,x,y,b,d,a in [(2,120.2,0,-22.123,B.SOUTH,90),
                               (5,132.2,0,-22.123,B.SOUTH,-90),
                               (3,120.2,12,34.123,B.NORTH,-90),
                               (6,132.2,12,34.123,B.NORTH,90)]],
        terminal_mount_sequence=[
            'Attach four ring terminals to S1 on the bench with specified insulation and independent wire grips.',
            'Install retained S1 module before Monitor; assembled driver sweeps are NOT claimed clear.',
            'Route four new complete source circuits and retain module independently of terminal screws.',
            'For S1 terminal service: isolate power, identify/disconnect only its four source wires, remove retained S1 module, then service on bench.',
            'Routine ATO access must not require these disconnections; qualify the separate bank access sequence.'],
        sequence_status='PROPOSED_NOT_NATIVE_REMOVAL_PROOF'),
        changed_case_names=['P_AUX','P_SYS','F_PI'],
        changed_path_names=['F_HY/input','F_HP/input','F_TY/input',
                            'F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        invalidated=['All four S1 source routes and historical920mm',
                     'P_SYS-connected conductors and full PI_VIN load route',
                     'P_AUX-connected conductors other than three newly rebuilt FHAC inputs',
                     'P_SYS/F_PI/P_AUX native mounts and connected removal'],
        independent_remaining=['Complete RL/W045/tail receiving family',
            'HY body/head transition and HP moving continuation',
            'All remaining wiring, native strain relief, stock and selected exports',
            'Delivered U1/AUX padmap gate; no invented pins'],
        status='SHARED_SOURCE_RECEIVING_SPACE_PREPARATION_NOT_COMPLETE_WIRING',
        previous_geometry_digest=before,selected=False,stage_completed=False,W5_complete=False,physical_pass=False)
    return p

def compact():
    p=build()
    files=[Path(__file__),Path(R.__file__),Path(B.__file__),
        Path(input_recipe.__globals__['__file__']),
        OUT/'rr-receiving-branch-plan.json',OUT/'s1-terminal-plane-budget.json',
        ROOT/'tools/cad/whole_cat_interior.py',OUT/'obstacle-map-current.json']
    return dict(status=p['status'],recipe_compact=True,
        geometry_digest=R.geometry_digest(p),s1_module=p['s1_module'],
        changed_cases=[s for s in p['stations']+p['holders'] if s['role'] in p['changed_case_names']],
        changed_holder_inputs=[dict(role=h['role'],target=h['input_target'],
            segments=h['input_segments'],blank_mm=h['input_blank_mm'],
            factory_limit_is_project_assumption=h['role']=='F_PI')
            for h in p['holders'] if h['role'] in ('F_PI','F_HY','F_HP','F_TY')],
        invalidated=p['invalidated'],remaining=p['independent_remaining'],
        external_control_interpretation_correction=dict(
            historical_proof='s1-terminal-plane-budget.json',
            outside_volume_mm3=1231.504193,
            outside_does_not_reject_external_operator=True,
            P_AUX_interference_mm3=1928.103344,interference_still_requires_change=True,
            original_driver_obstructions_retained=True,original_proof_not_overwritten=True),
        ports=100,occupied=86,NC=14,body_ends=160,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,W5_complete=False,physical_pass=False)

if __name__=='__main__':
    assert not PLAN.exists(),'Receive existing result, no unchanged retry'
    tick=time.monotonic();p=compact()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],input_blanks=[(h['role'],h['blank_mm']) for h in p['changed_holder_inputs']],seconds=p['worker_seconds'])),flush=True)
