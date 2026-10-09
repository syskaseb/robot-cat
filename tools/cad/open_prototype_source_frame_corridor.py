"""Replace under-frame coils as a whole family, not micro-shifts of P0.

Lower3 uses a forward lower corridor then rises outside the rear MTA case.
Lower6 exits downward into an outward rear coil rather than through P0.
RR output moves its independent grip to the vertical leg; PI output turns
west before its insulated joint. Retained P0/body/bank are not edited.
"""
from datetime import datetime, timezone
from pathlib import Path
import json,time,math
import open_prototype_source_group as B
import open_prototype_source_capacity_plan as C
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import screen

ROOT=B.ROOT;OUT=B.OUT;read=B.read;sha=B.sha
PLAN=OUT/'source-group-frame-corridor-plan.json'
PROOF=OUT/'source-group-frame-point-screen.json'
CAPACITY=C.CAPACITY

def build():
    p=C.build()
    for r in p['s1_routes']:
        if r['wire']=='W064':
            r.update(barrel_mm=[98.077,33,73],barrel_direction=B.WEST,terminal_straight_mm=9)
            parts=B.compose(r['barrel_mm'],[
                ('line',[75.6,33,73]),('quarter',B.WEST,B.SOUTH,25.2),
                ('line',[50.4,-19.8,73]),('quarter',B.SOUTH,B.UP,25.2),
                ('line',[50.4,-45,105.8]),('quarter',B.UP,B.WEST,25.2)])
            parts+=input_recipe(parts[-1]['end'],p['ports'][r['target']]['point_mm'],B.WEST,25.2)['segments']
            r['source_restraint_plan']='First22.477mm WEST straight and final9mm before terminal; native mounts OPEN'
        elif r['wire']=='W065':
            parts=B.compose(r['barrel_mm'],[
                ('line',[132.2,33,47.877]),('quarter',B.DOWN,B.EAST,25.2),
                ('line',[160.4,33,22.677]),('quarter',B.EAST,B.UP,25.2)])
            parts+=input_recipe(parts[-1]['end'],p['ports'][r['target']]['point_mm'],B.UP,25.2)['segments']
            r['source_restraint_plan']='Outward rear quarter/3mm horizontal between arcs; native9mm grip on rising leg, not short factory/barrel segment'
        else:continue
        r.update(segments=parts,centreline_mm=B.check_path(parts,r['barrel_mm'],p['ports'][r['target']]['point_mm'],25.2))
    r=next(r for r in p['tails'] if r['wire']=='W053')
    end=p['ports'][r['target']]['point_mm']
    parts=input_recipe(r['segments'][0]['start'],B.add(end,B.mul(B.SOUTH,6)),B.SOUTH,7.5)['segments']
    parts[-1]['end']=end
    r.update(segments=parts,centreline_mm=B.check_path(parts,end=end,min_radius=7.5),
        terminal_straight_mm=3,independent_grip_plan='At least9mm on vertical factory insulation before final bend; entry3mm is provisional, not supplier datum')
    r['required_blank_mm']=r['centreline_mm']+r['strip_allowance_mm'];assert r['required_blank_mm']<=100
    h=next(h for h in p['holders'] if h['role']=='F_PI')
    parts=B.compose(h['output_mm'],[('line',B.add(h['output_mm'],[0,0,-3])),
        ('quarter',B.DOWN,B.WEST,6),('line',[-36,-34.9,62.323])])
    cut=parts[-1]['end'];d=B.WEST
    h.update(output_segments=parts,output_prefix_mm=B.check_path(parts,h['output_mm'],min_radius=6),
        sleeve_start_mm=B.sub(cut,B.mul(d,17.25)),sleeve_end_mm=B.add(cut,B.mul(d,9.25)),
        new_insulation_end_mm=B.add(cut,B.mul(d,18.25)))
    for r in p['tails']+p['s1_routes']:
        assert B.dot(B.segment_geometry(r['segments'][-1])[2],p['ports'][r['target']]['departure'])<-1+1e-7
    p.update(status='FRAME_CLEARANCE_CORRIDOR_HYPOTHESIS_NOT_ACCEPTED',
        changed_path_names=['W064','W065','W053','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        changed_cause='Remove two under-frame inward coils; allocate full lower3 forward rise/lower6 outward return, RR grip away from tail wall and PI joint above P0. No P0 removal or scalar case retry.')
    return p

if __name__=='__main__':
    previous=None
    if PLAN.exists():
        import sys
        assert '--replace-planning-rejection' in sys.argv and not PROOF.exists(),'No unreceived or unchanged retry'
        previous=read(PLAN)
        assert any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in previous['mutual_path_preflight']['near_pairs'])
    tick=time.monotonic();p=build();report=screen(p)
    if previous:
        assert previous['s1_routes']!=p['s1_routes'],'No unchanged geometry retry'
        p['previous_rejected_planning']=dict(cause='Roof-level W064 crosses W068 and F_HY prefix. Whole forward approach now shares P_FRONT131mm layer below protected outputs, not149.323mm roof layer.',
            rejected_pairs=[r for r in previous['mutual_path_preflight']['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'],
            no_native_trial_was_launched=True)
    p.update(mutual_path_preflight=report,source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in
        (Path(__file__),Path(C.__file__),Path(B.__file__),C.PLAN,C.CAPACITY,OUT/'source-group-point-screen.json')},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],conflicts=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'],
        source_lengths=[(r['wire'],r['centreline_mm']) for r in p['s1_routes']],seconds=p['worker_seconds'])),flush=True)
