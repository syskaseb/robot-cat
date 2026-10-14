"""Whole four-Hip1 approach hypothesis, not an accepted wiring interface.

Changes the rigid factory approach AND moving/fixed grips together. Keeps
actual source PCB/socket datums and other eight families. No native mutations.
Body-root seeds stay inside approved torso; moving lands follow real servos.
"""
import copy, json, math, time
from pathlib import Path
from plan_body_fanout_layout import OUT,ROOT,SHA
from plan_current_moving_looms import add,sub,mul,norm,rotation,exact_turn_to
from plan_current_mta_interfaces import line
from spatial_down_up_flex import build
from plan_continuous_joint_family import self_screen

UP=[0,0,1]


def endpoints(row,h):
    pivot=row['pivot_mm'];v=rotation(UP,row['joint_axis'],h)
    moving=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],h))
    return add(row['fixed_anchor_world_mm'],[0,0,-9]),sub(moving,mul(v,9)),v,moving


def run():
    tick=time.monotonic();file=OUT/'leg-source-near-member-plan.json';family=json.loads(file.read_text())
    rows=copy.deepcopy([r for r in family['hips'] if r['loom'].endswith('1')]);rejected=[]
    root_x={'FL1':-100,'FR1':-50,'RL1':185,'RR1':135}
    for row in rows:
        source=next(r for r in family['routes'] if r['loom']==row['loom'])
        datum=source['source']['connector_reservation_world_mm'][source['source']['project_connector_choice']]
        axis=source['source']['cable_exit_world_axis'];axis=[float(round(x)) for x in axis]
        R=39. if row['physical_leg'].endswith('Left') else 31.5
        moving=add(add(datum,mul(axis,23+R)),[0,0,-R])
        turn=exact_turn_to(moving,UP,mul(axis,-1),R)
        end=add(datum,mul(axis,14));factory=[turn,line(turn['end'],end)]
        assert norm(sub(turn['end'],add(datum,mul(axis,23))))<1e-6
        row.update(previous_moving_anchor_world_mm=row['moving_anchor_rest_world_mm'],
            moving_anchor_rest_world_mm=moving,moving_tangent_rest_world=UP,
            fixed_tangent_world=[0,0,-1],source_parts=factory,source=source['source'],
            factory_guide_mm=sum(p['length_mm'] for p in factory),factory_static_R_mm=R)
        side=1 if moving[1]>0 else -1
        moving_ys=[side*endpoints({**row,'fixed_anchor_world_mm':[0,0,0]},h)[1][1] for h in range(-15,16)]
        width=math.ceil(73-min(moving_ys))
        row['fixed_anchor_world_mm']=[root_x[row['loom']],-side*width,50]
        assert -120<root_x[row['loom']]<205 and width<100
        row['poses']=[];chosen=None
        # Bounded nominal-length design, not precision-only midpoint picking.
        for length in range(150,401,5):
            candidates=[]
            for h in range(-15,16):
                a,b,v,m=endpoints(row,h)
                middle=build(a,b,v,length)
                if middle is None or any(build(a,b,v,length+d) is None for d in (-5,5)):break
                parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                if self_screen(parts) is not None:break
                candidates.append(dict(angle=h,parts=parts))
            if len(candidates)==31:
                chosen=length;row['poses']=candidates;break
        if chosen is None:
            rejected.append(dict(loom=row['loom'],reason='No31pose positive spatial CSC with +/-5mm margin in bounded150..400mm'))
            continue
        row.update(flex_length_mm=chosen,guide_mm=chosen+18,
            fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[row['poses'][15]['parts'][0]],owner='Body')],
            moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[row['poses'][15]['parts'][-1]],owner='Hip')])
        print('nearaxis hypothesis',row['loom'],'flex',chosen,'factory',round(row['factory_guide_mm'],3),'root',row['fixed_anchor_world_mm'],flush=True)
    result=dict(status='REJECTED_NEAR_AXIS_HIP_MATH' if rejected else 'NEAR_AXIS_WHOLE_SOURCE_MATH_ONLY_SHARED_MATERIAL_RETENTION_OPEN',
        hips=rows,rejected=rejected,body_root_seeds_only=True,changed_factory_approaches=4,changed_moving_lands=4,
        changed_fixed_lands=4,project_length_margin_mm=5,project_jacket_OD_mm=6,project_dynamic_R_mm=31.5,
        manufacturer_OD_Cu_dynamicR_usableLength_known=False,
        preserved=['OriginalPCB/housing/socketdatums and electricalendIDs','Other8factoryfamilies','20bodyroutes, noneHip1','P0/E6/15drives/torso325x200x160'],
        invalidated=['OnlyfourHip1factoryapproaches/flexes/eightgrips/ownedterminalarms/bodyfanouts/lengthbudgets'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (file,Path(__file__),Path(__file__).with_name('spatial_down_up_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-near-axis-hip-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=rejected,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
