"""One coupled lower source plane, paired side galleries and SYS/Pi inlet.

Move the entire S1 including rings/control, not individual terminal directions.
The source plane is above Monitor material and below the D_RL/D_RR allowances.
Reserve both SOUTH paths on separate lower galleries before any 3D rises.
Native S1 retention and all other full wiring stay OPEN.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time
import open_prototype_rl_tail_group as T
import open_prototype_s1_biarc_plan as G
B=T.B;ROOT=T.ROOT;OUT=T.OUT
PLAN=OUT/'s1-lower-coupled-receivers-plan.json';PROOF=OUT/'s1-lower-corridor-space.json';REUSE_PROOF=None

def base():
    p=T.build();spec=p['s1_module']
    # Saved Monitor top54 plus ring underside3.175 plus project2mm gap;
    # whole plane60 is rounded UP, not another guessed free-wire offset.
    plane=60;dz=plane-85
    spec['translation_mm']=B.add(spec['translation_mm'],[0,0,dz])
    for r in spec['rings']:
        for key in ('eye_mm','barrel_mm'):r[key]=B.add(r[key],[0,0,dz])
    spec.update(body_bounds_mm=[114.2,-21,64,138.2,21,101],
        operator_bounds_mm=[112.2,-14,101,140.2,14,135],
        lower_plane_basis='Monitor top54 + ring underside3.175 +2mm design gap; plane60',
        previous_mount_invalidated=True)
    # Release the entire south receiver approach from HY, while recomputing
    # the PI input with its existing50mm stock, body and protected output.
    s=next(s for s in p['stations'] if s['role']=='P_SYS');s['centre_mm']=[10,-5,148]
    for n in range(1,6):p['ports'][f'P_SYS.{n}']['point_mm']=B.add(p['ports'][f'P_SYS.{n}']['point_mm'],[0,5,0])
    # The first cheap allocation lowered SYS into the HP output/joint. Keep
    # SYS above that retained conductor and move the WHOLE Pi family UP3,
    # including both prefixes and the insulated joint, to preserve50mm input.
    h=next(h for h in p['holders'] if h['role']=='F_PI');end=p['ports'][h['input_target']]['point_mm']
    for key in ('centre_mm','input_mm','output_mm','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):
        h[key]=B.add(h[key],[0,0,3])
    h['output_segments']=[{k:B.add(v,[0,0,3]) if k in ('start','mid','end') else v for k,v in s.items()} for s in h['output_segments']]
    turn_start=[h['input_mm'][0],h['input_mm'][1],end[2]-6]
    turn=B.quarter(turn_start,B.UP,B.NORTH,6)
    h['input_segments']=[B.line(h['input_mm'],turn_start),turn,B.line(turn['end'],end)]
    h['input_blank_mm']=B.check_path(h['input_segments'],h['input_mm'],end,6)+14
    assert h['input_blank_mm']<=50 and B.segment_geometry(h['input_segments'][-1])[0]>=9
    for r in p['body_ends']:r['datum']=p['ports'].get(r['current_role'])
    return p

def connector(start,departure,end,arrival,d1):
    if departure==B.SOUTH:
        y=-65 if abs(start[0]-120.2)<1e-6 else -72
        a=[start[0],y+25.2,start[2]]
    else:
        a=B.add(start,B.mul(B.NORTH,9 if arrival==B.WEST else 16))
    q=B.quarter(a,departure,B.WEST,25.2)
    return [B.line(start,a),q]+G.A.connect(q['end'],B.WEST,end,arrival,d1)

def build():
    p=B.read(PLAN);assert p['family'] is not None,'No qualified lower source family'
    for n,h in p['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return p['family']

def main():
    assert not PLAN.exists(),'Do not repeat unchanged capacity'
    tick=time.monotonic();p=base()
    choices,counts,rejections=G.search(connector,base_override=p,receiving_goals=[(10,-5,148)],source_budget_allowance=0,max_joint_combinations=64)
    chosen=choices[0][1] if choices else None
    if chosen:chosen.update(s1_geometry_changed=True,changed_case_names=['P_SYS','F_PI'],
        changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        status='LOWER_SOURCE_PLANE_AND_FULL4ROUTES_REQUIRE_ACTUAL_GATE')
    files=[Path(__file__),Path(T.__file__),Path(G.__file__),Path(G.A.__file__),T.PLAN,
        OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    result=dict(status='ONE_LOWER_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if chosen else 'NO_LOWER_SOURCE_SUBSET_NOT_IMPOSSIBILITY',
        family=chosen,counts=counts,conservative_rejections=rejections,
        mutual_preflight=choices[0][2] if choices else None,
        geometry_digest=T.R.geometry_digest(chosen) if chosen else None,
        PI_input_blank_mm=next(h['input_blank_mm'] for h in p['holders'] if h['role']=='F_PI'),
        whole_S1_plane_mm=60,one_SYS_position_mm=[10,-5,148],
        rejected_first_receiver_plan='s1-lower-corridor-plan.json: SYS bottom139.5 enters HP output/joint; no expensive gate',
        retained_upper_tail_joint_not_whole_S1_clearance=True,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','counts','conservative_rejections','PI_input_blank_mm','worker_seconds')}),flush=True)

if __name__=='__main__':main()
