"""Plan the complete rigid servo approaches with all three cables per leg.

Exact project-radius channels, explicit source socket reservations and a body
reach lower bound are considered together before native supports. Socket pin
order/lead OD/900mm usable length remain delivery gates, not supplier facts.
"""
import copy
import itertools
import json
import math
import time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import parts_for_loom,self_screen
from rigid_tangent_channel import candidates
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs


def moved_parts(parts,source,hip,knee,axes):
    result=copy.deepcopy(parts);chain=['Hip'] if source['moving_saved_stage'].endswith('_Hip') else ['Hip','Knee']
    for stage,angle in reversed(list(zip(chain,(hip,knee)))):
        ax=next(a for a in axes if a['code']==source['cad_code'] and a['stage']==stage)
        for q in result:
            for key in ('start','mid','end'):
                if key in q:q[key]=add(ax['pivot_mm'],rotation(sub(q[key],ax['pivot_mm']),ax['axis'],angle))
    return result


def build():
    tick=time.monotonic();fp=OUT/'continuous-joint-family-plan.json';ef=OUT/'harness-interfaces-plan.json'
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    df=OUT/'current-leg-receiver-datums.json';datums=json.loads(df.read_text())
    for n,h in datums['source_sha256'].items():assert SHA(ROOT/n)==h,n
    family=json.loads(fp.read_text());ends=json.loads(ef.read_text());axes=json.loads(af.read_text())['axes']
    assert family['status']=='CONTINUOUS_JOINT_SECTIONS_MATH_SCREEN_ONLY'
    src={r['loom']:r for r in ends['looms']};conductors={r['id']:r for r in ends['body_conductors']}
    options={};trials=[];selected=[];errors=[];combination_count=0
    for h in family['hips']:
        n=h['loom'];source=src[n];k=next((r for r in family['knees'] if r['loom']==n),None);last=k or h
        start=last['moving_anchor_rest_world_mm'];entry=last.get('moving_tangent_rest_world',[0,0,1])
        port=source['connector_reservation_world_mm'][source['project_connector_choice']]
        axis=source['cable_exit_world_axis'];end=add(port,mul(axis,23));outer=add(port,mul(axis,14))
        body=[]
        for core,r in source['electrical'].items():
            row=conductors[r['wire']]
            point=datums['ports'][r['body_end']]['point_mm'] if r['body_end'] in datums['ports'] else next(e['point_mm'] for e in row['current_ends'] if e['role']==r['body_end'])
            body.append(point)
        lower=max(math.dist(h['fixed_anchor_world_mm'],p) for p in body)+21
        joint=parts_for_loom(family,n,0,0,axes);joint_length=sum(p['length_mm'] for p in joint)
        options[n]=[]
        for choice in candidates(start,entry,end,mul(axis,-1)):
            choice['parts'].append(line(end,outer));choice['guide_mm']+=9
            budget=850-joint_length-choice['guide_mm']-lower
            hit=self_screen(joint+choice['parts'])
            trials.append(dict(loom=n,topology=choice['topology'],factory_join_mm=choice['guide_mm'],
                body_reach_lower_bound_plus_21mm_mm=lower,remaining_after_lower_bound_mm=budget,
                self_contact=hit,eligible=budget>=0 and hit is None))
            if budget>=0 and hit is None:
                options[n].append(dict(**choice,loom=n,physical_leg=h['physical_leg'],cad_code=h['cad_code'],
                    source=source,body_reach_lower_bound_plus_21mm_mm=lower,
                    lower_bound_only_remaining_mm=budget,joint_sections_mm=joint_length,
                    source_socket_outer_mm=outer,connector_14mm_is_provisional=True))
        if not options[n]:errors.append(dict(loom=n,cause='NO_SELF_CLEAR_SOURCE_JOIN_WITH_BODY_REACH_BUDGET'))
        print('factory joint options',n,len(options[n]),flush=True)
    if not errors:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            names=[r['loom'] for r in family['hips'] if r['physical_leg']==leg];chosen=None
            combinations=list(itertools.product(*(options[n] for n in names)))
            combinations.sort(key=lambda rows:sum(r['guide_mm'] for r in rows))
            for rows in combinations:
                combination_count+=1;clear=True
                for hip,knee in itertools.product((-15,0,15),repeat=2):
                    paths=[]
                    for r in rows:
                        full=parts_for_loom(family,r['loom'],hip,knee,axes)+moved_parts(r['parts'],r['source'],hip,knee,axes)
                        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(full,full[1:]))
                        if self_screen(full):clear=False;break
                        paths.append(dict(wire=r['loom'],OD_mm=6,segments=sampling_parts(full)))
                    if not clear or any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in only_new_pairs([],paths)):
                        clear=False;break
                if clear:chosen=rows;break
            if chosen:selected.extend(chosen)
            else:errors.append(dict(leg=leg,cause='NO_SHARED_THREE_CABLE_TOPOLOGY_IN_DERIVED_CHANNELS',combinations=len(combinations)))
            print('factory common leg',leg,'chosen',bool(chosen),flush=True)
    report=dict(status='REJECTED_SHARED_FACTORY_JOIN_PLAN' if errors else 'SHARED_FACTORY_JOINS_MATH_ONLY_BODY_ROUTES_AND_MATERIAL_OPEN',
        routes=selected,errors=errors,trials=trials,topological_combinations_checked=combination_count,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        scope='Rigid actual-project socket approaches + connected local joints,9same-leg coupled samples. Body reach is a lower bound, not an actual route or stock allocation.',
        source_qualification='14mm socket envelope/6mm jacket/R31.5/850mm usable are provisional reservations. No pin cavity order or cable dimensions fabricated.',
        open=['actual material and retained wires for factory approaches','all body fanouts/grips/stock',
              'all joint supports/native and assembly','actual delivered keyed socket, OD/length/radius and cable data'],
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (fp,ef,af,df,Path(__file__),
            Path(__file__).with_name('rigid_tangent_channel.py'),Path(__file__).with_name('plan_continuous_joint_family.py'))})
    (OUT/'rigid-factory-joins-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','errors','topological_combinations_checked','worker_seconds')}),flush=True)
    return report


if __name__=='__main__':build()
