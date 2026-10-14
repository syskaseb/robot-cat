"""Solve observed conflicts as one radial-seat/flex-run correction plan.

No further root offsets or cable lengths: preserve4root positions. Front
head/arm arrivals face inward. RR uses ONE feasible bridge angle for all31poses,
chosen against actual knee-carrier witnesses before any new support build.
"""
import copy
import json
import time
from pathlib import Path
import FreeCAD as A
from whole_current_body_material import load
from plan_low_hip_rail_exit import ends
from planar_round_flex import domain,build
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import self_screen
import current_body_fanout_material as M
P=M.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-low-hip-rail-exit-plan.json';prior=P.OUT/'body-rail-hip-shared-space.json'
    plan=json.loads(pf.read_text());rejected=json.loads(prior.read_text())
    assert rejected['status']=='REJECTED_RAIL_HIP_SHARED_SPACE' and len(rejected['contacts'])==5
    targets,wires,pins=load();row=next(r for r in plan['hips'] if r['loom']=='RR1')
    trials=[];choices=[]
    for beta in range(-60,61,2):
        poses=[]
        for angle in range(-15,16):
            a,b,v,moving=ends(row,angle);d=domain(a,b,v,beta)
            if not d or not d['minimum_mm']-1e-7<=155<=d['maximum_mm']+1e-7:break
            middle=build(a,b,v,155,d);parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,moving)]
            assert self_screen(parts) is None
            poses.append(dict(angle=angle,parts=parts,bridge_beta_degrees=beta))
        if len(poses)!=31:continue
        minimum=float('inf');witness=None
        for pose in poses:
            if pose['angle'] not in (-15,0,15):continue
            wire=P.wire(pose['parts'])
            for k in (-15,0,15):
                name=f'RearRightKneeCarrier/{pose["angle"]}/{k}';shape=targets[name]
                gap=wire.distToShape(shape)[0]
                if gap<minimum:minimum=gap;witness=dict(target=name,hip=pose['angle'],knee=k)
        trials.append(dict(beta_degrees=beta,minimum_actual_gap_mm=minimum,witness=witness))
        if minimum>=3.25-1e-6:choices.append((minimum,beta,poses))
    plan['retention_overrides']={loom:dict(arrival_normal=normal,terminal_axis_order=['Z','Y','X'])
        for loom,normal in (('FL1',[0,-1,0]),('FR1',[0,1,0]))}
    plan['correction_trials']=trials
    plan['correction_basis']='Two front band head contacts: rotate complete radial seat/arm arrivals inward. RR knee crossing: allocate one constant bridge angle across31poses from actual three-knee-motion witnesses; no root/length offsets.'
    plan['source_sha256']={**plan['source_sha256'],**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,prior,Path(__file__))}}
    plan['worker_seconds']=round(time.monotonic()-tick,3)
    if choices:
        gap,beta,poses=max(choices,key=lambda r:(r[0],-abs(r[1])))
        row['poses']=poses;row['common_bridge_beta_degrees']=beta
        plan['status']='COORDINATED_RAIL_HEADS_AND_RR_BRIDGE_PLAN_COMPLETE_FULL_SPACE_OPEN'
        plan['RR_witness_clearance_mm']=gap
    else:plan['status']='NO_RR_BRIDGE_ANGLE_CLEARS_ACTUAL_KNEE_WITNESSES_CHANGE_SPATIAL_PLANE'
    dest=P.OUT/'body-rail-hip-correction-plan.json';dest.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps(dict(status=plan['status'],trials=trials,worker_seconds=plan['worker_seconds'])),flush=True)


if __name__=='__main__':run()
