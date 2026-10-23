"""Reuse saved current graph; one changed bank departure, no module scan."""
import json,time,heapq
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz,coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
import feline_tangent_routes as ft
from plan_feline_tangent_corridor_network import DIRECTIONS
from solve_feline_W047_simple_graph import self_conflict
from plan_feline_W033_curved_grip import build
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def run(seconds=90,reach=32,destination='n01-W033-curved-grip-shared-graph.json',outboard=False):
    tick=time.monotonic();folder=OUT/'joint-corridor-space-20261021'
    resource=OUT/'W009-W069-harness-corridor/resource.json'
    rf=json.loads(resource.read_text());spec=rf['network']['classes']['1.55-R16']
    gf=ROOT/spec['graph'];nf=ROOT/spec['nodes'];assert sha(gf)==spec['graph_sha256'] and sha(nf)==spec['nodes_sha256']
    graph=load_npz(gf).tocsr()
    with np.load(nf,allow_pickle=False) as f:coords=f['origin_mm']+float(f['step_mm'])*np.argwhere(f['ids']>=0)
    exactfile=folder/'current-full-source-links-exact.json'
    entry=json.loads(exactfile.read_text())['ends']['W033/body/start']['candidates'][0]
    assert not entry['failures'];sourceparts=entry['recipe']['parts']
    index,=np.where(np.all(np.abs(coords-sourceparts[-1]['end'])<1e-7,axis=1))[0]
    source=int(index)*6+entry['recipe']['heading']
    _,bankparts,_=build(True);bankparts=bankparts[:2]
    end=np.array(bankparts[-1]['end']);axis=np.array(bankparts[-1]['end_tangent'])
    files=[resource,gf,nf,exactfile,Path(__file__),Path(__file__).with_name('plan_feline_W033_curved_grip.py')]
    trees=[]
    for wire in ('W009','W069','W047','W020','W022','W024'):
        f=OUT/(f'n01-current-{wire}-shared-complete-body-plan.json' if wire=='W024' else f'n01-current-{wire}-complete-body-plan.json');r=json.loads(f.read_text())['middle_recipe'];files.append(f)
        trees.append((cKDTree(np.array([p for s in r['parts'] for p in ft.samples(s,.5)])),r['radius_mm']))
    def jackets(parts):
        pts=np.array([p for s in parts for p in ft.samples(s,.5)])
        return all(float(t.query(pts)[0].min())-.5-1-radius>=.2 for t,radius in trees)
    fieldfile=folder/'n01-integrated-signed-space.json';fm=json.loads(fieldfile.read_text());fp=ROOT/fm['field'];assert sha(fp)==fm['field_sha256'];files.extend([fieldfile,fp])
    from plan_feline_current_joint_tangent_space import available_room
    with np.load(fp,allow_pickle=False) as f:origin=f['origin_mm'].copy();room=available_room(f);inside=f['inside'].copy()
    if outboard:
        return joint_departures(graph,coords,room,inside,origin,jackets,files,tick,seconds,destination)
    links={};source_costs=dijkstra(graph,directed=True,indices=source)
    local=np.where(np.all(np.abs(coords-end)<reach,axis=1))[0]
    order=np.argsort(np.linalg.norm(coords[local]-end,axis=1)+source_costs.reshape(-1,6)[local].min(axis=1))
    tried=0
    for i in local[order]:
        if time.monotonic()-tick>min(30,seconds/2):break
        for heading in range(6):
            if not np.isfinite(source_costs[int(i)*6+(heading+3)%6]):continue
            tried+=1
            try:parts=ft.biarc(end,axis,coords[i],DIRECTIONS[heading])
            except ValueError:continue
            if ft.min_radius(parts)<12.4 or not jackets(parts):continue
            pts=np.array([p for s in parts for p in ft.samples(s,.5)])
            # Historical field contains retired straight-cap geometry. Only
            # proposal filtering outside the local changed interface; all actual
            # material is checked later, never exempted by this filter.
            pts=pts[np.linalg.norm(pts-end,axis=1)>12]
            ijk=np.rint(pts-origin).astype(int)
            if len(ijk) and (not np.all(ijk>=0) or not np.all(ijk<room.shape) or not np.all(inside[tuple(ijk.T)]&(room[tuple(ijk.T)]>=1))):continue
            links[int(i)*6+(heading+3)%6]=[ft.reverse(s) for s in reversed(parts)]
    virtual=graph.shape[0];coo=graph.tocoo()
    g=coo_matrix((np.r_[coo.data,[ft.length(p) for p in links.values()]],(np.r_[coo.row,list(links)],np.r_[coo.col,np.full(len(links),virtual)])),shape=(virtual+1,virtual+1)).tocsr()
    blocked=set();cache={};history=[];accepted=None
    def disable(h,edges):
        for u,v in edges:
            sl=slice(h.indptr[u],h.indptr[u+1]);offset,=np.where(h.indices[sl]==v)[0];h.data[h.indptr[u]+offset]=np.inf
    def solve(forbidden):
        h=g.copy();disable(h,forbidden|blocked)
        while time.monotonic()-tick<seconds:
            costs,pred=dijkstra(h,directed=True,indices=source,return_predecessors=True)
            if not np.isfinite(costs[virtual]):return None
            chain=[virtual]
            while chain[-1]!=source:chain.append(int(pred[chain[-1]]));assert chain[-1]>=0
            chain.reverse();parts=list(sourceparts);owners=[None]*len(parts)
            for u,v in zip(chain,chain[1:]):
                chunk=links[u] if v==virtual else [ft.line(coords[u//6],coords[v//6]) if u%6==v%6 else ft.arc(coords[u//6],DIRECTIONS[u%6],coords[v//6])]
                parts.extend(chunk);owners.extend([(u,v)]*len(chunk))
            bad=[]
            for s,e in zip(parts,owners):
                key=json.dumps(s,sort_keys=True)
                if key not in cache:cache[key]=jackets([s])
                if not cache[key]:bad.append(e)
            if not bad:return parts,owners
            assert None not in bad,'Fixed source fails; no silent movement'
            blocked.update(bad);disable(h,set(bad))
        return None
    first=solve(frozenset()) if links else None
    queue=[(ft.length(first[0]),0,frozenset(),first)] if first else [];seen={frozenset()};serial=0
    while queue and time.monotonic()-tick<seconds:
        _,_,forbidden,(parts,owners)=heapq.heappop(queue)
        gap,pair=self_conflict(parts,owners)
        history.append(dict(length_mm=ft.length(parts),self_gap_lower_mm=gap,forbidden=len(forbidden)))
        if gap>=.2:accepted=dict(parts=parts,radius_mm=1,minimum_R_mm=ft.min_radius(parts),length_mm=ft.length(parts),self_gap_lower_mm=gap);break
        for edge in set(pair)-{None}:
            child=forbidden|{edge}
            if child in seen:continue
            seen.add(child);candidate=solve(child)
            if candidate:serial+=1;heapq.heappush(queue,(ft.length(candidate[0]),serial,child,candidate))
    result=dict(status='PROPOSAL_ACTUAL_MATERIAL_AND_GRIP_RECEIPT_OPEN',accepted=accepted,bank_prefix_parts=bankparts,legal_local_links=len(links),history=history,blocked_edges=sorted(blocked),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    result.update(connection_reach_mm=reach,conflicts_branched_individually=True,connection_trials=tried,
                  source_cost_ordered_links=True,local_connection_budget_seconds=min(30,seconds/2))
    dest=OUT/destination;assert not dest.exists();save_json(dest,result)
    print('W033 GRAPH',len(links),history[-1:] if history else [],result['worker_seconds'],flush=True)
    return result


def joint_departures(graph,coords,room,inside,origin,jackets,files,tick,seconds,destination):
    """Two constructive changed departures; no original blocked outlet reused."""
    bank_axis=np.array([-1.,0.,-1.])/np.sqrt(2)
    bank_point=np.array([-18,-1.752,69])+12.4*bank_axis
    endpoints=[(np.array([-77.,-26.4,99.]),np.array([-1.,0.,0.])),(bank_point,bank_axis)]
    all_links=[];trials=[]
    for point,axis in endpoints:
        links={};count=0;start=time.monotonic()
        local=np.where(np.all(np.abs(coords-point)<36,axis=1))[0]
        for i in local[np.argsort(np.linalg.norm(coords[local]-point,axis=1))]:
            if time.monotonic()-start>25 or len(links)>=48:break
            for heading in range(6):
                count+=1
                try:parts=ft.biarc(point,axis,coords[i],DIRECTIONS[heading])
                except ValueError:continue
                if ft.min_radius(parts)<12.4:continue
                pts=np.array([p for s in parts for p in ft.samples(s,.5)])
                pts=pts[np.linalg.norm(pts-point,axis=1)>12];ijk=np.rint(pts-origin).astype(int)
                if len(ijk) and (not np.all(ijk>=0) or not np.all(ijk<room.shape) or not np.all(inside[tuple(ijk.T)]&(room[tuple(ijk.T)]>=1))):continue
                if jackets(parts):links[int(i)*6+heading]=parts
        all_links.append(links);trials.append(count)
    starts,ends=all_links;ends={n//6*6+(n%6+3)%6:[ft.reverse(s) for s in reversed(p)] for n,p in ends.items()}
    source=graph.shape[0];goal=source+1;c=graph.tocoo()
    g=coo_matrix((np.r_[c.data,[ft.length(p) for p in starts.values()],[ft.length(p) for p in ends.values()]],
        (np.r_[c.row,np.full(len(starts),source),list(ends)],np.r_[c.col,list(starts),np.full(len(ends),goal)])),shape=(goal+1,goal+1)).tocsr()
    blocked=set();history=[];accepted=None;cache={}
    # Exact-scene gate remains mandatory; global jacket blockers are lazy.
    while starts and ends and time.monotonic()-tick<seconds:
        costs,pred=dijkstra(g,directed=True,indices=source,return_predecessors=True)
        if not np.isfinite(costs[goal]):break
        chain=[goal]
        while chain[-1]!=source:chain.append(int(pred[chain[-1]]));assert chain[-1]>=0
        chain.reverse();parts=[];owners=[]
        for u,v in zip(chain,chain[1:]):
            chunk=starts[v] if u==source else ends[u] if v==goal else [ft.line(coords[u//6],coords[v//6]) if u%6==v%6 else ft.arc(coords[u//6],DIRECTIONS[u%6],coords[v//6])]
            parts.extend(chunk);owners.extend([(u,v)]*len(chunk))
        bad=[]
        for s,e in zip(parts,owners):
            key=json.dumps(s,sort_keys=True)
            if key not in cache:cache[key]=jackets([s])
            if not cache[key]:bad.append(e)
        gap,pair=self_conflict(parts,owners)
        history.append(dict(length_mm=ft.length(parts),self_gap_lower_mm=gap,jacket_blocked=len(bad)))
        if not bad:
            # Preserve a self-conflicting proposal as OPEN, rather than deleting
            # both alternatives and falsely claiming the resource exhausted.
            accepted=dict(parts=parts,edge_owners=owners,radius_mm=1,minimum_R_mm=ft.min_radius(parts),length_mm=ft.length(parts),self_gap_lower_mm=gap);break
        for u,v in set(bad):
            blocked.add((u,v));sl=slice(g.indptr[u],g.indptr[u+1]);j,=np.where(g.indices[sl]==v)[0];g.data[g.indptr[u]+j]=np.inf
    result=dict(status='JOINT_CHANGED_DEPARTURE_PROPOSAL_ACTUAL_MATERIAL_OPEN',accepted=accepted,
        source_and_bank_points=[p.tolist() for p,_ in endpoints],source_and_bank_axes=[a.tolist() for _,a in endpoints],
        link_counts=[len(starts),len(ends)],connection_trials=trials,history=history,blocked_edges=sorted(blocked),
        retained_source_links={str(k):v for k,v in starts.items()},retained_bank_links={str(k):v for k,v in ends.items()},
        all_six_current_middle_jackets_checked=True,
        three_FR_row_sources_CHANGED_first9_seam_and_W009_unchanged=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    dest=OUT/destination;assert not dest.exists();save_json(dest,result)
    print('W033 JOINT GRAPH',result['link_counts'],history[-1:],result['worker_seconds'],flush=True)
    return result
