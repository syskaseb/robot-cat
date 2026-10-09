"""One coupled lower source plane, paired side galleries and SYS/Pi inlet.

Move the entire S1 including rings/control, not individual terminal directions.
The source plane is above Monitor material and below the D_RL/D_RR allowances.
Reserve both SOUTH paths on separate lower galleries before any 3D rises.
Native S1 retention and all other full wiring stay OPEN.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import open_prototype_rl_tail_group as T
import open_prototype_s1_biarc_plan as G
B=T.B;ROOT=T.ROOT;OUT=T.OUT
PLAN=OUT/'s1-ordered-full-corridor-plan.json';PROOF=OUT/'s1-ordered-full-corridor-space.json';REUSE_PROOF=None

def base():
    p=T.build();spec=p['s1_module']
    # Saved Monitor top54 plus ring underside3.175 plus project2mm gap;
    # whole plane60 is rounded UP, not another guessed free-wire offset.
    plane=60;dz=plane-85
    spec['translation_mm']=B.add(spec['translation_mm'],[0,0,dz])
    for r in spec['rings']:
        for key in ('eye_mm','barrel_mm'):r[key]=B.add(r[key],[0,0,dz])
        if r['terminal'] in (3,6):
            # The two previous bounded concepts exposed a ROW, not a wire
            # endpoint. Turn both northern actual terminals inward in their
            # existing bearing plane; leave their spacing/eyes unchanged.
            direction=B.WEST[:] if r['terminal']==3 else B.unit([-1,1,0]);r['direction']=direction
            r['barrel_mm']=B.add(r['eye_mm'],B.mul(direction,22.123))
            r['ring_rotation_z_deg']+=90 if r['terminal']==3 else 45
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
    # Allocate TWO4.2mm southern conductors, not one fictitious axis in the
    #5mm old G_AUX/leg-row gap. Move the whole unused ground station east/
    #north, away from the PI joint, and rebind every one of its five ports.
    ground=next(s for s in p['stations'] if s['role']=='G_AUX')
    ground['centre_mm']=[58,-41,70]
    for n in range(1,6):p['ports'][f'G_AUX.{n}']['point_mm']=B.add(p['ports'][f'G_AUX.{n}']['point_mm'],[24,10,0])
    # All terminals are the SAME P_SYS net. Use the vacant third terminal
    # for W068; original fifth becomesNC, occupied/NC counts unchanged.
    swap={'P_SYS.3':'P_SYS.5','P_SYS.5':'P_SYS.3'}
    p['permutation']={k:swap.get(v,v) for k,v in p['permutation'].items()}
    for r in p['body_ends']:r['current_role']=swap.get(r['current_role'],r['current_role'])
    assert next(r['net'] for r in p['body_ends'] if r['wire']=='W068')=='P_SYS'
    p['source_corridor_allocation']=dict(G_AUX_mm=[58,-41,70],southern_gallery_y_mm=[-56,-62],
        W067_inner_lane_y_mm=-56,W068_outer_lane_y_mm=-62,
        W068_current_target='P_SYS.3',NC_now='P_SYS.5',no_added_connectors=True,
        affected_ground_station_mount_and_routes_open=True)
    for r in p['body_ends']:r['datum']=p['ports'].get(r['current_role'])
    return p

def connector(start,departure,end,arrival,d1):
    if departure==B.WEST:
        # Full source3: turn UP west of PWM, rise east of front MTA,
        # then turn WEST above those cases. No northern-row rise atY68.
        a=B.add(start,B.mul(departure,9));q=B.quarter(a,B.WEST,B.UP,25.2)
        b=[q['end'][0],q['end'][1],end[2]-25.2]
        q2=B.quarter(b,B.UP,B.WEST,25.2)
        return [B.line(start,a),q,B.line(q['end'],b),q2]+T.input_recipe(q2['end'],end,B.WEST,25.2)['segments']
    if departure!=B.SOUTH:
        # Full source6: inward+UP plane puts the complete rise below the
        # northern row and outside AUX; both terminal planes stay horizontal.
        a=B.add(start,B.mul(departure,9));q=B.quarter(a,departure,B.UP,25.2)
        return [B.line(start,a),q]+T.input_recipe(q['end'],end,B.UP,25.2)['segments']
    if departure==B.SOUTH:
        # Preserve the order of the two source eyes through their two bends.
        # The outer/right eye takes the outer/south lane, not a crossing braid.
        y=-56 if abs(start[0]-120.2)<1e-6 else -62
        a=[start[0],y+25.2,start[2]]
    else:
        a=B.add(start,B.mul(departure,9))
    angle=math.acos(B.dot(departure,B.WEST));side=B.unit(B.sub(B.WEST,B.mul(departure,math.cos(angle))))
    point=lambda t:B.add(a,B.mul(B.add(B.mul(departure,math.sin(t)),B.mul(side,1-math.cos(t))),25.2))
    q=dict(kind='arc',start=a,mid=point(angle/2),end=point(angle))
    b=[end[0]+25.2,y,start[2]];rise=B.quarter(b,B.WEST,B.UP,25.2)
    c=[end[0],y,end[2]-25.2];finish=B.quarter(c,B.UP,B.NORTH,25.2)
    return [B.line(start,a),q,B.line(q['end'],b),rise,B.line(rise['end'],c),finish,B.line(finish['end'],end)]

def build():
    if PROOF.exists():
        proof=B.read(PROOF)
        assert not any(proof.get(k) for k in ('contacts','outside','input_point_intrusions','receiving_trunk_intrusions','errors')), 'Rejected lowerS1 family must not be reused as current geometry'
    p=B.read(PLAN);assert p['family'] is not None,'No qualified lower source family'
    for n,h in p['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return p['family']

def main():
    assert not PLAN.exists(),'Do not repeat unchanged capacity'
    tick=time.monotonic();p=base()
    choices,counts,rejections=G.search(connector,base_override=p,receiving_goals=[(10,-5,148)],source_budget_allowance=0,max_joint_combinations=1,construction_lengths=(1,))
    chosen=choices[0][1] if choices else None
    if chosen:chosen.update(s1_geometry_changed=True,changed_case_names=['P_SYS','F_PI','G_AUX'],
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
