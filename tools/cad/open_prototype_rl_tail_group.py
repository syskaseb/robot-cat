"""One coupled RL/MTA/tail gallery, not moving the occupied tail endpoint.

Move whole RL MTA and both100mm-reserved sides; retain receiving case/ports.
Tail uses a shared SOUTH gallery and a30mm final EAST straight, not the old
core that cannot be joined to the current TY output. Motion remains OPEN.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import open_prototype_aux_fanout_choice as F
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import samples
ROOT=F.ROOT;OUT=F.OUT
PLAN=OUT/'rl-tail-group-plan.json';PROOF=OUT/'rl-tail-group-space.json';REUSE_PROOF=None

def build():
    p=F.build();m=next(m for m in p['mta'] if m['role']=='MTA_RL')
    delta=[-20,0,0]
    for name in ('centre_mm','source_exit_mm','output_exit_mm'):m[name]=B.add(m[name],delta)
    source=next(r for r in p['tails'] if r['wire']=='W044')
    output=next(r for r in p['tails'] if r['wire']=='W045')
    end=p['ports'][source['target']]['point_mm']
    anchor=B.add(end,[0,-6,-15])
    parts=input_recipe(m['source_exit_mm'],anchor,B.NORTH,6)['segments']
    turn=B.quarter(anchor,B.NORTH,B.UP,6)
    parts += [turn,B.line(turn['end'],end)]
    source.update(segments=parts,centreline_mm=B.check_path(parts,m['source_exit_mm'],end,6))
    source['required_blank_mm']=source['centreline_mm']+14
    end=p['ports'][output['target']]['point_mm']
    parts=input_recipe(m['output_exit_mm'],end,B.SOUTH,7.5)['segments']
    output.update(segments=parts,centreline_mm=B.check_path(parts,m['output_exit_mm'],end,7.5))
    output['required_blank_mm']=output['centreline_mm']+11
    assert max(source['required_blank_mm'],output['required_blank_mm'])<=100
    h=next(h for h in p['holders'] if h['role']=='F_TY')
    start=h['new_insulation_end_mm'];end=[68,-45,116.78756443470179]
    a=B.add(start,B.mul(B.WEST,9));q=B.quarter(a,B.WEST,B.SOUTH,12.6)
    bottom=[q['end'][0],-62.4,151];turn=B.quarter(bottom,B.SOUTH,B.EAST,12.6)
    approach=input_recipe(turn['end'],end,B.EAST,12.6)['segments']
    approach[-1]['end']=end
    parts=[B.line(start,a),q,B.line(q['end'],bottom),turn]+approach
    full=[B.line(h['output_segments'][-1]['end'],start)]+parts
    length=B.check_path(full,full[0]['start'],end,12.6)
    B.check_path(h['output_segments']+full,h['output_mm'],end)
    row=dict(wire='XB32',holder='F_TY',leg='TY',side='output',target='',segments=full,
        OD_mm=2.1,min_radius_mm=12.6,extension_centreline_mm=length,
        station_mm=end,terminal_straight_mm=9,
        covered_joint_is_existing_recipe=True,stock_selected=False,
        independent_grips_open=True,moving_continuation_not_qualified=True)
    p['tails'].append(row);p['protected_receiving_rows'].append(row)
    p.update(changed_case_names=['MTA_RL'],changed_path_names=['W044','W045','XB32'],
        s1_geometry_changed=False,status='RL_BOTH_SIDES_AND_TAIL_GALLERY_NOT_NATIVE_ACCEPTANCE')
    return p

def compact():
    p=build();report=F.F.proximity(p)
    space=B.read(OUT/'routing-space-map.json')['samples'];outside=[]
    for r in p['tails']:
        if r['wire'] not in p['changed_path_names']:continue
        for i,q in samples(r['segments'],step=2):
            spans=min(space,key=lambda v:(v['x_mm']-q[0])**2+(v['y_mm']-q[1])**2)['torso_z_intervals_mm']
            if not spans or q[2]<min(v[0] for v in spans)+r['OD_mm']/2+.5 or q[2]>max(v[1] for v in spans)-r['OD_mm']/2-.5:
                outside.append(dict(wire=r['wire'],segment=i,point=q));break
    failures=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(F.__file__),F.PLAN,F.PROOF,OUT/'source-fanouts-plan.json',OUT/'routing-space-map.json']
    return dict(status='REQUIRES_SHARED_CHANGE_BEFORE_CAD' if failures or outside else 'RL_TAIL_SHARED_PLAN_REQUIRES_ONE_ACTUAL_GATE',
        family=p,geometry_digest=R.geometry_digest(p),mutual_preflight=report,
        known_mutual_failures=failures,conservative_boundary_exclusions=outside,
        old_tail_endpoint_preserved=True,legacy_source920mm_open=True,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False)

if __name__=='__main__':
    assert not PLAN.exists(),'One received group, no unchanged retry'
    tick=time.monotonic();data=compact()
    data.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(status=data['status'],blanks=[(r['wire'],r['required_blank_mm']) for r in data['family']['tails'] if r['wire'] in ('W044','W045')],
        conflicts=data['known_mutual_failures'],outside=data['conservative_boundary_exclusions'],seconds=data['worker_seconds'])),flush=True)
