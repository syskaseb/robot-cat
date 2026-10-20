"""Current whole topology/123 interfaces; bulky machine rows stay compressed."""
import gzip,json,math,os,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import save_npz
from scipy.sparse.csgraph import connected_components
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from build_feline_retention_space_delta import load_fields
from plan_feline_tangent_corridor_network import transitions,DIRECTIONS
from compose_feline_integrated_boundaries import apply_updates


def main():
    tick=time.monotonic();fields,space=load_fields();origin=fields['origin_mm']
    sf=OUT/'n01-retention-space-delta.json';ef=OUT/'n01-shared-routing-boundaries.json'
    uf=OUT/'n01-integrated-upper-boundary-overlay.json';rf=OUT/'n01-current-retention-layout-overlay.json'
    reg=json.loads(ef.read_text());upper=json.loads(uf.read_text());retention=json.loads(rf.read_text())
    assert upper['parent_sha256']==sha(ef) and retention['base_sha256']==sha(ef) and retention['upper_sha256']==sha(uf)
    endpoints=apply_updates(apply_updates(reg['endpoints'],upper['updates']),retention['updates']);ends={e['id']:e for e in endpoints}
    assert len(ends)==246 and len(reg['portions'])==123
    room=np.minimum(fields['rigid_signed_distance']-2.45,fields['motion36_signed_distance']-2.45)
    room=np.minimum(room,fields['outer_distance']-4.45);inside=fields['inside']
    af=OUT/'n01-flat-station-architecture.json';pf=OUT/'prefix-allocation.json';lf=OUT/'n01-full-lower-bay-plan-r3.json'
    radii={};minimum={}
    for station in json.loads(af.read_text())['stations']:
        for e in station['ports']:
            radii[e['wire']]=max(radii.get(e['wire'],0),e['radius_mm']);minimum[e['wire']]=max(minimum.get(e['wire'],0),e['minimum_project_R_mm'])
    for e in json.loads(pf.read_text())['specifications']:radii[e['wire']]=max(radii.get(e['wire'],0),e['radius'])
    for e in endpoints:
        if e.get('radius_from_current_source_cap_mm'):radii[e['wire']]=max(radii.get(e['wire'],0),e['radius_from_current_source_cap_mm'])
    custom={r['id']:r for r in json.loads(lf.read_text())['custom_ends']}
    sources=[sf,ROOT/space['field'],ROOT/space['inherited_fields'],ef,uf,rf,af,pf,lf,Path(__file__),ROOT/'tools/cad/plan_feline_tangent_corridor_network.py']
    dest=OUT/'n01-current-corridor-topology.json';pins={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    result=dict(status='RUNNING_CURRENT_SHARED_CORRIDOR_TOPOLOGY',source_sha256=pins,classes={},N01_complete=False,selected=False,physical_pass=False)
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    classes=((2.1,16),(4.,16),(6.,16),(3.5,28),(2.1,28))
    for radius,bend in classes:
        key=str(radius)+'-R'+str(bend)
        if key in result['classes']:continue
        ids,graph=transitions(inside&(room>=radius),bend);count,comp=connected_components(graph,directed=True,connection='strong')
        sizes=np.bincount(comp);gf=OUT/('n01-current-corridor-'+key+'.graph.npz');nf=OUT/('n01-current-corridor-'+key+'.nodes.npz')
        save_npz(gf,graph);np.savez_compressed(nf,ids=ids,component=comp,origin_mm=origin,step_mm=4)
        result['classes'][key]=dict(radius_mm=radius,bend_mm=bend,states=graph.shape[0],primitives=graph.nnz,strong_components=count,
            largest_states=int(sizes.max()),graph=gf.relative_to(ROOT).as_posix(),graph_sha256=sha(gf),nodes=nf.relative_to(ROOT).as_posix(),nodes_sha256=sha(nf))
        save();print('Current tangent class',key,flush=True)
    trees={}
    for key in ('2.1-R16','2.1-R28','3.5-R28'):
        f=ROOT/result['classes'][key]['nodes'];assert sha(f)==result['classes'][key]['nodes_sha256']
        with np.load(f,allow_pickle=False) as a:ids=a['ids'];comp=a['component'];step=int(a['step_mm'])
        cells=np.argwhere(ids>=0);base=ids[tuple(cells.T)];points=origin+step*cells;counts=np.bincount(comp);hh=[]
        for h in range(6):
            cc=comp[base*6+h];keep=counts[cc]>=100;assert keep.any(),key
            hh.append(dict(tree=cKDTree(points[keep]),points=points[keep],component=cc[keep]))
        trees[key]=dict(headings=hh,high=origin+(np.asarray(ids.shape)-1)*step)
    factory={r['portion_id'] for r in reg['received_factory4MTA_curves']};assignments={}
    for name,ee in reg['portions'].items():
        wire=ends[ee[0]]['wire']
        if name in factory or wire=='W043':assignments[name]=dict(status='RECEIVED_COMPLETE_UNCHANGED_CURVE');continue
        radius=radii.get(wire,1.05 if wire.startswith('X') else 1.55)
        bend=max([minimum.get(wire,12.4)]+[float(ends[e].get('minimum_R_mm') or 0) for e in ee])
        key=('2.1-R16' if bend<=16 else '2.1-R28') if radius<=2.1 else '3.5-R28';assert radius<=3.5 and bend<=28,(name,radius,bend)
        data=trees[key];candidates=[];actual=[]
        for side,end_id in enumerate(ee):
            e=ends[end_id];q=np.asarray(e['routing_exit_mm'],float);d=np.asarray(e['routing_exit_axis'],float);d/=np.linalg.norm(d)
            if end_id in custom:
                c=custom[end_id];assert np.linalg.norm(q-c['point_mm'])<1e-5;q=q+float(c['prefix_mm'])*d
            actual.append(dict(id=end_id,point_mm=q.tolist(),outward_axis=d.tolist()))
            if np.any(q<origin) or np.any(q>data['high']):candidates.append({});continue
            direction=d if side==0 else -d;h=int(np.argmax(DIRECTIONS@direction));tree=data['headings'][h]
            distances,index=tree['tree'].query(q,k=min(64,len(tree['points'])));cc={}
            for distance,i in zip(np.atleast_1d(distances),np.atleast_1d(index)):
                component=int(tree['component'][i])
                if component not in cc:cc[component]=dict(anchor_mm=tree['points'][i].tolist(),unqualified_link_mm=float(distance),
                    heading=DIRECTIONS[h].tolist(),tangent_change_deg=math.degrees(math.acos(float(np.clip(DIRECTIONS[h]@direction,-1,1)))))
            candidates.append(cc)
        common=set(candidates[0])&set(candidates[1]);row=dict(ends=actual,radius_mm=radius,minimum_R_mm=bend,corridor_class=key,
            project_dimensions_not_supplier_guaranteed=True,radius_fallback_without_station_or_prefix_spec=wire not in radii)
        if common:
            c=min(common,key=lambda c:sum(v[c]['unqualified_link_mm'] for v in candidates));row.update(status='COMMON_TANGENT_REGION_ACTUAL_LINKS_PACKING_OPEN',component=c,anchors=[v[c] for v in candidates])
        else:row['status']='EXTERNAL_OR_NO_COMMON_NEAREST_COMPONENT_NOT_INFEASIBILITY'
        assignments[name]=row
    rowsfile=OUT/'n01-current-corridor-assignments.json.gz';raw=json.dumps(assignments,separators=(',',':')).encode()
    rowsfile.write_bytes(gzip.compress(raw,mtime=0));counts={s:sum(r['status']==s for r in assignments.values()) for s in sorted({r['status'] for r in assignments.values()})}
    links=[a['unqualified_link_mm'] for r in assignments.values() for a in r.get('anchors',[])]
    result.update(status='CURRENT_WHOLE123_TANGENT_REGIONS_RECEIVED_LINKS_PACKING_OPEN',ordinary_portions=123,ordinary_ends=246,
        summary=counts,assignments=rowsfile.relative_to(ROOT).as_posix(),assignments_sha256=sha(rowsfile),largest_unqualified_link_mm=max(links),
        whole_bought_USB_retained=True,balance4tap_separate_unassigned_pinout_unchanged=True,
        source_links_packed_turns_other_roots_head_sweeps_and_installation_still_OPEN=True)
    save();print(json.dumps(dict(status=result['status'],summary=counts,max_link=max(links),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
