"""Plan four current S1 circuits with their receiving family before CAD.

Ring barrels rotate in their actual XY bearing plane, as whole terminals.
R25.2/OD4.2 and9mm insulation grips are project wire reservations, not
manufacturer acceptance. Conservative boxes restrict search, not contacts.
Only one full SYS/PI/source family is emitted, never native trial variants.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,itertools,json,math,time
import open_prototype_aux_fanout_choice as F
import open_prototype_aux_fanout_capacity as C
import open_prototype_pi_capacity_plan as K
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import samples

ROOT=F.ROOT;OUT=F.OUT
PLAN=OUT/'s1-shared-routes-plan.json'
PROOF=OUT/'s1-shared-routes-space.json'
REUSE_PROOF=None
RADIUS=25.2

def route_sources(p):
    """First solve required end tangent, then aim each whole ring at its bend."""
    rings=p['s1_module']['rings'];routes=[]
    for wire,t,target in [('W064',3,'P_FRONT.5'),('W065',6,'P_REAR.3'),
                          ('W067',2,'P_SYS.4'),('W068',5,'P_SYS.5')]:
        ring=next(r for r in rings if r['terminal']==t)
        eye=ring['eye_mm'];end=p['ports'][target]['point_mm']
        arrival=B.mul(p['ports'][target]['departure'],-1)
        if t==3:
            direction=B.WEST
            start=B.add(eye,B.mul(direction,22.123))
            parts=input_recipe(start,end,direction,RADIUS)['segments']
        else:
            #6 enters P_REAR from below;2/5 rise outside SYS, then turn
            #NORTH into its south face. No vertical wire through the case.
            anchor=end[:] if t==6 else B.add(end,[0,-9-RADIUS,0])
            flat=B.sub(anchor,eye);flat[2]=0;direction=B.unit(flat)
            start=B.add(eye,B.mul(direction,22.123))
            corner=B.sub([anchor[0],anchor[1],eye[2]],B.mul(direction,RADIUS))
            assert math.dist(start,corner)>=9,'Ring barrel grip has no straight'
            q=B.quarter(corner,direction,B.UP,RADIUS)
            parts=[B.line(start,corner),q]
            if t==6:
                assert end[2]-q['end'][2]>=9
                parts.append(B.line(q['end'],end))
            else:
                top=[anchor[0],anchor[1],end[2]-RADIUS]
                assert top[2]-q['end'][2]>=3,'Source height cannot carry both bends'
                turn=B.quarter(top,B.UP,B.NORTH,RADIUS)
                parts += [B.line(q['end'],top),turn,B.line(turn['end'],end)]
        old=math.degrees(math.atan2(ring['direction'][1],ring['direction'][0]))
        azimuth=math.degrees(math.atan2(direction[1],direction[0]))
        ring['ring_rotation_z_deg']+=azimuth-old
        ring.update(direction=direction,barrel_mm=start)
        length=B.check_path(parts,start,end,RADIUS)
        assert B.dot(B.segment_geometry(parts[-1])[2],arrival)>1-1e-7
        routes.append(dict(wire=wire,terminal=t,target=target,eye_mm=eye,
            barrel_mm=start,barrel_direction=direction,segments=parts,
            OD_mm=4.2,min_radius_mm=RADIUS,centreline_mm=length,
            source_straight_mm=B.segment_geometry(parts[0])[0],
            end_straight_mm=B.segment_geometry(parts[-1])[0],
            nominal_cut_length_mm=None,termination_allowances='OPEN actual ring insertion/WAGO stripping; centreline is not cut length',
            native_grips_open=True,legacy920mm_not_selected=True))
    p['s1_routes']=routes
    return p

def relocate_pair(p,goal):
    p=copy.deepcopy(p)
    station=next(s for s in p['stations'] if s['role']=='P_SYS')
    delta=B.sub(goal,station['centre_mm']);station['centre_mm']=goal
    for n in range(1,6):
        port=p['ports'][f'P_SYS.{n}'];port['point_mm']=B.add(port['point_mm'],delta)
    h=next(h for h in p['holders'] if h['role']=='F_PI')
    for name in ('centre_mm','input_mm','output_mm','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):
        h[name]=B.add(h[name],delta)
    for name in ('input_segments','output_segments'):
        h[name]=[{k:B.add(v,delta) if k in ('start','mid','end') else v for k,v in s.items()} for s in h[name]]
    for end in p['body_ends']:end['datum']=p['ports'].get(end['current_role'])
    return route_sources(p)

def search():
    base=F.build();records=B.read(OUT/'obstacle-map-current.json')['objects']
    fixed=[dict(name=r['role'],bounds=K.bounds(r['centre_mm'],r['size_mm']))
        for r in base['stations']+base['mta']+base['holders'] if r['role'] not in ('P_SYS','F_PI')]
    fixed += [dict(name=r['name'],bounds=r['bounds_mm']) for r in records
        if r['basis'].startswith('Canonical whole-component/reference envelope') or r['name']=='U1UnknownModuleReservation']
    fixed += [dict(name='S1/body',bounds=[114.2,-21,89,138.2,21,126]),
              dict(name='S1/operator',bounds=[112.2,-14,126,140.2,14,160])]
    space=B.read(OUT/'routing-space-map.json')['samples']
    def contained(bb):
        for x,y in itertools.product((bb[0],bb[3]),(bb[1],bb[4])):
            v=min(space,key=lambda v:(v['x_mm']-x)**2+(v['y_mm']-y)**2)['torso_z_intervals_mm']
            if not v or bb[2]<min(t[0] for t in v)+.5 or bb[5]>max(t[1] for t in v)-.5:return False
        return True
    grid={};cell=10
    for name,radius,parts in C.profiles(base):
        for _,point in samples(parts):
            grid.setdefault(tuple(math.floor(v/cell) for v in point),[]).append((name,point,radius))
    def near(point,radius):
        key=tuple(math.floor(v/cell) for v in point)
        return any(math.dist(point,q)<radius+od+.5
            for d in itertools.product((-1,0,1),repeat=3)
            for _,q,od in grid.get(tuple(key[i]+d[i] for i in range(3)),[]))
    choices=[];reasons={};counts=dict(families=0,case_exclusions=0,prefix_exclusions=0,source_exclusions=0,mutual_exclusions=0)
    for x,y in itertools.product(range(-90,131,10),range(-60,61,10)):
        counts['families']+=1
        try:p=relocate_pair(base,[x,y,148])
        except (AssertionError,ValueError):counts['source_exclusions']+=1;continue
        pair=[r for r in p['stations']+p['holders'] if r['role'] in ('P_SYS','F_PI')]
        boxes=[dict(name=r['role'],bounds=K.bounds(r['centre_mm'],r['size_mm'])) for r in pair]
        if any(not contained(r['bounds']) or any(K.overlap(r['bounds'],s['bounds']) for s in fixed) for r in boxes):
            counts['case_exclusions']+=1;continue
        if any(K.distance_squared(q,b['bounds'])<(rad+.5)**2
               for b in boxes for points in grid.values() for _,q,rad in points):
            counts['case_exclusions']+=1;continue
        h=next(h for h in p['holders'] if h['role']=='F_PI')
        prefix=[(side,h[side+'_segments'],2) for side in ('input','output')]+[
            ('sleeve',[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],3),
            ('new',[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],1.05)]
        blocked=False
        for name,parts,radius in prefix:
            for _,q in samples(parts,step=2):
                if near(q,radius) or any(K.distance_squared(q,b['bounds'])<(radius+.5)**2 for b in fixed):blocked=True;break
                for b in boxes:
                    owncap=name=='input' and math.dist(q,parts[0]['start'] if b['name']=='F_PI' else parts[-1]['end'])<=radius+1e-5
                    owncap|=name=='output' and b['name']=='F_PI' and math.dist(q,parts[0]['start'])<=radius+1e-5
                    if not owncap and K.distance_squared(q,b['bounds'])<radius**2:blocked=True;break
                if blocked:break
            if blocked:break
        if blocked:counts['prefix_exclusions']+=1;continue
        for r in p['s1_routes']:
            for _,q in samples(r['segments'],step=2):
                if near(q,2.1):reasons['other_route']=reasons.get('other_route',0)+1;blocked=True;break
                for b in fixed+boxes:
                    if b['name']==r['target'].split('.')[0] and math.dist(q,r['segments'][-1]['end'])<=2.1+1e-5:continue
                    if K.distance_squared(q,b['bounds'])<(2.1+.5)**2:
                        key=r['wire']+'/'+b['name'];reasons[key]=reasons.get(key,0)+1;blocked=True;break
                if blocked:break
            if blocked:break
        if blocked:counts['source_exclusions']+=1;continue
        report=F.F.proximity(p)
        if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']):counts['mutual_exclusions']+=1;continue
        choices.append((math.dist([x,y,148],[10,-10,148]),p,report))
    choices.sort(key=lambda r:r[0])
    return choices,counts,reasons

def build():
    data=B.read(PLAN);assert data['family'] is not None,'No conservative source family'
    for name,h in data['source_sha256'].items():assert B.sha(ROOT/name)==h,name
    return data['family']

if __name__=='__main__':
    assert not PLAN.exists(),'Receive one source allocation, not unchanged retry'
    tick=time.monotonic();choices,counts,reasons=search();p=choices[0][1] if choices else None
    if p:
        p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,
            changed_ring_terminals=[2,3,5,6],changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
            status='ALL4S1_PREFIX_AND_RECEIVING_FAMILY_PLANNED_NOT_NATIVE_ACCEPTANCE')
    files=[Path(__file__),Path(F.__file__),Path(C.__file__),Path(K.__file__),
           F.PLAN,F.PROOF,OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    result=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_SOURCE_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY',
        counts=counts,conservative_rejections=reasons,shortlisted=len(choices),family=p,
        mutual_preflight=choices[0][2] if p else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        geometric_boxes_are_search_limits_not_actual_contacts=True,
        supplier_ring_barrel_and_bend_assumptions_not_qualified=True,
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','counts','conservative_rejections','shortlisted','worker_seconds')}),flush=True)
