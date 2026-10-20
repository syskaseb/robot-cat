"""Recompose owner occupancy, rasterizing only the15 changed actors.

Motion3888 and torso fields stay in the source artifact. Do not subtract a
retired part from a union: another actual part may occupy the same voxel.
"""
import hashlib,io,json,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from scipy.ndimage import distance_transform_edt
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_retention_composed_context import compose
from feline_common_space_context import is_jacket
from feline_signed_voxels import raster,deposit,union_integer_boxes


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    pf=OUT/'n01-integrated-signed-space.json';parent=json.loads(pf.read_text());field=ROOT/parent['field']
    assert parent['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY' and sha(field)==parent['field_sha256']
    engine=ROOT/'tools/cad/feline_signed_voxels.py';assert parent['source_sha256'][engine.relative_to(ROOT).as_posix()]==sha(engine)
    for name in ('n01-shared-Pi-carrier-r3-core-received.json','n01-shared-Pi-carrier-r3-world-received.json'):
        f=OUT/name;assert parent['source_sha256'][f.relative_to(ROOT).as_posix()]==sha(f)
    archives=[ROOT/parent['voxel_source_archive'],docs['archive']];old_docs=[parent,docs['parent']]
    for f,d in zip(archives,old_docs):assert sha(f)==d['voxel_source_archive_sha256']
    with np.load(field,allow_pickle=False) as a:origin=a['origin_mm'];step=float(a['grid_mm']);shape=a['inside'].shape
    assert step==1 and parent['unchanged_motion_field_reused']['poses']==3888
    dest=OUT/'n01-retention-space-delta.json';cache=dest.with_suffix('.voxels.zip');output=dest.with_suffix('.npz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (pf,field,engine,Path(__file__))})
    result=dict(status='RUNNING_RETENTION_OWNER_SPACE_DELTA',source_sha256=pins,parts={},N01_complete=False,physical_pass=False,
        inherited_fields=field.relative_to(ROOT).as_posix(),inherited_fields_sha256=sha(field),retired_source_names=docs['retention_retired'])
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    layers={k:np.zeros(shape,bool) for k in ('rigid','harness')};reused=0
    try:
        with zipfile.ZipFile(archives[0]) as z0,zipfile.ZipFile(archives[1]) as z1:
            for name,s in parts.items():
                b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
                if np.any(hi<origin) or np.any(lo>origin+np.asarray(shape)-1):continue
                if not s.Solids:
                    points=np.asarray([list(p) for e in s.Edges for p in e.discretize(Distance=.5)])
                    assert len(points),'Do not delete an unknown curve source'
                    ids=np.rint(points-origin).astype(int);union_integer_boxes(layers['harness'],ids-4,ids+4);continue
                key='Static:'+name;row=None;raw=None
                if name not in docs['retention_changed']:
                    for index,d in enumerate(old_docs):
                        if key in d['parts'] and (index==0 or name in docs['unchanged']):
                            row=d['parts'][key];raw=(z0 if index==0 else z1).read(row['entry']);reused+=1;break
                    assert row is not None,('Missing unchanged source cache',name)
                elif key in result['parts']:
                    row=result['parts'][key]
                    with zipfile.ZipFile(cache) as z:raw=z.read(row['entry'])
                else:
                    assert s.isValid();vertices,faces=s.tessellate(.25)
                    triangles=np.asarray([list(v) for v in vertices])[np.asarray(faces)]
                    solids=s.Solids;classify=lambda p:any(ss.isInside(A.Vector(*p),1e-7,True) for ss in solids)
                    local,mask=raster(triangles,1.,classify);buf=io.BytesIO();np.savez_compressed(buf,origin=local,occupied=mask);raw=buf.getvalue()
                    entry=hashlib.sha256(key.encode()).hexdigest()[:24]+'.npz'
                    with zipfile.ZipFile(cache,'a',zipfile.ZIP_DEFLATED) as z:z.writestr(entry,raw)
                    row=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=meta[name].get('kind'))
                    result['parts'][key]=row;save();print('Changed owner cached',name,flush=True)
                assert hashlib.sha256(raw).hexdigest()==row['sha256']
                with np.load(io.BytesIO(raw),allow_pickle=False) as a:local=a['origin'];mask=a['occupied']
                deposit(layers['harness' if is_jacket(name,meta[name]) else 'rigid'],mask,local,origin)
                if time.monotonic()-tick>230:raise TimeoutError('Changed source cells saved; resume same inputs')
        values={}
        for key,mask in layers.items():
            d=distance_transform_edt(~mask).astype(np.float32);d[mask]=-distance_transform_edt(mask)[mask]
            values[key+'_occupied']=mask;values[key+'_signed_distance']=d
        np.savez_compressed(output,**values)
        result.update(status='CURRENT_RETENTION_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY',field=output.relative_to(ROOT).as_posix(),field_sha256=sha(output),
            changed_owners_rasterized=len(result['parts']),unchanged_source_caches_reused=reused,
            motion3888_outer_and_inside_fields_unchanged=True,voxel_source_archive=cache.relative_to(ROOT).as_posix(),voxel_source_archive_sha256=sha(cache))
    except TimeoutError as exc:result.update(status='PARTIAL_RETENTION_OWNER_SPACE_DELTA',slice_note=str(exc))
    save();print(json.dumps(dict(status=result['status'],new=len(result['parts']),reused=reused,seconds=result['worker_seconds'])),flush=True)


def load_fields():
    source=OUT/'n01-retention-space-delta.json';d=json.loads(source.read_text());assert d['status']=='CURRENT_RETENTION_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY'
    base=ROOT/d['inherited_fields'];delta=ROOT/d['field'];assert sha(base)==d['inherited_fields_sha256'] and sha(delta)==d['field_sha256']
    with np.load(base,allow_pickle=False) as f:fields={k:f[k] for k in f.files if not k.startswith(('rigid_','harness_'))}
    with np.load(delta,allow_pickle=False) as f:fields.update({k:f[k] for k in f.files})
    return fields,d


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
