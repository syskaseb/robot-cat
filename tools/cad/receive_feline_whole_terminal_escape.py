"""Whole246-terminal NECESSITY screen, before more routing/detail CAD.

Six analytic axial sections per verified cap; no new curve/pose search.
Reuse received cap identities and the two received bottleneck certificates.
A non-rejection is NOT a feasible route, packing or N01 acceptance.
"""
import collections,gzip,json,os,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_output_composed_context import compose
from compose_feline_output_boundaries import current,cap_at
from feline_selected_material_contract import load as profiles
from feline_common_space_context import is_jacket
from reconcile_feline_source_portal_contracts import own_channel
from feline_terminal_escape import bound


def main():
    tick=time.monotonic();base,ends,files=current();contract,pf,bf=profiles()
    cf=OUT/'n01-current-source-cap-profiles.json';caps=json.loads(cf.read_text())
    af=OUT/'n01-curvature-source-portals.json';old=json.loads(af.read_text());raw=ROOT/old['rows'];assert sha(raw)==old['rows_sha256']
    old_ends=json.loads(gzip.decompress(raw.read_bytes()))
    sf=OUT/'n01-terminal-escape-bottlenecks.json';seed=json.loads(sf.read_text())
    for p,h in seed['source_sha256'].items():assert sha(ROOT/p)==h,p
    context=compose();world,parts,meta,pins,docs=context
    changed=docs['output_changed']|docs['corrected_profile_actor_names']
    complete={r['portion_id'] for r in base['received_factory4MTA_curves']}
    complete|={e['portion_id'] for e in ends if e['wire']=='W043'}
    sources=(*files,pf,bf,cf,af,raw,sf,Path(__file__),ROOT/'tools/cad/feline_terminal_escape.py',ROOT/'tools/cad/reconcile_feline_source_portal_contracts.py',ROOT/'tools/cad/feline_selected_material_contract.py')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    dest=OUT/'n01-whole-terminal-escape.json';rowsfile=dest.with_suffix('.rows.json.gz')
    result=dict(status='RUNNING_WHOLE_TERMINAL_NECESSITY_SCREEN',source_sha256=pins,queries=0,N01_complete=False,selected=False,physical_pass=False,
        no_rejection_is_not_route_approval=True,soft_stock_other_jackets_motion_and_assembly_NOT_qualified=True)
    rows={}
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(rowsfile)==result['rows_sha256'];rows=json.loads(gzip.decompress(rowsfile.read_bytes()))
    def save():
        rowsfile.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
        result.update(rows=rowsfile.relative_to(ROOT).as_posix(),rows_sha256=sha(rowsfile),completed=len(rows),
            summary=dict(collections.Counter(r['status'] for r in rows.values())),worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    # Bounds are only a safe query filter. Every negative certificate below
    # uses valid actual closed material and its signed boundary distance.
    boxes={n:np.array([[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]]) for n,s in parts.items()}
    jackets=[n for n,s in parts.items() if s.Solids and is_jacket(n,meta[n])]
    def soft(n):
        r=meta[n]
        return r.get('kind') in ('tie_reservation','project_stock_reservation','head_budget','band_budget') or r.get('material_role')=='selected_T18I_nylon_budget'
    rigid=[n for n,s in parts.items() if s.Solids and not is_jacket(n,meta[n]) and not soft(n)]
    if world.bus['name'] in rigid:
        bb=world.bus['original'].BoundBox;tf=docs['inverse'].inverse();points=np.array([list(tf.multVec(bb.getPoint(i))) for i in range(8)])
        boxes[world.bus['name']]=np.array([points.min(0),points.max(0)])
    bounds=np.asarray([boxes[n] for n in rigid]);surface={};valid={}
    seeded={r['endpoint']:r for r in seed['rows'] if r['no_admissible_clearance_path']}
    for e in ends:
        name=e['id']
        if name in rows:continue
        if e['portion_id'] in complete:rows[name]=dict(status='RECEIVED_COMPLETE_PORTION_NO_NEW_MIDDLE');save();continue
        profile=contract['portions'][e['portion_id']];R=profile.get('minimum_project_R_mm');radius=profile.get('project_radius_mm')
        if not R or not radius or e.get('routing_exit_mm') is None or e.get('routing_exit_axis') is None:
            rows[name]=dict(status='SOURCE_CONTRACT_OPEN_NO_CERTIFICATE');save();continue
        q=np.asarray(e['routing_exit_mm'],float);d=np.asarray(e['routing_exit_axis'],float);d/=np.linalg.norm(d)
        if name in seeded:
            r=seeded[name];assert np.linalg.norm(q-r['current_actual_cap_mm'])<1e-5 and np.linalg.norm(d-r['outward_axis'])<1e-5
            assert abs(R-r['minimum_project_R_mm'])<1e-6 and abs(radius-r['jacket_radius_mm'])<1e-6
            rows[name]=dict(status='PROVEN_TERMINAL_BLOCK_REUSED',blocks=[r],seed_receipt_sha256=sha(sf));save();continue
        matches=[];previous=old_ends.get(name);old_cap=caps['rows'].get(name,{})
        if previous and np.linalg.norm(q-previous['source']['point_mm'])<1e-5 and np.linalg.norm(d-previous['source']['outward_axis'])<1e-5:
            matches=[r['owner'] for r in old_cap.get('cap_matches',[]) if r['owner'] in parts and r['owner'] not in changed and r['actual_project_cap_radius_mm']>=radius-1e-6]
        reused_cap=bool(matches)
        if not matches:
            preferred=e.get('prefix_geometry_owner');candidates=[preferred] if preferred in parts else jackets
            for n in candidates:
                b=boxes[n]
                if np.any(q<b[0]-1e-4) or np.any(q>b[1]+1e-4):continue
                try:cap_at(parts[n],q,d,radius)
                except AssertionError:continue
                matches.append(n)
        if not matches:rows[name]=dict(status='ACTUAL_CAP_OR_SELECTED_PROFILE_OPEN',point_mm=q.tolist());save();continue
        margins=np.array([own_channel(e,n) for n in rigid]);blocks={};unresolved=set()
        for fraction in (.15,.3,.45,.6,.75,.9):
            L=float(R*fraction);p=q+L*d;excursion=R-np.sqrt(R*R-L*L)
            outside=np.linalg.norm(np.maximum(0,np.maximum(bounds[:,0]-p,p-bounds[:,1])),axis=1)
            inside=np.all(p>=bounds[:,0],1)&np.all(p<=bounds[:,1],1)
            depth=np.min(np.minimum(p-bounds[:,0],bounds[:,1]-p),axis=1)
            lower=np.where(inside,-depth,outside)
            for i in np.flatnonzero(lower+excursion-radius<margins-1e-6):
                owner=rigid[i]
                if owner in blocks or owner in matches:continue
                material=world.bus['original'] if owner==world.bus['name'] else parts[owner]
                point=docs['inverse'].multVec(A.Vector(*p)) if owner==world.bus['name'] else A.Vector(*p)
                if owner not in valid:
                    valid[owner]=material.isValid() and all(s.isValid() for s in material.Solids)
                    if valid[owner]:surface[owner]=Part.makeCompound(material.Faces)
                if not valid[owner]:unresolved.add(owner);continue
                gap=float(Part.Vertex(point).distToShape(surface[owner])[0]);is_inside=any(s.isInside(point,1e-7,True) for s in material.Solids)
                r=bound(R,L,-gap if is_inside else gap,radius,float(margins[i]));result['queries']+=1
                if r['no_admissible_clearance_path']:
                    blocks[owner]=dict(r,owner=owner,axial_witness_mm=p.tolist(),source_kind=meta[owner].get('kind'),nominal_budget_not_supplier_delivered_claim=True)
        rows[name]=dict(status='PROVEN_TERMINAL_CLEARANCE_BLOCK' if blocks else 'NO_NECESSITY_VIOLATION_AT_SIX_PLANES_NOT_ROUTE_PASS',
            cap_owners=matches,cap_evidence_reused=reused_cap,point_mm=q.tolist(),axis=d.tolist(),blocks=list(blocks.values()),unresolved_geometry=list(unresolved))
        save();print('Terminal',len(rows),name,rows[name]['status'],len(blocks),flush=True)
        if time.monotonic()-tick>225:result['status']='PARTIAL_WHOLE_TERMINAL_NECESSITY_SCREEN';save();return
    assert len(rows)==246
    result.update(status='WHOLE246_TERMINAL_NECESSITY_SCREEN_RECEIVED_NOT_N01',
        blocking_owners=collections.Counter(b['owner'] for r in rows.values() for b in r.get('blocks',[])).most_common())
    save();print(result['status'],result['summary'],result['queries'],result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
