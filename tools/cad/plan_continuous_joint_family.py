"""Couple Hip/Knee anchors BEFORE supports; keep a real rigid interstage bend.

No claim of complete servo-to-body cables: these still need actual end joins,
material clearance, support load paths and stock. Old isolated-flex proofs do
not validate these changed anchors. All coordinates remain world-rest mm.
"""
import copy
import itertools
import json
import math
import time
from pathlib import Path

from plan_current_main_sources import ROOT, OUT, SHA
from plan_current_joint_local_looms import solve_loop, scene_parts, expanded_pose
from plan_current_moving_looms import add, sub, mul, rotation
from plan_current_mta_interfaces import line
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs
from open_prototype_path_preflight import samples

R = 31.5  # project reservation, NOT manufacturer dynamic qualification
LAND = 9.0
ANGLES = tuple(range(-15, 16))


def flex(row, angle, length):
    pivot = row['pivot_mm']
    moving = add(pivot, rotation(sub(row['moving_anchor_rest_world_mm'], pivot), row['joint_axis'], angle))
    entry = row.get('fixed_tangent_world', [0, 0, -1])
    exit = rotation(row.get('moving_tangent_rest_world', [0, 0, 1]), row['joint_axis'], angle)
    start = add(row['fixed_anchor_world_mm'], mul(entry, LAND))
    end = sub(moving, mul(exit, LAND))
    for first in (70, 65, 75, 60, 80, 55, 85, 50, 90):
        q = solve_loop(start, entry, end, exit, length=length, first_candidates=(first,))
        if q is not None and q['sampled_minimum_R_mm'] >= R:
            return [line(row['fixed_anchor_world_mm'], start), q, line(end, moving)]
    return None


def quarter(start, end, dx):
    assert abs(end[0]-start[0]-dx*R) < 1e-7
    assert abs(end[1]-start[1]) < 1e-7
    assert abs(end[2]-start[2]-R) < 1e-7
    mid = add(start, [dx*R*(1-math.sqrt(.5)), 0, R*math.sqrt(.5)])
    return dict(kind='arc', start=start, mid=mid, end=end,
                radius_mm=R, length_mm=math.pi*R/2,
                parent_stage='Hip', motion_stage='Hip', fixed_relative_to_Hip=True)


def rigid_scene(row, hip, axes):
    result = copy.deepcopy(row['parts'])
    ax = next(a for a in axes if a['code']==row['cad_code'] and a['stage']=='Hip')
    for q in result:
        for key in ('start', 'mid', 'end'):
            if key in q:
                q[key] = add(ax['pivot_mm'], rotation(sub(q[key], ax['pivot_mm']), ax['axis'], hip))
    return result


def parts_for_loom(family, loom, hip, knee, axes):
    h = next(r for r in family['hips'] if r['loom']==loom)
    result = copy.deepcopy(expanded_pose(h,hip)['parts'])
    k = next((r for r in family['knees'] if r['loom']==loom), None)
    if k:
        link = next(r for r in family['interstage'] if r['loom']==loom)
        result += rigid_scene(link, hip, axes) + scene_parts(k, hip, knee, axes)
    for a, b in zip(result, result[1:]):
        assert math.dist(a['end'], b['start']) < 1e-6, (loom, hip, knee, 'discontinuity')
    return result


def self_screen(parts):
    """Sample nonlocal jacket self-contact; adjacent12mm is one cable land.

    This does not prove exact clearance. A true nearby self-return separated
    by >12mm of centreline must not be hidden by grouping one continuous row.
    """
    grid={};length=0.;previous=None
    for _,p in samples(sampling_parts(parts),step=1):
        if previous is not None:length+=math.dist(previous,p)
        previous=p;key=tuple(math.floor(v/6) for v in p)
        for delta in itertools.product((-1,0,1),repeat=3):
            for q,walked in grid.get(tuple(a+b for a,b in zip(key,delta)),()):
                if length-walked>12 and math.dist(p,q)<6:
                    return dict(sample_a_mm=q,sample_b_mm=p,centreline_gap_mm=math.dist(p,q),
                                separated_along_cable_mm=length-walked)
        grid.setdefault(key,[]).append((p,length))
    return None


def build():
    tick=time.monotonic()
    hf=OUT/'low-joint-family-plan.json'; kf=OUT/'outboard-knee-planes-plan.json'
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    family=dict(hips=copy.deepcopy(json.loads(hf.read_text())['hips']),
                knees=copy.deepcopy(json.loads(kf.read_text())['knees']), interstage=[])
    axes=json.loads(af.read_text())['axes']; errors=[]; trials=[]
    # Derive BOTH endpoints from one tangent-continuous quarter-circle. The
    # fixed Hip endpoint translates with its moving endpoint along shaft X;
    # their larger radial lever arm is then solved at every sampled angle.
    for knee in family['knees']:
        hip=next(r for r in family['hips'] if r['loom']==knee['loom'])
        dx=knee['fixed_tangent_world'][0]
        assert abs(abs(dx)-1)<1e-7
        x=knee['fixed_anchor_world_mm'][0]-dx*R
        delta=x-hip['moving_anchor_rest_world_mm'][0]
        for key in ('fixed_anchor_world_mm', 'moving_anchor_rest_world_mm'):
            hip[key][0]+=delta
            hip[key][1]=knee['fixed_anchor_world_mm'][1]
        knee['fixed_anchor_world_mm'][2]=hip['moving_anchor_rest_world_mm'][2]+R
        family['interstage'].append(dict(loom=hip['loom'], cad_code=hip['cad_code'],
            physical_leg=hip['physical_leg'], section=hip['loom']+'/HipRigidJoin',
            parts=[quarter(hip['moving_anchor_rest_world_mm'], knee['fixed_anchor_world_mm'], dx)],
            guide_mm=math.pi*R/2, new_electrical_connectors=0, rigid_owner='Hip'))
    # One bounded family length choice, not a new CAD variant per failed pose.
    for stage in ('hips', 'knees'):
        rows=family[stage]; chosen=None
        for length in (160, 170, 180, 190):
            feasible=all(flex(r,a,length) is not None for r in rows for a in (-15,0,15))
            trials.append(dict(stage=stage, length_mm=length, all_extrema_feasible=feasible))
            if feasible: chosen=length; break
        if chosen is None:
            errors.append(dict(stage=stage, cause='NO_COMMON_LENGTH_FOR_DERIVED_SHARED_ANCHORS'))
            continue
        for row in rows:
            row['poses']=[];row['flex_length_mm']=chosen;row['flex_guide_mm']=chosen
            row['guide_mm']=chosen+2*LAND
            row['recipe']='Joint anchors derived together with Hip-owned R31.5 quarter connector, independent9mm lands'
            for angle in ANGLES:
                parts=flex(row,angle,chosen)
                if parts is None:
                    errors.append(dict(loom=row['loom'],stage=stage,angle=angle,cause='RADIUS_OR_LENGTH'))
                else: row['poses'].append(dict(angle=angle,parts=parts))
            print('continuous family math', row['section'], 'poses',len(row['poses']),flush=True)
    rejected=[];near=[];cases=0;budgets=[];self_contacts=[]
    if not errors:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            looms=[h['loom'] for h in family['hips'] if h['physical_leg']==leg]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                rows=[]
                for n in looms:
                    parts=parts_for_loom(family,n,hip,knee,axes)
                    hit=self_screen(parts)
                    if hit:self_contacts.append(dict(loom=n,hip=hip,knee=knee,**hit))
                    rows.append(dict(wire=n,OD_mm=6,segments=sampling_parts(parts)))
                hits=only_new_pairs([],rows);cases+=1
                near.extend(dict(physical_leg=leg,hip=hip,knee=knee,**q) for q in hits)
            for loom in looms:
                parts=parts_for_loom(family,loom,0,0,axes)
                length=sum(p['length_mm'] for p in parts)
                budgets.append(dict(loom=loom,connected_joint_sections_mm=length,
                    project_assumed_usable_900mm_lead_mm=850, remaining_for_actual_factory_and_body_joins_mm=850-length,
                    delivered_length_confirmed=False, complete_cable=False))
            print('continuous mutual screen',leg,flush=True)
        rejected=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    family.update(status='REJECTED_CONTINUOUS_JOINT_FAMILY_PLAN' if errors or rejected or self_contacts else 'CONTINUOUS_JOINT_SECTIONS_MATH_SCREEN_ONLY',
        errors=errors, rejected=rejected, self_contacts=self_contacts, near_pairs=near, cases=cases, length_trials=trials,
        math_poses=sum(len(r['poses']) for s in ('hips','knees') for r in family[s]), length_budgets=budgets,
        project_minimum_R_mm=R, insulation_OD_mm=6, independent_land_mm=LAND,
        shared_topology='8Hip-owned exact quarter-circle joins, with both endpoint anchors derived together;12Hip and8Knee fixed-length flex sections.',
        invalidated_candidates=['old separate Hip/Knee clearance does not validate changed flex paths or supports'],
        open=['actual factory exits to Knee grips and Hip-only servo','body receiver to Hip grips and all36 ends',
              'exact self-contact/clearance within each continuous loom','actual material at coupled motions',
              'all changed fixed and moving supports and access','delivered cable dimensions and factory length',
              'editable native/printable exports','stock/full assembly and selection'],
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        continuous_sweep_verified=False,manufacturer_dynamic_radius_verified=False,
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (hf,kf,af,Path(__file__),
            Path(__file__).with_name('plan_current_joint_local_looms.py'),Path(__file__).with_name('plan_current_moving_looms.py'))})
    (OUT/'continuous-joint-family-plan.json').write_text(json.dumps(family,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:family[k] for k in ('status','math_poses','cases','errors','worker_seconds')}),'rejected',len(rejected),flush=True)
    return family


def compact_existing():
    """Mechanical storage change, only after exact620recipe equivalence.

    Preserve the original material result/time. Do NOT rerun identical
    Booleans or represent this as another collision validation milestone.
    """
    tick=time.monotonic();fp=OUT/'continuous-joint-family-plan.json'
    gp=OUT/'continuous-joint-family-checks.json';family=json.loads(fp.read_text());gate=json.loads(gp.read_text())
    assert family['status']=='CONTINUOUS_JOINT_SECTIONS_MATH_SCREEN_ONLY'
    assert gate['status']=='CONTINUOUS_JOINT_SECTIONS_SAMPLED_MATERIAL_CLEAR_SUPPORTS_OPEN'
    assert gate['source_sha256'][fp.relative_to(ROOT).as_posix()]==SHA(fp)
    keys=('kind','start','end','mid','poles_mm','radius_mm')
    def geometry(parts):return [{k:s[k] for k in keys if k in s} for s in parts]
    count=0
    for stage in ('hips','knees'):
        for row in family[stage]:
            if stage=='hips':
                row.setdefault('fixed_tangent_world',[0,0,-1]);row.setdefault('moving_tangent_rest_world',[0,0,1])
            before=copy.deepcopy(row['poses'])
            row['poses']=[dict(angle=p['angle'],**{k:p['parts'][1][k] for k in
                ('first_handle_mm','second_handle_mm','length_mm','sampled_minimum_R_mm')}) for p in before]
            for old in before:
                assert geometry(old['parts'])==geometry(expanded_pose(row,old['angle'])['parts']), (row['loom'],old['angle'])
                count+=1
    assert count==620
    receipt=dict(storage_only=True,exact_equal_geometry_recipes=620,
                 new_collision_tests=0,original_material_worker_seconds=gate['worker_seconds'],
                 equivalence_seconds=round(time.monotonic()-tick,3))
    family['storage_equivalence']=receipt
    family['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
    fp.write_text(json.dumps(family,indent=2)+'\n',encoding='utf-8')
    gate['source_sha256'][fp.relative_to(ROOT).as_posix()]=SHA(fp)
    gate['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
    gate['storage_equivalence']=receipt
    gp.write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    import sys
    compact_existing() if '--compact-existing' in sys.argv else build()
