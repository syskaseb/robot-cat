"""One source-derived planar circular flex family and full source approaches.

Retain all12Hip sections; derive each Knee plane from the socket/actual axis,
connect that plane with a Hip-owned S, then solve one constant-length circular
topology at all31angles. No source splice, smallerR or pretend supplier data.
"""
import copy,itertools,json,math,time,sys
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,dot,rotation
from plan_current_mta_interfaces import line
from circular_joint_flex import csc,plane_shift,fixed_length
if '--straight-slack' in sys.argv:
    from circular_joint_flex import fixed_length_straight_slack as fixed_length
from rigid_tangent_channel import turn,candidates
from plan_source_quarter_leg_looms import reverse
from plan_continuous_joint_family import parts_for_loom,self_screen
from plan_current_rigid_factory_joins import moved_parts
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs

ANGLES=tuple(range(-15,16));R=31.5

def endpoints(row,a):
    p=row['pivot_mm'];moving=add(p,rotation(sub(row['moving_anchor_rest_world_mm'],p),row['joint_axis'],a))
    tangent=rotation(row['moving_tangent_rest_world'],row['joint_axis'],a)
    return add(row['fixed_anchor_world_mm'],mul(row['fixed_tangent_world'],9)),row['fixed_tangent_world'],sub(moving,mul(tangent,9)),tangent,moving

def run():
    tick=time.monotonic();files=[OUT/'continuous-joint-family-plan.json',OUT/'harness-interfaces-plan.json',
        ROOT/'hardware/simulation/p0/e6-leg-compatibility.json']
    family,ends,ax=[json.loads(p.read_text()) for p in files]
    srcs={r['loom']:r for r in ends['looms']};approaches={};errors=[];trials=[]
    raised='--raised-second-plane' in sys.argv
    if raised:
        # Required transverse span for the whole role2 angular range, not
        # an incremental clash offset. Preserve Hip flex and add a full
        # R of Hip-owned straight rise before the interstage quarter.
        for row in family['knees']:
            if not row['loom'].endswith('2'):continue
            link=next(r for r in family['interstage'] if r['loom']==row['loom'])
            old=copy.deepcopy(link['parts']);start=old[0]['start']
            for part in old:
                for key in ('start','mid','end'):
                    if key in part:part[key]=add(part[key],[0,0,R])
            link['parts']=[line(start,add(start,[0,0,R]))]+old
            row['fixed_anchor_world_mm']=add(row['fixed_anchor_world_mm'],[0,0,R])
    for row in family['knees']:
        name=row['loom'];src=srcs[name];exit=src['cable_exit_world_axis'];port=src['connector_reservation_world_mm'][src['project_connector_choice']]
        outer=add(port,mul(exit,14));land=add(port,mul(exit,23))
        arc,_=turn(land,exit,mul(row['moving_tangent_rest_world'],-1),math.pi/2,R)
        approaches[name]=reverse([line(outer,land)]+arc)
        row['moving_anchor_rest_world_mm']=arc[-1]['end'];row['poses']=[]
        shift=dot(sub(row['moving_anchor_rest_world_mm'],row['fixed_anchor_world_mm']),row['joint_axis'])
        bridge,new_fixed=plane_shift(row['fixed_anchor_world_mm'],row['fixed_tangent_world'],row['joint_axis'],shift)
        link=next(r for r in family['interstage'] if r['loom']==name)
        link['parts']+=bridge;link['guide_mm']=sum(p['length_mm'] for p in link['parts'])
        row['fixed_anchor_world_mm']=new_fixed
        options=[]
        for signs in ((1,1),(-1,-1),(1,-1),(-1,1)):
            paths=[csc(*endpoints(row,a)[:4],row['joint_axis'],R,signs) for a in ANGLES]
            if any(p is None for p in paths):continue
            length=math.ceil((max(p['length_mm'] for p in paths)+5)/5)*5
            solved=[fixed_length(*endpoints(row,a)[:4],row['joint_axis'],signs,length) for a in ANGLES]
            trials.append(dict(loom=name,signs=signs,length_mm=length,all31=all(p is not None for p in solved)))
            if all(p is not None for p in solved):options.append((length,signs,solved))
        if not options:
            errors.append(dict(loom=name,cause='NO_CONTINUOUS_CIRCULAR_TOPOLOGY'));continue
        length,signs,solved=min(options,key=lambda q:q[0]);row.update(flex_length_mm=length,flex_guide_mm=length,guide_mm=length+18,circular_topology=signs)
        for a,q in zip(ANGLES,solved):
            start,u,last,v,moving=endpoints(row,a)
            row['poses'].append(dict(angle=a,parts=[line(row['fixed_anchor_world_mm'],start),*q['parts'],line(last,moving)],radius_mm=q['radius_mm']))
        print('Circular source Knee',name,length,'minR',min(q['radius_mm'] for q in solved),flush=True)
    routes=[];near=[];cases=0
    if not errors:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            hips=[r for r in family['hips'] if r['physical_leg']==leg];h=next(r for r in hips if r['loom'].endswith('1'))
            src=srcs[h['loom']];port=src['connector_reservation_world_mm'][src['project_connector_choice']];exit=src['cable_exit_world_axis']
            options=candidates(h['moving_anchor_rest_world_mm'],h['moving_tangent_rest_world'],add(port,mul(exit,23)),mul(exit,-1))
            chosen=None;witnesses=[]
            for option in options:
                current={**approaches,h['loom']:option['parts']+[line(add(port,mul(exit,23)),add(port,mul(exit,14)))]}
                bad=[];mutual=[]
                for hip,knee in itertools.product((-15,0,15),repeat=2):
                    rows=[]
                    for row in hips:
                        n=row['loom'];parts=parts_for_loom(family,n,hip,knee,ax['axes'])+moved_parts(current[n],srcs[n],hip,knee,ax['axes'])
                        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(parts,parts[1:]))
                        hit=self_screen(parts)
                        if hit:bad.append(dict(loom=n,hip=hip,knee=knee,**hit))
                        rows.append(dict(wire=n,OD_mm=6,segments=sampling_parts(parts)))
                    hits=only_new_pairs([],rows);mutual.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in hits)
                    if bad or any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in hits):break
                if not bad and not any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in mutual):chosen=current;near+=mutual;cases+=9;break
                witnesses.append(dict(topology=option['topology'],self=bad[:1],mutual=mutual[:1]))
            if chosen:
                for row in hips:
                    n=row['loom'];parts=parts_for_loom(family,n,0,0,ax['axes'])+chosen[n];guide=sum(p['length_mm'] for p in parts)
                    routes.append(dict(loom=n,source=srcs[n],source_parts=chosen[n],guide_to_body_grip_mm=guide,
                        nominal_factory_remaining_after50mm_trim_mm=850-guide,body_route_not_included=True))
            else:errors.append(dict(leg=leg,cause='SHARED_THREE_CABLE_PLANNING_SCREEN',witnesses=witnesses))
            print('Circular shared',leg,bool(chosen),flush=True)
    result=dict(status='REJECTED_CIRCULAR_SOURCE_LEG_PLAN' if errors else 'CIRCULAR_SOURCE_LEG_PLAN_MATERIAL_OPEN',
        hips=family['hips'],knees=family['knees'],interstage=family['interstage'],routes=routes,errors=errors,trials=trials,
        near_pairs=near,cases=cases,changed_math_poses=sum(len(r['poses']) for r in family['knees']),
        project_minimum_R_mm=R,project_bundle_OD_mm=6,source_14mm_is_project_reservation=True,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
        open=['actual material with current head/stations','actual whole body fanouts/ends/grips/stock','native load paths and assembly','delivered wire/protectionE3'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files+[Path(__file__),Path(__file__).with_name('circular_joint_flex.py')]},
        worker_seconds=round(time.monotonic()-tick,3))
    result['straight_slack']='--straight-slack' in sys.argv
    result['raised_second_plane']=raised
    filename='circular-straight-slack-leg-plan.json' if result['straight_slack'] else 'circular-source-leg-plan.json'
    if raised:filename='circular-shared-planes-leg-plan.json'
    (OUT/filename).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','cases','worker_seconds')}),'errors',len(errors),flush=True)
    return result

def upper_front():
    """Reuse rear and all8Knee math; separate whole front Hip1 flex above.

    Exact planning witnesses identified retained LOWHip1 versus role2 source
    quarters. Changing source lead offsets would not fix that shared corridor.
    Reverse the two whole frontHip1 flex departures, not an anchor nudge.
    """
    from plan_continuous_joint_family import flex
    tick=time.monotonic();pf=OUT/'circular-shared-planes-leg-plan.json'
    family=json.loads(pf.read_text());ef=OUT/'harness-interfaces-plan.json';af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    srcs={r['loom']:r for r in json.loads(ef.read_text())['looms']};axes=json.loads(af.read_text())['axes']
    errors=[];near=[];cases=0;routes=copy.deepcopy(family['routes']);changed=[]
    for h in family['hips']:
        if h['loom'] not in ('FL1','FR1'):continue
        h['fixed_tangent_world']=[0,0,1];h['moving_tangent_rest_world']=[0,0,-1]
        length=h['flex_guide_mm'];h['poses']=[]
        for a in ANGLES:
            parts=flex(h,a,length)
            if parts is None:errors.append(dict(loom=h['loom'],angle=a,cause='UPPER_HIP1_FIXED_LENGTH_RADIUS'))
            else:h['poses'].append(dict(angle=a,parts=parts))
        changed.append(h['loom']);print('Front upperHip',h['loom'],len(h['poses']),flush=True)
    if not errors:
        for leg in ('FrontLeft','FrontRight'):
            hips=[r for r in family['hips'] if r['physical_leg']==leg];h=hips[0];approaches={}
            for row in family['knees']:
                if row['physical_leg']!=leg:continue
                src=srcs[row['loom']];port=src['connector_reservation_world_mm'][src['project_connector_choice']];exit=src['cable_exit_world_axis']
                arc,_=turn(add(port,mul(exit,23)),exit,mul(row['moving_tangent_rest_world'],-1),math.pi/2,R)
                approaches[row['loom']]=reverse([line(add(port,mul(exit,14)),add(port,mul(exit,23)))]+arc)
            src=srcs[h['loom']];port=src['connector_reservation_world_mm'][src['project_connector_choice']];exit=src['cable_exit_world_axis']
            options=candidates(h['moving_anchor_rest_world_mm'],h['moving_tangent_rest_world'],add(port,mul(exit,23)),mul(exit,-1))
            chosen=None;witnesses=[]
            for option in options:
                current={**approaches,h['loom']:option['parts']+[line(add(port,mul(exit,23)),add(port,mul(exit,14)))]}
                bad=[];mutual=[]
                for hip,knee in itertools.product((-15,0,15),repeat=2):
                    rows=[]
                    for row in hips:
                        n=row['loom'];parts=parts_for_loom(family,n,hip,knee,axes)+moved_parts(current[n],srcs[n],hip,knee,axes)
                        hit=self_screen(parts)
                        if hit:bad.append(dict(loom=n,hip=hip,knee=knee,**hit))
                        rows.append(dict(wire=n,OD_mm=6,segments=sampling_parts(parts)))
                    hits=only_new_pairs([],rows);mutual.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in hits)
                    if bad or any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in hits):break
                rejected=[r for r in mutual if r['status']=='REJECT_PLANNING_PROXIMITY']
                if not bad and not rejected:chosen=current;near+=mutual;cases+=9;break
                witnesses.append(dict(topology=option['topology'],self=bad[:1],mutual=(rejected or mutual)[:1]))
            if chosen:
                for row in hips:
                    n=row['loom'];parts=parts_for_loom(family,n,0,0,axes)+chosen[n];guide=sum(p['length_mm'] for p in parts)
                    routes.append(dict(loom=n,source=srcs[n],source_parts=chosen[n],guide_to_body_grip_mm=guide,
                        nominal_factory_remaining_after50mm_trim_mm=850-guide,body_route_not_included=True))
            else:errors.append(dict(leg=leg,cause='UPPER_FRONT_SHARED_SCREEN',witnesses=witnesses))
            print('Upper front shared',leg,bool(chosen),flush=True)
    report={k:v for k,v in family.items() if k not in ('status','errors','routes','source_sha256','worker_seconds','trials','near_pairs','cases')}
    report.update(status='REJECTED_UPPER_FRONT_LEG_PLAN' if errors else 'LEG_SOURCE_CURRENT_MATH_CLEAR_MATERIAL_OPEN',errors=errors,
        routes=routes,near_pairs=near,new_shared_cases=cases,exact_reused_rear_shared_cases=18,
        changed_Hip_sections=changed,changed_math_poses=62,exact_reused_Knee_math_poses=248,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (pf,ef,af,Path(__file__),Path(__file__).with_name('circular_joint_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'leg-source-current-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','worker_seconds','new_shared_cases')}),'errors',len(errors),flush=True)
    return report

if __name__=='__main__':
    upper_front() if '--front-hip-upper' in sys.argv else run()
