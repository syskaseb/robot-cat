"""Allocate complete leg cable galleries against retained wires and Knees.

No module is moved, no retained wire is rerouted, no frame is cut. The outer
leg gallery is distinct from the unchanged325x200x160 body. Bounded whole
family capacity allocation replaces sequential witness nudges. Brackets,
rigid links and actual material qualification remain required.
"""
import copy
import itertools
import json
import time
from pathlib import Path
from plan_current_hip_axial_looms import s_offset
from plan_current_mta_interfaces import line
from plan_current_moving_looms import add, sub, mul, rotation
from plan_current_main_sources import ROOT, OUT, SHA
from plan_current_joint_local_looms import scene_parts
from route_current_leg_fanouts import sampling_parts
from screen_current_remaining_routes import route_rows
from screen_current_moving_looms import only_new_pairs


def flex_up(start,end,t):
    centre=mul(add(start,end),.5)
    def at(h):
        mid=add(centre,[0,0,h])
        return s_offset(start,mid,t)+s_offset(mid,end,t)
    lo,hi=0.,50.
    if not sum(p['length_mm'] for p in at(lo))<=108<=sum(p['length_mm'] for p in at(hi)):return None
    for _ in range(40):
        h=(lo+hi)/2
        if sum(p['length_mm'] for p in at(h))<108:lo=h
        else:hi=h
    q=at((lo+hi)/2)
    return q if min(p['radius_mm'] for p in q)>=31 else None


def expanded(row,angle):
    p=next(p for p in row['poses'] if p['angle']==angle)
    fixed=row['fixed_anchor_world_mm'];t=row['axial_tangent'];pivot=row['pivot_mm']
    end=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],angle))
    a,b=add(fixed,mul(t,9)),sub(end,mul(t,9));mid=add(mul(add(a,b),.5),[0,0,p['up_bulge_mm']])
    return [line(fixed,a)]+s_offset(a,mid,t)+s_offset(mid,b,t)+[line(b,end)]


def family_at(family, first_y):
    rows=copy.deepcopy(family)
    for i,row in enumerate(rows):
        # Bow UP into a separate free-plane, not OUT through the DATA rails.
        # Keep the original short axial root region; avoid long new brackets.
        for key in ('fixed_anchor_world_mm','moving_anchor_rest_world_mm'):
            row[key][1]=row['side']*(first_y+8*i)
            row[key][2]=65
        row['poses']=[]
        for angle in range(-15,16):
            pivot=row['pivot_mm'];t=row['axial_tangent'];fixed=row['fixed_anchor_world_mm']
            end=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],angle))
            first,last=add(fixed,mul(t,9)),sub(end,mul(t,9))
            q=flex_up(first,last,t)
            if q is None:return None
            row['poses'].append(dict(angle=angle,
                up_bulge_mm=q[1]['end'][2]-(first[2]+last[2])/2,
                flex_length_mm=sum(p['length_mm'] for p in q),minimum_R_mm=min(p['radius_mm'] for p in q)))
    return rows


def run():
    tick=time.monotonic();source=OUT/'hip-axial-loom-plan.json';base=json.loads(source.read_text())
    knee=OUT/'joint-local-knee-plan.json';kp=json.loads(knee.read_text())
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    head=OUT/'head-wire-screen-reference.json';hp=json.loads(head.read_text())
    for p in (base,kp,hp):
        for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    retained,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    fixed=[dict(r,segments=sampling_parts(r['segments'])) for r in list(retained.values())+hp['rows']]
    def row(r,h=0,k=0):
        q=expanded(r,h) if r['child_stage']=='Hip' else scene_parts(r,h,k,axes)
        return dict(wire=r['section'],OD_mm=6,segments=sampling_parts(q))
    chosen=[];allocation=[];bad=[]
    # One vertical ribbon proposal, not another sweep of scalar offsets.
    # The prior horizontal three-lane allocation crossed retained Knees.
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        originals=[r for r in base['loops'] if r['physical_leg']==leg]
        knees=[r for r in kp['loops'] if r['physical_leg']==leg]
        others=[row(r) for r in kp['loops'] if r['physical_leg']!=leg]+[row(r) for r in chosen]
        attempts=[];accepted=None
        for y in (40,):
            candidate=family_at(originals,y)
            if candidate is None:
                attempts.append(dict(first_lane_y_mm=y,cause='FIXED_LENGTH_R31_NOT_FEASIBLE'));continue
            hits=[];count=0
            for h,k in itertools.product((-15,0,15),repeat=2):
                changed=[row(r,h,k) for r in candidate+knees]
                near=only_new_pairs(fixed+others,changed)
                rejected=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
                count+=1
                if rejected:
                    hits=sorted({q['a']+' / '+q['b'] for q in rejected});break
            attempts.append(dict(first_lane_y_mm=y,sampled_cases=count,rejected_pairs=hits))
            if not hits:accepted=candidate;break
        if accepted is None:bad.append(dict(leg=leg,cause='NO_COMMON_FIXED_WIRE_AND_KNEE_CAPACITY'))
        else:chosen.extend(accepted)
        allocation.append(dict(leg=leg,attempts=attempts))
        print('Whole leg side gallery',leg,'accepted',accepted is not None,flush=True)
    pins.update((source,knee,af,head,Path(__file__),ROOT/'tools/cad/check_current_hip_axial_looms.py',ROOT/'tools/cad/plan_current_hip_axial_looms.py'))
    result=dict(status='REJECTED_HIP_SIDE_GALLERY_CAPACITY' if bad else 'HIP_SIDE_GALLERY_SAMPLED_WIRES_ONLY_MATERIAL_AND_ROOTS_OPEN',
        loops=chosen,allocation=allocation,failures=bad,selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        P0_retained=True,retained_fixed_routes_changed=False,knee_reference='joint-local-knee-plan.json',
        topology='UP-bowed four arcs, absY40/48/56 and Z65 anchors, axial span120, flex108, two9mm lands',
        prior_rejected_topology='Outward bows: Y-spaced Z65 galleries75/83/91/99 crossed Knees; vertical stackY75/Z85/93/101 crossed fixed sources/head. No native edits.',
        assumptions=['325x200x160 torso unchanged; local leg cable seats may extend outboard, not a wider cosmetic body; final bounds not yet qualified',
            'OD6/R31 project allowance, not delivered loom data; exact keyed plug and operating range are phase2 gates',
            'All existing frame and motor material retained; common bracket roots/tools/load path must pass before native detail'],
        worker_seconds=time.monotonic()-tick,source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins})
    (OUT/'hip-side-gallery-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','allocation','failures','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':run()
