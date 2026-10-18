"""Finish the cached atlas with bounded-memory 1mm surface voxels.

Not a CAD-layout retry. Retains all completed source clouds, completes only
missing sampled leg poses, and deduplicates their union before building trees.
Voxel-centre error is EXPLICITLY added to the conservative screen budget.
"""
import io
import json
import math
import pickle
import time
import zipfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import label
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE,STAGES,transforms,apply
from compose_feline_shared_space_atlas import inside_ruled
from plan_feline_skin_access import surface_samples
from feline_tangent_routes import quarter_prefix


def main():
    tick=time.monotonic();src=OUT/'n01-shared-space-atlas.json';dest=OUT/'n01-shared-space-atlas-received.json';cache=OUT/'n01-shared-space-atlas-voxels.npz';field=OUT/'n01-shared-space-atlas-received-field.npz'
    parent=json.loads(src.read_text());assert parent['status']!='RUNNING_SHARED_SURFACE_ATLAS','Receive worker before continuation'
    for p,h in parent['source_sha256'].items():assert sha(ROOT/p)==h,p
    previous=json.loads(dest.read_text()) if dest.exists() else None
    report=previous or dict(status='RUNNING_BOUNDED_MEMORY_ATLAS_RECEIVER',selected=False,N01_complete=False,physical_pass=False,
        stage='union',parts=list(parent['parts']),source_sha256={**parent['source_sha256'],src.relative_to(ROOT).as_posix():sha(src),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        parent_clouds_reused=len(parent['parts']),new_pose_clouds=0,errors=[],voxel_mm=1,
        surface_sampling_budget_mm=2.3,voxel_centre_budget_mm=.8662,
        conservative_total_sample_budget_mm=3.1662,source_geometries_or_mesh_resolution_changed=False,
        full_routes_or_mating_or_roots_or_tools_qualified=False)
    if previous:assert report['source_sha256'][src.relative_to(ROOT).as_posix()]==sha(src)
    lo=np.array([-147,-104,-54]);hi=np.array([189,104,118]);dims=hi-lo+1;total=int(np.prod(dims));cats=('material','reservation','motion36','outer','curve_hold')
    def save():
        report['worker_seconds_this_run']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def checkpoint():np.savez_compressed(cache,**owners);report['voxel_cache']=cache.relative_to(ROOT).as_posix();report['voxel_cache_sha256']=sha(cache);save()
    def gate():
        if time.monotonic()-tick>300:raise TimeoutError('300s receiver; bounded voxel union preserved')
    if previous:
        assert sha(cache)==report['voxel_cache_sha256'];saved=np.load(cache,allow_pickle=False);owners={k:saved[k] for k in cats}
    else:
        owners={k:np.zeros(total,dtype=np.uint16) for k in cats}
    if not report.get('static_cloud_union_complete'):
        bundle=ROOT/parent['bundle']
        try:
            with zipfile.ZipFile(bundle) as z:
                for i in range(report.get('parent_clouds_consumed',0),len(parent['parts'])):
                    gate();r=parent['parts'][i]
                    raw=z.read(r['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==r['sha256']
                    p=np.load(io.BytesIO(raw),allow_pickle=False)
                    if len(p):
                        q=np.rint(p-lo).astype(np.int32);ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2];o=owners[r['category']];take=o[ids]==0;o[ids[take]]=i+1
                    report['parent_clouds_consumed']=i+1
                    if i%150==0:print('Voxel source union',i,'/',len(parent['parts']),flush=True)
                    if i%300==0:checkpoint()
            report['static_cloud_union_complete']=True;checkpoint()
        except Exception as e:
            report['status']='PARTIAL_BOUNDED_MEMORY_ATLAS_RECEIVER';report['errors'].append(repr(e));checkpoint();print('Atlas source union partial',repr(e),flush=True);return
    done={r['key'] for r in report['parts']};motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text());axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    try:
        if report['stage']=='union':
            meshes={};needed={n for code,g in motion['membership'].items() for ns in g.values() for n in ns if not all(f'motion:{code}:{i}:{n}' in done for i in range(36))}
            with (BASE/'phase1-prototype-final/preview/triangulation-cache.pkl').open('rb') as f:
                pickle.load(f)
                while True:
                    try:n,m=pickle.load(f)
                    except EOFError:break
                    if n in needed:meshes[n]=m[0]
            assert set(meshes)==needed
            for code,g in motion['membership'].items():
                aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
                for stage in STAGES:
                    for n in g[stage]:
                        gate()
                        if n not in needed:continue
                        pp=surface_samples(meshes[n],2)
                        for i,pose in enumerate(motion['poses'][:36]):
                            key=f'motion:{code}:{i}:{n}'
                            if key in done:continue
                            tf=transforms(aa,pose['legs'][code]['angles_delta_degrees'])[STAGES.index(stage)];p=apply(pp,tf);p=p[np.all(p>=lo,axis=1)&np.all(p<=hi,axis=1)]
                            if len(p):
                                q=np.rint(p-lo).astype(np.int32);ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2];o=owners['motion36'];take=o[ids]==0;o[ids[take]]=len(report['parts'])+1
                            report['parts'].append(dict(key=key,source=n,category='motion36',leg=code,pose_index=i,stage=stage,sample_count=len(p),stored_in_voxel_union_not_duplicate_raw_cloud=True));done.add(key);report['new_pose_clouds']+=1
                        print('Remaining motion union',code,stage,n,'new',report['new_pose_clouds'],flush=True)
                        checkpoint()
            report['stage']='field';checkpoint()
        # At most five small occupancy/owner arrays, not tens of millions of
        # duplicated raw leg-pose samples accumulated in RAM.
        xx=np.arange(-140,181,4,dtype=float);yy=np.arange(-96,97,4,dtype=float);zz=np.arange(-46,111,4,dtype=float)
        grid=np.stack(np.meshgrid(xx,yy,zz,indexing='ij'),axis=-1);points=grid.reshape(-1,3);shape=grid.shape[:3]
        values={};nearest={};samplecounts={}
        for cat in cats:
            gate();ids=np.flatnonzero(owners[cat]);samplecounts[cat]=len(ids)
            if not len(ids):continue
            x=ids//(dims[1]*dims[2]);y=(ids//dims[2])%dims[1];z=ids%dims[2];p=np.column_stack((x,y,z))+lo
            tree=cKDTree(p);dist,index=tree.query(points,workers=1);values[cat]=dist.astype(np.float32);nearest[cat]=owners[cat][ids[index]]-1
            print('Voxel field layer',cat,len(ids),'unique centres',flush=True);del tree,p
        inside=inside_ruled(points);nominal=inside.copy();conservative=inside.copy()
        for cat in ('material','reservation','motion36'):
            nominal&=values[cat]>=3.75;conservative&=values[cat]>=6.9162
        nominal&=values['outer']>=5.75;conservative&=values['outer']>=8.9162
        # Actual R47 source withdrawal is a FUNCTIONAL keepout, not a claim
        # that every point in the conservative source bbox is real material.
        mapfile=OUT/'n01-whole-constraint-map.json';mapping=json.loads(mapfile.read_text());report['source_sha256'][mapfile.relative_to(ROOT).as_posix()]=sha(mapfile)
        service=np.zeros(len(points),dtype=bool);reservations=[]
        for r in mapping['parts']:
            if '_CP2_ATO_' not in r['name']:continue
            a,b=np.array(r['world_bounds_mm']);sign=1 if (a[1]+b[1])>0 else -1
            if sign>0:b[1]+=60
            else:a[1]-=60
            a-=3.75;b+=3.75;service|=np.all(points>=a,axis=1)&np.all(points<=b,axis=1)
            reservations.append(dict(name=r['name'],centreline_keepout_mm=[a.tolist(),b.tolist()],source_extraction_mm=60,bbox_is_functional_reservation_not_physical_collision=True))
        assert len(reservations)==12
        nominal&=~service;conservative&=~service;components,count=label(nominal.reshape(shape))
        previousUSB=json.loads((OUT/'n01-joint-usb-route.json').read_text());anchors=[];groups={'PiUSB':set(),'BUSUSB':set()}
        for owner,p,d in [('PiUSB',previousUSB['start_mm'],(-1,0,0)),('BUSUSB',previousUSB['end_mm'],(0,-1,0))]:
            # 3mm was a minimum PROJECT lead allowance, not an immutable
            # manufacturer length. Allocate this freedom with whole452mm.
            for first in (3,15,30,45,60):
                for i in range(24):
                    a=i*math.pi/12;b=(0,math.cos(a),math.sin(a)) if owner=='PiUSB' else (math.cos(a),0,math.sin(a));prefix=quarter_prefix(p,d,b,first=first);q=np.array(prefix[-1]['end'])
                    ix=tuple(int(np.argmin(abs(axis-q[k]))) for k,axis in enumerate((xx,yy,zz)));registration=float(np.linalg.norm(grid[ix]-q));cid=int(components[ix]) if registration<=4 else 0
                    anchors.append(dict(owner=owner,domain=i,first_straight_mm=first,after9_mm=q.tolist(),cell=list(ix),component=cid,grid_registration_gap_mm=registration,prefix_not_exactly_qualified=True))
                    if cid:groups[owner].add(cid)
        curvehold=values.get('curve_hold',np.full(len(points),np.inf))<5.75
        np.savez_compressed(field,x=xx,y=yy,z=zz,inside=inside.reshape(shape),nominal=nominal.reshape(shape),conservative=conservative.reshape(shape),components=components,
            service=service.reshape(shape),curve_hold=curvehold.reshape(shape),**{cat+'_distance':v.reshape(shape) for cat,v in values.items()},**{cat+'_owner':v.reshape(shape) for cat,v in nearest.items()})
        report.update(status='SHARED_SURFACE_MOTION_SERVICE_ATLAS_PLANNING_NOT_N01',stage='complete',field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),
            grid_shape=list(shape),grid_points=len(points),nominal_candidate_cells=int(nominal.sum()),conservative_candidate_cells=int(conservative.sum()),connected_component_count=count,
            unique_surface_voxel_counts=samplecounts,ATO_withdrawal_reservations=reservations,USB_variable_land_anchors=anchors,USB_shared_component_ids=sorted(groups['PiUSB']&groups['BUSUSB']),
            graph_connected_not_a_radius_length_or_collision_proof=True,whole_solid_interiors_not_globally_classified=True,
            declared_next='Choose a coupled corridor guide from actual field and free straight/after-grip lengths, then R30/full452 smooth route and exact changed interfaces; no third hand-chosen waypoint family')
    except Exception as e:
        report['status']='PARTIAL_BOUNDED_MEMORY_ATLAS_RECEIVER';report['errors'].append(repr(e));checkpoint();print('Atlas receiver partial',repr(e),flush=True)
    save();print(json.dumps(dict(status=report['status'],stage=report['stage'],new_motion=report['new_pose_clouds'],seconds=report['worker_seconds_this_run'],errors=report['errors'])),flush=True)


if __name__=='__main__':main()
