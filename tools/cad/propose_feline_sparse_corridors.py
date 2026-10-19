"""Whole-space proposals on a sparse lattice of the SAME signed1mm field.

Every intermediate1mm cell on each2mm edge is checked. No coarse occupancy
resampling is accepted as clearance; endpoint links, curves and capacity are
still open. Sparse global Dijkstra replaces thousands of bounded Python heap
searches, not geometry/radii. Positive saved guides are retained unchanged.
"""
import json,math,os,time
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components,dijkstra
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from propose_feline_current_corridors import radius_bucket,macro_boundary,nearest_cell


def grid_graph(free,penalty=None,stride=2):
    coarse=free[::stride,::stride,::stride];ids=np.full(coarse.shape,-1,np.int32)
    ids[coarse]=np.arange(int(coarse.sum()),dtype=np.int32);rows=[];cols=[];costs=[]
    score=np.zeros(coarse.shape,np.float32) if penalty is None else penalty[::stride,::stride,::stride]
    for axis in range(3):
        aa=[slice(None)]*3;bb=list(aa);aa[axis]=slice(None,-1);bb[axis]=slice(1,None)
        a=ids[tuple(aa)];b=ids[tuple(bb)];valid=(a>=0)&(b>=0)
        n=coarse.shape[axis]-1
        for j in range(1,stride):
            sl=[slice(None,None,stride)]*3;sl[axis]=slice(j,stride*n+j,stride)
            valid&=free[tuple(sl)]
        rows.append(a[valid]);cols.append(b[valid]);costs.append(stride*(1+(score[tuple(aa)][valid]+score[tuple(bb)][valid])/2))
    graph=coo_matrix((np.concatenate(costs),(np.concatenate(rows),np.concatenate(cols))),shape=(int(coarse.sum()),)*2).tocsr()
    return ids,graph


def main():
    tick=time.monotonic();sf=OUT/'n01-current-signed-space.json';s=json.loads(sf.read_text())
    assert s['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY';fp=ROOT/s['field'];assert sha(fp)==s['field_sha256']
    with np.load(fp,allow_pickle=False) as a:
        origin=a['origin_mm'];rigid=a['rigid_signed_distance'];motion=a['motion36_signed_distance'];outer=a['outer_distance'];inside=a['inside'];soft=a['harness_signed_distance']
    ef=OUT/'n01-shared-routing-boundaries.json';reg=json.loads(ef.read_text());ends={r['id']:r for r in reg['endpoints']};tasks=dict(reg['portions'])
    cf=OUT/'n01-physical-cable-contract.json';extra=json.loads(cf.read_text());usb=extra['usb'];tasks[usb['id']]=[usb['id']+'/start',usb['id']+'/end']
    for side,key in (('start','pi'),('end','bus')):
        ends[usb['id']+'/'+side]=dict(id=usb['id']+'/'+side,wire=usb['id'],routing_exit_mm=usb[key+'_prefix_exit_mm'],routing_exit_axis=usb[key+'_prefix_exit_axis'],routing_boundary_status='RECEIVED_PREFIX_ONLY_WHOLE_USB_OPEN')
    lf=OUT/'n01-full-lower-bay-plan-r3.json';lower=json.loads(lf.read_text());custom={r['id']:r for r in lower['custom_ends']}
    specs=OUT/'prefix-allocation.json';radii={usb['id']:2.5}
    for r in json.loads(specs.read_text())['specifications']:radii[r['wire']]=max(r['radius'],radii.get(r['wire'],0))
    factory={r['portion_id'] for r in reg['received_factory4MTA_curves']}
    oldfile=OUT/'n01-current-corridor-guides.json';old=json.loads(oldfile.read_text())
    files=(sf,fp,ef,cf,lf,specs,oldfile,Path(__file__),Path(__file__).with_name('propose_feline_current_corridors.py'))
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files};dest=OUT/'n01-current-sparse-corridor-guides.json'
    result=dict(status='RUNNING_SHARED_SPARSE_GUIDES',source_sha256=pins,portions={},classes={},N01_complete=False,physical_pass=False,selected=False,
        total_ordinary_portions=123,separate_USB_assemblies=1,balance=extra['balance'],graph_cell_step_mm=2,underlying_occupied_volume_grid_mm=1,
        every_intermediate_1mm_cell_checked=True,all_anchor_links_curvature_shared_capacity_and_grip_roots_open=True,
        old_bounded_failures_are_not_geometry_rejections=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def radius(ids):
        w=ends[ids[0]]['wire'];return radii.get(w,1.05 if w.startswith('X') else 1.55)
    # Only unchanged positive source-pinned proposals are reused. Old time-cap
    # failures are not retried with the same bounded algorithm or called CAD.
    for n,row in old['portions'].items():
        if row['status']=='CONNECTED_GRID_GUIDE_CURVATURE_AND_EXACT_GATES_OPEN':
            assert all(old['source_sha256'][p.relative_to(ROOT).as_posix()]==sha(p) for p in (sf,fp,ef,cf,lf,specs))
            result['portions'].setdefault(n,dict(row,positive_unchanged_guide_reused_from=oldfile.relative_to(ROOT).as_posix()))
    try:
        for r in sorted({radius_bucket(radius(ids)) for ids in tasks.values()}):
            pending=[n for n,ids in tasks.items() if n not in result['portions'] and radius_bucket(radius(ids))==r]
            if not pending:continue
            free=inside&(rigid>=r+2.45)&(motion>=r+2.45)&(outer>=r+4.45)
            penalty=(3*np.maximum(0,r+1.4-soft)).astype(np.float32)
            ids,graph=grid_graph(free,penalty);coarse=ids>=0;count,comp=connected_components(graph,directed=False)
            populations=np.bincount(comp);main_component=int(populations.argmax());main=np.zeros(coarse.shape,bool);main[coarse]=comp==main_component
            nearest=distance_transform_edt(~main,return_distances=False,return_indices=True)
            result['classes'][str(r)]=dict(nodes=graph.shape[0],undirected_edges=graph.nnz,components=count,largest_component_nodes=int(populations[main_component]),
                component_sizes=sorted(populations.tolist(),reverse=True),whole_source_link_to_main_component_NOT_qualified=True)
            cache_start=None;dist=pred=None;save()
            for n in pending:
                if time.monotonic()-tick>235:raise TimeoutError('Saved completed whole-space proposals')
                aa,bb=[ends[e] for e in tasks[n]];wire=aa['wire'];row=dict(wire=wire,end_ids=tasks[n],prototype_radius_mm=radius(tasks[n]),graph_radius_mm=r,final_full_curve_grip_stock_and_capacity_open=True)
                if n in factory or wire=='W043':
                    row['status']='RECEIVED_COMPLETE_UNCHANGED_CURVE_NOT_REROUTED';result['portions'][n]=row;save();continue
                anchors=[]
                for e in (aa,bb):
                    q,d,bs=macro_boundary(e,custom);local=q-origin
                    if np.any(local<0) or np.any(local>np.asarray(free.shape)-1):
                        anchors.append(dict(end=e['id'],point_mm=q.tolist(),status='EXTERNAL_HEAD_OR_APPENDAGE_NOT_CLAMPED_TO_TORSO'));continue
                    cell=np.rint(local/2).astype(int);anchor=nearest_cell(nearest,cell);point=origin+2*anchor;node=int(ids[tuple(anchor)])
                    anchors.append(dict(end=e['id'],point_mm=q.tolist(),boundary_status=bs,anchor_mm=point.tolist(),coarse_cell=anchor.tolist(),node=node,
                        unqualified_anchor_link_mm=float(np.linalg.norm(q-point)),status='PROPOSAL_LINK_TO_MAIN_COMPONENT_NOT_ACTUAL_SOURCE_EXIT_APPROVAL'))
                row['anchors']=anchors
                if any('node' not in a for a in anchors):row['status']='EXTERNAL_INTERFACE_ROUTE_STILL_OPEN'
                else:
                    start,goal=[v['node'] for v in anchors]
                    if cache_start!=start:dist,pred=dijkstra(graph,directed=False,indices=start,return_predecessors=True);cache_start=start
                    assert np.isfinite(dist[goal]),'Same graph component must be connected'
                    nodes=[goal]
                    while nodes[-1]!=start:
                        previous=int(pred[nodes[-1]]);assert previous>=0 and len(nodes)<=graph.shape[0];nodes.append(previous)
                    nodes.reverse();lookup=np.argwhere(coarse);points=lookup[nodes];compact=[points[0]]
                    for a,b,c in zip(points,points[1:],points[2:]):
                        if not np.array_equal(b-a,c-b):compact.append(b)
                    compact.append(points[-1]);row['guide']=dict(points_mm=(origin+2*np.asarray(compact)).tolist(),length_mm=2*(len(nodes)-1),weighted_cost=float(dist[goal]),
                        not_a_bend_radius_curve_or_shared_capacity_proof=True)
                    row['status']='CONNECTED_SPARSE_GUIDE_CURVATURE_AND_EXACT_GATES_OPEN'
                result['portions'][n]=row;save()
                if len(result['portions'])%10==0:print('Sparse whole-space',len(result['portions']),'/',len(tasks),flush=True)
            del graph,ids,free,penalty,main,nearest,comp
        result['status']='ALL123_PLUS_USB_SPARSE_GUIDES_RECORDED_NOT_N01' if len(result['portions'])==len(tasks) else 'PARTIAL_SHARED_SPARSE_GUIDES'
    except TimeoutError as exc:result.update(status='PARTIAL_SHARED_SPARSE_GUIDES',slice_note=str(exc))
    save();print(json.dumps(dict(status=result['status'],portions=len(result['portions']),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
