"""Receive GLOBAL whole-case domains in real static/sampled-motion BReps.

Not a new hand placement or a whole N01 PASS. Saves every completed pair and
resumes missing pairs only. Full factory tails, mounts/tools and continuous
motion remain separate required gates.
"""
import itertools
import json
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL,STAGES,transforms
from feline_current_candidate_scene import current
from check_feline_all_current_lands import near


def matrix_rotation(perm):
    matrix=np.zeros((3,3))
    for source,world in enumerate(perm):matrix[world,source]=1
    if np.linalg.det(matrix)<0:matrix[:,2]*=-1
    return matrix


def placement(rotation,translation):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',float(rotation[i,j]))
    return A.Placement(A.Vector(*translation),A.Rotation(m))


def bounds_near(a,b,gap=1.25):
    return float(np.sum(np.maximum(0,np.maximum(a[0]-b[1],b[0]-a[1]))**2))<=gap*gap


def main():
    tick=time.monotonic();src=OUT/'n01-global-case-capacity.json';dest=OUT/'n01-global-case-candidates-received.json'
    p=json.loads(src.read_text());assert p['status']=='GLOBAL_CASE_CAPACITY_RECEIVED_EXACT_CASES_TAILS_OPEN'
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    scene,meta,templates,pins,bus,_,_,_=current();reader=SavedShapes()
    env=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd';outer=reader.shape(env,'TorsoEnvelope');assert outer.isValid()
    motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    boxes={n:s.BoundBox for n,s in scene.items()};motionparts=[];rest={};tfs={}
    for code,stages in motion['membership'].items():
        aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
        for i,pose in enumerate(motion['poses'][:36]):
            for stage,tf in zip(STAGES,transforms(aa,pose['legs'][code]['angles_delta_degrees'])):tfs[code,stage,i]=tf
        for stage,names in stages.items():
            for name in names:
                s=reader.shape(MODEL,name);rest[name]=s;bb=s.BoundBox
                corners=np.array(list(itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))))
                for i in range(36):
                    r,t=tfs[code,stage,i];v=corners@r.T+t
                    motionparts.append(dict(name=name,code=code,stage=stage,pose=i,bounds=[v.min(0),v.max(0)]))
    pins.update(reader.hashes)
    for f in (src,MODEL,motionfile,axesfile,Path(__file__)):pins[f.relative_to(ROOT).as_posix()]=sha(f)
    pool=[];seen=set()
    # All connected-domain representatives first, then global ranked centres.
    for key in ('all_component_representatives','ranked_distinct_centres'):
        choices=[]
        for orientation in p['orientations']:
            for row in orientation[key]:choices.append(dict(row,source_axis_to_world_axis=orientation['source_axis_to_world_axis']))
        for row in sorted(choices,key=lambda r:(r['conservative'],r['nominal_min_voxel_surface_gap_mm']),reverse=True):
            key_=tuple(row['source_axis_to_world_axis']+row['cell'])
            if key_ in seen:continue
            seen.add(key_);row['id']=len(pool);pool.append(row)
    result=dict(status='RUNNING_GLOBAL_CASE_RECEIVE',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,pool=pool,completed_candidates=[],completed_queries=[],errors=[],
        full_tails_tools_roots_stock_not_qualified=True,continuous_motion_not_qualified=True,
        sampled_motion_source_parts=len(rest),sampled_motion_pose_parts=len(motionparts),
        three_nonoverlapping_case_capacity=None)
    if dest.exists():
        old=json.loads(dest.read_text());assert old['status']=='PARTIAL_GLOBAL_CASE_RECEIVE' and old['source_sha256']==pins
        result=old;result.setdefault('prior_attempts',[]).append(dict(seconds=old['worker_seconds'],errors=old['errors']));result['errors']=[]
    cache={r['key']:r for r in result['completed_queries']};done={r['id']:r for r in result['completed_candidates']}
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s exact receiver cap; resume unfinished candidates/pairs only')
    def check(key,function,**record):
        if key in cache:return cache[key]['gap_mm']
        gate();gap=float(function());row=dict(key=key,gap_mm=gap,**record);cache[key]=row;result['completed_queries'].append(row)
        if len(cache)%10==0:save()
        return gap
    cases={};source=templates['F_HY'][1]
    def case(row):
        r=matrix_rotation(row['source_axis_to_world_axis']);a=placement(r,[0,0,0]).Rotation
        shape=source.copy();shape.Placement=A.Placement(A.Vector(*row['centre_mm'])-a.multVec(source.BoundBox.Center),a)*shape.Placement
        assert shape.isValid() and shape.Solids
        return shape
    for row in result['completed_candidates']:
        if row['status']=='SOURCE_CASE_STATIC_AND36SAMPLED_MOTION_CLEAR_TAILS_OPEN':cases[row['id']]=case(row)
    save()
    try:
        for row in pool:
            gate()
            if len(cases)>=12:break
            if row['id'] in done:continue
            s=case(row);bb=s.BoundBox;cb=[np.array([bb.XMin,bb.YMin,bb.ZMin]),np.array([bb.XMax,bb.YMax,bb.ZMax])]
            received=dict(row,status='pending',bounds_mm=[x.tolist() for x in cb])
            outside=s.cut(outer)
            if not outside.isNull():assert outside.isValid()
            if outside.Volume>1e-5:received.update(status='ACTUAL_OUTSIDE_VOLUME',outside_volume_mm3=outside.Volume)
            else:
                distance=check(f"{row['id']}|outer",lambda:s.distToShape(outer.Shells[0])[0],scope='true_outer',candidate=row['id'])
                if distance<3.25-1e-5:received.update(status='ACTUAL_OUTER_GAP_FAILURE',gap_mm=distance)
            if received['status']=='pending':
                for n,t in scene.items():
                    if not near(bb,boxes[n],1.25):continue
                    if not t.Solids:
                        received.update(status='NEAR_CURRENT_CURVE_REQUIRES_JACKET_OWNER_PLAN',part=n);break
                    if n==bus['name']:
                        q=s.copy();q.Placement=bus['inverse']*q.Placement
                        function=lambda:q.distToShape(bus['original'])[0]
                    else:
                        if not t.isValid():received.update(status='INVALID_SOURCE_HOLD',part=n);break
                        function=lambda:s.distToShape(t)[0]
                    distance=check(f"{row['id']}|static|{n}",function,scope='actual_static',candidate=row['id'],part=n)
                    if distance<1.25-1e-5:
                        reservation='reservation' in meta[n].get('kind','') or meta[n].get('role')=='ScaffoldPlanning' or n.startswith(('StructureReserve:','PiBudget:')) or n=='RetainedMAINCutForeCap'
                        received.update(status='RESERVATION_HOLD' if reservation else 'ACTUAL_MATERIAL_GAP_FAILURE',part=n,gap_mm=distance);break
            if received['status']=='pending':
                for part in motionparts:
                    if not bounds_near(cb,part['bounds']):continue
                    original=rest[part['name']];r,t=tfs[part['code'],part['stage'],part['pose']]
                    if not original.isValid() or not original.Solids:received.update(status='INVALID_MOTION_SOURCE_HOLD',motion=part['name']);break
                    moved=original
                    if np.linalg.norm(r-np.eye(3))>1e-12 or np.linalg.norm(t)>1e-7:
                        moved=original.copy();moved.Placement=placement(r,t)*moved.Placement
                    if not moved.isValid():received.update(status='INVALID_TRANSFORMED_MOTION_SOURCE_HOLD',motion=part['name']);break
                    key=f"{row['id']}|motion|{part['name']}|{part['pose']}"
                    distance=check(key,lambda:s.distToShape(moved)[0],scope='actual_sampled_motion',candidate=row['id'],
                        part=part['name'],leg=part['code'],stage=part['stage'],pose_index=part['pose'])
                    if distance<1.25-1e-5:received.update(status='ACTUAL_SAMPLED_MOTION_GAP_FAILURE',part=part['name'],pose_index=part['pose'],gap_mm=distance);break
            if received['status']=='pending':received['status']='SOURCE_CASE_STATIC_AND36SAMPLED_MOTION_CLEAR_TAILS_OPEN';cases[row['id']]=s
            result['completed_candidates'].append(received);done[row['id']]=received;save()
            print('Whole case',row['id'],received['status'],'clear',len(cases),flush=True)
        for combo in itertools.combinations(cases,3):
            if all(not near(cases[a].BoundBox,cases[b].BoundBox,1.25) or cases[a].distToShape(cases[b])[0]>=1.25-1e-5 for a,b in itertools.combinations(combo,2)):
                result['three_nonoverlapping_case_capacity']=list(combo);break
        result['status']='GLOBAL_CASES_RECEIVED_FULL_FACTORY_TAILS_OPEN'
    except Exception as e:result['status']='PARTIAL_GLOBAL_CASE_RECEIVE';result['errors'].append(repr(e))
    result['clear_case_candidates']=list(cases);save()
    print(json.dumps(dict(status=result['status'],received=len(result['completed_candidates']),clear_cases=len(cases),
        capacity3=result['three_nonoverlapping_case_capacity'],pairs=len(cache),errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
