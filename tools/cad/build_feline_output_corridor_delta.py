"""Filter five existing shared classes; construct one four-HELU R32 class.

No new core poses, source portal optimizer, individual full routes or N01
award. Components describe shared space, not accepted source connections.
"""
import json,time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz,save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from build_feline_output_space_delta import load_fields
from plan_feline_tangent_corridor_network import transitions
from feline_corridor_delta import filter_existing
from feline_bundle_sections import certificate,square


def main():
    tick=time.monotonic();fields,source=load_fields();nf=OUT/'n01-current-corridor-topology.json';parent=json.loads(nf.read_text())
    room=np.minimum(fields['rigid_signed_distance']-2.45,fields['motion36_signed_distance']-2.45)
    room=np.minimum(room,fields['outer_distance']-4.45);origin=fields['origin_mm']
    power=certificate(square(2.1),[2.1]*4,[25.2]*4,6,32);assert power['section_and_turn_fit']
    result=dict(status='RUNNING_OUTPUT_CORRIDOR_DELTA',classes={},four_HELU_section_and_turn=power,
        source_links_shared_packing_other_roots_tools_and_installation_OPEN=True,N01_complete=False,selected=False,physical_pass=False)
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (nf,OUT/'n01-output-space-delta.json',ROOT/source['field'],ROOT/source['inherited_fields'],Path(__file__),ROOT/'tools/cad/feline_corridor_delta.py',ROOT/'tools/cad/plan_feline_tangent_corridor_network.py',ROOT/'tools/cad/feline_bundle_sections.py')}
    for key,r in list(parent['classes'].items())+[('6.0-R32',dict(radius_mm=6.,bend_mm=32))]:
        free=fields['inside']&(room>=r['radius_mm'])
        if 'nodes' in r:
            nodes=ROOT/r['nodes'];graphfile=ROOT/r['graph'];assert sha(nodes)==r['nodes_sha256'] and sha(graphfile)==r['graph_sha256']
            pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (nodes,graphfile)})
            with np.load(nodes,allow_pickle=False) as a:ids=a['ids'];assert np.array_equal(a['origin_mm'],origin) and int(a['step_mm'])==4
            graph,reuse=filter_existing(ids,load_npz(graphfile),free,r['bend_mm'])
        else:ids,graph=transitions(free,r['bend_mm']);reuse=dict(new_required_bundle_class=True)
        count,component=connected_components(graph,directed=True,connection='strong');sizes=np.bincount(component)
        gf=OUT/('n01-output-corridor-'+key+'.graph.npz');df=OUT/('n01-output-corridor-'+key+'.nodes.npz')
        save_npz(gf,graph);np.savez_compressed(df,ids=ids,component=component,origin_mm=origin,step_mm=4)
        result['classes'][key]=dict(radius_mm=r['radius_mm'],bend_mm=r['bend_mm'],states=graph.shape[0],primitives=graph.nnz,
            strong_components=count,largest_states=int(sizes.max()),graph=gf.relative_to(ROOT).as_posix(),graph_sha256=sha(gf),
            nodes=df.relative_to(ROOT).as_posix(),nodes_sha256=sha(df),**reuse)
        print('Received',key,graph.nnz,'largest',int(sizes.max()),reuse,flush=True)
    result.update(status='SIX_CURRENT_SHARED_CORRIDOR_CLASSES_RECEIVED_LINKS_PACKING_OPEN',source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-output-corridor-topology.json',result);print('Seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
