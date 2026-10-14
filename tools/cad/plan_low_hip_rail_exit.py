"""Four shared vertical low exits, derived from the complete core bend space.

Keep existing fixed/moving orientations and rootX/Y; lower only the four
Hip1 fixed lands enough for the5mm breakout+R10core bend beneath the boss.
Full fixed-root drop, three-core fan choices, changed arm and flex material
must be checked together before native detail. No native mutation.
"""
import copy
import json
import math
import time
from pathlib import Path
from plan_body_fanout_layout import OUT,ROOT,SHA
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from planar_round_flex import build,domain,merge,intersect


def ends(row,angle):
    pivot=row['pivot_mm']
    moving=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],angle))
    exit=rotation(row['moving_tangent_rest_world'],row['joint_axis'],angle)
    start=add(row['fixed_anchor_world_mm'],[0,0,-9]);end=sub(moving,mul(exit,9))
    return start,end,exit,moving


def run():
    tick=time.monotonic();source=OUT/'leg-source-near-member-plan.json'
    family=json.loads(source.read_text());rows=[copy.deepcopy(r) for r in family['hips'] if r['loom'].endswith('1')]
    # Actual retained boss bearing plane isZ-2, proved in station support data.
    boss_bottom=-2.;entry=5.;coreR=10.;core_envelope=1.25;reserve=1.75
    root_z=boss_bottom-entry-coreR-core_envelope-reserve
    requirements=[];domains={};common=[[0,850.]];angles=list(range(-60,61,2))
    for row in rows:
        row['previous_fixed_anchor_world_mm']=list(row['fixed_anchor_world_mm'])
        row['previous_flex_length_mm']=row['flex_length_mm']
        row['fixed_anchor_world_mm'][2]=root_z
        assert row['fixed_tangent_world']==[0,0,-1]
        for angle in range(-15,16):
            a,b,v,moving=ends(row,angle)
            choices=[d for beta in angles if (d:=domain(a,b,v,beta,31.5)) is not None]
            assert choices,(row['loom'],angle,'No positive-run circular construction')
            domains[row['loom'],angle]=choices
            intervals=merge([(d['minimum_mm'],d['maximum_mm']) for d in choices])
            requirements.append(dict(loom=row['loom'],angle=angle,feasible_intervals_mm=intervals))
            common=intersect(common,intervals)
    assert common,'No common exact length in bounded bridge-angle domains'
    fixed=[]
    for beta in angles:
        interval=[[0,850.]]
        for values in domains.values():
            interval=intersect(interval,[(d['minimum_mm'],d['maximum_mm']) for d in values if d['beta_degrees']==beta])
        if interval:fixed.append((abs(beta),beta,interval))
    selected_beta=None;allowance=5.;robust=[]
    for rank,beta,intervals in fixed:
        for lo,hi in intervals:
            nominal=math.ceil((lo+allowance)/5)*5
            if nominal+allowance<=hi+1e-8:robust.append((rank,beta,intervals,nominal))
    if robust:
        _,selected_beta,common,preset=min(robust,key=lambda r:(r[0],r[3]))
    else:preset=None
    length=None
    for lo,hi in common:
        nominal=math.ceil((lo+allowance)/5)*5 if preset is None else preset
        if nominal+allowance<=hi+1e-8:length=nominal;break
    assert length is not None,'No common length with project+/-5mm allowance; do not choose a precision-only midpoint'
    for row in rows:
        row['flex_length_mm']=length;row['flex_guide_mm']=length;row['guide_mm']=length+18;row['poses']=[]
        for angle in range(-15,16):
            a,b,v,moving=ends(row,angle)
            choices=[d for d in domains[row['loom'],angle] if d['minimum_mm']-1e-7<=length<=d['maximum_mm']+1e-7
                and (selected_beta is None or d['beta_degrees']==selected_beta)]
            assert choices
            choice=min(choices,key=lambda d:abs(d['beta_degrees']));middle=build(a,b,v,length,choice);assert middle is not None
            parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,moving)]
            row['poses'].append(dict(angle=angle,parts=parts,bridge_beta_degrees=choice['beta_degrees']))
        first=row['poses'][15]['parts'][0]
        row['fixed_lands']=[dict(id=row['loom']+'/Hip/Fixed',parts=[first],owner='Body')]
    files=(source,Path(__file__),Path(__file__).with_name('planar_round_flex.py'),Path(__file__).with_name('plan_current_moving_looms.py'),Path(__file__).with_name('plan_current_mta_interfaces.py'),OUT/'data-ground-mounts-plan.json')
    result=dict(status='LOW_HIP_VERTICAL_RAIL_EXIT_MATH_CLEAR_SHARED_FANS_ARMS_MATERIAL_OPEN',hips=rows,
        chosen_common_flex_mm=length,common_bridge_beta_degrees=selected_beta,common_feasible_intervals_mm=common,
        project_common_length_allowance_mm=allowance,
        exact_motion_length_requirements=requirements,errors=[],fixed_land_count=4,additional_fixed_bands=0,
        construction='Preserved vertical9mm fixedland withfourderivedZdrops, exactR31.5two-arc constant-length U, unchanged moving9mm land',
        root_space_derivation=dict(actual_boss_bottom_Z_mm=boss_bottom,maximum_core_entry_mm=entry,core_R_mm=coreR,
            core_radius_plus_margin_mm=core_envelope,additional_project_vertical_reserve_mm=reserve,new_root_Z_mm=root_z),
        source_core_fans='Allocate all three cores together. For each horizontal exit direction, entry_i=5+min(dot(offset,v))-dot(offset_i,v); transported triangular packing preserves separation throughR10 bend. Four whole directions perleg; choose only with current material/arms/otherwires.',
        preserved=['RootX/Y, original fixed/moving tangents and moving9mm lands','Other8sourcefamilies','Elevenqualifiedbodyroutes','Samefourbodyframeparents/mountinghardware'],
        invalidates=['Four fixedportZpositions/armendextensions','FourHip1completeflex/material andlengthbudget, no inherited current acceptance'],
        rejected_prior='daa5875 whole2501-instance gate:37actualcontacts, no errors. Do not repeat compoundquarter/long250-240mm U or add its4extraT18I toselectedstock.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-low-hip-rail-exit-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],common_flex_mm=length,whole_guide_mm=length+18,root_Z_mm=root_z,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
