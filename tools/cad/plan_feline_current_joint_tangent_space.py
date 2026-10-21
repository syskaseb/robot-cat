"""Existing finite-radius engine on the received WHOLE current space.

No new pose catalogue, rasterizer, optimizer or route acceptance policy.
Single and shared-bundle resources have actual circular turns. Actual
source links, lane packing and installation remain explicit N01 gates.
"""
import json,time
from pathlib import Path
import numpy as np
from scipy.sparse import save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_tangent_corridor_network import transitions


def run():
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    sf=directory/'n01-integrated-signed-space.json';space=json.loads(sf.read_text())
    assert space['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    sources=[sf,fp,Path(__file__),ROOT/'tools/cad/plan_feline_tangent_corridor_network.py']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    dest=directory/'current-tangent-resources.json'
    result=dict(status='RUNNING_CURRENT_WHOLE_TANGENT_RESOURCES',source_sha256=pins,classes={},
        N01_complete=False,selected=False,physical_pass=False,
        source_links_shared_lane_packing_tools_roots_assembly_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'].copy();assert float(f['grid_mm'])==1
        room=np.minimum(f['rigid_signed_distance']-2.45,f['motion36_signed_distance']-2.45)
        room=np.minimum(room,f['outer_distance']-4.45);inside=f['inside'].copy()
    for radius,bend in ((1.55,16),(2.1,28),(6.,16),(6.,28)):
        key=str(radius)+'-R'+str(bend)
        if key in result['classes']:continue
        ids,graph=transitions(inside&(room>=radius),bend)
        count,component=connected_components(graph,directed=True,connection='strong')
        sizes=np.bincount(component)
        gf=directory/('tangent-'+key+'.graph.npz');nf=directory/('tangent-'+key+'.nodes.npz')
        save_npz(gf,graph)
        np.savez_compressed(nf,ids=ids,component=component,origin_mm=origin,step_mm=4)
        result['classes'][key]=dict(radius_mm=radius,bend_mm=bend,states=graph.shape[0],
            directed_primitives=graph.nnz,strong_components=count,
            largest_component_states=int(sizes.max()) if len(sizes) else 0,
            graph=gf.relative_to(ROOT).as_posix(),graph_sha256=sha(gf),
            nodes=nf.relative_to(ROOT).as_posix(),nodes_sha256=sha(nf),
            source_links_NOT_received=True,shared_packing_NOT_received=True)
        save();print('CURRENT_TANGENT_RESOURCE',key,result['classes'][key]['largest_component_states'],flush=True)
        if time.monotonic()-tick>225:break
    result['status']='CURRENT_WHOLE_FINITE_RADIUS_RESOURCES_LINKS_PACKING_OPEN' if len(result['classes'])==4 else 'PARTIAL_CURRENT_FINITE_RADIUS_RESOURCES'
    save();return result
