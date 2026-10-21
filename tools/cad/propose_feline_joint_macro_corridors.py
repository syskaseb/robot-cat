"""Apply the existing sparse graph to CURRENT246 ends and typed123 portions.

Closed portions are referenced, not rerouted. Old positive guides survive
only exact current endpoint matching AND all-current1mm-cell checks. These
are macro proposals, never bend/anchor/shared-capacity or N01 approval.
"""
import copy,json,time
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.sparse.csgraph import connected_components,dijkstra
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from propose_feline_sparse_corridors import grid_graph,guide_cells_clear
from propose_feline_current_corridors import radius_bucket,nearest_cell


def run(rows,profiles,pins):
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    sf=directory/'n01-integrated-signed-space.json';space=json.loads(sf.read_text())
    assert space['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    ends={r['id']:r for r in rows};tasks={}
    for r in rows:tasks.setdefault(r['portion_id'],[]).append(r['id'])
    assert len(rows)==246 and len(tasks)==123 and all(len(v)==2 for v in tasks.values())
    assert set(tasks)<=set(profiles)
    oldfile=OUT/'n01-integrated-sparse-corridor-guides.json';old=json.loads(oldfile.read_text())
    sourcepins={**pins,sf.relative_to(ROOT).as_posix():sha(sf),fp.relative_to(ROOT).as_posix():sha(fp),
        oldfile.relative_to(ROOT).as_posix():sha(oldfile),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
        'tools/cad/propose_feline_sparse_corridors.py':sha(ROOT/'tools/cad/propose_feline_sparse_corridors.py')}
    dest=directory/'current123-macro-corridors.json'
    result=dict(status='RUNNING_CURRENT123_MACRO_CORRIDORS',source_sha256=sourcepins,portions={},classes={},
        fixed_total_portions=123,ordinary_ends=246,N01_complete=False,physical_pass=False,selected=False,
        full_source_links_curvature_shared_capacity_roots_assembly_OPEN=True,
        no_external_or_None_end_clamped_to_body=True,no_extra9_added_to_current_boundaries=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==sourcepins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    # First classify all ordinary portions. Do not spend graph time on
    # factory/body curves already received or invent internal pin positions.
    for pid,ids in tasks.items():
        if pid in result['portions']:continue
        pair=[ends[n] for n in ids];r=profiles[pid]['project_radius_mm']
        row=dict(end_ids=ids,wire=pair[0]['wire'],project_radius_mm=r,
                 minimum_project_R_mm=profiles[pid]['minimum_project_R_mm'])
        if all(e.get('full_middle_route_accepted') for e in pair):
            row.update(status='CURRENT_WHOLE_PORTION_RECEIVED_NOT_REROUTED',receipts=sorted({e.get('whole_portion_receipt') or e.get('current_restraint_receipt') or 'retained_current_receipt' for e in pair}))
        elif all(e.get('complete_factory_curve_reused') for e in pair):
            row.update(status='CURRENT_WHOLE_FACTORY_SUBASSEMBLY_RECEIVED_NOT_REROUTED')
        elif any(e.get('routing_exit_mm') is None or e.get('routing_exit_axis') is None for e in pair):
            row.update(status='INTERNAL_ACCOUNTING_POSITION_NOT_INVENTED_WHOLE_UNIT_GATE_OPEN')
        else:continue
        result['portions'][pid]=row
    save()
    with np.load(fp,allow_pickle=False) as data:
        assert float(data['grid_mm'])==1.
        origin=data['origin_mm'].copy();rigid=data['rigid_signed_distance'];motion=data['motion36_signed_distance']
        outer=data['outer_distance'];inside=data['inside'];soft=data['harness_signed_distance']
    try:
        for radius in sorted({radius_bucket(profiles[p]['project_radius_mm']) for p in tasks if p not in result['portions']}):
            if time.monotonic()-tick>235:raise TimeoutError('Whole completed macro proposals retained')
            pending=[p for p in tasks if p not in result['portions'] and radius_bucket(profiles[p]['project_radius_mm'])==radius]
            if not pending:continue
            free=inside&(rigid>=radius+2.45)&(motion>=radius+2.45)&(outer>=radius+4.45)
            for pid in pending[:]:
                previous=old['portions'].get(pid,{});points=previous.get('guide',{}).get('points_mm')
                anchors=previous.get('anchors',[]);pair=[ends[n] for n in tasks[pid]]
                if not points or len(anchors)!=2:continue
                if not all(np.allclose(e['routing_exit_mm'],a.get('point_mm'),atol=1e-7,rtol=0) for e,a in zip(pair,anchors)):continue
                if not guide_cells_clear(points,origin,free):continue
                result['portions'][pid]=dict(copy.deepcopy(previous),status='UNCHANGED_POSITIVE_GUIDE_RECHECKED_IN_CURRENT_CELLS_NOT_N01',
                    current_project_radius_mm=profiles[pid]['project_radius_mm'],current_minimum_R_mm=profiles[pid]['minimum_project_R_mm'],
                    inherited_anchor_links_remain_UNQUALIFIED=True)
                pending.remove(pid)
            if not pending:save();continue
            ids,graph=grid_graph(free,(3*np.maximum(0,radius+1.4-soft)).astype(np.float32))
            coarse=ids>=0
            if not graph.shape[0]:
                for pid in pending:result['portions'][pid]=dict(status='CONSERVATIVE_GRAPH_EMPTY_NOT_GEOMETRY_IMPOSSIBILITY',end_ids=tasks[pid])
                save();continue
            count,components=connected_components(graph,directed=False);population=np.bincount(components)
            main=np.zeros(coarse.shape,bool);main[coarse]=components==int(population.argmax())
            nearest=distance_transform_edt(~main,return_distances=False,return_indices=True);lookup=np.argwhere(coarse)
            result['classes'][str(radius)]=dict(nodes=graph.shape[0],edges=graph.nnz,components=count,
                source_link_to_main_component_NOT_qualified=True)
            cache_start=None;dist=pred=None;save()
            for pid in pending:
                if time.monotonic()-tick>235:raise TimeoutError('Whole completed macro proposals retained')
                pair=[ends[n] for n in tasks[pid]];anchors=[]
                for e in pair:
                    q=np.array(e['routing_exit_mm']);axis=np.array(e['routing_exit_axis'])
                    assert q.shape==axis.shape==(3,) and np.isfinite(q).all() and abs(np.linalg.norm(axis)-1)<1e-6
                    local=q-origin
                    if np.any(local<0) or np.any(local>np.array(free.shape)-1):
                        anchors.append(dict(end_id=e['id'],point_mm=q.tolist(),status='EXTERNAL_HEAD_OR_APPENDAGE_NOT_CLAMPED_TO_BODY'));continue
                    cell=nearest_cell(nearest,np.rint(local/2).astype(int));point=origin+2*cell;node=int(ids[tuple(cell)])
                    anchors.append(dict(end_id=e['id'],point_mm=q.tolist(),departure_axis=axis.tolist(),anchor_mm=point.tolist(),node=node,
                        link_length_mm=float(np.linalg.norm(q-point)),status='PROPOSED_ANCHOR_LINK_NOT_CURVATURE_OR_AIRGAP_PROOF'))
                row=dict(end_ids=tasks[pid],wire=pair[0]['wire'],anchors=anchors,project_radius_mm=profiles[pid]['project_radius_mm'],
                         minimum_project_R_mm=profiles[pid]['minimum_project_R_mm'],graph_radius_mm=radius)
                if any('node' not in a for a in anchors):row['status']='APPENDAGE_DOMAIN_PLAN_OPEN_NOT_A_BODY_ROUTE'
                else:
                    start,goal=[a['node'] for a in anchors]
                    if start!=cache_start:dist,pred=dijkstra(graph,directed=False,indices=start,return_predecessors=True);cache_start=start
                    assert np.isfinite(dist[goal]);nodes=[goal]
                    while nodes[-1]!=start:
                        previous=int(pred[nodes[-1]]);assert previous>=0 and len(nodes)<graph.shape[0];nodes.append(previous)
                    points=lookup[nodes[::-1]];compact=[points[0]]
                    for a,b,c in zip(points,points[1:],points[2:]):
                        if not np.array_equal(b-a,c-b):compact.append(b)
                    compact.append(points[-1]);row.update(status='CURRENT_SPARSE_MACRO_GUIDE_NOT_N01',
                        guide=dict(points_mm=(origin+2*np.array(compact)).tolist(),length_mm=2*(len(nodes)-1),
                                   not_a_bend_or_shared_capacity_proof=True))
                result['portions'][pid]=row;save()
                if len(result['portions'])%10==0:print('CURRENT123_PROPOSALS',len(result['portions']),'/123',flush=True)
        assert len(result['portions'])==123
        result['status']='CURRENT123_MACRO_CLASSIFICATION_AND_GUIDES_RECORDED_NOT_N01'
    except TimeoutError as e:result.update(status='PARTIAL_CURRENT123_MACRO_GUIDES',slice_note=str(e))
    save();print('CURRENT123_RESULT',result['status'],len(result['portions']),result['worker_seconds'],flush=True)
    return result
