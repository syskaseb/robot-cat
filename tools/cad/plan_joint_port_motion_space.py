"""Shared layout is not an unnecessary equal-height constraint.

Select individual roots from complete assembly reservation domains, retaining
the original inward X breakout topology. RR takes the lower robust portion
because its old flex crossed the knee carrier. One common cable length is
then solved across all124poses; actual new motion/material gate remains open.
"""
import copy
import json
import math
import time
from pathlib import Path
from plan_low_hip_rail_exit import ends
from planar_round_flex import domain,build,merge,intersect
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import self_screen
from plan_body_fanout_layout import OUT,ROOT,SHA


def run():
    tick=time.monotonic();df=OUT/'body-fixed-port-vertical-space.json';space=json.loads(df.read_text())
    assert len(space['domains'])==16 and 'INCOMPLETE' not in space['status']
    for n,h in space['source_sha256'].items():assert SHA(ROOT/n)==h,n
    pf=OUT/'body-low-hip-rail-exit-plan.json';prior=json.loads(pf.read_text())
    rows=copy.deepcopy(prior['hips']);chosen=[];domains={};common=[[0,850.]];per_loom={}
    for row in rows:
        loom=row['loom'];direction=[1,0,0] if row['physical_leg'].startswith('Front') else [-1,0,0]
        reservation=next(r for r in space['domains'] if r['loom']==loom and r['direction']==direction)
        options=[]
        for lo,hi in reservation['allowed_root_Z_mm']:
            low,high=math.ceil(lo+1),math.floor(hi-1)
            if high<low:continue
            z=low if loom=='RR1' else max(low,min(high,-20))
            options.append((abs(z+20),z,[lo,hi]))
        assert options,(loom,'No reserved root with1mm interval-edge reserve; do not guess')
        _,z,interval=min(options)
        chosen.append(dict(loom=loom,root_Z_mm=z,source_direction=direction,allowed_root_Z_mm=interval,
            basis='RR1 lower robust domain: old flex intersects knee carrier' if loom=='RR1' else 'Nearest previous nominal root within whole-material reserved domain',
            project_interval_edge_reserve_mm=1))
        row['fixed_anchor_world_mm'][2]=z
        per_loom[loom]=[[0,850.]]
        for angle in range(-15,16):
            a,b,v,moving=ends(row,angle)
            choices=[d for beta in range(-74,75,2) if (d:=domain(a,b,v,beta)) is not None]
            assert choices,(loom,angle)
            domains[loom,angle]=choices
            interval=merge([(d['minimum_mm'],d['maximum_mm']) for d in choices])
            common=intersect(common,interval);per_loom[loom]=intersect(per_loom[loom],interval)
    length=None
    for lo,hi in common:
        candidate=155 if lo+5<=155<=hi-5 else math.ceil((lo+5)/5)*5
        if lo+5<=candidate<=hi-5:length=candidate;break
    print(json.dumps(dict(common=common,per_loom=per_loom)),flush=True)
    for row in rows:
        loom=row['loom'];nominal=length
        if nominal is None:
            for lo,hi in per_loom[loom]:
                candidate=155 if lo+5<=155<=hi-5 else math.ceil((lo+5)/5)*5
                if lo+5<=candidate<=hi-5:nominal=candidate;break
        if nominal is None:
            failed=dict(status='VERTICAL_TWO_ARC_FLEX_HAS_NO_ROBUST_LENGTH_CHANGE_WHOLE_ENTRY_DIRECTION',
                root_selection=chosen,common_intervals_mm=common,per_loom_intervals_mm=per_loom,
                failed_loom=loom,requested_length_allowance_mm=5,
                source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (df,pf,Path(__file__),Path(__file__).with_name('planar_round_flex.py'))},
                worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False,
                decision='Do not select a precision-only midpoint or weaken5mm allowance to green. Vertical fixed-entry CSC class is overconstrained; plan whole oblique fixed-entry family and full source-port/corefan geometry together.')
            (OUT/'body-joint-port-motion-plan.json').write_text(json.dumps(failed,indent=2)+'\n')
            raise AssertionError(('No constant nominal guide with+/-5mm allowance',loom,per_loom[loom]))
        guide=nominal;row['poses']=[];row['flex_length_mm']=guide;row['flex_guide_mm']=guide;row['guide_mm']=guide+18
        fixed=[beta for beta in range(-74,75,2) if all(any(d['beta_degrees']==beta and d['minimum_mm']<=guide-5 and d['maximum_mm']>=guide+5
            for d in domains[loom,angle]) for angle in range(-15,16))]
        beta=min(fixed,key=abs) if fixed else None
        row['common_bridge_beta_degrees']=beta
        for angle in range(-15,16):
            a,b,v,moving=ends(row,angle)
            choices=[d for d in domains[loom,angle] if d['minimum_mm']-1e-8<=guide<=d['maximum_mm']+1e-8 and (beta is None or d['beta_degrees']==beta)]
            assert choices,(loom,angle,guide)
            choice=min(choices,key=lambda d:abs(d['beta_degrees']));middle=build(a,b,v,guide,choice)
            parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,moving)]
            assert self_screen(parts) is None,(loom,angle)
            row['poses'].append(dict(angle=angle,parts=parts,bridge_beta_degrees=choice['beta_degrees']))
        row['fixed_lands']=[dict(id=loom+'/Hip/Fixed',parts=[row['poses'][15]['parts'][0]],owner='Body')]
    files=(df,pf,Path(__file__),Path(__file__).with_name('planar_round_flex.py'),Path(__file__).with_name('plan_low_hip_rail_exit.py'),
        OUT/'body-rail-knee-crossing-witnesses.json')
    result=dict(status='JOINT_PORT_ROOTS_AND124CONSTANT_LENGTH_POSES_PLANNED_FULL_MATERIAL_ARMS_OPEN',hips=rows,
        root_selection=chosen,chosen_common_flex_mm=length,chosen_flex_by_loom_mm={r['loom']:r['flex_length_mm'] for r in rows},common_feasible_intervals_mm=common,per_loom_feasible_intervals_mm=per_loom,project_common_length_allowance_mm=5,
        fixed_land_count=4,additional_fixed_bands=0,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3),
        selected=False,W5_complete=False,physical_pass=False,
        scope='Individual four roots from FULL scene port/band/corefan reservation domains; one common R31.5 nominal flex length across124poses. Actual newflex/ground/retainedKneeCarrier/changedterminalarms and wholeW5 remain OPEN. No requirement for equal root heights.',
        preserved=['Existing rootX/Y and moving factory-end positions/tangents','Other8sourcefamilies and11qualifiedbodypaths','No extra fixed bands or new electrical connections'])
    (OUT/'body-joint-port-motion-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],roots=chosen,flex_by_loom_mm=result['chosen_flex_by_loom_mm'],common_intervals=common,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
