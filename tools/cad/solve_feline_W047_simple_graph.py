"""Bounded conflict branching on SAVED route edges, not source pose scans.

Each self-contact branches on removing either participating directed edge.
Fixed source caps cannot be moved. Graph is only a proposal generator: its
cached fields are never promoted to actual-solid clearance authority.
"""
import heapq
import json
import time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra
from scipy.spatial.distance import cdist
import feline_tangent_routes as ft
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_tangent_corridor_network import DIRECTIONS
from feline_atomic_save import save_json


def self_conflict(parts,owners,radius=1.):
    points=[];along=[];labels=[];travel=0.
    for s,owner in zip(parts,owners):
        sample=list(ft.samples(s,.5));points.extend(sample)
        along.extend(np.linspace(travel,travel+s['length'],len(sample)))
        labels.extend([owner]*len(sample));travel+=s['length']
    along=np.asarray(along);gaps=cdist(points,points)
    gaps[np.abs(along[:,None]-along[None,:])<=8*max(radius,1)]=np.inf
    i,j=np.unravel_index(gaps.argmin(),gaps.shape)
    return float(gaps[i,j]-.5-2*radius),(labels[i],labels[j])


def run(max_expansions=96,max_seconds=90,received_sources=False,initial_forbidden=(),destination=None,companion_departure=False,all_entry_tangents=False):
    tick=time.monotonic();folder=OUT/'joint-corridor-space-20261021'
    lf=folder/'current-curved-source-links.json';nf=folder/'current-tangent-resources.json'
    links=json.loads(lf.read_text())['ends'];spec=json.loads(nf.read_text())['classes']['1.55-R16']
    gf=ROOT/spec['graph'];nodes=ROOT/spec['nodes']
    assert sha(gf)==spec['graph_sha256'] and sha(nodes)==spec['nodes_sha256']
    graph=load_npz(gf).tocsr()
    with np.load(nodes,allow_pickle=False) as data:
        coords=data['origin_mm']+float(data['step_mm'])*np.argwhere(data['ids']>=0)
    a,=links['W047/body/start']['field_positive'];b,=links['W047/body/end']['field_positive']
    extra_sources=[]
    if received_sources:
        import copy
        exactfile=folder/'current-full-source-links-exact.json'
        exact=json.loads(exactfile.read_text())['ends'];chosen=[]
        for side in ('start','end'):
            candidates=exact['W047/body/'+side]['candidates'];assert len(candidates)==1
            candidate=candidates[0];assert not candidate['failures']
            chosen.append(copy.deepcopy(candidate['recipe']))
        a,b=chosen
        resource=OUT/'W009-W069-harness-corridor/resource.json'
        spec=json.loads(resource.read_text())['network']['classes']['1.55-R16']
        gf=ROOT/spec['graph'];nodes=ROOT/spec['nodes']
        assert sha(gf)==spec['graph_sha256'] and sha(nodes)==spec['nodes_sha256']
        with np.load(nodes,allow_pickle=False) as data:
            newcoords=data['origin_mm']+float(data['step_mm'])*np.argwhere(data['ids']>=0)
            for item in (a,b):
                coord=coords[item['node']//6]
                matches=np.where(np.all(np.abs(newcoords-coord)<1e-7,axis=1))[0]
                assert len(matches)==1, ('Received source node removed in harness graph',coord)
                item['node']=int(matches[0])*6+item['heading']
        coords=newcoords;graph=load_npz(gf).tocsr();extra_sources=[exactfile,resource]
    delta_trees=[];delta_cache={};delta_rejected=set();source_links={}
    if companion_departure:
        assert received_sources
        from scipy.spatial import cKDTree
        from plan_feline_RL_shared_bundle import construct
        for filename in ('n01-current-W009-complete-body-plan.json','n01-current-W069-complete-body-plan.json'):
            f=OUT/filename;entry=json.loads(f.read_text());recipe=entry['middle_recipe']
            samples=np.array([p for s in recipe['parts'] for p in ft.samples(s,.5)])
            delta_trees.append((entry['portion'],cKDTree(samples),recipe.get('radius_mm',1.)))
            extra_sources.append(f)
        # Link the FIXED received departure to existing upward tangent states.
        # No module/source-pose search and no assumed node existence.
        candidates=[]
        goal=b['node']//6*6+(b['heading']+3)%6
        costs=dijkstra(graph.transpose().tocsr(),directed=True,indices=goal)
        low,high=([100,-30,42],[152,30,94]) if all_entry_tangents else ([128,-22,74],[152,-2,94])
        local=np.where(np.all(coords>=low,axis=1)&np.all(coords<=high,axis=1))[0]
        if all_entry_tangents:
            from plan_feline_current_joint_tangent_space import available_room
            fieldmeta=folder/'n01-integrated-signed-space.json';fm=json.loads(fieldmeta.read_text())
            fieldpath=ROOT/fm['field'];assert sha(fieldpath)==fm['field_sha256']
            with np.load(fieldpath,allow_pickle=False) as f:
                origin=f['origin_mm'].copy();room=available_room(f);inside=f['inside'].copy()
            extra_sources.extend([fieldmeta,fieldpath])
        rawlinks=[]
        for index in local:
            for heading in (range(6) if all_entry_tangents else [2]):
                node=int(index)*6+heading
                if not np.isfinite(costs[node]):continue
                try:link=ft.biarc([116,-13,64],[1,0,0],coords[index],DIRECTIONS[heading])
                except ValueError:continue
                if ft.min_radius(link)<12.4:continue
                rawlinks.append((ft.length(link)+costs[node],node,link))
        for cost,node,link in sorted(rawlinks,key=lambda x:x[0]):
            if time.monotonic()-tick>=max_seconds:break
            sample=np.array([p for s in link for p in ft.samples(s,.5)])
            if all_entry_tangents:
                ijk=np.rint(sample-origin).astype(int)
                if not (np.all(ijk>=0) and np.all(ijk<room.shape)):continue
                if not np.all(inside[tuple(ijk.T)]&(room[tuple(ijk.T)]>=1.)):continue
            if any(float(tree.query(sample)[0].min())-.5-1.-radius<.2 for _,tree,radius in delta_trees):continue
            candidates.append((cost,node,link))
        assert candidates,'No current local graph connection; do not move the received departure'
        # A single entry selected using the OLD graph cost can force a huge
        # detour after jacket exclusions. Keep all legal links in one solve.
        from scipy.sparse import coo_matrix
        source_links={node:construct(3)[0]+link for _,node,link in candidates}
        coo=graph.tocoo();virtual=graph.shape[0]
        graph=coo_matrix((np.r_[coo.data,[ft.length(p) for p in source_links.values()]],
            (np.r_[coo.row,np.full(len(source_links),virtual)],np.r_[coo.col,list(source_links)])),
            shape=(virtual+1,virtual+1)).tocsr()
        a['node']=virtual
        extra_sources.extend([ROOT/'tools/cad/plan_feline_RL_shared_bundle.py',OUT/'n01-RL-W047-companion-prefix-received.json'])
    source=a['node'];goal=b['node']//6*6+(b['heading']+3)%6
    def delta_blocked(parts,owners):
        failed=[]
        for s,edge in zip(parts,owners):
            key=json.dumps(s,sort_keys=True)
            if key not in delta_cache:
                sample=np.array(list(ft.samples(s,.5)))
                delta_cache[key]=all(float(tree.query(sample)[0].min())-.5-1.-radius>=.2 for _,tree,radius in delta_trees)
            if not delta_cache[key]:failed.append(edge)
        return failed
    def path(forbidden):
        g=graph.copy()
        for u,v in forbidden|delta_rejected:
            start,end=g.indptr[u:u+2];index=np.where(g.indices[start:end]==v)[0]
            assert len(index)==1
            g.data[start+index[0]]=np.inf
        while time.monotonic()-tick<max_seconds:
            distance,pred=dijkstra(g,directed=True,indices=source,return_predecessors=True)
            if not np.isfinite(distance[goal]):return None
            chain=[goal]
            while chain[-1]!=source:
                chain.append(int(pred[chain[-1]]));assert chain[-1]>=0 and len(chain)<=graph.shape[0]
            chain.reverse()
            if source_links:chain=chain[1:];parts=list(source_links[chain[0]])
            else:parts=list(a['parts'])
            owners=[None]*len(parts)
            for u,v in zip(chain,chain[1:]):
                p,q=coords[u//6],coords[v//6]
                parts.append(ft.line(p,q) if u%6==v%6 else ft.arc(p,DIRECTIONS[u%6],q))
                owners.append((u,v))
            tail=[ft.reverse(s) for s in reversed(b['parts'])];parts.extend(tail);owners.extend([None]*len(tail))
            assert ft.min_radius(parts)>=12.4-1e-6
            bad=delta_blocked(parts,owners) if delta_trees else []
            if not bad:return ft.length(parts),parts,owners
            assert None not in bad,'Fixed departure/receiver fails conservative jacket bound; do not move boundary silently'
            for edge in bad:
                delta_rejected.add(edge);u,v=edge
                start,end=g.indptr[u:u+2];idx=np.where(g.indices[start:end]==v)[0];assert len(idx)==1
                g.data[start+idx[0]]=np.inf
        return None
    initial_set=frozenset(tuple(e) for e in initial_forbidden)
    initial=path(initial_set)
    queue=[(initial[0],0,initial_set,initial)] if initial else [];seen={initial_set};history=[];accepted=None;serial=0
    while queue and len(history)<max_expansions and time.monotonic()-tick<max_seconds:
        _,_,forbidden,entry=heapq.heappop(queue);length,parts,owners=entry
        gap,pair=self_conflict(parts,owners)
        history.append(dict(length_mm=length,gap_lower_mm=gap,forbidden_edges=len(forbidden),conflict_edges=pair))
        if gap>=.2:
            accepted=dict(parts=parts,edge_owners=owners,length_mm=length,minimum_R_mm=ft.min_radius(parts),radius_mm=1.,self_gap_lower_mm=gap);break
        for edge in set(pair)-{None}:
            child=forbidden|{edge}
            if child in seen:continue
            seen.add(child);proposal=path(child)
            if proposal is not None:
                serial+=1;heapq.heappush(queue,(proposal[0],serial,child,proposal))
        if len(history)%12==0:print('W047 conflict branches',len(history),'queue',len(queue),flush=True)
    result=dict(status='SELF_CLEAR_GRAPH_PROPOSAL_ACTUAL_SCENE_OPEN' if accepted else 'BOUNDED_GRAPH_CONFLICT_SEARCH_UNRESOLVED',
        accepted=accepted,history=history,pending_branches=len(queue),max_expansions=max_expansions,max_seconds=max_seconds,
        no_source_pose_scan=True,retained_source_links=True,cached_graph_NOT_clearance_authority=True,
        uses_latest_exact_source_links=received_sources,initial_forbidden_edges=sorted(initial_set),
        companion_departure=companion_departure,delta_jacket_blocked_edges=sorted(delta_rejected),
        retained_departure_graph_links=len(source_links),
        all_existing_entry_tangents=all_entry_tangents,
        delta_curve_tests=len(delta_cache),delta_bound_is_proposal_not_actual_collision=True,
        N01_complete=False,physical_pass=False,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (lf,nf,gf,nodes,Path(__file__),*extra_sources)},
        worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/(destination or ('n01-W047-received-simple-graph-proposal.json' if received_sources else 'n01-W047-simple-graph-proposal.json'));assert not dest.exists()
    save_json(dest,result);print(result['status'],len(history),result['worker_seconds'],flush=True)
    return result
