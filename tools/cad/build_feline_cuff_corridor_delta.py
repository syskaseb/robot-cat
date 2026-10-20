"""Filter the six received primitive graphs through the changed35-owner field.

No new primitive generation or newly freed cells. A conservative component
is not a source connection, shared packing, final route or N01 acceptance.
"""
import json,time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz,save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from build_feline_cuff_space_delta import load_fields
from feline_corridor_delta import filter_existing
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();fields,source=load_fields()
    pf=OUT/'n01-output-corridor-topology.json';parent=json.loads(pf.read_text())
    assert parent['status']=='SIX_CURRENT_SHARED_CORRIDOR_CLASSES_RECEIVED_LINKS_PACKING_OPEN'
    room=np.minimum(fields['rigid_signed_distance']-2.45,fields['motion36_signed_distance']-2.45)
    room=np.minimum(room,fields['outer_distance']-4.45);origin=fields['origin_mm']
    sources=(pf,OUT/'n01-cuff-space-delta.json',ROOT/source['field'],ROOT/source['inherited_fields'],Path(__file__),ROOT/'tools/cad/feline_corridor_delta.py')
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in sources};classes={}
    for key,r in parent['classes'].items():
        nf=ROOT/r['nodes'];gf=ROOT/r['graph']
        assert sha(nf)==r['nodes_sha256'] and sha(gf)==r['graph_sha256']
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (nf,gf)})
        with np.load(nf,allow_pickle=False) as a:
            ids=a['ids'];assert np.array_equal(a['origin_mm'],origin) and int(a['step_mm'])==4
        graph,reuse=filter_existing(ids,load_npz(gf),fields['inside']&(room>=r['radius_mm']),r['bend_mm'])
        count,component=connected_components(graph,directed=True,connection='strong');sizes=np.bincount(component)
        outgraph=OUT/('n01-cuff-corridor-'+key+'.graph.npz');outnodes=OUT/('n01-cuff-corridor-'+key+'.nodes.npz')
        save_npz(outgraph,graph);np.savez_compressed(outnodes,ids=ids,component=component,origin_mm=origin,step_mm=4)
        classes[key]=dict(radius_mm=r['radius_mm'],bend_mm=r['bend_mm'],states=graph.shape[0],primitives=graph.nnz,
            strong_components=count,largest_states=int(sizes.max()),graph=outgraph.relative_to(ROOT).as_posix(),graph_sha256=sha(outgraph),
            nodes=outnodes.relative_to(ROOT).as_posix(),nodes_sha256=sha(outnodes),**reuse)
        print(key,graph.nnz,'largest',int(sizes.max()),flush=True)
    result=dict(status='SIX_CUFF_DELTA_CLASSES_RECEIVED_LINKS_PACKING_OPEN',classes=classes,
        source_sha256=pins,unchanged_primitives_only=True,newly_freed_cells_not_added=True,
        source_links_shared_packing_roots_and_assembly_not_accepted=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-cuff-corridor-topology.json',result);print('Seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
