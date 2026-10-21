"""Only four selected factory leads into the existing finite-radius network.

Planning links, never endpoint/contact acceptance or a new general solver.
Completed source entries are saved after each lead. No native CAD is built.
"""
import math,time,copy
import numpy as np
import FreeCAD as A
from feline_source_saddles import segment
from feline_spatial_csc import spatial_csc
from plan_feline_coupled_rear_power import arc_rows
import feline_tangent_routes as tangent
from plan_feline_tangent_corridor_network import DIRECTIONS
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from receive_feline_underplate_return_gallery import forward


def field_link(rows,free,origin,skip_first=0.,skip_last=0.):
    total=sum(r['length_mm'] for r in rows);distance=0.;points=[]
    for row in rows:
        e=segment(row);count=max(1,math.ceil(e.Length))
        for i,p in enumerate(e.discretize(Number=count+1)):
            s=distance+i*e.Length/count
            if skip_first<=s<=total-skip_last:points.append(list(p))
        distance+=e.Length
    if not points:return False
    ids=np.rint(np.asarray(points)-origin).astype(int)
    return bool(np.all(ids>=0) and np.all(ids<np.array(free.shape)) and free[tuple(ids.T)].all())


def options(p,d,q,t):
    choices=[]
    for ratio in (.125,.25,.5,1.,2.,4.,8.):
        try:
            a=tangent.biarc(p,d,q,t,ratio)
            if tangent.min_radius(a)>=12.4-1e-7:choices.append(arc_rows(a))
        except (ValueError,AssertionError):pass
    try:choices.append(spatial_csc(p,d,q,t))
    except (ValueError,AssertionError):pass
    return sorted(choices,key=lambda rows:sum(r['length_mm'] for r in rows))


def source_entries(sources,heading_trees,free,origin,pins,max_seconds=180,existing_result=None,directional_portals=False,output_name='n01-four-factory-source-network-entries.json'):
    tick=time.monotonic();result=dict(status='FOUR_SOURCE_ENTRY_PROPOSALS_PARTIAL',
        sources={},source_sha256=pins,N01_complete=False,physical_pass=False,
        first8mm_actual_own_interfaces_full_routes_stock_and_capacity_OPEN=True)
    path=OUT/output_name
    if existing_result:
        result=copy.deepcopy(existing_result)
        result['reused_source_rows']=[w for w in result['sources'] if w not in sources]
        result['previous_source_sha256']=result['source_sha256'];result['source_sha256']=pins
    for w,source in sources.items():
        p=np.asarray(source['point_mm'],float);d=np.asarray(source['axis'],float)
        prefix=[]
        if source.get('channel_overrun_mm',0):p=forward(prefix,p,d,source['channel_overrun_mm'])
        links=[];tried=0
        for h,data in enumerate(heading_trees):
            centre=p;excluded=set()
            if directional_portals:
                _,old=data['tree'].query(p,k=min(48,len(data['nodes'])))
                excluded={int(data['nodes'][i]) for i in np.atleast_1d(old)}
                t=DIRECTIONS[h];dot=float(d@t)
                if abs(dot)<1e-7:centre=p+12.4*(d+t)
                elif dot>0:centre=p+24.8*d
                else:
                    normal=np.cross(d,[0,1,0])
                    if np.linalg.norm(normal)<1e-7:normal=np.cross(d,[1,0,0])
                    normal/=np.linalg.norm(normal);centre=p+24.8*normal
            _,indices=data['tree'].query(centre,k=min(48,len(data['nodes'])))
            distances=np.linalg.norm(data['points'][np.atleast_1d(indices)]-p,axis=1)
            for gap,i in zip(np.atleast_1d(distances),np.atleast_1d(indices)):
                if int(data['nodes'][i]) in excluded:continue
                if gap+source['debit_mm']>=220:continue
                q=data['points'][i];best=None;tried+=1
                for middle in options(p,d,q,DIRECTIONS[h]):
                    rows=prefix+middle;length=sum(r['length_mm'] for r in rows)
                    if length+source['debit_mm']>220:continue
                    if field_link(rows,free,origin,skip_first=8.):
                        best=dict(node=int(data['nodes'][i]),heading=h,point_mm=q.tolist(),
                            parts=rows,length_mm=length,remaining_mm=220-source['debit_mm']-length)
                        break
                if best:links.append(best)
                if time.monotonic()-tick>max_seconds:break
            if time.monotonic()-tick>max_seconds:break
        previous=result['sources'].get(w)
        result['sources'][w]=dict(**source,links=links,attempted_node_links=tried,
            previous_family_attempts=previous['attempted_node_links'] if previous else 0,
            directional_portals=directional_portals,previous_nearest48_nodes_excluded=directional_portals,
            status='NETWORK_ENTRIES_PROPOSED_NOT_CONTACT_APPROVAL' if links else 'NO_LINK_IN_THIS_BOUNDED_FAMILY_NOT_INFEASIBILITY')
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(path,result)
        print('FACTORY_SOURCE_ENTRY',w,len(links),tried,result['worker_seconds'],flush=True)
        if time.monotonic()-tick>max_seconds:break
    if len(result['sources'])==4:result['status']='FOUR_SOURCE_NETWORK_ENTRIES_RECORDED_NOT_N01'
    save_json(path,result);return result
