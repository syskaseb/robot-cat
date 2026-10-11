"""Reject incompatible complete loom planes cheaply, BEFORE another BRep run."""
import json,math,time,itertools,argparse
from pathlib import Path
from plan_current_moving_looms import OUT,ROOT,SHA,add,mul,sub,norm,transformed
from open_prototype_path_preflight import samples
from screen_current_remaining_routes import route_rows
from plan_current_mta_interfaces import line

def only_new_pairs(old,new,skip=None):
    """Do not repeatedly compare the126 unchanged head reference segments."""
    grid={};near={};cell=7
    for compare,rows in ((False,old),(True,new)):
        for row in rows:
            name,od=row['wire'],row['OD_mm'];local=[]
            for segment,p in samples(row['segments']):
                key=tuple(math.floor(v/cell) for v in p)
                if compare:
                    for dx in (-1,0,1):
                        for dy in (-1,0,1):
                            for dz in (-1,0,1):
                                for other,q,r,seg in grid.get((key[0]+dx,key[1]+dy,key[2]+dz),[]):
                                    d=math.dist(p,q);minimum=(od+r)/2
                                    if d>minimum+2:continue
                                    if skip is not None and skip(other,name,seg,segment,q,p):continue
                                    pair=(other,name)
                                    if pair not in near or d<near[pair]['sampled_distance_mm']:
                                        near[pair]=dict(a=other,b=name,sampled_distance_mm=d,centreline_minimum_mm=minimum,
                                            sampling_allowance_mm=2,sample_a_mm=q,sample_b_mm=p,segment_a=seg,segment_b=segment,
                                            status='REJECT_PLANNING_PROXIMITY' if d<minimum else 'REQUIRES_EXACT_DISTANCE_CHECK')
                local.append((key,(name,p,od,segment)))
            for key,record in local:grid.setdefault(key,[]).append(record)
    return list(near.values())

def pose_row(r,v):
    parts=[]
    if math.dist(v['start'],v['flex_start'])>1e-8:parts.append(line(v['start'],v['flex_start']))
    parts.extend(v.get('departure_parts_mm',[]));parts.extend(v.get('transition_parts_mm',[]))
    for q in v.get('spans_mm',[v.get('poles_mm')]):
        count=math.ceil(3*max(math.dist(a,b) for a,b in zip(q,q[1:])));previous=q[0]
        for i in range(1,count+1):
            t=i/count;s=1-t
            point=add(add(mul(q[0],s**3),mul(q[1],3*s*s*t)),add(mul(q[2],3*s*t*t),mul(q[3],t**3)))
            parts.append(line(previous,point));previous=point
    parts.extend(v.get('return_parts_mm',[]))
    return dict(wire='Loom/'+r['loom'],OD_mm=6,segments=parts)

def plan(motion=False):
    tick=time.monotonic();f=OUT/'moving-looms-plan.json';p=json.loads(f.read_text())
    assert p['status']=='PROJECT_FLEX_ALLOCATION_ONLY'
    old,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension')))
    rows=[]
    for r in p['looms']:
        v=next(v for v in r['poses'] if not any(v['angles']));rows.append(pose_row(r,v))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for n,h in heads['source_sha256'].items():assert SHA(ROOT/n)==h,n
    pins.add(hf)
    if motion:
        cases=[];rejected=[]
        for leg in ('FL','FR','RL','RR'):
            moving=[r for r in p['looms'] if r['loom'].startswith(leg)]
            fixed=list(old.values())+heads['rows']+[r for r in rows if not r['wire'].startswith('Loom/'+leg)]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                if hip==knee==0:continue
                changed=[pose_row(r,next(v for v in r['poses'] if v['angles']==([hip] if r['motion_stage'].endswith('_Hip') else [hip,knee]))) for r in moving]
                near=only_new_pairs(fixed,changed)
                bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
                case=dict(leg=leg,hip=hip,knee=knee,near_pairs=near,rejected_count=len(bad));cases.append(case)
                rejected.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in bad)
            print('Cheap coupled motion',leg,'rejects',len(rejected),flush=True)
        pins.update((f,Path(__file__)))
        report=dict(status='REJECTED_SHARED_LOOM_SAMPLED_PROXIMITY' if rejected else 'SAMPLED_LOOM_PROXIMITY_ONLY_REAL_MATERIAL_OPEN',
            allocation_revision=p['allocation_revision'],cases=cases,rejected=rejected,screen_seconds=time.monotonic()-tick,
            scope='32same-leg Hip/Knee samples; other legs nominal, all126 retained head paths. Not continuous or simultaneous full-robot travel.',
            selected=False,W5_complete=False,physical_pass=False,
            source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
        (OUT/'moving-looms-motion-screen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(status=report['status'],rejected=rejected,seconds=report['screen_seconds'])),flush=True)
        return report
    near=only_new_pairs(list(old.values())+heads['rows'],rows)
    rejected=[r for r in near if r['status']=='REJECT_PLANNING_PROXIMITY']
    # Whole Hip socket/window allocation, not a cover silently omitted from CAD.
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    original=json.loads((OUT/'harness-interfaces-plan.json').read_text());covers=[]
    for front,cover,x in ((True,'P0_Part__Feature',-123.4575664610465),(False,'P0_Part__Feature107',165.65756646104086)):
        cuts=[]
        for r in p['looms']:
            if not r['loom'].endswith('1') or r['loom'].startswith('F')!=front:continue
            source=next(v for v in original['looms'] if v['loom']==r['loom'])
            a=next(v for v in axes if v['code']==source['cad_code'] and v['stage']=='Hip')
            root=source['connector_reservation_world_mm'][r['project_connector_choice']]
            pts=[transformed(root,source['cable_exit_world_axis'],[a],[angle])[0] for angle in range(-15,16)]
            cuts.append(dict(loom=r['loom'],bounds_mm=[x-3,min(v[1] for v in pts)-3.5,min(v[2] for v in pts)-3.5,
                x+3,max(v[1] for v in pts)+3.5,max(v[2] for v in pts)+3.5]))
        covers.append(dict(target=cover,cut_windows=cuts,bolt_bearing_protection_radius_mm=3.4,
            native_pockets_and_reopen='OPEN',actual_plug_envelope_verified=False,
            caveat='Swept6mm wire envelope plus0.5mm margin only. Delivered keyed plug installation/removal and cover strength remain gates. No source frame omitted.'))
    pins.update((f,af,OUT/'harness-interfaces-plan.json',Path(__file__)))
    report=dict(status='REJECTED_SHARED_LOOM_PROXIMITY' if rejected else 'SHARED_LOOM_PROXIMITY_ONLY_REAL_MATERIAL_OPEN',
        allocation_revision=p['allocation_revision'],near_pairs=near,rejected=rejected,
        proposed_cover_windows=covers,screen_seconds=time.monotonic()-tick,
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins})
    (OUT/'moving-looms-screen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],rejected=rejected,near_count=len(near),seconds=report['screen_seconds'])))
    return report

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--motion',action='store_true')
    plan(args.parse_args().motion)
