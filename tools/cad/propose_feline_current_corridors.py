"""Whole123-portions connectivity GUIDES on current signed proposal space.

Not final physical curves: anchor links, minimum bend radii, stock, shared
capacity, full grips and exact BRep checks remain explicit. External head
interfaces are not clamped silently to the torso map or called connected.
"""
import heapq,json,math,time
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt,label
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def astar(mask,start,goal,clearance,seconds=5,maximum=120000,soft_penalty=None):
    shape=mask.shape;ny,nz=shape[1:];stride=ny*nz
    index=lambda p:int(p[0]*stride+p[1]*nz+p[2])
    point=lambda k:(k//stride,(k%stride)//nz,k%nz)
    s,t=index(start),index(goal);flat=mask.reshape(-1);space=clearance.reshape(-1)
    penalty=soft_penalty.reshape(-1) if soft_penalty is not None else None
    assert flat[s] and flat[t]
    estimate=lambda p:sum(abs(a-b) for a,b in zip(p,goal))
    queue=[(estimate(start),0.,s)];g={s:0.};parent={};tick=time.monotonic();count=0
    while queue and count<maximum and time.monotonic()-tick<seconds:
        _,cost,k=heapq.heappop(queue)
        if cost!=g[k]:continue
        count+=1
        if k==t:
            path=[point(k)]
            while k!=s:k=parent[k];path.append(point(k))
            path.reverse();compact=[path[0]]
            for a,b,c in zip(path,path[1:],path[2:]):
                if tuple(y-x for x,y in zip(a,b))!=tuple(y-x for x,y in zip(b,c)):compact.append(b)
            compact.append(path[-1])
            return dict(points=compact,length_mm=len(path)-1,expansions=count,seconds=round(time.monotonic()-tick,3),cost_including_existing_harness_avoidance=cost,weighted_guide_not_proven_shortest=True)
        x,y,z=point(k)
        for good,other in ((x>0,k-stride),(x+1<shape[0],k+stride),(y>0,k-nz),(y+1<ny,k+nz),(z>0,k-1),(z+1<nz,k+1)):
            if not good or not flat[other]:continue
            distance=cost+1+.1/(1+max(0,float(space[other])))+(float(penalty[other]) if penalty is not None else 0)
            if distance>=g.get(other,math.inf):continue
            g[other]=distance;parent[other]=k
            heapq.heappush(queue,(distance+1.04*estimate(point(other)),distance,other))
    return dict(points=[],expansions=count,seconds=round(time.monotonic()-tick,3),bounded_search_not_infeasibility=True)


def main():
    tick=time.monotonic();source=OUT/'n01-current-signed-space.json';p=json.loads(source.read_text())
    assert p['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    field=ROOT/p['field'];assert sha(field)==p['field_sha256'];data=np.load(field,allow_pickle=False)
    origin=data['origin_mm'];step=float(data['grid_mm']);assert step==1
    ends_file=OUT/'n01-shared-routing-boundaries.json';register=json.loads(ends_file.read_text());ends={e['id']:e for e in register['endpoints']}
    spec=OUT/'prefix-allocation.json';bywire={}
    for r in json.loads(spec.read_text())['specifications']:bywire[r['wire']]=max(r['radius'],bywire.get(r['wire'],0))
    dest=OUT/'n01-current-corridor-guides.json';pins={f.relative_to(ROOT).as_posix():sha(f) for f in (source,field,ends_file,spec,Path(__file__))}
    result=dict(status='RUNNING_WHOLE_CORRIDOR_CONNECTIVITY_PROPOSALS',source_sha256=pins,portions={},N01_complete=False,physical_pass=False,
        selected=False,all123_covered_not_all123_routed=True,graph_is_not_a_curve_or_airgap_proof=True)
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    rigid=data['rigid_signed_distance'];motion=data['motion36_signed_distance'];outer=data['outer_distance'];inside=data['inside'];soft=data['harness_signed_distance']
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    factory={r['portion_id'] for r in register['received_factory4MTA_curves']}
    try:
        for radius in (1.05,1.55,2.1):
            free=inside&(rigid>=radius+2.45)&(motion>=radius+2.45)&(outer>=radius+4.45)
            components,_=label(free);nearest=distance_transform_edt(~free,return_distances=False,return_indices=True)
            clearance=np.minimum(rigid,motion)
            soft_penalty=20*np.maximum(0,radius+1.4-soft)
            for portion,ids in register['portions'].items():
                if portion in result['portions']:continue
                if time.monotonic()-tick>235:raise TimeoutError('Completed whole portion guides retained')
                aa,bb=[ends[n] for n in ids];wire=aa['wire']
                r=bywire.get(wire,1.05 if wire.startswith('X') else 1.55);bucket=min((1.05,1.55,2.1),key=lambda k:abs(k-r))
                if bucket!=radius:continue
                row=dict(end_ids=ids,wire=wire,prototype_radius_mm=r,graph_radius_mm=radius,final_bend_radius_stock_and_physical_check_open=True)
                if portion in factory or wire=='W043':row['status']='RECEIVED_COMPLETE_UNCHANGED_CURVE_NOT_REROUTED';result['portions'][portion]=row;continue
                anchors=[]
                for e in (aa,bb):
                    q=np.asarray(e['routing_exit_mm'],float);d=np.asarray(e['routing_exit_axis'],float)
                    if not e.get('routing_boundary_status','').startswith(('RECEIVED_','CURRENT_FULL_','CURRENT_MAIN_')):q=q+9*d
                    cell=np.rint((q-origin)/step).astype(int)
                    if np.any(cell<0) or np.any(cell>=free.shape):
                        anchors.append(dict(end=e['id'],point_mm=q.tolist(),status='EXTERNAL_HEAD_OR_APPENDAGE_ROUTE_NOT_IN_TORSO_FIELD'));continue
                    anchor=nearest[tuple(cell)].astype(int);point=origin+anchor*step
                    anchors.append(dict(end=e['id'],point_mm=q.tolist(),anchor_mm=point.tolist(),cell=anchor.tolist(),
                        component=int(components[tuple(anchor)]),unqualified_anchor_link_mm=float(np.linalg.norm(point-q)),
                        status='NEAREST_FREE_MACRO_ANCHOR_NOT_A_QUALIFIED_SOURCE_EXIT'))
                row['anchors']=anchors
                if any('cell' not in a for a in anchors):row['status']='EXTERNAL_INTERFACE_ROUTE_STILL_OPEN'
                elif anchors[0]['component']!=anchors[1]['component']:row['status']='CURRENT_CONSERVATIVE_FIELD_COMPONENTS_DISCONNECTED_NOT_GEOMETRIC_IMPOSSIBILITY'
                else:
                    path=astar(free,anchors[0]['cell'],anchors[1]['cell'],clearance,soft_penalty=soft_penalty)
                    row['guide']={**path,'points_mm':[(origin+np.asarray(c)*step).tolist() for c in path.pop('points')]}
                    row['status']='CONNECTED_GRID_GUIDE_CURVATURE_AND_EXACT_GATES_OPEN' if row['guide']['points_mm'] else 'BOUNDED_GUIDE_SEARCH_OPEN'
                result['portions'][portion]=row;save()
            del free,components,nearest
        result['status']='ALL123_PORTION_CONNECTIVITY_PROPOSALS_RECORDED' if len(result['portions'])==123 else 'PARTIAL_WHOLE_CORRIDOR_CONNECTIVITY_PROPOSALS'
    except TimeoutError as exc:result.update(status='PARTIAL_WHOLE_CORRIDOR_CONNECTIVITY_PROPOSALS',slice_note=str(exc))
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],portions=len(result['portions']))),flush=True)


if __name__=='__main__':main()
