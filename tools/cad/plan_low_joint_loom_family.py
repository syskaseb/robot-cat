"""Plan BOTH Hip/Knee flex directions before any detailed support operation.

The previous low Hip collided with the inherited inward Knee arch. Here the
Knee family turns toward the free outer-X side. Ten-mm cable lanes reserve
8.4mm strap silhouettes rather than the impossible old8mm pitch. Full
material/roots/body and connector joins remain separate required gates.
"""
import copy,itertools,json,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_joint_local_looms import solve_loop,scene_parts,LENGTH
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs


def hip_parts(r,angle):
    pv=r['pivot_mm'];fixed=r['fixed_anchor_world_mm']
    moving=add(pv,rotation(sub(r['moving_anchor_rest_world_mm'],pv),r['joint_axis'],angle))
    entry=[0,0,-1];exit=rotation([0,0,1],r['joint_axis'],angle)
    start=add(fixed,mul(entry,9));end=sub(moving,mul(exit,9))
    q=solve_loop(start,entry,end,exit,length=r['flex_length_mm'])
    return None if q is None else [line(fixed,start),q,line(end,moving)]


def build():
    tick=time.monotonic();hf=OUT/'side-hip-arches-plan.json';kf=OUT/'joint-local-knee-plan.json'
    hips=copy.deepcopy(json.loads(hf.read_text())['loops']);knees=copy.deepcopy(json.loads(kf.read_text())['loops'])
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    errors=[];trials=[]
    for leg in dict.fromkeys(r['physical_leg'] for r in hips):
        for i,r in enumerate(v for v in hips if v['physical_leg']==leg):
            r.pop('poses',None);r['fixed_anchor_world_mm'][2]=30;r['moving_anchor_rest_world_mm'][2]=30
            r['fixed_anchor_world_mm'][1]=r['side']*(104+10*i)
            r['moving_anchor_rest_world_mm'][1]=r['side']*(104+10*i)
    chosen=None
    for length in range(125,186,5):
        for r in hips:r['flex_length_mm']=length
        good=all(hip_parts(r,a) is not None for r in hips for a in (-15,0,15))
        trials.append(dict(length_mm=length,all_extrema_feasible=good))
        if good:chosen=length;break
    if chosen is None:errors.append('No common Hip flex solution in125..185')
    mathposes=0
    if chosen:
        for r in hips:
            r['guide_mm']=chosen+18;r['recipe']='LOW DOWNWARD XZ, fixed DOWN/moving UP; 10mm lanes'
            for angle in range(-15,16):
                mathposes+=1
                if hip_parts(r,angle) is None:errors.append([r['section'],angle,'Hip radius/length'])
    for r in knees:
        # Reverse the complete Knee arch, not one waypoint. Endpoints and
        # inherited actual axis retained; both independent grip lands reverse.
        r['fixed_tangent_world']=mul(r['fixed_tangent_world'],-1)
        r['moving_tangent_rest_world']=mul(r['moving_tangent_rest_world'],-1)
        r['poses']=[];r['recipe']='OUTWARD X knee arch, full tangent reversal, actual tilted Knee axis retained'
        for angle in range(-15,16):
            mathposes+=1;pv=r['pivot_mm'];fixed=r['fixed_anchor_world_mm']
            moving=add(pv,rotation(sub(r['moving_anchor_rest_world_mm'],pv),r['joint_axis'],angle))
            entry=r['fixed_tangent_world'];exit=rotation(r['moving_tangent_rest_world'],r['joint_axis'],angle)
            start=add(fixed,mul(entry,9));end=sub(moving,mul(exit,9))
            q=solve_loop(start,entry,end,exit,length=LENGTH)
            if q is None:errors.append([r['section'],angle,'Knee radius/length']);continue
            r['poses'].append(dict(angle=angle,parts=[line(fixed,start),q,line(end,moving)]))
    near=[];cases=0
    if not errors:
        for leg in dict.fromkeys(r['physical_leg'] for r in hips):
            hh=[r for r in hips if r['physical_leg']==leg];kk=[r for r in knees if r['physical_leg']==leg]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                rows=[dict(wire=r['section'],OD_mm=6,segments=sampling_parts(hip_parts(r,hip))) for r in hh]
                rows += [dict(wire=r['section'],OD_mm=6,segments=sampling_parts(scene_parts(r,hip,knee,axes))) for r in kk]
                cases+=1
                near.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in only_new_pairs([],rows))
            print('shared Hip/Knee planned',leg,flush=True)
    bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    report=dict(status='REJECTED_LOW_JOINT_FAMILY_PLANNING' if errors or bad else 'LOW_JOINT_FAMILY_SAMPLED_SCREEN_CLEAR_MATERIAL_ROOTS_OPEN',
        hips=hips,knees=knees,math_poses=mathposes,cases=cases,near_pairs=near,errors=errors,rejected=bad,
        common_Hip_length_trials=trials,selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        scope='12Hip+8Knee flex sections only; same-leg9poses, other legs nominal. Whole cables/end joins and actual support/material gates OPEN.',
        fixed_root_plan='Use current four P station clamp positions X40/115, clear of F0; bridge along rail before descending at flex planes. No hole in P0; full inherited envelope not accepted.',
        moving_root_plan='Keyed case cap; band around casing ONLY, not protruding connector. Head above case, not across centerline or into Knee motor. Front low-X/rear high-X side beams and complete outer rung support all three posts.',
        rejected_topology='LowHip with old inwardKnee; unconnected posts,8mm lanes with8.4mm straps,rail feet under F0/splice and inward strapheads.',
        required=['Actual valid BRep+all affected supports and fasteners','Whole cable body/servo ends and grips','Motion and assembly access','Factory length/stock and selection'],
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (hf,kf,af,Path(__file__))})
    (OUT/'low-joint-family-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','math_poses','cases','errors','worker_seconds')}), 'rejected',len(bad),flush=True)


if __name__=='__main__':build()
