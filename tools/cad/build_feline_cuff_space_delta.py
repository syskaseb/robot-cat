"""Only the received RR_P eight plus27 cuff owners need new cells.

Recompose per-owner occupancy, not subtraction from somebody else's union.
The cached motion/inside/outer fields stay byte-identical. Proposal cells
are conservative search data, never actual contact or N01 acceptance.
"""
import hashlib,io,json,os,time,zipfile
from contextlib import ExitStack
from pathlib import Path
import numpy as np
import FreeCAD as A
from scipy.ndimage import distance_transform_edt
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_cuff_composed_context import compose
from feline_common_space_context import is_jacket
from feline_signed_voxels import raster,deposit,union_integer_boxes
from build_feline_output_space_delta import cache_inputs
from feline_atomic_save import save_json


def inputs():
    files,parents,history=cache_inputs()
    f=OUT/'n01-output-space-delta.json';r=json.loads(f.read_text())
    assert r['status']=='CURRENT_OUTPUT_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY'
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/r['voxel_source_archive'])==r['voxel_source_archive_sha256']
    return [f,*files],[r,*parents],history


def main():
    tick=time.monotonic();parentfiles,parents,history=inputs()
    world,parts,meta,pins,docs=compose()
    changed=docs['RRP_changed']|docs['cuff_changed'];assert len(changed)==35
    base=ROOT/parents[0]['inherited_fields'];assert sha(base)==parents[0]['inherited_fields_sha256']
    with np.load(base,allow_pickle=False) as a:
        origin=a['origin_mm'];shape=a['inside'].shape;assert float(a['grid_mm'])==1
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*parentfiles,base,Path(__file__),ROOT/'tools/cad/feline_signed_voxels.py')})
    dest=OUT/'n01-cuff-space-delta.json';cache=dest.with_suffix('.voxels.zip');field=dest.with_suffix('.npz')
    result=dict(status='RUNNING_CUFF_OWNER_SPACE_DELTA',source_sha256=pins,parts={},
        inherited_fields=base.relative_to(ROOT).as_posix(),inherited_fields_sha256=sha(base),
        retired_source_names=docs['RRP_retired'],changed_source_names=sorted(changed),
        historical_generator_not_geometry_authority=history,N01_complete=False,physical_pass=False)
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    layers={k:np.zeros(shape,bool) for k in ('rigid','harness')};reused=0
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    with ExitStack() as stack:
        archives=[stack.enter_context(zipfile.ZipFile(ROOT/d['voxel_source_archive'])) for d in parents]
        try:
            for n,s in parts.items():
                b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
                if np.any(hi<origin) or np.any(lo>origin+np.asarray(shape)-1):continue
                if not s.Solids:
                    pts=np.asarray([list(p) for e in s.Edges for p in e.discretize(Distance=.5)])
                    ids=np.rint(pts-origin).astype(int);union_integer_boxes(layers['harness'],ids-4,ids+4);continue
                key='Static:'+n;row=None;raw=None
                if n not in changed:
                    for i,d in enumerate(parents):
                        if key in d['parts'] and (i<len(parents)-1 or n in docs['unchanged']):
                            row=d['parts'][key];raw=archives[i].read(row['entry']);reused+=1;break
                    assert row is not None,('Unknown unchanged owner',n)
                elif key in result['parts']:
                    row=result['parts'][key]
                    with zipfile.ZipFile(cache) as z:raw=z.read(row['entry'])
                else:
                    assert s.isValid(),n
                    vertices,faces=s.tessellate(.25);triangles=np.asarray([list(v) for v in vertices])[np.asarray(faces)]
                    solids=s.Solids;classify=lambda p:any(q.isInside(A.Vector(*p),1e-7,True) for q in solids)
                    local,mask=raster(triangles,1.,classify);buf=io.BytesIO();np.savez_compressed(buf,origin=local,occupied=mask);raw=buf.getvalue()
                    entry=hashlib.sha256(key.encode()).hexdigest()[:24]+'.npz'
                    with zipfile.ZipFile(cache,'a',zipfile.ZIP_DEFLATED) as z:z.writestr(entry,raw)
                    row=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=meta[n].get('kind'))
                    result['parts'][key]=row;save();print('Changed owner',n,flush=True)
                assert hashlib.sha256(raw).hexdigest()==row['sha256']
                with np.load(io.BytesIO(raw),allow_pickle=False) as a:local=a['origin'];mask=a['occupied']
                deposit(layers['harness' if is_jacket(n,meta[n]) else 'rigid'],mask,local,origin)
                if time.monotonic()-tick>230:raise TimeoutError('Changed35 owner cells saved; receive before resume')
            values={}
            for key,mask in layers.items():
                distance=distance_transform_edt(~mask).astype(np.float32);distance[mask]=-distance_transform_edt(mask)[mask]
                values.update({key+'_occupied':mask,key+'_signed_distance':distance})
            np.savez_compressed(field,**values)
            result.update(status='CURRENT_CUFF_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY',field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),
                changed_owners_rasterized=len(result['parts']),unchanged_source_caches_reused=reused,
                motion3888_outer_and_inside_fields_unchanged=True,voxel_source_archive=cache.relative_to(ROOT).as_posix(),voxel_source_archive_sha256=sha(cache))
        except TimeoutError as e:result.update(status='PARTIAL_CUFF_OWNER_SPACE_DELTA',slice_note=str(e))
    save();print(result['status'],len(result['parts']),reused,result['worker_seconds'],flush=True)


def load_fields():
    f=OUT/'n01-cuff-space-delta.json';r=json.loads(f.read_text())
    assert r['status']=='CURRENT_CUFF_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY'
    base=ROOT/r['inherited_fields'];delta=ROOT/r['field']
    assert sha(base)==r['inherited_fields_sha256'] and sha(delta)==r['field_sha256']
    with np.load(base,allow_pickle=False) as a:values={k:a[k] for k in a.files if not k.startswith(('rigid_','harness_'))}
    with np.load(delta,allow_pickle=False) as a:values.update({k:a[k] for k in a.files})
    return values,r


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
