"""Use the retained body-side layer, not a vertical drop through knee motion.

The high same-side corner hypothesis crosses actual XG-ZIJI/MOTOR/LegLink
material. Keep near-axis factory approaches, derive all body Y/Z from the
existing underframe interfaces and retain spatial X reach. No native writes.
"""
import copy,json,time
from pathlib import Path
from plan_near_axis_hip_sources import OUT,ROOT,SHA,endpoints,build,line,self_screen


def run():
    tick=time.monotonic();pf=OUT/'body-same-side-near-axis-plan.json';prior=json.loads(pf.read_text())
    ff=OUT/'leg-source-near-member-plan.json';original=json.loads(ff.read_text())
    rows=copy.deepcopy(prior['hips']);rejected=[]
    for row in rows:
        original_root=next(r['fixed_anchor_world_mm'] for r in original['hips'] if r['loom']==row['loom'])
        row['previous_fixed_anchor_world_mm']=row['fixed_anchor_world_mm']
        row['fixed_anchor_world_mm']=[row['fixed_anchor_world_mm'][0],*original_root[1:]]
        chosen=None
        for length in range(130,351,5):
            poses=[]
            for h in range(-15,16):
                a,b,v,m=endpoints(row,h);middle=build(a,b,v,length)
                if middle is None or any(build(a,b,v,length+d) is None for d in (-5,5)):break
                parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                if self_screen(parts) is not None:break
                poses.append(dict(angle=h,parts=parts))
            if len(poses)==31:chosen=length;break
        if chosen is None:
            rejected.append(dict(loom=row['loom'],reason='No robust31pose underframe spatial construction'))
            row['poses']=[];continue
        row.update(poses=poses,flex_length_mm=chosen,guide_mm=chosen+18,
            fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
            moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
        print('underframe source hypothesis',row['loom'],'flex',chosen,'root',row['fixed_anchor_world_mm'],flush=True)
    result=copy.deepcopy(prior);result.update(status='REJECTED_UNDERFRAME_NEAR_AXIS_MATH' if rejected else 'UNDERFRAME_WHOLE_SOURCE_MATH_ONLY_SHARED_SPACE_ARMS_OPEN',
        hips=rows,rejected=rejected,
        root_derivation='Y/Z from current retained body-frame layer, X from spatial90mm reach to the shortened factory approach; not an upper-corner downward wire through knee material.',
        changed_cause='High side-corner downward leg crossed actual XG-ZIJI_006/MOTOR-1723_006/LegLink005. Change whole source routing layer to retained underframe; do not vary scalar offsets around that knee.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,ff,Path(__file__),Path(__file__).with_name('plan_near_axis_hip_sources.py'),Path(__file__).with_name('spatial_down_up_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-underframe-near-axis-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=rejected,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
