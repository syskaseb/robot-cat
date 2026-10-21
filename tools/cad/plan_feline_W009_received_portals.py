"""Reuse the five saved D_FR portal hypotheses; no new pose or offset sweep.

Rank only portals reachable from the unchanged source in the corrected graph.
These are proposals: old local candidates are not exact clearance receipts.
"""
import json,time
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_tangent_corridor_network import DIRECTIONS
import feline_tangent_routes as ft


def run():
    tick=time.monotonic();folder=OUT/'W009-W069-harness-corridor';old=OUT/'joint-corridor-space-20261021'
    dest=folder/'W009-saved-portals.json';assert not dest.exists()
    resource=json.loads((folder/'resource.json').read_text())['network']['classes']['1.55-R16']
    graph=load_npz(ROOT/resource['graph'])
    with np.load(ROOT/resource['nodes']) as f:ids=f['ids'];origin=f['origin_mm'];cells=np.argwhere(ids>=0)
    coords=origin+4*cells
    oldnet=json.loads((old/'current-tangent-resources.json').read_text())
    with np.load(ROOT/oldnet['classes']['1.55-R16']['nodes']) as f:oldcells=np.argwhere(f['ids']>=0)
    full=json.loads((old/'current-full-source-links-exact.json').read_text())
    a=next(c['recipe'] for c in full['ends']['W009/body/start']['candidates'] if not c['failures'] and c['outer']['ok'])
    def mapnode(c):
        cell=oldcells[c['node']//6];index=int(ids[tuple(cell)])
        return None if index<0 else index*6+c['heading']
    start=mapnode(a);assert start is not None
    distance,pred=dijkstra(graph,indices=start,directed=True,return_predecessors=True)
    domains=json.loads((old/'current-local-exact-link-proposals.json').read_text())
    e=domains['ends']['W009/body/end'];rows=[];proposals=[]
    for b in e['field_positive']+e['near_source_exact_required']:
        node=mapnode(b);goal=None if node is None else node//6*6+(b['heading']+3)%6
        row=dict(heading=b['heading'],point_mm=b['parts'][-1]['end'],node=node,
                 reachable=goal is not None and bool(np.isfinite(distance[goal])))
        rows.append(row)
        if not row['reachable']:continue
        chain=[goal]
        while chain[-1]!=start:
            prior=int(pred[chain[-1]]);assert prior>=0 and len(chain)<=graph.shape[0];chain.append(prior)
        chain.reverse();parts=list(a['parts'])
        for u,v in zip(chain,chain[1:]):
            p,q=coords[u//6],coords[v//6]
            s=ft.line(p,q) if u%6==v%6 else ft.arc(p,DIRECTIONS[u%6],q)
            if parts[-1]['kind']==s['kind']=='line' and ft.dot(ft.unit(ft.sub(s['end'],s['start'])),ft.unit(ft.sub(parts[-1]['end'],parts[-1]['start'])))>1-1e-9:
                parts[-1]=ft.line(parts[-1]['start'],s['end'])
            else:parts.append(s)
        parts.extend(ft.reverse(s) for s in reversed(b['parts']))
        proposals.append(dict(parts=parts,length_mm=ft.length(parts),radius_mm=e['radius_mm'],
                              minimum_R_mm=ft.min_radius(parts),end_heading=b['heading'],
                              endpoint_link_exact_check_OPEN=True))
    proposals.sort(key=lambda r:r['length_mm'])
    pins=[folder/'resource.json',old/'current-local-exact-link-proposals.json',old/'current-full-source-links-exact.json']
    result=dict(status='SAVED_PORTALS_CONNECTIVITY_PROPOSALS_NOT_RECEIVED',portals=rows,proposals=proposals,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        full_exact_static_motion_self_mutual_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(rows,[(r['end_heading'],r['length_mm']) for r in proposals],flush=True)
    return result

if __name__=='__main__':run()
