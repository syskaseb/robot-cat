"""Shared finite-radius corridor topology, not individual N04 wire routing.

Six tangent states; straight primitives and circular90deg transitions only.
Every sampled intermediate1mm occupancy cell is checked. The field remains a
conservative proposal: actual endpoint links, packing through turns, exact BRep
and assembly/service acceptance are separate, never silently credited here.
"""
import json,math,os,time
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.sparse import coo_matrix,save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json

DIRECTIONS=np.concatenate((np.eye(3,dtype=int),-np.eye(3,dtype=int)))


def primitive(d,t,radius,step=4):
    d=np.asarray(d);t=np.asarray(t)
    if np.array_equal(d,t):return np.arange(step+1)[:,None]*d
    assert np.dot(d,t)==0 and radius>0 and radius%step==0
    theta=np.linspace(0,math.pi/2,math.ceil(math.pi*radius)+1)
    return radius*(np.sin(theta)[:,None]*d+(1-np.cos(theta))[:,None]*t)


def transitions(free,radius,step=4):
    coarse=free[::step,::step,::step];cells=np.argwhere(coarse)
    ids=np.full(coarse.shape,-1,np.int32);ids[coarse]=np.arange(len(cells))
    rows=[];cols=[];costs=[];shape=np.asarray(free.shape)
    base=cells*step
    for h,d in enumerate(DIRECTIONS):
        for j,t in enumerate(DIRECTIONS):
            if j!=h and np.dot(d,t)!=0:continue
            points=primitive(d,t,radius,step);offsets=np.unique(np.rint(points).astype(int),axis=0)
            valid=np.ones(len(cells),bool)
            for offset in offsets:
                q=base+offset;inside=np.all(q>=0,1)&np.all(q<shape,1);live=np.flatnonzero(valid&inside)
                valid&=inside
                valid[live]&=free[tuple(q[live].T)]
            live=np.flatnonzero(valid)
            if not len(live):continue
            finish=cells[live]+np.rint(points[-1]/step).astype(int)
            target=ids[tuple(finish.T)];assert np.all(target>=0)
            rows.append(live*6+h);cols.append(target*6+j)
            costs.append(np.full(len(live),float(step) if h==j else math.pi*radius/2,np.float32))
    if not rows:return ids,coo_matrix((len(cells)*6,)*2).tocsr()
    graph=coo_matrix((np.concatenate(costs),(np.concatenate(rows),np.concatenate(cols))),shape=(len(cells)*6,)*2).tocsr()
    return ids,graph


def main():
    tick=time.monotonic();sf=OUT/'n01-integrated-signed-space.json';scene=json.loads(sf.read_text())
    assert scene['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    fp=ROOT/scene['field'];assert sha(fp)==scene['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];assert float(f['grid_mm'])==1
        room=np.minimum(f['rigid_signed_distance']-2.45,f['motion36_signed_distance']-2.45)
        room=np.minimum(room,f['outer_distance']-4.45);inside=f['inside']
    dest=OUT/'n01-tangent-corridor-network.json';pins={p.relative_to(ROOT).as_posix():sha(p) for p in (sf,fp,Path(__file__))}
    result=dict(status='RUNNING_FINITE_RADIUS_CORRIDOR_TOPOLOGY',source_sha256=pins,classes={},
        endpoint_links_and_actual_packing_tools_roots_OPEN=True,N01_complete=False,selected=False,physical_pass=False)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    for cable_radius,bend in ((2.1,16),(4.,16),(6.,16),(3.5,28)):
        key=str(cable_radius)+'-R'+str(bend)
        if key in result['classes']:continue
        free=inside&(room>=cable_radius);ids,graph=transitions(free,bend)
        count,component=connected_components(graph,directed=True,connection='strong')
        sizes=np.bincount(component);main=int(sizes.argmax()) if len(sizes) else -1
        graphfile=OUT/('n01-tangent-corridor-'+key+'.graph.npz');nodesfile=OUT/('n01-tangent-corridor-'+key+'.nodes.npz')
        save_npz(graphfile,graph)
        np.savez_compressed(nodesfile,ids=ids,component=component,origin_mm=origin,step_mm=4)
        result['classes'][key]=dict(project_corridor_radius_mm=cable_radius,minimum_circular_bend_mm=bend,
            tangent_states=graph.shape[0],directed_primitives=graph.nnz,strong_components=count,
            largest_component=main,largest_component_states=int(sizes[main]) if main>=0 else 0,
            graph=graphfile.relative_to(ROOT).as_posix(),graph_sha256=sha(graphfile),
            nodes=nodesfile.relative_to(ROOT).as_posix(),nodes_sha256=sha(nodesfile),
            fixed_sampling_step_max_mm=.5,primitive_rounding_error_covered_by_existing_1p2mm_proposal_allowance=True,
            existing_harness_interaction_and_source_links_not_qualified=True)
        save();print(json.dumps(dict(received_class=key,states=graph.shape[0],primitives=graph.nnz,main_states=result['classes'][key]['largest_component_states'])),flush=True)
        if time.monotonic()-tick>225:break
    result['status']='FINITE_RADIUS_SHARED_CORRIDOR_TOPOLOGY_RECEIVED_LINKS_PACKING_OPEN' if len(result['classes'])==4 else 'PARTIAL_FINITE_RADIUS_CORRIDOR_TOPOLOGY'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
