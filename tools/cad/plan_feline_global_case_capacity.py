"""GLOBAL complete-case capacity BEFORE another hand-picked component pose.

Reuses unchanged raw source surface clouds and the complete36motion union.
Replaces only changed static sources. Six axial whole-case footprints are
screened nominally/conservatively; no box overlap becomes a collision claim.
Full tails/tools/roots and real BRep reception remain OPEN.
"""
import io
import itertools
import json
import time
import zipfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import minimum_filter,label
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_candidate_scene import current
from plan_feline_skin_access import surface_samples
from compose_feline_shared_space_atlas import inside_ruled


def points_from_ids(ids,lo,dims):
    return np.column_stack((ids//(dims[1]*dims[2]),ids//dims[2]%dims[1],ids%dims[2]))+lo


def kernel_size(dimensions,spacing=4):
    return tuple(int(2*np.ceil(d/2/spacing)+1) for d in dimensions)


def main():
    tick=time.monotonic();dest=OUT/'n01-global-case-capacity.json';cache=OUT/'n01-global-current-static-voxels.npz'
    fieldfile=OUT/'n01-global-current-case-field.npz';previous=json.loads(dest.read_text()) if dest.exists() else None
    if previous:assert previous['status']=='PARTIAL_GLOBAL_CASE_CAPACITY'
    files=dict(raw=OUT/'n01-shared-space-atlas.json',received=OUT/'n01-shared-space-atlas-received.json',
        oldvoxels=OUT/'n01-shared-space-atlas-voxels.npz',oldfield=OUT/'n01-shared-space-atlas-received-field.npz')
    data={k:json.loads(p.read_text()) for k,p in files.items() if p.suffix=='.json'}
    # No stale surface cloud is silently called the current source.
    for n,h in data['raw']['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(files['oldvoxels'])==data['received']['voxel_cache_sha256']
    assert sha(files['oldfield'])==data['received']['field_sha256']
    scene,meta,templates,pins,bus,changed,removed,variable=current()
    bundle=ROOT/data['raw']['bundle']
    # Original cloud stage was partial before its whole-zip checksum. Its
    # source-pinned per-entry hashes are complete for all cached static clouds.
    # Verify EVERY reused entry below, and pin the current whole zip as input.
    if data['raw'].get('bundle_sha256'):assert sha(bundle)==data['raw']['bundle_sha256']
    for p in (*files.values(),bundle,Path(__file__)):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_GLOBAL_CASE_CAPACITY',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,scene_parts=len(scene),changed_static_parts=sorted(changed),
        removed_old_candidate_or_reallocated_or_moving_rest_parts=removed,
        variable_scaffold_still_requires_load_paths=sorted(variable),
        completed_clouds=[],errors=[],stage='static',case_axes_source_dimensions_mm=None,
        spacing_mm=4,surface_budget_mm=2.3,voxel_budget_mm=.8662,
        grid_interior_budget_mm=float(np.sqrt(3)*2),
        masks_are_capacity_not_material_contact=True,
        material_solid_interiors_not_globally_classified=True,
        whole123routes_two_tails_tool_roots_not_qualified=True)
    lo=np.array([-147,-104,-54]);hi=np.array([189,104,118]);dims=hi-lo+1;count=int(np.prod(dims))
    owners={k:np.zeros(count,dtype=np.uint16) for k in ('material','reservation','curve_hold')}
    if previous:
        assert previous['source_sha256']==pins,'Changed sources: do not reuse capacity masks'
        result=previous;result.setdefault('prior_attempts',[]).append(dict(seconds=result['worker_seconds'],errors=result['errors']))
        result['errors']=[]
        assert sha(cache)==result['voxel_cache_sha256'];v=np.load(cache,allow_pickle=False);owners={k:v[k] for k in owners}
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def checkpoint():
        np.savez_compressed(cache,**owners);result['voxel_cache_sha256']=sha(cache);save()
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s global capacity cap; completed source clouds retained')
    def category(n):
        r=meta[n]
        if not scene[n].Solids:return 'curve_hold'
        return 'reservation' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' or n.startswith(('StructureReserve:','PiBudget:')) or n=='RetainedMAINCutForeCap' else 'material'
    done={r['source'] for r in result['completed_clouds']}
    oldclouds={r['source']:r for r in data['raw']['parts'] if r['key'].startswith('static:')}
    save()
    try:
        with zipfile.ZipFile(bundle) as z:
            for n,s in scene.items():
                gate()
                if n in done:continue
                cat=category(n);old=oldclouds.get(n);reused=old is not None and n not in changed
                if reused:
                    assert old['category']==cat,(n,old['category'],cat)
                    raw=z.read(old['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==old['sha256']
                    pts=np.load(io.BytesIO(raw),allow_pickle=False)
                elif cat=='curve_hold':
                    pts=np.array([list(v) for e in s.Edges for v in e.discretize(Distance=1)])
                else:
                    assert n!=bus['name'],'BUS must retain its unchanged source cloud/inverse frame'
                    assert s.isValid(),n
                    vv,ff=s.tessellate(.3);vv=np.array([list(v) for v in vv])
                    pts=surface_samples(vv[np.array(ff,dtype=int)],2)
                if len(pts):
                    pts=pts[np.all(pts>=lo,axis=1)&np.all(pts<=hi,axis=1)]
                    q=np.rint(pts-lo).astype(np.int32);ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2]
                    o=owners[cat];take=o[ids]==0;o[ids[take]]=len(result['completed_clouds'])+1
                result['completed_clouds'].append(dict(source=n,category=cat,reused_raw_cloud=reused,
                    sample_count=len(pts),source_record=old if reused else None))
                done.add(n)
                if len(done)%100==0:
                    print('Current global static',len(done),'/',len(scene),flush=True);checkpoint()
        result['stage']='field';checkpoint()
        oldvox=np.load(files['oldvoxels'],allow_pickle=False);oldfield=np.load(files['oldfield'],allow_pickle=False)
        axes=[oldfield[k] for k in ('x','y','z')];grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);shape=grid.shape[:3];points=grid.reshape(-1,3)
        distance={};nearest={}
        for cat in ('material','reservation','curve_hold','motion36'):
            gate();o=oldvox[cat] if cat=='motion36' else owners[cat];ids=np.flatnonzero(o)
            tree=cKDTree(points_from_ids(ids,lo,dims));dd,ix=tree.query(points,workers=1)
            distance[cat]=dd.reshape(shape).astype(np.float32);nearest[cat]=(o[ids[ix]]-1).reshape(shape)
            print('Global capacity field',cat,len(ids),flush=True)
        inside=inside_ruled(points).reshape(shape);service=oldfield['service'];outside_distance=oldfield['outer_distance']
        nominal=inside&~service;conservative=nominal.copy();samplebudget=2.3+.8662+np.sqrt(3)*2
        for cat in ('material','reservation','motion36'):
            nominal&=distance[cat]>=1.25;conservative&=distance[cat]>=1.25+samplebudget
        nominal&=distance['curve_hold']>=3.35;conservative&=distance['curve_hold']>=3.35+samplebudget
        nominal&=outside_distance>=3.25;conservative&=outside_distance>=3.25+samplebudget
        dimensions=np.array([templates['F_HY'][1].BoundBox.XLength,templates['F_HY'][1].BoundBox.YLength,templates['F_HY'][1].BoundBox.ZLength])
        assert np.max(abs(dimensions-[51,20.25,22]))<1e-5,dimensions
        result['case_axes_source_dimensions_mm']=dimensions.tolist();result['orientations']=[]
        score=np.minimum.reduce([distance[c] for c in ('material','reservation','motion36')])
        for perm in itertools.permutations(range(3)):
            gate();worlddims=np.empty(3)
            for source_axis,world_axis in enumerate(perm):worlddims[world_axis]=dimensions[source_axis]
            kernel=kernel_size(worlddims);mn=minimum_filter(nominal.astype(np.uint8),size=kernel,mode='constant',cval=0).astype(bool)
            mc=minimum_filter(conservative.astype(np.uint8),size=kernel,mode='constant',cval=0).astype(bool)
            capacityscore=minimum_filter(score,size=kernel,mode='constant',cval=0)
            cc,num=label(mn);ranked=[];used=[];indices=np.argwhere(mn)
            order=np.argsort(capacityscore[mn])[::-1];representatives={}
            for ix in order:
                ind=indices[ix];p=grid[tuple(ind)];component=int(cc[tuple(ind)])
                if component not in representatives:
                    representatives[component]=dict(centre_mm=p.tolist(),cell=ind.tolist(),component=component,
                        conservative=bool(mc[tuple(ind)]),nominal_min_voxel_surface_gap_mm=float(capacityscore[tuple(ind)]))
            for ix in order:
                ind=indices[ix];p=grid[tuple(ind)]
                if any(np.linalg.norm(p-q)<12 for q in used):continue
                used.append(p);ranked.append(dict(centre_mm=p.tolist(),cell=ind.tolist(),component=int(cc[tuple(ind)]),
                    conservative=bool(mc[tuple(ind)]),nominal_min_voxel_surface_gap_mm=float(capacityscore[tuple(ind)])))
                if len(ranked)>=128:break
            result['orientations'].append(dict(source_axis_to_world_axis=list(perm),world_case_dimensions_mm=worlddims.tolist(),
                rectangular_kernel_cells=list(kernel),nominal_centres=int(mn.sum()),conservative_centres=int(mc.sum()),
                nominal_components=num,ranked_distinct_centres=ranked,all_component_representatives=list(representatives.values()),
                footprint_candidates_not_BRep_or_two_tail_acceptance=True))
        np.savez_compressed(fieldfile,x=axes[0],y=axes[1],z=axes[2],inside=inside,nominal=nominal,conservative=conservative,
            service=service,outer_distance=outside_distance,**{k+'_distance':v for k,v in distance.items()},**{k+'_owner':v for k,v in nearest.items()})
        result.update(status='GLOBAL_CASE_CAPACITY_RECEIVED_EXACT_CASES_TAILS_OPEN',stage='complete',
            field=fieldfile.relative_to(ROOT).as_posix(),field_sha256=sha(fieldfile),
            reused_static_clouds=sum(r['reused_raw_cloud'] for r in result['completed_clouds']),
            replaced_static_clouds=sum(not r['reused_raw_cloud'] for r in result['completed_clouds']),
            motion_union_reused_without_retessellation=True,complete_cases_selected=False)
    except Exception as e:
        result['status']='PARTIAL_GLOBAL_CASE_CAPACITY';result['errors'].append(repr(e));checkpoint()
    save();print(json.dumps(dict(status=result['status'],errors=result['errors'],seconds=result['worker_seconds'],
        domains=[(r['source_axis_to_world_axis'],r['nominal_centres'],r['conservative_centres']) for r in result.get('orientations',[])])),flush=True)


if __name__=='__main__':main()
