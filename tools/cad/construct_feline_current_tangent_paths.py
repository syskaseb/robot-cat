"""Join positive actual source links through the received circular graph.

Four currently complete link pairs, not a new pose search. All paths are
received together for self/separation preflight before any exact CAD work.
Independent paths sharing a graph edge are NOT an allocated bundle.
"""
import json,time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
import feline_tangent_routes as ft
from plan_feline_tangent_corridor_network import DIRECTIONS


def run():
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    lf=directory/'current-curved-source-links.json';links=json.loads(lf.read_text())
    assert links['status']=='CURRENT246_CURVED_SOURCE_LINK_DOMAINS_RECORDED_NOT_N01'
    nf=directory/'current-tangent-resources.json';network=json.loads(nf.read_text())
    result=dict(status='CURRENT_CURVED_PATH_PREFLIGHT_NOT_SHARED_ALLOCATION',paths={},mutual=[],
        N01_complete=False,selected=False,physical_pass=False,exact_CAD_and_whole123_OPEN=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (lf,nf,Path(__file__))})
    portions={r['portion'] for r in links['ends'].values() if r.get('field_positive')}
    cache={};samples={}
    for pid in sorted(portions):
        ee=[links['ends'].get(pid+'/'+s,{}) for s in ('start','end')]
        if not all(e.get('field_positive') for e in ee):continue
        key=ee[0]['resource_class'];assert ee[1]['resource_class']==key
        if key not in cache:
            spec=network['classes'][key];gf=ROOT/spec['graph'];nodes=ROOT/spec['nodes']
            assert sha(gf)==spec['graph_sha256'] and sha(nodes)==spec['nodes_sha256']
            with np.load(nodes,allow_pickle=False) as data:
                ids=data['ids'];origin=data['origin_mm'];step=float(data['step_mm'])
            cache[key]=(load_npz(gf),origin+step*np.argwhere(ids>=0),spec['bend_mm'])
        graph,coords,R=cache[key];best=None
        for a in ee[0]['field_positive']:
            distances,pred=dijkstra(graph,directed=True,indices=a['node'],return_predecessors=True)
            for b in ee[1]['field_positive']:
                h=b['heading'];opposite=(h+3)%6;goal=b['node']//6*6+opposite
                total=a['length_mm']+b['length_mm']+distances[goal]
                if not np.isfinite(total) or best and total>=best[0]:continue
                chain=[goal]
                while chain[-1]!=a['node']:
                    node=int(pred[chain[-1]]);assert node>=0 and len(chain)<=graph.shape[0];chain.append(node)
                best=(float(total),a,b,list(reversed(chain)))
        if best is None:
            result['paths'][pid]=dict(status='NO_DIRECTED_CONNECTION_FOR_RECEIVED_LINKS');continue
        total,a,b,chain=best;parts=list(a['parts'])
        for u,v in zip(chain,chain[1:]):
            p=coords[u//6];q=coords[v//6];d=DIRECTIONS[u%6]
            s=ft.line(p,q) if u%6==v%6 else ft.arc(p,d,q)
            if s['kind']=='arc':assert abs(s['radius']-R)<1e-6
            if parts and s['kind']==parts[-1]['kind']=='line' and np.dot(ft.unit(ft.sub(s['end'],s['start'])),ft.unit(ft.sub(parts[-1]['end'],parts[-1]['start'])))>1-1e-9:
                parts[-1]=ft.line(parts[-1]['start'],s['end'])
            else:parts.append(s)
        parts.extend(ft.reverse(s) for s in reversed(b['parts']))
        assert abs(ft.length(parts)-total)<1e-3 and ft.min_radius(parts)>=ee[0]['minimum_R_mm']-1e-6
        points=[];along=[];travel=0.
        for s in parts:
            pp=list(ft.samples(s,.5));points.extend(pp);along.extend(np.linspace(travel,travel+s['length'],len(pp)));travel+=s['length']
        points=np.asarray(points);along=np.asarray(along);radius=ee[0]['radius_mm']
        gaps=cdist(points,points);gaps[np.abs(along[:,None]-along[None,:])<=8*max(radius,1)]=np.inf
        bound=float(gaps.min()-.5-2*radius)
        samples[pid]=(points,radius)
        result['paths'][pid]=dict(status='SELF_SEPARATION_PROPOSAL_POSITIVE' if bound>=.2 else 'SELF_SEPARATION_PROPOSAL_HOLD',
            parts=parts,length_mm=total,minimum_R_mm=ft.min_radius(parts),radius_mm=radius,
            nonlocal_self_gap_lower_bound_mm=bound,source_geometry_UNCHANGED=True)
    for i,a in enumerate(samples):
        for b in list(samples)[i+1:]:
            p,r=samples[a];q,t=samples[b];bound=float(cdist(p,q).min()-.5-r-t)
            result['mutual'].append(dict(a=a,b=b,sampled_gap_lower_bound_mm=bound,
                status='SEPARATION_PROPOSAL_POSITIVE' if bound>=.2 else 'SHARED_LANE_ALLOCATION_OPEN_NOT_PHYSICAL_INFEASIBILITY'))
    result['worker_seconds']=round(time.monotonic()-tick,3)
    save_json(directory/'current-curved-path-preflight.json',result);return result
