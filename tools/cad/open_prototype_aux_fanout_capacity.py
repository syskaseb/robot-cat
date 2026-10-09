"""Allocate PI/SYS with the entire changed FHAC fanout already present.

Reuse the mathematical family/box helpers, not an old clearance verdict.
Known routed profiles participate in the capacity search before one CAD run.
Conservative exclusions are search limits, never actual material contacts.
"""
from pathlib import Path
from datetime import datetime,timezone
import itertools,json,math,time
import open_prototype_aux_fanout_plan as G
import open_prototype_pi_capacity_plan as C
import open_prototype_source_group as B
from open_prototype_path_preflight import samples

ROOT=G.ROOT;OUT=G.OUT;DEST=OUT/'aux-fanout-capacity.json'

def profiles(p):
    rows=[(r['wire'],r['OD_mm']/2,r['segments']) for r in p['tails']]
    for h in p['holders']:
        if h['role']=='F_PI':continue
        for side in ('input','output'):rows.append((h['role']+'/'+side,2,h[side+'_segments']))
        rows += [(h['role']+'/sleeve',3,[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])]),
            (h['role']+'/new_insulation',1.05,[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])])]
    return rows

def main():
    assert not DEST.exists(),'Use received shared capacity'
    tick=time.monotonic();base=G.build();report=G.proximity(base)
    assert not any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']),'Fix full fanout before capacity/CAD'
    records=B.read(OUT/'obstacle-map-current.json')['objects']
    exclusions=[dict(name=r['role'],bounds=C.bounds(r['centre_mm'],r['size_mm']))
        for r in base['stations']+base['mta']+base['holders'] if r['role'] not in ('P_SYS','F_PI')]
    for r in records:
        if r['basis'].startswith('Canonical whole-component/reference envelope') or r['name']=='U1UnknownModuleReservation' or r['name'].startswith('F_') and '_CP2' in r['name']:
            exclusions.append(dict(name=r['name'],bounds=r['bounds_mm']))
    exclusions += [dict(name='S1/body',bounds=[114.2,-21,89,138.2,21,126]),
        dict(name='S1/external_control',bounds=[112.2,-14,126,140.2,14,160])]
    space=B.read(OUT/'routing-space-map.json')['samples']
    def sampled_capacity(bb):
        for x,y in itertools.product((bb[0],bb[3]),(bb[1],bb[4])):
            r=min(space,key=lambda r:(r['x_mm']-x)**2+(r['y_mm']-y)**2);spans=r['torso_z_intervals_mm']
            if not spans or bb[2]<min(s[0] for s in spans)+.5 or bb[5]>max(s[1] for s in spans)-.5:return False
        return True
    rows=profiles(base);grid={};cell=10;point_count=0
    for name,radius,parts in rows:
        for _,q in samples(parts):
            key=tuple(math.floor(v/cell) for v in q)
            grid.setdefault(key,[]).append((name,q,radius));point_count+=1
    def box_hits_route(bb):
        for key in itertools.product(*(range(math.floor((bb[i]-4)/cell),math.floor((bb[i+3]+4)/cell)+1) for i in range(3))):
            for name,q,radius in grid.get(key,[]):
                if C.distance_squared(q,bb)<(radius+.5)**2:return True
        return False
    def close_to_routes(q,radius):
        key=tuple(math.floor(v/cell) for v in q)
        for delta in itertools.product((-1,0,1),repeat=3):
            for name,other,r in grid.get(tuple(key[i]+delta[i] for i in range(3)),[]):
                if math.dist(q,other)<radius+r:return True
        return False
    counts=dict(whole_pairs=0,case_capacity_exclusions=0,case_budget_exclusions=0,
        case_route_exclusions=0,prefix_choices=0,prefix_exclusions=0,shortlisted=0)
    choices=[];original=next(s['centre_mm'] for s in base['stations'] if s['role']=='P_SYS')
    for goal,turn in itertools.product(itertools.product(range(-90,131,10),range(-60,61,10),(125,130,135,140,145,148)),range(4)):
        goal=list(goal);counts['whole_pairs']+=1;c=C.family(base,goal,turn,B.EAST)
        cb={n:C.bounds(c[n]['centre_mm'],c[n]['size_mm']) for n in ('SYS','PI')}
        if not all(sampled_capacity(b) for b in cb.values()):counts['case_capacity_exclusions']+=1;continue
        if any(C.overlap(b,e['bounds']) for b in cb.values() for e in exclusions):counts['case_budget_exclusions']+=1;continue
        if any(box_hits_route(b) for b in cb.values()):counts['case_route_exclusions']+=1;continue
        for outdir in (B.EAST,B.WEST,B.NORTH,B.SOUTH):
            counts['prefix_choices']+=1;c=C.family(base,goal,turn,outdir)
            paths=[('input',c['input_segments'],2),('output',c['output_segments'],2),
                ('sleeve',[B.line(c['sleeve_start_mm'],c['sleeve_end_mm'])],3),
                ('new_insulation',[B.line(c['output_segments'][-1]['end'],c['new_insulation_end_mm'])],1.05)]
            blocked=False
            for name,parts,radius in paths:
                for _,q in samples(parts,step=3):
                    if any(C.distance_squared(q,e['bounds'])<(radius+.5)**2 for e in exclusions) or close_to_routes(q,radius):blocked=True;break
                    for own in ('SYS','PI'):
                        if name=='input' and ((own=='PI' and math.dist(q,parts[0]['start'])<=radius+1e-5) or (own=='SYS' and math.dist(q,parts[-1]['end'])<=radius+1e-5)):continue
                        if name=='output' and own=='PI' and math.dist(q,parts[0]['start'])<=radius+1e-5:continue
                        if C.distance_squared(q,cb[own])<radius**2:blocked=True;break
                    if blocked:break
                if blocked:break
            if blocked:counts['prefix_exclusions']+=1;continue
            c['score']=round(math.dist(goal,original)+3*turn+2*(outdir!=B.EAST),6);choices.append(c)
    choices.sort(key=lambda c:c['score']);counts['shortlisted']=len(choices)
    files=(Path(__file__),Path(G.__file__),Path(C.__file__),G.PLAN,OUT/'obstacle-map-current.json',OUT/'routing-space-map.json')
    result=dict(status='SHARED_FANOUT_CAPACITY_REQUIRES_ONE_ACTUAL_GATE' if choices else 'NO_CONSERVATIVE_CAPACITY_NOT_PROOF_OF_IMPOSSIBILITY',
        counts=counts,choice=choices[0] if choices else None,
        retained_profiles=len(rows),retained_profile_points=point_count,
        no_native_variants_generated=True,conservative_bbox_exclusion_not_material_collision=True,
        sampled_torso_not_containment_proof=True,sampled_paths_not_full_thickness=True,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],counts=counts,choice={k:result['choice'][k] for k in ('SYS','PI','whole_pair_turns_z','output_direction')} if choices else None,seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':main()
