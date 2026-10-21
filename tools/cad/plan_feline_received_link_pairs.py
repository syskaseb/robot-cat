"""Join only exactly received current cap links through existing graph resources.

No new graph, pose catalogue or field rebuild. One common preflight reports
self-contact and lane conflicts; those are not selected routes or N01 points.
"""
import time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_tangent_corridor_network import DIRECTIONS
import feline_tangent_routes as ft


def run(domains,exact,aliases,current_ends,network,source_pins):
    tick=time.monotonic();received={**exact['ends'],**aliases['ends']}
    byid={e['id']:e for e in current_ends};cache={};samples={}
    result=dict(status='RECEIVED_SOURCE_LINK_PAIRS_PREFLIGHT_NOT_ALLOCATION',paths={},mutual=[],
                selected=False,N01_complete=False,physical_pass=False,
                source_sha256={**source_pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    for name in ('current-local-exact-link-proposals.json','current-full-source-links-exact.json',
                 'current-named-station-source-links-exact.json','current-tangent-resources.json'):
        p=OUT/'joint-corridor-space-20261021'/name
        result['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    for pid in sorted({e['portion_id'] for e in current_ends}):
        ends=[pid+'/'+s for s in ('start','end')]
        if any(byid[e].get('whole_portion_received') for e in ends):continue
        if not all(received.get(e,{}).get('status')=='FULL_SOURCE_LINK_STATIC_RECEIVED_MOTION_AND_PACKING_OPEN' for e in ends):continue
        ee=[domains['ends'][e] for e in ends];key=ee[0]['resource_class'];assert ee[1]['resource_class']==key
        if key not in cache:
            spec=network['classes'][key];gf=ROOT/spec['graph'];nf=ROOT/spec['nodes']
            assert sha(gf)==spec['graph_sha256'] and sha(nf)==spec['nodes_sha256']
            with np.load(nf,allow_pickle=False) as data:
                coords=data['origin_mm']+float(data['step_mm'])*np.argwhere(data['ids']>=0)
            cache[key]=(load_npz(gf),coords,spec['bend_mm'])
        graph,coords,R=cache[key];candidates=[]
        links=[[c['recipe'] for c in received[e]['candidates'] if not c['failures'] and c['outer']['ok']] for e in ends]
        for a in links[0]:
            distances,pred=dijkstra(graph,directed=True,indices=a['node'],return_predecessors=True)
            for b in links[1]:
                goal=b['node']//6*6+(b['heading']+3)%6
                if not np.isfinite(distances[goal]):continue
                chain=[goal]
                while chain[-1]!=a['node']:
                    n=int(pred[chain[-1]]);assert n>=0 and len(chain)<=graph.shape[0];chain.append(n)
                chain.reverse();parts=list(a['parts'])
                for u,v in zip(chain,chain[1:]):
                    p,q=coords[u//6],coords[v//6]
                    s=ft.line(p,q) if u%6==v%6 else ft.arc(p,DIRECTIONS[u%6],q)
                    if s['kind']=='arc':assert abs(s['radius']-R)<1e-6
                    if parts and s['kind']==parts[-1]['kind']=='line' and ft.dot(ft.unit(ft.sub(s['end'],s['start'])),ft.unit(ft.sub(parts[-1]['end'],parts[-1]['start'])))>1-1e-9:
                        parts[-1]=ft.line(parts[-1]['start'],s['end'])
                    else:parts.append(s)
                parts.extend(ft.reverse(s) for s in reversed(b['parts']))
                assert ft.min_radius(parts)>=ee[0]['minimum_R_mm']-1e-6
                points=[];along=[];travel=0.
                for s in parts:
                    pp=list(ft.samples(s,.5));points.extend(pp);along.extend(np.linspace(travel,travel+s['length'],len(pp)));travel+=s['length']
                points=np.asarray(points);along=np.asarray(along);radius=ee[0]['radius_mm']
                gaps=cdist(points,points);gaps[np.abs(along[:,None]-along[None,:])<=8*max(radius,1)]=np.inf
                bound=float(gaps.min()-.5-2*radius)
                candidates.append((bound,travel,parts,points,radius))
        if not candidates:
            result['paths'][pid]=dict(status='NO_DIRECTED_CONNECTION_FOR_RECEIVED_LINKS');continue
        positive=[c for c in candidates if c[0]>=.2];choice=min(positive,key=lambda c:c[1]) if positive else max(candidates,key=lambda c:c[0])
        bound,travel,parts,points,radius=choice;samples[pid]=(points,radius)
        result['paths'][pid]=dict(status='SELF_SEPARATION_PROPOSAL_POSITIVE' if positive else 'SELF_SEPARATION_PROPOSAL_HOLD',
            parts=parts,length_mm=travel,minimum_R_mm=ft.min_radius(parts),radius_mm=radius,
            nonlocal_self_gap_lower_bound_mm=bound,exact_full_body_static_motion_and_shared_packing_OPEN=True)
    for i,a in enumerate(samples):
        for b in list(samples)[i+1:]:
            p,r=samples[a];q,t=samples[b];bound=float(cdist(p,q).min()-.5-r-t)
            result['mutual'].append(dict(a=a,b=b,sampled_gap_lower_bound_mm=bound,separated=bound>=.2))
    result['worker_seconds']=round(time.monotonic()-tick,3)
    save_json(OUT/'joint-corridor-space-20261021/current-exact-linked-body-preflight.json',result)
    return result
