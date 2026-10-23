"""One changed pair on the saved corridor graph; no placement catalogue.

Output is a proposal only. Exact solids, changed caps, all interfaces and
assembly still require receipt. Store connector state compressed for reuse.
"""
import gzip,json,time
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz,coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
import feline_tangent_routes as ft
from plan_feline_tangent_corridor_network import DIRECTIONS
from plan_feline_current_joint_tangent_space import available_room
from solve_feline_W047_simple_graph import self_conflict
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def run(endpoints,jackets,stem,extra_pins,seconds=90):
    tick=time.monotonic();dest=OUT/(stem+'.json');assert not dest.exists()
    rf=OUT/'W009-W069-harness-corridor/resource.json';resource=json.loads(rf.read_text())
    spec=resource['network']['classes']['1.55-R16'];gf=ROOT/spec['graph'];nf=ROOT/spec['nodes']
    assert sha(gf)==spec['graph_sha256'] and sha(nf)==spec['nodes_sha256']
    graph=load_npz(gf).tocsr()
    with np.load(nf,allow_pickle=False) as f:coords=f['origin_mm']+float(f['step_mm'])*np.argwhere(f['ids']>=0)
    ff=OUT/'joint-corridor-space-20261021/n01-integrated-signed-space.json';fm=json.loads(ff.read_text());fp=ROOT/fm['field'];assert sha(fp)==fm['field_sha256']
    with np.load(fp,allow_pickle=False) as f:origin=f['origin_mm'].copy();room=available_room(f);inside=f['inside'].copy()
    trees=[(cKDTree(np.array([p for s in parts for p in ft.samples(s,.25)])),radius) for parts,radius in jackets]
    def clear(parts):
        pts=np.array([p for s in parts for p in ft.samples(s,.25)])
        return all(float(t.query(pts)[0].min())-.25-1-r>=.2 for t,r in trees)
    all_links=[]
    for point,axis in endpoints:
        point=np.array(point);links={};start=time.monotonic()
        local=np.where(np.all(np.abs(coords-point)<36,axis=1))[0]
        for i in local[np.argsort(np.linalg.norm(coords[local]-point,axis=1))]:
            if time.monotonic()-start>25 or len(links)>=48:break
            for heading in range(6):
                try:parts=ft.biarc(point,axis,coords[i],DIRECTIONS[heading])
                except ValueError:continue
                if ft.min_radius(parts)<12.4 or not clear(parts):continue
                pts=np.array([p for s in parts for p in ft.samples(s,.5)])
                pts=pts[np.linalg.norm(pts-point,axis=1)>12];ijk=np.rint(pts-origin).astype(int)
                if len(ijk) and (not np.all(ijk>=0) or not np.all(ijk<room.shape) or not np.all(inside[tuple(ijk.T)]&(room[tuple(ijk.T)]>=1))):continue
                links[int(i)*6+heading]=parts
        all_links.append(links)
    starts,ends=all_links;ends={n//6*6+(n%6+3)%6:[ft.reverse(s) for s in reversed(p)] for n,p in ends.items()}
    source=graph.shape[0];goal=source+1;c=graph.tocoo()
    g=coo_matrix((np.r_[c.data,[ft.length(p) for p in starts.values()],[ft.length(p) for p in ends.values()]],
        (np.r_[c.row,np.full(len(starts),source),list(ends)],np.r_[c.col,list(starts),np.full(len(ends),goal)])),shape=(goal+1,goal+1)).tocsr()
    blocked=set();cache={};accepted=None
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
            if key not in cache:cache[key]=clear([s])
            if not cache[key]:bad.append(e)
        if not bad:
            gap,pair=self_conflict(parts,owners)
            accepted=dict(parts=parts,edge_owners=owners,self_gap_lower_mm=gap,self_conflict_edges=pair,length_mm=ft.length(parts),minimum_R_mm=ft.min_radius(parts));break
        for u,v in set(bad):
            blocked.add((u,v));sl=slice(g.indptr[u],g.indptr[u+1]);j,=np.where(g.indices[sl]==v)[0];g.data[g.indptr[u]+j]=np.inf
    state=dict(source_links=starts,bank_links=ends,blocked_edges=sorted(blocked),endpoints=endpoints)
    archive=dest.with_suffix('.links.json.gz');assert not archive.exists()
    with gzip.open(archive,'wt',encoding='utf8') as f:json.dump(state,f,separators=(',',':'))
    result=dict(status='CHANGED_PAIR_PROPOSAL_ACTUAL_WORLD_OPEN',accepted=accepted,link_counts=[len(starts),len(ends)],
        retained_state=archive.relative_to(ROOT).as_posix(),retained_state_sha256=sha(archive),
        source_sha256={**extra_pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (rf,gf,nf,ff,fp,Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    save_json(dest,result);print(stem,result['link_counts'],None if accepted is None else (accepted['length_mm'],accepted['self_gap_lower_mm']),result['worker_seconds'],flush=True)
    return result
