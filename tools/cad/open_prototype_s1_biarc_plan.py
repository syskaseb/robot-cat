"""Joint S1/receiving capacity with exact endpoint tangents before one CAD.

The first directional plan was excluded cheaply because the WEST barrel
entered PWM's whole-module allowance. Preserve original free NORTH/SOUTH
ring exits; construct bounded tangent biarcs rather than lower coils or
terminal micro-offsets. No native files or manufacturer claims.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,itertools,json,math,time
import open_prototype_s1_shared_routes as S
import open_prototype_biarc as A
from open_prototype_path_preflight import samples

B=S.B;F=S.F;K=S.K;C=S.C;ROOT=S.ROOT;OUT=S.OUT
PLAN=OUT/'s1-biarc-family-plan.json';PROOF=OUT/'s1-biarc-family-space.json';REUSE_PROOF=None

def search(connector=A.connect,base_override=None):
    base=copy.deepcopy(base_override) if base_override is not None else F.build()
    records=B.read(OUT/'obstacle-map-current.json')['objects']
    fixed=[dict(name=r['role'],bounds=K.bounds(r['centre_mm'],r['size_mm']))
        for r in base['stations']+base['mta']+base['holders'] if r['role'] not in ('P_SYS','F_PI')]
    fixed += [dict(name=r['name'],bounds=r['bounds_mm']) for r in records
        if r['basis'].startswith('Canonical whole-component/reference envelope') or r['name']=='U1UnknownModuleReservation']
    fixed += [dict(name='S1/body',bounds=[114.2,-21,89,138.2,21,126]),dict(name='S1/operator',bounds=[112.2,-14,126,140.2,14,160])]
    space=B.read(OUT/'routing-space-map.json')['samples'];cell=10;grid={}
    for name,radius,parts in C.profiles(base):
        for _,q in samples(parts):grid.setdefault(tuple(math.floor(v/cell) for v in q),[]).append((q,radius))
    def near(q,radius):
        key=tuple(math.floor(v/cell) for v in q)
        return any(math.dist(q,v)<radius+r+.5 for d in itertools.product((-1,0,1),repeat=3)
            for v,r in grid.get(tuple(key[i]+d[i] for i in range(3)),[]))
    def inside(q,radius):
        spans=min(space,key=lambda r:(r['x_mm']-q[0])**2+(r['y_mm']-q[1])**2)['torso_z_intervals_mm']
        return bool(spans) and min(v[0] for v in spans)+radius+.5<=q[2]<=max(v[1] for v in spans)-radius-.5
    def boxes_clear(parts,radius,boxes,receiver=None):
        points=list(samples(parts,step=2))
        for _,q in points:
            if near(q,radius) or not inside(q,radius):return False,'route_or_boundary'
            for r in boxes:
                if r['name']==receiver and math.dist(q,parts[-1]['end'])<=radius+1e-6:continue
                if K.distance_squared(q,r['bounds'])<(radius+.5)**2:return False,r['name']
        return True,points
    counts=dict(families=0,case_exclusions=0,prefix_exclusions=0,biarc_constructions=0,source_exclusions=0,joint_combinations=0)
    rejections={};choices=[]
    goals=sorted(itertools.product(range(-90,131,10),range(-60,61,10)),key=lambda q:math.dist(q,[10,-10]))
    #All four outputs need the148mm level in this bounded family. Lower
    #levels are not retried as undeclared shorter-radius curves.
    for x,y in goals:
        counts['families']+=1
        p=copy.deepcopy(base);delta=B.sub([x,y,148],next(s for s in p['stations'] if s['role']=='P_SYS')['centre_mm'])
        next(s for s in p['stations'] if s['role']=='P_SYS')['centre_mm']=[x,y,148]
        for n in range(1,6):
            port=p['ports'][f'P_SYS.{n}'];port['point_mm']=B.add(port['point_mm'],delta)
        pi=next(h for h in p['holders'] if h['role']=='F_PI')
        for name in ('centre_mm','input_mm','output_mm','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):pi[name]=B.add(pi[name],delta)
        for name in ('input_segments','output_segments'):
            pi[name]=[{k:B.add(v,delta) if k in ('start','mid','end') else v for k,v in s.items()} for s in pi[name]]
        for end in p['body_ends']:end['datum']=p['ports'].get(end['current_role'])
        p['s1_routes']=[]
        pair=[r for r in p['stations']+p['holders'] if r['role'] in ('P_SYS','F_PI')]
        boxes=[dict(name=r['role'],bounds=K.bounds(r['centre_mm'],r['size_mm'])) for r in pair]
        if any(any(K.overlap(r['bounds'],s['bounds']) for s in fixed) or
            any(K.distance_squared(q,r['bounds'])<(od+.5)**2 for points in grid.values() for q,od in points) for r in boxes):
            counts['case_exclusions']+=1;continue
        h=next(h for h in p['holders'] if h['role']=='F_PI')
        prefixes=[(h[side+'_segments'],2) for side in ('input','output')]+[
            ([B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],3),
            ([B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],1.05)]
        if any(not boxes_clear(parts,radius,fixed)[0] for parts,radius in prefixes):counts['prefix_exclusions']+=1;continue
        groups=[]
        for wire,terminal,target in [('W064',3,'P_FRONT.5'),('W065',6,'P_REAR.3'),('W067',2,'P_SYS.4'),('W068',5,'P_SYS.5')]:
            ring=next(r for r in p['s1_module']['rings'] if r['terminal']==terminal)
            end=p['ports'][target]['point_mm'];arrival=B.mul(p['ports'][target]['departure'],-1);rows=[]
            for d1 in (16,24,32,40,48,60,75,90,110,135,165):
                counts['biarc_constructions']+=1
                try:
                    parts=connector(ring['barrel_mm'],ring['direction'],end,arrival,d1)
                    length=B.check_path(parts,min_radius=25.2)
                except (AssertionError,ValueError,ZeroDivisionError):continue
                clear,detail=boxes_clear(parts,2.1,fixed+boxes,target.split('.')[0])
                if not clear:
                    key=wire+'/'+detail;rejections[key]=rejections.get(key,0)+1;continue
                rows.append(dict(wire=wire,terminal=terminal,target=target,eye_mm=ring['eye_mm'],
                    barrel_mm=ring['barrel_mm'],barrel_direction=ring['direction'],segments=parts,
                    OD_mm=4.2,min_radius_mm=25.2,centreline_mm=length,
                    source_straight_mm=9,end_straight_mm=9,nominal_cut_length_mm=None,
                    tangent_construction_d1=d1,termination_allowances='OPEN actual ring insertion/WAGO stripping; centreline is not cut length',
                    native_grips_open=True,legacy920mm_not_selected=True))
            groups.append(sorted(rows,key=lambda r:r['centreline_mm']))
            if not rows:break
        if len(groups)!=4 or any(not g for g in groups):counts['source_exclusions']+=1;continue
        for rows in itertools.product(*groups):
            counts['joint_combinations']+=1;p['s1_routes']=list(rows)
            report=F.F.proximity(p)
            if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']):continue
            choices.append((sum(r['centreline_mm'] for r in rows),copy.deepcopy(p),report));break
        if choices:break #ONE feasible space family, no detail variant loop.
    return choices,counts,rejections

def build():
    data=B.read(PLAN);assert data['family'] is not None,'No conservative source family'
    for name,h in data['source_sha256'].items():assert B.sha(ROOT/name)==h,name
    return data['family']

if __name__=='__main__':
    assert not PLAN.exists(),'Receive one source allocation'
    tick=time.monotonic();choices,counts,rejections=search();p=choices[0][1] if choices else None
    if p:p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,
        changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation'],
        status='ALL4S1_TANGENT_ROUTES_REQUIRE_MATERIAL_AND_THICKNESS_GATE')
    files=[Path(__file__),Path(A.__file__),Path(S.__file__),Path(F.__file__),F.PLAN,F.PROOF,
        OUT/'s1-shared-routes-plan.json',OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    result=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_SOURCE_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY',
        family=p,counts=counts,conservative_rejections=rejections,
        mutual_preflight=choices[0][2] if p else None,
        geometry_digest=S.R.geometry_digest(p) if p else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        circles_and_tangents_exact_samples_and_boxes_not_clearance=True,
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','counts','conservative_rejections','worker_seconds')}),flush=True)
