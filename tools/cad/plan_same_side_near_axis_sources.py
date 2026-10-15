"""Change shared routing topology: body roots on the SAME leg side.

The first near-axis hypothesis crossed the opposite leg because its Y-span
rule was planar. Spatial bends depend on XY reach, not Y alone. Retain the
short factory approaches/moving lands; replace all four body root placements
as one macro layout. No native mutation or material acceptance.
"""
import copy,json,math,time
from pathlib import Path
from plan_near_axis_hip_sources import OUT,ROOT,SHA,endpoints,build,line,self_screen


def run():
    tick=time.monotonic();pf=OUT/'body-near-axis-hip-plan.json';prior=json.loads(pf.read_text())
    rows=copy.deepcopy(prior['hips']);rejected=[]
    # Approved torso Y=+/-100; port/band reaches4.4mm; retain5mm edge reserve.
    y=math.floor(100-4.4-5)
    for front in (True,False):
        group=[r for r in rows if r['physical_leg'].startswith('Front')==front]
        source_x=sum(r['moving_anchor_rest_world_mm'][0] for r in group)/len(group)
        root_x=round(source_x+(90 if front else -90))
        for row in group:
            side=1 if row['moving_anchor_rest_world_mm'][1]>0 else -1
            row['previous_fixed_anchor_world_mm']=row['fixed_anchor_world_mm']
            row['fixed_anchor_world_mm']=[root_x,side*y,50]
            assert -120<root_x<205
            chosen=None
            for length in range(150,401,5):
                poses=[]
                for h in range(-15,16):
                    a,b,v,m=endpoints(row,h)
                    middle=build(a,b,v,length)
                    if middle is None or any(build(a,b,v,length+d) is None for d in (-5,5)):break
                    parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                    if self_screen(parts) is not None:break
                    poses.append(dict(angle=h,parts=parts))
                if len(poses)==31:chosen=length;break
            if chosen is None:
                rejected.append(dict(loom=row['loom'],reason='No robust31pose spatial construction'))
                row['poses']=[];continue
            row.update(poses=poses,flex_length_mm=chosen,guide_mm=chosen+18,
                fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
                moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
            print('same-side source hypothesis',row['loom'],'flex',chosen,'bodyroot',row['fixed_anchor_world_mm'],flush=True)
    result=copy.deepcopy(prior);result.update(status='REJECTED_SAME_SIDE_NEAR_AXIS_MATH' if rejected else 'SAME_SIDE_WHOLE_SOURCE_MATH_ONLY_SHARED_SPACE_ARMS_OPEN',
        hips=rows,rejected=rejected,
        root_derivation=dict(torso_halfwidth_mm=100,band_radial_envelope_mm=4.4,edge_reserve_mm=5,
            body_root_absY_mm=y,mean_factory_grip_X_to_body_root_mm=90,root_Z_seed_mm=50),
        changed_cause='The initial opposite-side body roots crossed the other leg; spatial XY reach replaces an unnecessary planar Y-span constraint. No catalog radius reduction.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,Path(__file__),Path(__file__).with_name('plan_near_axis_hip_sources.py'),Path(__file__).with_name('spatial_down_up_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-same-side-near-axis-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=rejected,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
