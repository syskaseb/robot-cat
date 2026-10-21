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


def portal_centres(q,d,t,R):
    """Tangent/radius-derived reach, not a moved module or extra straight9."""
    q=np.asarray(q,float);d=np.asarray(d,float);t=np.asarray(t,float)
    c=float(np.clip(d@t,-1,1))
    if c>1-1e-8:return [q+2*R*d]
    if c<-1+1e-8:
        seed=np.eye(3)[int(np.argmin(abs(d)))];b=np.cross(d,seed);b/=np.linalg.norm(b)
        other=np.cross(d,b)
        return [q+2*R*v for v in (b,-b,other,-other)]
    theta=math.acos(c);b=(t-c*d)/math.sin(theta)
    return [q+R*math.sin(theta)*d+R*(1-c)*b,q+R*d]


def local_field_proposal(points,radius,fields,source):
    """Keep FULL curves for exact checking; never waive an actual clearance.

Only a rigid-field hold inside a declared local proposal ball survives.
Motion/outer holds do not. Returned rows are NOT positive field receipts.
"""
    ordinary=field_test(points,radius,fields)
    if ordinary['status']=='POSITIVE_CONSERVATIVE_FIELD_ONLY':return ordinary
    indices=np.rint(points-fields['origin_mm']).astype(int)
    if np.any(indices<0) or np.any(indices>=np.asarray(fields['inside'].shape)):return None
    ix=tuple(indices.T);rigid=fields['rigid_signed_distance'][ix]-radius-2.45
    motion=fields['motion36_signed_distance'][ix]-radius-2.45
    outer=fields['outer_distance'][ix]-radius-4.45
    # Proposal-only extent: wire radius plus the existing field allowances.
    # Its entire curve, INCLUDING this ball, still needs exact solid checks.
    local_radius=radius+2.45+4.
    local=np.linalg.norm(points-source,axis=1)<=local_radius
    if not (fields['inside'][ix].all() and (motion>=0).all() and (outer>=0).all()):return None
    if not np.all((rigid>=0)|local):return None
    return dict(ordinary,status='LOCAL_RIGID_FIELD_HOLD_EXACT_WHOLE_LINK_REQUIRED',
        source_local_proposal_radius_mm=local_radius,skipped_actual_geometry_samples=0,
        actual_clearance_not_relaxed=True,exact_entire_link_NOT_received=True)


def run(rows,profiles,pins,portal_policy='nearest'):
    assert portal_policy in ('nearest','curvature','curvature_local')
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    nf=directory/'current-tangent-resources.json';network=json.loads(nf.read_text())
    assert network['status']=='CURRENT_WHOLE_FINITE_RADIUS_RESOURCES_LINKS_PACKING_OPEN'
    sf=directory/'n01-integrated-signed-space.json';space=json.loads(sf.read_text())
    fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        fields={k:f[k].copy() for k in ['origin_mm','inside','rigid_signed_distance','motion36_signed_distance','outer_distance']}
    sourcepins={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in
        (nf,sf,fp,Path(__file__),ROOT/'tools/cad/feline_tangent_routes.py',ROOT/'tools/cad/check_feline_current_corridor_links.py')}}
    dest=directory/({'nearest':'current-curved-source-links.json','curvature':'current-curvature-portal-links.json',
                    'curvature_local':'current-local-exact-link-proposals.json'}[portal_policy])
    result=dict(status='RUNNING_CURRENT_CURVED_SOURCE_LINKS',source_sha256=sourcepins,ends={},
        N01_complete=False,selected=False,physical_pass=False,
        actual_BRep_shared_packing_assembly_OPEN=True,whole_portions_NOT_replanned=True,
        portal_policy=portal_policy,no_extra9_or_new_source_pose=True)
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
                radius_mm=radius,minimum_R_mm=minimum,resource_class=key,math_candidates=0,
                field_positive=[],near_source_exact_required=[])
            if np.any(q<origin) or np.any(q>origin+np.array(fields['inside'].shape)-1):
                record['status']='EXTERNAL_DOMAIN_NOT_CLAMPED';result['ends'][e['id']]=record;continue
            # Both ends are linked OUTWARD. Reverse the receiving link when
            # assembling a full path; never silently reverse its source axis.
            for h,t in enumerate(DIRECTIONS):
                tree=trees[key][h]
                centres=[q] if portal_policy=='nearest' else portal_centres(q,d,t,network['classes'][key]['bend_mm'])
                candidates={}
                for centre in centres:
                    _,indices=tree['tree'].query(centre,k=min(64,len(tree['points'])))
                    for i in np.atleast_1d(indices):candidates[int(i)]=float(np.linalg.norm(tree['points'][i]-q))
                ranked=sorted(candidates,key=candidates.get)
                distance=[candidates[i] for i in ranked];index=ranked
                for dist,i in zip(np.atleast_1d(distance),np.atleast_1d(index)):
                    if dist>64:continue
                    target=tree['points'][i]
                    try:parts=biarc(q,d,target,t)
                    except ValueError:continue
                    R=min_radius(parts)
                    if R<minimum-1e-6:continue
                    record['math_candidates']+=1
                    points=np.asarray([v for s in parts for v in samples(s,.5)])
                    field=local_field_proposal(points,radius,fields,q) if portal_policy=='curvature_local' else field_test(points,radius,fields)
                    if field is None:continue
                    if field['status'] not in ('POSITIVE_CONSERVATIVE_FIELD_ONLY','LOCAL_RIGID_FIELD_HOLD_EXACT_WHOLE_LINK_REQUIRED'):continue
                    bucket='field_positive' if field['status']=='POSITIVE_CONSERVATIVE_FIELD_ONLY' else 'near_source_exact_required'
                    record[bucket].append(dict(parts=parts,length_mm=length(parts),minimum_constructed_R_mm=R if math.isfinite(R) else None,
                        node=int(tree['nodes'][i]),component=int(tree['component'][i]),heading=h,field=field))
                    break
            record['field_positive'].sort(key=lambda r:r['length_mm'])
            record['near_source_exact_required'].sort(key=lambda r:r['length_mm'])
            record['status']='ACTUAL_CURVED_LINKS_POSITIVE_FIELD_NOT_BREP_OR_PACKING' if record['field_positive'] else 'FULL_LOCAL_LINK_PROPOSAL_REQUIRES_EXACT_GEOMETRY' if record['near_source_exact_required'] else 'THIS_RESOURCE_LINK_DOMAIN_OPEN_NOT_INFEASIBILITY'
            result['ends'][e['id']]=record
        save()
        if time.monotonic()-tick>225:break
    result['status']='CURRENT246_CURVED_SOURCE_LINK_DOMAINS_RECORDED_NOT_N01' if len(result['ends'])==246 else 'PARTIAL_CURRENT_CURVED_SOURCE_LINK_DOMAINS'
    save();return result
