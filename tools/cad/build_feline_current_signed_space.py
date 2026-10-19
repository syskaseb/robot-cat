"""Build one current signed/filled routing proposal map, with cached sources.

No unsigned-surface interior acceptance. Separate rigid, existing harness and
adopted36-pose motion occupancy. Mesh/voxel routes still need exact full BRep
gates and curvature/length/assembly checks; this is never N01 or physical PASS.
"""
import hashlib,io,json,os,sys,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.ndimage import distance_transform_edt,label
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_common_space_context import current,is_jacket
from feline_signed_voxels import raster,deposit


def main():
    tick=time.monotonic();integrated_upper='--integrated-upper' in sys.argv
    if integrated_upper:
        from feline_integrated_space_context import integrated,reusable_cell
        world,parts,meta,pins,docs=integrated()
    else:world,parts,meta,pins,docs=current()
    step=1.
    origin=np.array([-144.,-102.,-50.]);size=np.array([331,205,165]);high=origin+(size-1)*step
    stem='n01-integrated-signed-space' if integrated_upper else 'n01-current-signed-space'
    dest=OUT/(stem+'.json');archive=dest.with_suffix('.voxels.zip')
    files=(Path(__file__),Path(__file__).with_name('feline_signed_voxels.py'),Path(__file__).with_name('feline_common_space_context.py'))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in files})
    result=dict(status='RUNNING_CURRENT_SIGNED_SPACE',source_sha256=pins,parts={},errors=[],N01_complete=False,
        physical_pass=False,selected=False,grid_mm=step,origin_mm=origin.tolist(),shape=size.tolist(),
        mesh_deflection_project_mm=.25,closed_volume_fill=True,surface_only_voids_are_not_free=True,
        exact_geometry_and_curvature_acceptance_still_required=True)
    if dest.exists():
        result=json.loads(dest.read_text())
        if result['source_sha256']!=pins and '--adopt-conservative-source-cells' in sys.argv:
            allowed={'tools/cad/build_feline_current_signed_space.py':{'020770f1653de98dd8e7628ab373cb5fa1533d242e6f6091552b8aba07fcc506','7dda7960261c9a40b4f55fcf863b8431daf178f05a48c6c141813ef75633e935'},'tools/cad/feline_signed_voxels.py':{'98d60a368b26da06d6b6e62b933870a655a3e8bf93c805281256c898c18be015','472e372e7b7e76620a0db81ff346329b7b4a0e531a9a36631b0c8baa2432fcb2'}}
            allowed['tools/cad/build_feline_current_signed_space.py'].add('bef4e01fe7bc4b2917b3887a11023648f3ffa81c911196fa0e0e13e6b54229c2')
            allowed['tools/cad/build_feline_current_signed_space.py'].add('5def763a351c3136eba45ad925e57980c376db94abed1b861a74d24c30eeaae4')
            allowed['tools/cad/feline_signed_voxels.py'].add('6476735f237c4df969519c7460dc10dbc27511164d097131048c396bb682cea7')
            for n,h in result['source_sha256'].items():assert h==pins[n] or (n in allowed and h in allowed[n]),n
            if result.get('conservative_source_cell_adoption'):result.setdefault('source_cell_adoption_history',[]).append(result['conservative_source_cell_adoption'])
            result['conservative_source_cell_adoption']=dict(previous_source_sha256=result['source_sha256'],
                previous_result_sha256=sha(dest),source_cells_retained=len(result['parts']),
                reason='Identical triangle SAT, poses, cube expansion and source geometry. Eight-corner integer range union is byte-identical to former offset/scatter oracle. Existing source/layer cells retained; legacy filled cavities remain conservative OCCUPIED supersets. Only proposal data reused, no geometry PASS.')
            result['source_sha256']=pins
        else:assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
        if result.get('errors')==["PermissionError(13, 'Access is denied')"]:
            result.setdefault('handled_implementation_errors',[]).append(dict(error=result['errors'][0],
                cause='np.load archive handle kept open while alternating checkpoint file replaced on Windows',
                fix='Close loaded layer archive after arrays materialized; no source voxels or geometry changed'))
            result['errors']=[]
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('Signed-space source cells saved; receive before resuming')
    last_rest={}
    def cached(name,shape=None,triangles=None,classify_region=None):
        gate();key=hashlib.sha256(name.encode()).hexdigest()[:24]+'.npz'
        if name.startswith('Rest:') and name in last_rest:return last_rest[name]
        if integrated_upper and reusable_cell(name,docs['unchanged'],docs['parent']['parts']):
            row=docs['parent']['parts'][name]
            with zipfile.ZipFile(docs['archive']) as z:raw=z.read(row['entry'])
            assert hashlib.sha256(raw).hexdigest()==row['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as data:value=(data['origin'].copy(),data['occupied'].copy())
            result.setdefault('unchanged_cached_source_names',[])
            if name not in result['unchanged_cached_source_names']:result['unchanged_cached_source_names'].append(name)
            return value
        if name in result['parts']:
            with zipfile.ZipFile(archive) as z:raw=z.read(key)
            assert hashlib.sha256(raw).hexdigest()==result['parts'][name]['sha256']
            data=np.load(io.BytesIO(raw),allow_pickle=False);value=(data['origin'],data['occupied'])
            if name.startswith('Rest:'):last_rest.clear();last_rest[name]=value
            return value
        if triangles is None:
            assert shape.isValid() and shape.Solids,name
            v,f=shape.tessellate(.25);triangles=np.asarray([list(p) for p in v])[np.asarray(f)]
        if classify_region is None:
            assert shape is not None and shape.isValid() and shape.Solids
            solids=shape.Solids
            classify_region=lambda p:any(s.isInside(A.Vector(*p),1e-7,True) for s in solids)
        local,mask=raster(triangles,step,classify_region);buf=io.BytesIO();np.savez_compressed(buf,origin=local,occupied=mask);raw=buf.getvalue()
        with zipfile.ZipFile(archive,'a',zipfile.ZIP_DEFLATED) as z:z.writestr(key,raw)
        result['parts'][name]=dict(entry=key,sha256=hashlib.sha256(raw).hexdigest(),occupied_cells=int(mask.sum()),local_shape=list(mask.shape))
        if len(result['parts'])%20==0:save();print('Closed-volume sources',len(result['parts']),flush=True)
        if name.startswith('Rest:'):last_rest.clear();last_rest[name]=(local,mask)
        return local,mask
    layers={k:np.zeros(tuple(size),bool) for k in ('rigid','harness','motion36')};done_static=set();done_motion=0
    if integrated_upper:
        with np.load(docs['field'],allow_pickle=False) as data:
            assert np.array_equal(data['origin_mm'],origin) and float(data['grid_mm'])==step
            assert data['motion36_occupied'].shape==tuple(size)
            layers['motion36']=data['motion36_occupied'].copy()
        done_motion=len(world.motion)
        result['unchanged_motion_field_reused']=dict(poses=done_motion,source=docs['parentfile'].relative_to(ROOT).as_posix(),
            sha256=sha(docs['parentfile']),fixed_world_and_voxel_engine_hashes_verified=True)
    saved=result.get('layer_checkpoint')
    if saved:
        p=ROOT/saved['file'];assert sha(p)==saved['sha256']
        with np.load(p,allow_pickle=False) as data:
            for k in layers:layers[k]=data[k]
        done_static=set(saved['static_names']);done_motion=saved['motion_count']
    layer_generation=result.get('layer_checkpoint',{}).get('generation',0)
    def checkpoint_layers():
        nonlocal layer_generation
        layer_generation+=1;p=OUT/(stem+'-layers-'+str(layer_generation%2)+'.npz')
        temp=p.with_suffix('.writing.npz');np.savez_compressed(temp,**layers);temp.replace(p)
        result['layer_checkpoint']=dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),static_names=sorted(done_static),
            motion_count=done_motion,generation=layer_generation)
        save()
    result['status']='RUNNING_CURRENT_SIGNED_SPACE';save()
    try:
        for n,s in parts.items():
            if n in done_static:continue
            gate();b=s.BoundBox
            if np.any(np.array([b.XMax,b.YMax,b.ZMax])<origin) or np.any(np.array([b.XMin,b.YMin,b.ZMin])>high):continue
            if not s.Solids:
                # A curve-only source cannot silently become a zero-size cable.
                pts=[list(p) for e in s.Edges for p in e.discretize(Distance=.5)]
                if not pts:continue
                # Explicit conservative3.35mm unknown jacket/fit budget; only
                # proposals, never manufacturer OD or a deleted actual wire.
                points=np.asarray(pts);ids=np.rint((points-origin)/step).astype(int)
                for delta in np.ndindex((9,9,9)):
                    q=ids+np.asarray(delta)-4;valid=np.all(q>=0,1)&np.all(q<size,1);q=q[valid]
                    if len(q):layers['harness'][tuple(q.T)]=True
                done_static.add(n)
                if len(done_static)%40==0:checkpoint_layers()
                continue
            if n==world.bus['name']:
                inverse=docs['inverse'] if integrated_upper else world.bus['inverse']
                v,f=world.bus['original'].tessellate(.25);tf=inverse.inverse()
                points=np.array([list(tf.multVec(p)) for p in v]);triangles=points[np.asarray(f)]
                original=world.bus['original']
                local,mask=cached('Static:'+n,triangles=triangles,
                    classify_region=lambda p:original.isInside(inverse.multVec(A.Vector(*p)),1e-7,True))
            else:local,mask=cached('Static:'+n,s)
            deposit(layers['harness' if is_jacket(n,meta[n]) else 'rigid'],mask,local,origin,step)
            done_static.add(n)
            if len(done_static)%40==0:checkpoint_layers()
        checkpoint_layers()
        for index,p in enumerate(world.motion):
            if index<done_motion:continue
            gate();lo,hi=map(np.asarray,p['bounds'])
            if np.any(hi<origin) or np.any(lo>high):done_motion=index+1;continue
            local,mask=cached('Rest:'+p['name'],world.rest[p['name']])
            deposit(layers['motion36'],mask,local,origin,step,p['r'],p['t'])
            done_motion=index+1
            if done_motion%60==0:checkpoint_layers();print('Saved motion-space poses',done_motion,'/',len(world.motion),flush=True)
        checkpoint_layers()
        if integrated_upper:outer=docs['outer']
        else:outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
        local,mask=cached('ActualTorsoBoundary',outer);inside=np.zeros(tuple(size),bool);deposit(inside,mask,local,origin,step)
        field=dest.with_suffix('.npz');values={}
        for key,mask in layers.items():
            gate();values[key+'_occupied']=mask
            distance=distance_transform_edt(~mask,sampling=step).astype(np.float32)
            distance[mask]=-distance_transform_edt(mask,sampling=step)[mask]
            values[key+'_signed_distance']=distance
        values['inside']=inside
        values['outer_distance']=distance_transform_edt(inside,sampling=step).astype(np.float32)
        np.savez_compressed(field,**values,origin_mm=origin,grid_mm=step)
        counts={}
        for radius in (1.05,1.55,2.1,3.5,5.):
            # Deliberately conservative proposal allowance, not airgap proof.
            free=inside&(values['rigid_signed_distance']>=radius+1.25+1.2)&(values['motion36_signed_distance']>=radius+1.25+1.2)&(values['outer_distance']>=radius+3.25+1.2)
            _,count=label(free);counts[str(radius)]=dict(free_cells=int(free.sum()),connected_components=int(count))
        result.update(status='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY',field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),
            counts_by_radius=counts,voxel_source_archive=archive.relative_to(ROOT).as_posix(),voxel_source_archive_sha256=sha(archive),
            scope='Shared current modules, full end kits, accepted foundation, both4MTA sides and36motion; graph paths are NOT curvature/full BRep/stock/installation approval.')
    except TimeoutError as exc:
        checkpoint_layers();result.update(status='PARTIAL_CURRENT_SIGNED_SPACE',slice_note=str(exc))
    except Exception as exc:result['status']='CURRENT_SIGNED_SPACE_ERROR';result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],sources=len(result['parts']),errors=result['errors'])),flush=True)


def two_fore_lower_deck():
    """Translate16 integer-grid cached sources; never retessellate the world."""
    tick=time.monotonic();world,parts,meta,pins,docs=current();oldfile=OUT/'n01-current-signed-space.json'
    old=json.loads(oldfile.read_text());fp=ROOT/old['field'];archive=ROOT/old['voxel_source_archive']
    assert sha(fp)==old['field_sha256'] and sha(archive)==old['voxel_source_archive_sha256']
    gate=OUT/'n01-usb-fore-lower-deck-space.json';accepted=json.loads(gate.read_text())
    assert accepted['status']=='TWO_WHOLE_FORE_KITS_LOWER_DECK_SPACE_RECEIVED_USB_ROOTS_OPEN' and not accepted['failures'] and not accepted['errors']
    assert all(accepted['source_sha256'][p]==h for p,h in pins.items())
    names=set(accepted['changed_owners']);assert len(names)==16
    with np.load(fp,allow_pickle=False) as f:values={k:f[k] for k in f.files}
    origin=values['origin_mm'];rigid=np.zeros_like(values['rigid_occupied']);harness=values['harness_occupied'].copy();received=0
    with zipfile.ZipFile(archive) as z:
        for key,row in old['parts'].items():
            if not key.startswith('Static:'):continue
            n=key.removeprefix('Static:');assert n in parts,n
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as f:local=f['origin'].copy();mask=f['occupied']
            if n in names:local=local+np.array([0,0,-8]);received+=1
            if is_jacket(n,meta[n]):
                if n in names:deposit(harness,mask,local,origin)
            else:deposit(rigid,mask,local,origin)
    assert received==16,received
    values['rigid_occupied']=rigid;values['harness_occupied']=harness
    for key,mask in (('rigid',rigid),('harness',harness)):
        distance=distance_transform_edt(~mask).astype(np.float32);distance[mask]=-distance_transform_edt(mask)[mask]
        values[key+'_signed_distance']=distance
    dest=OUT/'n01-two-fore-lower-deck-signed-space.json';field=dest.with_suffix('.npz');assert not dest.exists()
    np.savez_compressed(field,**values)
    result=dict(status='CHANGED16_CACHED_SIGNED_SPACE_PROPOSALS_ONLY',source_sha256={**pins,
        **{p.relative_to(ROOT).as_posix():sha(p) for p in (oldfile,fp,archive,gate,Path(__file__))}},field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),
        translated_sources=received,translation_mm=[0,0,-8],all_other_source_voxels_reused=True,retessellated_sources=0,
        old_harness_occupancy_retained_as_conservative_superset=True,motion36_and_actual_outer_fields_byte_unchanged=True,
        N01_complete=False,physical_pass=False,selected=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(json.dumps(result),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True)
    two_fore_lower_deck() if '--two-fore-lower-deck' in sys.argv else main()
