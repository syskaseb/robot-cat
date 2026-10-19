"""Add the actual2.1mm source-wire class; retain all four received classes."""
import json,time
from pathlib import Path
import numpy as np
from scipy.sparse import save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_tangent_corridor_network import transitions


def main():
    tick=time.monotonic();nf=OUT/'n01-tangent-corridor-network.json';parent=json.loads(nf.read_text());assert len(parent['classes'])==4
    sf=OUT/'n01-integrated-signed-space.json';scene=json.loads(sf.read_text());fp=ROOT/scene['field'];assert sha(fp)==scene['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        room=np.minimum(f['rigid_signed_distance']-2.45,f['motion36_signed_distance']-2.45)
        room=np.minimum(room,f['outer_distance']-4.45);free=f['inside']&(room>=2.1);origin=f['origin_mm']
    ids,graph=transitions(free,28);count,comp=connected_components(graph,directed=True,connection='strong');sizes=np.bincount(comp)
    gf=OUT/'n01-tangent-corridor-2.1-R28.graph.npz';df=OUT/'n01-tangent-corridor-2.1-R28.nodes.npz'
    save_npz(gf,graph);np.savez_compressed(df,ids=ids,component=comp,origin_mm=origin,step_mm=4)
    result=dict(status='ACTUAL_2P1_RADIUS_LARGE_BEND_CLASS_RECEIVED',parent=nf.relative_to(ROOT).as_posix(),parent_sha256=sha(nf),
        added_class='2.1-R28',row=dict(project_corridor_radius_mm=2.1,minimum_circular_bend_mm=28,
        graph=gf.relative_to(ROOT).as_posix(),graph_sha256=sha(gf),nodes=df.relative_to(ROOT).as_posix(),nodes_sha256=sha(df),
        tangent_states=graph.shape[0],directed_primitives=graph.nnz,strong_components=count,largest_component_states=int(sizes.max())),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (nf,sf,fp,Path(__file__),ROOT/'tools/cad/plan_feline_tangent_corridor_network.py')},
        N01_complete=False,selected=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-tangent-corridor-thin-large-bend.json',result)
    print(json.dumps(dict(status=result['status'],states=graph.shape[0],primitives=graph.nnz,main_states=int(sizes.max()),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
