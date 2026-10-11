"""All twelve fixed-length nominal loops before any new material CAD."""
import argparse,itertools,json,time
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA
from screen_current_moving_looms import only_new_pairs,pose_row
from screen_current_remaining_routes import route_rows
from route_current_leg_fanouts import sampling_parts


def run(motion=False):
    tick=time.monotonic();source=OUT/'leg-body-joins-plan.json';p=json.loads(source.read_text())
    dest=OUT/('leg-body-joins-motion-screen.json' if motion else 'leg-body-joins-screen.json')
    if p['status']!='BODY_JOIN_FIXED_LENGTH_MATH_ONLY' or len(p['looms'])!=12:
        # A prior green nominal screen is not current evidence after the
        # planner rejects a family. Emit a blocked receipt WITHOUT rerunning
        # geometry or borrowing that older screen's green status.
        result=dict(status='BLOCKED_INCOMPLETE_BODY_JOIN_MATH',rejected=p['rejected'],
                    present_families=[q['loom'] for q in p['looms']],geometry_checks_run=0,
                    motion_requested=motion,selected=False,W5_complete=False,physical_pass=False,
                    worker_seconds=time.monotonic()-tick,
                    source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (source,Path(__file__))})
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(status=result['status'],geometry_checks_run=0,rejected=p['rejected'])),flush=True)
        return result
    assert p['status']=='BODY_JOIN_FIXED_LENGTH_MATH_ONLY' and len(p['looms'])==12
    for name,digest in p['source_sha256'].items():assert SHA(ROOT/name)==digest,name
    fixed,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in
                              ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for name,digest in heads['source_sha256'].items():assert SHA(ROOT/name)==digest,name
    rows=[pose_row(r,next(v for v in r['poses'] if not any(v['angles']))) for r in p['looms']]
    retained=[dict(q,segments=sampling_parts(q['segments'])) for q in list(fixed.values())+heads['rows']]
    near=only_new_pairs(retained,rows);cases=[]
    bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    if motion:
        for leg in ('FL','FR','RL','RR'):
            moving=[r for r in p['looms'] if r['loom'].startswith(leg)]
            fixed=retained+[r for r in rows if not r['wire'].startswith('Loom/'+leg)]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                if hip==knee==0:continue
                changed=[pose_row(r,next(v for v in r['poses'] if v['angles']==([hip] if r['motion_stage'].endswith('_Hip') else [hip,knee]))) for r in moving]
                hits=only_new_pairs(fixed,changed)
                rejected=[dict(leg=leg,hip=hip,knee=knee,**q) for q in hits if q['status']=='REJECT_PLANNING_PROXIMITY']
                cases.append(dict(leg=leg,hip=hip,knee=knee,near_pairs=hits));bad.extend(rejected)
            print('Body join motion',leg,'rejected',len(bad),flush=True)
    result=dict(status='REJECTED_BODY_JOIN_LOOP_PROXIMITY' if bad else ('TWELVE_BODY_JOIN_LOOPS_SAMPLED_PROXIMITY_ONLY' if motion else 'TWELVE_BODY_JOIN_LOOPS_NOMINAL_PROXIMITY_ONLY'),
                cases=cases,
                rejected=bad,near_pairs=near,worker_seconds=time.monotonic()-tick,
                selected=False,W5_complete=False,physical_pass=False,
                scope='12nominal loops; optional32same-leg Hip/Knee samples with other legs nominal, unchanged ground/data/source/BUS/head. Fanouts/material/continuous or simultaneous motion/native OPEN.',
                source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins|{source,hf,Path(__file__),Path(__file__).with_name('route_current_leg_fanouts.py'),Path(__file__).with_name('screen_current_moving_looms.py')}})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],rejected=bad,near=len(near),seconds=result['worker_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--motion',action='store_true')
    run(parser.parse_args().motion)
