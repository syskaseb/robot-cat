"""Retain ALL166 oriented capacity cells before mandatory-end filtering.

A best static centre in each12mm neighbourhood can lose a feasible lead
exit. Recover the already-computed masks, no CAD pose/cloud/mesh changes.
"""
import json
import time
from pathlib import Path
import numpy as np
from scipy.ndimage import minimum_filter
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_global_case_capacity import kernel_size


def main():
    tick=time.monotonic();src=OUT/'n01-global-case-capacity.json';p=json.loads(src.read_text())
    assert p['status']=='GLOBAL_CASE_CAPACITY_RECEIVED_EXACT_CASES_TAILS_OPEN'
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    field=ROOT/p['field'];assert sha(field)==p['field_sha256'];a=np.load(field,allow_pickle=False)
    proof=OUT/'n01-global-case-candidates-received.json';old=json.loads(proof.read_text())
    assert old['status']=='GLOBAL_CASES_RECEIVED_FULL_FACTORY_TAILS_OPEN' and old['method_repairs']
    for n,h in old['source_sha256'].items():assert sha(ROOT/n)==h,n
    mapping={tuple(r['source_axis_to_world_axis']+r['cell']):r['id'] for r in old['pool']}
    clear={r['id']:r for r in old['completed_candidates'] if r['status']=='SOURCE_CASE_STATIC_AND36SAMPLED_MOTION_CLEAR_TAILS_OPEN'}
    nextid=max(mapping.values())+1 if mapping else 0;axes=[a[k] for k in ('x','y','z')];grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    score=np.minimum.reduce([a[k+'_distance'] for k in ('material','reservation','motion36')]);rows=[]
    for orientation in p['orientations']:
        kernel=kernel_size(orientation['world_case_dimensions_mm'])
        mask=minimum_filter(a['nominal'].astype(np.uint8),size=kernel,mode='constant',cval=0).astype(bool)
        conservative=minimum_filter(a['conservative'].astype(np.uint8),size=kernel,mode='constant',cval=0).astype(bool)
        filtered=minimum_filter(score,size=kernel,mode='constant',cval=0)
        assert int(mask.sum())==orientation['nominal_centres']
        for cell in np.argwhere(mask):
            xyz=grid[tuple(cell)];key=tuple(orientation['source_axis_to_world_axis']+cell.tolist())
            ident=mapping.get(key)
            if ident is None:ident=nextid;nextid+=1
            rows.append(dict(id=ident,centre_mm=xyz.tolist(),cell=cell.tolist(),
                source_axis_to_world_axis=orientation['source_axis_to_world_axis'],
                nominal_min_voxel_surface_gap_mm=float(filtered[tuple(cell)]),conservative=bool(conservative[tuple(cell)]),
                prior_exact_case_clear=ident in clear,
                prior_source_case_status=clear.get(ident),both_factory_ends_not_qualified=True))
    rows.sort(key=lambda r:(not r['prior_exact_case_clear'],-r['nominal_min_voxel_surface_gap_mm']))
    result=dict(status='ALL_GLOBAL_CASE_CELLS_RETAINED_END_DOMAINS_OPEN',selected=False,N01_complete=False,physical_pass=False,
        cells=rows,oriented_cells=len(rows),prior_actual_case_clear=sum(r['prior_exact_case_clear'] for r in rows),
        no_case_pose_or_geometry_or_grid_resolution_changed=True,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (src,field,proof,Path(__file__),Path(__file__).with_name('plan_feline_global_case_capacity.py'))},
        worker_seconds=round(time.monotonic()-tick,3))
    assert len({r['id'] for r in rows})==len(rows)==166
    (OUT/'n01-global-all-case-cells.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(cells=len(rows),prior_clear=result['prior_actual_case_clear'],seconds=result['worker_seconds'])))


if __name__=='__main__':main()
