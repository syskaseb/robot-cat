"""Actual curved links from current boundaries into existing tangent resources.

No moved modules, nearest-node acceptance or default wire sizes. A positive
field is conservative planning evidence only; whole BRep, packing and
assembly still require receipt. A field hold is not physical infeasibility.
"""
import json,math,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_tangent_routes import biarc,samples,length,min_radius
from plan_feline_tangent_corridor_network import DIRECTIONS
from check_feline_current_corridor_links import field_test


def run(rows,profiles,pins):
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    nf=directory/'current-tangent-resources.json';network=json.loads(nf.read_text())
    assert network['status']=='CURRENT_WHOLE_FINITE_RADIUS_RESOURCES_LINKS_PACKING_OPEN'
    sf=directory/'n01-integrated-signed-space.json';space=json.loads(sf.read_text())
    fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        fields={k:f[k].copy() for k in ['origin_mm','inside','rigid_signed_distance','motion36_signed_distance','outer_distance']}
    sourcepins={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in
        (nf,sf,fp,Path(__file__),ROOT/'tools/cad/feline_tangent_routes.py',ROOT/'tools/cad/check_feline_current_corridor_links.py')}}
    dest=directory/'current-curved-source-links.json'
    result=dict(status='RUNNING_CURRENT_CURVED_SOURCE_LINKS',source_sha256=sourcepins,ends={},
        N01_complete=False,selected=False,physical_pass=False,
        actual_BRep_shared_packing_assembly_OPEN=True,whole_portions_NOT_replanned=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==sourcepins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    trees={}
    for key in ('1.55-R16','2.1-R28'):
        spec=network['classes'][key];p=ROOT/spec['nodes'];assert sha(p)==spec['nodes_sha256']
        with np.load(p,allow_pickle=False) as a:
            ids=a['ids'];comp=a['component'];origin=a['origin_mm'];step=float(a['step_mm'])
        cells=np.argwhere(ids>=0);base=ids[tuple(cells.T)];points=origin+step*cells
        sizes=np.bincount(comp);headings=[]
        for h in range(6):
            keep=sizes[comp[base*6+h]]>=100
            headings.append(dict(points=points[keep],nodes=base[keep]*6+h,
                component=comp[base[keep]*6+h],tree=cKDTree(points[keep])))
        trees[key]=headings
    byportion={}
    for e in rows:byportion.setdefault(e['portion_id'],[]).append(e)
    assert len(rows)==246 and len(byportion)==123
    for pid,ee in byportion.items():
        if all(e.get('full_middle_route_accepted') or e.get('complete_factory_curve_reused') for e in ee):
            for e in ee:result['ends'].setdefault(e['id'],dict(status='WHOLE_RECEIVED_PORTION_NOT_RELINKED'))
            continue
        spec=profiles[pid];radius=spec['project_radius_mm'];minimum=spec['minimum_project_R_mm']
        key='1.55-R16' if radius<=1.55+1e-9 and minimum<=16 else '2.1-R28'
        assert radius<=network['classes'][key]['radius_mm']+1e-9 and minimum<=network['classes'][key]['bend_mm']
        for e in ee:
            if e['id'] in result['ends']:continue
            q=e['routing_exit_mm'];d=e['routing_exit_axis']
            if q is None or d is None:
                result['ends'][e['id']]=dict(status='INTERNAL_POSITION_NOT_INVENTED');continue
            q=np.asarray(q);d=np.asarray(d);record=dict(portion=pid,point_mm=q.tolist(),outward_axis=d.tolist(),
                radius_mm=radius,minimum_R_mm=minimum,resource_class=key,math_candidates=0,field_positive=[])
            if np.any(q<origin) or np.any(q>origin+np.array(fields['inside'].shape)-1):
                record['status']='EXTERNAL_DOMAIN_NOT_CLAMPED';result['ends'][e['id']]=record;continue
            # Both ends are linked OUTWARD. Reverse the receiving link when
            # assembling a full path; never silently reverse its source axis.
            for h,t in enumerate(DIRECTIONS):
                tree=trees[key][h];distance,index=tree['tree'].query(q,k=min(64,len(tree['points'])))
                for dist,i in zip(np.atleast_1d(distance),np.atleast_1d(index)):
                    if dist>64:continue
                    target=tree['points'][i]
                    try:parts=biarc(q,d,target,t)
                    except ValueError:continue
                    R=min_radius(parts)
                    if R<minimum-1e-6:continue
                    record['math_candidates']+=1
                    points=np.asarray([v for s in parts for v in samples(s,.5)])
                    field=field_test(points,radius,fields)
                    if field['status']!='POSITIVE_CONSERVATIVE_FIELD_ONLY':continue
                    record['field_positive'].append(dict(parts=parts,length_mm=length(parts),minimum_constructed_R_mm=R if math.isfinite(R) else None,
                        node=int(tree['nodes'][i]),component=int(tree['component'][i]),heading=h,field=field))
                    break
            record['field_positive'].sort(key=lambda r:r['length_mm'])
            record['status']='ACTUAL_CURVED_LINKS_POSITIVE_FIELD_NOT_BREP_OR_PACKING' if record['field_positive'] else 'THIS_RESOURCE_LINK_DOMAIN_OPEN_NOT_INFEASIBILITY'
            result['ends'][e['id']]=record
        save()
        if time.monotonic()-tick>225:break
    result['status']='CURRENT246_CURVED_SOURCE_LINK_DOMAINS_RECORDED_NOT_N01' if len(result['ends'])==246 else 'PARTIAL_CURRENT_CURVED_SOURCE_LINK_DOMAINS'
    save();return result
