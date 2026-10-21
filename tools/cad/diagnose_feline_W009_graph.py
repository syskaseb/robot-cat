"""Locate the W009 disconnect in the saved corrected graph, not a new search."""
import json
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import breadth_first_order
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def run():
    folder=OUT/'W009-W069-harness-corridor';old=OUT/'joint-corridor-space-20261021'
    dest=folder/'W009-disconnect.json';assert not dest.exists()
    resource=json.loads((folder/'resource.json').read_text())['network']['classes']['1.55-R16']
    graph=load_npz(ROOT/resource['graph'])
    with np.load(ROOT/resource['nodes']) as f:ids=f['ids'];origin=f['origin_mm'];cells=np.argwhere(ids>=0)
    oldnet=json.loads((old/'current-tangent-resources.json').read_text())
    with np.load(ROOT/oldnet['classes']['1.55-R16']['nodes']) as f:oldcells=np.argwhere(f['ids']>=0)
    ends={**json.loads((old/'current-full-source-links-exact.json').read_text())['ends'],
          **json.loads((old/'current-named-station-source-links-exact.json').read_text())['ends']}
    nodes=[];rows=[]
    for side in ('start','end'):
        eid='W009/body/'+side
        candidate=next(c['recipe'] for c in ends[eid]['candidates'] if not c['failures'] and c['outer']['ok'])
        cell=oldcells[candidate['node']//6];base=int(ids[tuple(cell)])
        assert base>=0
        heading=candidate['heading'] if side=='start' else (candidate['heading']+3)%6
        node=base*6+heading;nodes.append(node)
        rows.append(dict(end_id=eid,node=node,point_mm=(origin+4*cell).tolist(),heading=heading,
                         outgoing=int(graph.indptr[node+1]-graph.indptr[node]),
                         incoming=int(graph[:,node].nnz)))
    forward=breadth_first_order(graph,nodes[0],directed=True,return_predecessors=False)
    backward=breadth_first_order(graph.T.tocsr(),nodes[1],directed=True,return_predecessors=False)
    for row,reached in zip(rows,(forward,backward)):
        xyz=origin+4*cells[np.unique(reached//6)]
        row.update(reachable_states=len(reached),reachable_cells=len(xyz),bounds_mm=[xyz.min(0).tolist(),xyz.max(0).tolist()])
    result=dict(status='W009_FIXED_LINK_GRAPH_DISCONNECT_LOCALIZED',ends=rows,
        common_states=len(np.intersect1d(forward,backward)),
        graph_sha256=sha(ROOT/resource['graph']),graph=resource['graph'],
        physical_infeasibility_NOT_proved=True,N01_complete=False,physical_pass=False)
    save_json(dest,result);print(result,flush=True);return result

if __name__=='__main__':run()
