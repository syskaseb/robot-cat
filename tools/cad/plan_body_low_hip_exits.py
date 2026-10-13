"""One coordinated four-Hip1 exit-orientation plan, no native mutation.

The under-rail fixed lands cannot use an upward body fan behind a5mm straight.
Keep their locations and all moving lands; orient the fixed9mm land inward
so the body continuation leaves horizontally OUTWARD for15mm before rising.
Re-solve whole existing flexes at fixed common lengths, retaining R31.5.
All changed fixed-grip/support/material and stock gates remain OPEN.
"""
import copy
import json
import math
import time
from pathlib import Path
from plan_body_fanout_layout import OUT,ROOT,SHA
from plan_continuous_joint_family import flex
from plan_current_moving_looms import exact_quarter,add,mul,sub,rotation
from plan_current_mta_interfaces import line
from plan_current_joint_local_looms import solve_loop
from constant_radius_u_flex import build as round_u,minimum as minimum_u


def flex_inputs(row,angle):
    entry=row['fixed_tangent_world']
    first=line(row['fixed_anchor_world_mm'],add(row['fixed_anchor_world_mm'],mul(entry,9)))
    bend=exact_quarter(first['end'],entry,[0,0,-1],31.5)
    down=[0,0,-1];joint_start=add(bend['end'],mul(down,9))
    pv=row['pivot_mm']
    moving=add(pv,rotation(sub(row['moving_anchor_rest_world_mm'],pv),row['joint_axis'],angle))
    exit=rotation(row['moving_tangent_rest_world'],row['joint_axis'],angle)
    end=sub(moving,mul(exit,9))
    return [first,bend,line(bend['end'],joint_start)],joint_start,end,exit,moving


def compound_flex(row,angle,length):
    prefix,start,end,exit,moving=flex_inputs(row,angle)
    loop=round_u(start,end,exit,length,31.5)
    return None if loop is None else [*prefix,*loop,line(end,moving)]


def run():
    tick=time.monotonic();source=OUT/'leg-source-near-member-plan.json'
    old=json.loads(source.read_text());rows=[copy.deepcopy(r) for r in old['hips'] if r['loom'].endswith('1')]
    assert len(rows)==4
    for row in rows:
        row['previous_fixed_anchor_world_mm']=list(row['fixed_anchor_world_mm'])
        side=1 if row['fixed_anchor_world_mm'][1]>0 else -1
        # Paired left/right fixed quarters must never cross the centreline.
        # 9mm land + R31.5 turn +5mm half-gap leaves10mm between U roots
        # (8.4mm band envelopes plus1.6mm nominal separation).
        row['fixed_anchor_world_mm'][1]=side*(9+31.5+5)
        row['fixed_tangent_world']=[0,-side,0]
    requirements=[]
    for row in rows:
        for angle in range(-15,16):
            prefix,start,end,exit,moving=flex_inputs(row,angle)
            required=minimum_u(start,end,exit,31.5)
            requirements.append(dict(loom=row['loom'],angle=angle,minimum_flex_mm=required['length_mm']))
    chosen=math.ceil(max(r['minimum_flex_mm'] for r in requirements)/10)*10+10
    trials=[dict(common_flex_mm=chosen,basis='Maximum exact geometric minimum across124poses, rounded10mm plus10mm project length allowance')]
    errors=[]
    if chosen:
        for row in rows:
            row['previous_flex_length_mm']=row['flex_length_mm']
            row['flex_length_mm']=chosen+31.5*math.pi/2;row['flex_guide_mm']=row['flex_length_mm']
            row['guide_mm']=chosen+27+31.5*math.pi/2
            prefix,_,_,_,_=flex_inputs(row,0)
            row['fixed_lands']=[dict(id=row['loom']+'/Hip/Fixed',parts=[prefix[0]],owner='Body'),
                dict(id=row['loom']+'/Hip/FixedBend',parts=[prefix[2]],owner='Body',new_independent_band=True)]
            row['poses']=[]
            for angle in range(-15,16):
                parts=compound_flex(row,angle,chosen)
                if parts is None:errors.append([row['loom'],angle,'R31.5 common-length solution unavailable'])
                else:row['poses'].append(dict(angle=angle,parts=parts))
    result=dict(status='LOW_HIP1_HORIZONTAL_EXIT_MATH_CLEAR_MATERIAL_AND_RETENTION_OPEN' if chosen and not errors else 'LOW_HIP1_HORIZONTAL_EXIT_MATH_UNRESOLVED',
        hips=rows,common_length_trials=trials,chosen_common_flex_mm=chosen,errors=errors,
        body_exit_project_straight_mm=15,exact_motion_length_requirements=requirements,
        construction='Unmoved fixed9mm inward land + staticR31.5downwardquarter +9mm straight + variable-straights/exactR31.5two-arc constant-length U + preserved moving9mm land',
        design_basis='Keep X/Z and move the paired root centres toY+/-45.5 =9+31.5+5mm. This reserves10mm between mirrored quarters/8.4mm bands BEFORE CAD. Body leaves outward15mm below rail before rising. Exact roundU preserves R31.5 and constant cable length.',
        rejected_single_cubic=[dict(factory_direction='toward_leg',lengths_mm=[150,160,170,180],failed_extrema_each=12,worker_seconds=16.719),
            dict(factory_direction='inward',lengths_mm=[180,200,220,240],failed_extrema_each=12,worker_seconds=22.375)],
        received_compound_bracket=dict(lengths_mm=[180,200,220,240],failed_extrema_counts=[6,4,4,4],worker_seconds=7.219,
            diagnosis='Old50..90mm handle domain rejects opposite extremes even at210. New bounded20..160mm domain preserves cable length andR31.5 rather than moving roots or loosening radii.'),
        rejected_upper_gallery_cubic=dict(lengths_mm=[220,240,260,280],failed_extrema_each=12,worker_seconds=19.359,not_geometric_impossibility=True),
        fixed_land_count=8,additional_fixed_bands=4,changed_fixed_support_groups=4,
        preserves=['Fixed-root X/Z, same actual frame mounting interfaces','All four moving9mm lands and factory end joins','Other eight flex/support families','Eleven received body fanouts'],
        invalidates=['Four Hip1 fixed9mm land Ypositions/orientations/ports and their changed support arms; four additional fixed U-entry lands',
            'Four complete Hip1 flex material/motion results and associated cable budgets; no point retained for changed interfaces'],
        open=['Actual full four-cable motion against retained assembly and each other','Shared horizontal fixed grips/arms/assembly and native export',
            'Changed twelve-core breakout space, full body routes and corrected cut/stock'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (source,Path(__file__),Path(__file__).with_name('constant_radius_u_flex.py'),Path(__file__).with_name('plan_continuous_joint_family.py'),Path(__file__).with_name('plan_current_joint_local_looms.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-low-hip-exit-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','chosen_common_flex_mm','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
