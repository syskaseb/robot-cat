"""Stagger the complete three-FHAC fanout, not just WAGO terminal ends.

Different terminal straights reserve separated turning columns. Holder
source/output/joint datums and protected HY/HP approaches move together.
PI allocation is now a shared variable if this family consumes its space.
No native changes and no unqualified historical source-wire reuse.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,time,math
import open_prototype_pi_capacity_choice as P
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import screen

ROOT=P.ROOT;OUT=P.OUT;PLAN=OUT/'aux-fanout-plan.json'

def build():
    p=P.build()
    for role,dx,last in [('F_HY',-24,27),('F_HP',-12,18),('F_TY',0,9)]:
        h=next(h for h in p['holders'] if h['role']==role)
        for key in ('input_mm','output_mm','centre_mm','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):
            h[key]=B.add(h[key],[dx,0,0])
        h['output_segments']=[{k:B.add(v,[dx,0,0]) if k in ('start','mid','end') else v for k,v in seg.items()} for seg in h['output_segments']]
        end=p['ports'][h['input_target']]['point_mm']
        shortened=B.sub(end,B.mul(B.EAST,last-9))
        parts=input_recipe(h['input_mm'],shortened,B.EAST,6)['segments']
        parts[-1]['end']=end
        h.update(input_segments=parts,input_blank_mm=B.check_path(parts,h['input_mm'],end,6)+11,
            terminal_grip_straight_mm=last,whole_fanout_stagger_mm=dx)
        assert h['input_blank_mm']<=84.5 and math.dist(parts[-1]['start'],parts[-1]['end'])>=last-1e-7
    old=B.read(OUT/'source-fanouts-plan.json');rows=[]
    for role,wire in [('F_HY','XB12'),('F_HP','XB22')]:
        h=next(h for h in p['holders'] if h['role']==role)
        source=h['new_insulation_end_mm'];core=copy.deepcopy(next(r['core_segments'] for r in old['rows'] if r['wire']==wire))
        if wire=='XB12':
            mouth=core[0]['start'][:];mouth[0]=min(mouth[0],source[0]-(2*12.6+3+9+2))
            assert mouth[0]>core[0]['end'][0],'No residual head straight; change full approach'
            core[0]['start']=mouth
            approach=input_recipe(source,mouth,B.WEST,12.6)['segments']
            approach+=core
            basis='Old head core first straight shortened in-place, body/head exit remains OPEN'
        else:
            target=core[-1]['end'];anchor=B.add(target,[12.6,-9-12.6,0])
            approach=input_recipe(source,anchor,B.WEST,12.6)['segments']
            q=B.quarter(anchor,B.WEST,B.NORTH,12.6)
            approach += [q,B.line(q['end'],target)]
            basis='Replace obsolete HP upstream loop with direct tangent approach; retain final9mm NORTH insulation station and moving endpoint, not old loop'
        prefix=[B.line(h['output_segments'][-1]['end'],source)]
        extension=prefix+approach
        length=B.check_path(extension,extension[0]['start'],approach[-1]['end'],12.6)
        B.check_path(h['output_segments']+extension,h['output_mm'],approach[-1]['end'])
        rows.append(dict(wire=wire,holder=role,leg=role,side='output',target='',
            segments=extension,OD_mm=2.1,min_radius_mm=12.6,
            extension_centreline_mm=length,station_mm=approach[-1]['end'],
            terminal_straight_mm=9,retained_basis=basis,
            independent_grips_open=True,moving_continuation_not_qualified=True,
            covered_joint_is_existing_recipe=True,stock_selected=False))
    p['tails']+=rows
    p.update(protected_receiving_rows=rows,status='SHARED_THREE_FHAC_FANOUT_AND_PROTECTED_APPROACHES_NOT_SELECTED',
        changed_case_names=['F_HY','F_HP'],changed_path_names=[
            'F_HY/input','F_HP/input','F_TY/input','F_HY/output','F_HP/output',
            'F_HY/sleeve','F_HP/sleeve','F_HY/new_insulation','F_HP/new_insulation','XB12','XB22'],
        invalidated=p['invalidated']+['HY/HP native mounts and full current output blank/material amounts',
            'Old protected HY/HP source approaches replaced; moving continuation and head exit unqualified'],
        tail_receiving_blocker_retained='XB32/W045 endpoint unchanged/open; no new tail-only route selection')
    return p

def proximity(p):
    q=copy.deepcopy(p)
    for h in q['holders']:
        for suffix,parts,od in [('sleeve',[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],6),
            ('new_insulation',[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],2.1)]:
            q['tails'].append(dict(wire=h['role']+'/'+suffix,OD_mm=od,segments=parts))
    report=screen(q)
    joins={h['role']:{h['role']+'/'+side for side in ('output','sleeve','new_insulation')} for h in q['holders']}
    for r in p['protected_receiving_rows']:joins[r['holder']].add(r['wire'])
    intentional=lambda r:any(r['a'] in names and r['b'] in names for names in joins.values())
    report['declared_same_conductor_covered_profiles']=[r for r in report['near_pairs'] if intentional(r)]
    report['near_pairs']=[r for r in report['near_pairs'] if not intentional(r)]
    report['status']='REJECTED_MUTUAL_PLANNING_RESERVATION' if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']) else 'MUTUAL_FANOUT_PREFIXES_ONLY_MATERIAL_AND_FULL_SOURCE_OPEN'
    return report

def compact():
    p=build();preflight=proximity(p)
    changed=[h for h in p['holders'] if h['role'] in ('F_HY','F_HP','F_TY')]
    ps=next(s for s in p['stations'] if s['role']=='P_SYS')
    overlaps=[]
    for h in changed:
        widths=[max(0,min(h['centre_mm'][i]+h['size_mm'][i]/2,ps['centre_mm'][i]+ps['size_mm'][i]/2)-max(h['centre_mm'][i]-h['size_mm'][i]/2,ps['centre_mm'][i]-ps['size_mm'][i]/2)) for i in range(3)]
        volume=math.prod(widths)
        if volume>1e-6:overlaps.append(dict(a=h['role'],b='P_SYS',nominal_box_overlap_mm3=volume,not_measured_supplier_contact=True))
    files=[Path(__file__),Path(P.__file__),P.PLAN,P.PROOF,OUT/'source-fanouts-plan.json',
        OUT/'pi-capacity-choice-proximity.json',Path(input_recipe.__globals__['__file__'])]
    return dict(status=p['status'],geometry_digest=R.geometry_digest(p),
        holders=changed,protected_receiving_rows=p['protected_receiving_rows'],
        mutual_path_preflight=preflight,nominal_box_allocation_conflicts=overlaps,
        shared_PI_reallocation_required=bool(overlaps),
        no_expensive_gate_permitted_while_known_mutual_crossings=True,
        invalidated=p['invalidated'],remaining=['Full4S1 source routes','Tail/W045 receiving station',
            'Body/head exit and HP moving continuation','Native grips/all otherwires/stock/selected export'],
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False)

if __name__=='__main__':
    assert not PLAN.exists(),'Use received fanout, no unchanged repeat'
    tick=time.monotonic();p=compact()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],inputs=[(h['role'],h['input_blank_mm']) for h in p['holders']],
        planning_cases=p['nominal_box_allocation_conflicts'],
        crossings=[{k:r[k] for k in ('a','b','sampled_distance_mm','status')} for r in p['mutual_path_preflight']['near_pairs']],seconds=p['worker_seconds'])),flush=True)
