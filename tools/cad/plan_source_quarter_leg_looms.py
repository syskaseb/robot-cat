"""Source-owned round quarter exits + separate Knee flex, planned together.

Direct flex ending at the socket imposed incompatible tangents. A short rigid
R31.5 quarter on the same moving member takes the plug axis to the existing
flex plane. This changes all eight Knee sections, not their old proof.
"""
import copy, itertools, json, math, time
import sys
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,mul
from plan_current_mta_interfaces import line
from rigid_tangent_channel import turn,candidates
from plan_continuous_joint_family import parts_for_loom,self_screen
from plan_socket_anchored_leg_looms import pose,ANGLES,R,LAND
if '--piecewise' in sys.argv:
    from piecewise_joint_flex import pose
from plan_current_rigid_factory_joins import moved_parts
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs

def reverse(parts):
    result=copy.deepcopy(list(reversed(parts)))
    for part in result:part['start'],part['end']=part['end'],part['start']
    return result

def run():
    tick=time.monotonic();files=[OUT/'continuous-joint-family-plan.json',OUT/'harness-interfaces-plan.json',
        ROOT/'hardware/simulation/p0/e6-leg-compatibility.json']
    family,ends,ax=[json.loads(p.read_text()) for p in files]
    sources={r['loom']:r for r in ends['looms']};approaches={};errors=[];trials=[]
    raised='--raised-second-plane' in sys.argv
    if raised:
        # The second source's uppermost pose left only67mm transverse span.
        # More handle/length cannot restoreR31.5 there. Retain Hip anchors,
        # add ONE radius of straight Hip-owned rise before its existing
        # quarter, and allocate the entire second Knee flex in that plane.
        for row in family['knees']:
            if not row['loom'].endswith('2'):continue
            link=next(r for r in family['interstage'] if r['loom']==row['loom'])
            old=copy.deepcopy(link['parts']);start=old[0]['start']
            for part in old:
                for key in ('start','mid','end'):
                    if key in part:part[key]=add(part[key],[0,0,R])
            link['parts']=[line(start,add(start,[0,0,R]))]+old
            link['guide_mm']+=R
            row['fixed_anchor_world_mm']=add(row['fixed_anchor_world_mm'],[0,0,R])
    for row in family['knees']:
        src=sources[row['loom']];axis=src['cable_exit_world_axis'];port=src['connector_reservation_world_mm'][src['project_connector_choice']]
        outer=add(port,mul(axis,14));land=add(port,mul(axis,23))
        arc,heading=turn(land,axis,mul(row['moving_tangent_rest_world'],-1),math.pi/2,R)
        approaches[row['loom']]=reverse([line(outer,land)]+arc)
        row['previous_moving_anchor_rest_world_mm']=row['moving_anchor_rest_world_mm']
        row['moving_anchor_rest_world_mm']=arc[-1]['end'];row['poses']=[]
        row['source_end_land_mm']=[land,outer];row['source_owner']=src['moving_saved_stage']
    for role in ('2','3'):
        rows=[r for r in family['knees'] if r['loom'].endswith(role)]
        chord=max(math.dist(r['fixed_anchor_world_mm'],r['moving_anchor_rest_world_mm']) for r in rows)
        lengths=[math.ceil((chord+extra*math.pi*R/2)/10)*10 for extra in (1,2,3)]
        chosen=None
        for length in lengths:
            failed=[(r['loom'],a) for r in rows for a in (-15,0,15) if pose(r,a,length) is None]
            trials.append(dict(role=role,length_mm=length,failed=failed))
            if not failed:chosen=length;break
        if chosen is None:
            errors.append(dict(role=role,cause='QUARTER_EXIT_FLEX_RADIUS_OR_LENGTH',lengths_mm=lengths));continue
        for row in rows:
            row.update(flex_guide_mm=chosen,flex_length_mm=chosen,guide_mm=chosen+18)
            for angle in ANGLES:
                parts=pose(row,angle,chosen)
                if parts is None:errors.append(dict(loom=row['loom'],angle=angle,cause='INTERMEDIATE_RADIUS'))
                else:row['poses'].append(dict(angle=angle,parts=parts))
            print('Source quarter Knee',row['loom'],chosen,'poses',len(row['poses']),flush=True)
    routes=[];near=[];self_hits=[];cases=0
    if not errors:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            hips=[r for r in family['hips'] if r['physical_leg']==leg];h=next(r for r in hips if r['loom'].endswith('1'))
            src=sources[h['loom']];port=src['connector_reservation_world_mm'][src['project_connector_choice']];axis=src['cable_exit_world_axis']
            options=candidates(h['moving_anchor_rest_world_mm'],h['moving_tangent_rest_world'],add(port,mul(axis,23)),mul(axis,-1))
            options.sort(key=lambda r:r['guide_mm']);selected=None;witnesses=[]
            for option in options:
                candidate={**approaches,h['loom']:option['parts']+[line(add(port,mul(axis,23)),add(port,mul(axis,14)))]}
                bad=[];own_near=[]
                for hip,knee in itertools.product((-15,0,15),repeat=2):
                    paths=[]
                    for row in hips:
                        name=row['loom'];parts=parts_for_loom(family,name,hip,knee,ax['axes'])+moved_parts(candidate[name],sources[name],hip,knee,ax['axes'])
                        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(parts,parts[1:]))
                        hit=self_screen(parts)
                        if hit:bad.append(dict(loom=name,hip=hip,knee=knee,**hit))
                        paths.append(dict(wire=name,OD_mm=6,segments=sampling_parts(parts)))
                    hits=only_new_pairs([],paths);own_near.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in hits)
                    if bad or any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in hits):break
                if not bad and not any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in own_near):
                    selected=candidate;near.extend(own_near);cases+=9;break
                witnesses.append(dict(topology=option['topology'],self=bad[:1],mutual=own_near[:1]))
            if selected:
                for row in hips:
                    n=row['loom'];parts=parts_for_loom(family,n,0,0,ax['axes'])+selected[n]
                    guide=sum(p['length_mm'] for p in parts)
                    routes.append(dict(loom=n,source=sources[n],source_parts=selected[n],guide_to_body_grip_mm=guide,
                        nominal_factory_remaining_after50mm_trim_mm=850-guide,body_route_not_yet_included=True))
            else:errors.append(dict(leg=leg,cause='WHOLE_THREE_CABLE_SCREEN',witnesses=witnesses))
            print('Source quarter whole leg',leg,bool(selected),flush=True)
    result=dict(status='REJECTED_SOURCE_QUARTER_LEG_PLAN' if errors else 'SOURCE_QUARTER_LEG_MATH_ONLY_MATERIAL_OPEN',
        hips=family['hips'],knees=family['knees'],interstage=family['interstage'],routes=routes,
        errors=errors,trials=trials,near_pairs=near,cases=cases,changed_math_poses=sum(len(r['poses']) for r in family['knees']),
        unchanged_Hip_sections=12,selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        socket14_OD6_R31_5_are_project_reservations=True,continuous_sweep_verified=False,
        invalidated='All8Knee flex paths/material/roots changed; retained12Hip paths require exact recipe equality for reuse.',
        open=['actual material/changed roots and grip lands','whole body routes/36ends/stock/mounts/assembly','delivered wire/socket/protectionE3'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files+[Path(__file__),Path(__file__).with_name('plan_socket_anchored_leg_looms.py')]},
        worker_seconds=round(time.monotonic()-tick,3))
    result['piecewise_flex']='--piecewise' in sys.argv
    result['raised_second_plane']=raised
    if result['piecewise_flex']:
        helper=Path(__file__).with_name('piecewise_joint_flex.py')
        result['source_sha256'][helper.relative_to(ROOT).as_posix()]=SHA(helper)
    filename='source-quarter-piecewise-leg-plan.json' if result['piecewise_flex'] else 'source-quarter-leg-plan.json'
    if raised:filename='source-quarter-shared-planes-plan.json'
    (OUT/filename).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','errors','cases','worker_seconds')}),flush=True)
    return result

if __name__=='__main__':run()
