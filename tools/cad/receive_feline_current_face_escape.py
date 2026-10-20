"""Current246 necessary-source gate before any further detailed route CAD.

Use the resident current scene and typed123 contract. Read actual rectangular
faces once, not bounding-box contacts; no scene reload/raster or pose search.
"""
import collections,gzip,hashlib,itertools,json,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from feline_rectangular_escape import certificate
from feline_common_space_context import is_jacket
from feline_atomic_save import save_json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def run(fixed,metadata,ends,contract,pins):
    tick=time.monotonic();faces={};rigid=[];bounds={}
    for n,s in fixed.items():
        kind=metadata.get(n,{}).get('kind')
        if not s.Solids or is_jacket(n,metadata.get(n,{})) or kind in ('T18I','tie_reservation','project_stock_reservation'):continue
        rigid.append(n);b=s.BoundBox;bounds[n]=np.array([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
    rows={};valid=set()
    for e in ends:
        p=e.get('routing_exit_mm');d=e.get('routing_exit_axis');profile=contract['portions'][e['portion_id']]
        R=profile.get('minimum_project_R_mm');radius=profile.get('project_radius_mm')
        if p is None or d is None or not R or not radius:
            rows[e['id']]=dict(status='BOUNDARY_OR_TYPED_PROFILE_OPEN');continue
        p=np.asarray(p,float);d=np.asarray(d,float);axis=int(np.argmax(abs(d)))
        if abs(abs(d[axis])-1)>1e-7 or np.linalg.norm(np.delete(d,axis))>1e-7:
            rows[e['id']]=dict(status='NON_AXIAL_NO_RECT_FACE_CERTIFICATE');continue
        transverse=[i for i in range(3) if i!=axis];blocks=[]
        for n in rigid:
            box=bounds[n];ahead=(box[:,axis]-p[axis])*d[axis]
            if min(ahead)>=R or max(ahead)<=0:continue
            if any(p[i]<box[0,i]-1e-7 or p[i]>box[1,i]+1e-7 for i in transverse):continue
            if n not in faces:
                s=fixed[n];assert s.isValid() and all(c.isValid() for c in s.Solids),n;valid.add(n);rr=[]
                for face in s.Faces:
                    if not isinstance(face.Surface,Part.Plane) or len(face.Edges)!=4 or len(face.Vertexes)!=4:continue
                    v=np.array([list(a.Point) for a in face.Vertexes]);lo=v.min(0);hi=v.max(0)
                    flat=np.flatnonzero(hi-lo<1e-6)
                    if len(flat)!=1:continue
                    k=int(flat[0]);ij=[i for i in range(3) if i!=k]
                    if abs(face.Area-(hi[ij[0]]-lo[ij[0]])*(hi[ij[1]]-lo[ij[1]]))>1e-5:continue
                    corners={tuple(np.round(a[ij],6)) for a in v}
                    expected=set(itertools.product(*[(round(lo[i],6),round(hi[i],6)) for i in ij]))
                    if corners!=expected:continue
                    rr.append((k,float(lo[k]),lo,hi,float(face.Area)))
                faces[n]=rr
            for k,coordinate,lo,hi,area in faces[n]:
                if k!=axis:continue
                L=(coordinate-p[axis])*d[axis]
                if not 0<L<R:continue
                margin=min(min(p[i]-lo[i],hi[i]-p[i]) for i in transverse)
                if margin<0:continue
                proof=certificate(R,L,float(margin),radius)
                if proof['no_admissible_clearance_path']:
                    blocks.append(dict(proof,owner=n,actual_rectangular_face_area_mm2=area,
                        face_bounds_mm=[lo.tolist(),hi.tolist()],source_kind=metadata[n].get('kind'),
                        project_budget_NOT_manufacturer_delivered_contact_claim=True))
        rows[e['id']]=dict(status='PROVEN_CURRENT_BOUNDARY_CLEARANCE_HOLD' if blocks else 'NO_RECT_FACE_REJECTION_NOT_ROUTE_PASS',
            wire=e['wire'],point_mm=p.tolist(),axis=d.tolist(),blocks=blocks)
    assert len(rows)==246
    dest=OUT/'n01-current246-rectangular-source-escape.json';rf=dest.with_suffix('.rows.json.gz')
    rf.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    result=dict(status='CURRENT246_RECTANGULAR_SOURCE_NECESSITY_RECEIVED_NOT_N01',
        summary=dict(collections.Counter(r['status'] for r in rows.values())),
        blocking_owners=collections.Counter(b['owner'] for r in rows.values() for b in r.get('blocks',[])).most_common(),
        rows=rf.relative_to(ROOT).as_posix(),rows_sha256=sha(rf),
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/cad/feline_rectangular_escape.py':sha(Path(__file__).with_name('feline_rectangular_escape.py'))},
        current_ends_sha256=hashlib.sha256(json.dumps(ends,sort_keys=True).encode()).hexdigest(),
        actual_rectangular_faces_cached=len(faces),validated_actual_material_owners=len(valid),
        no_rejection_NOT_a_route_or_complete_source_audit=True,other_face_types_and_motion_OPEN=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],result['summary'],result['blocking_owners'],result['worker_seconds'],flush=True)
    return result,rows


def classify_current(base,ends,result,rows):
    """Reuse exact face evidence; don't invent free continuations of a
    received complete factory path or treat its own zero-depth face as a
    foreign forward barrier. Original raw evidence remains unchanged.
    """
    complete={r['portion_id'] for r in base['received_factory4MTA_curves'] if r['complete_current_curve_reused']}
    byid={e['id']:e for e in ends};active={};already=[];start=[]
    for eid,r in rows.items():
        if byid[eid]['portion_id'] in complete:already.append(eid);continue
        indices=[]
        for i,b in enumerate(r.get('blocks',[])):
            if b['axial_plane_distance_mm']<=1e-5:start.append([eid,i]);continue
            indices.append(i)
        if indices:active[eid]=indices
    source=OUT/'n01-current246-rectangular-source-escape.json'
    view=dict(status='CURRENT_SOURCE_ESCAPE_ACTION_GATE_NOT_N01',
        raw_receipt=source.relative_to(ROOT).as_posix(),raw_receipt_sha256=sha(source),
        raw_rows=result['rows'],raw_rows_sha256=result['rows_sha256'],
        current_ends_sha256=result['current_ends_sha256'],active_clearance_holds=active,
        received_complete_factory_no_new_continuation=already,zero_depth_start_planes_not_forward_barriers=start,
        unchanged_actual_face_queries_reused=True,new_geometry_queries=0,
        all_other_negative_witnesses_preserved=True,physical_collision_NOT_implied_by_margin_hold=True,
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-current-source-escape-action-gate.json',view)
    print(view['status'],'active_sources',len(active),'complete_ends',len(already),'start_faces',len(start),flush=True)
    return view


def require_receivers(ends,changed_source_ids=()):
    """Enforce the lesson: no more middle/pose searches past blocked mouths.

    Explicit changed-source proposals still need their own source acceptance;
    this exemption is not a route or source approval and grants no N01 point.
    """
    view=json.loads((OUT/'n01-current-source-escape-action-gate.json').read_text())
    actual=hashlib.sha256(json.dumps(ends,sort_keys=True).encode()).hexdigest()
    assert actual==view['current_ends_sha256'],'Receive the changed current boundary set before new searches'
    for k in ('raw_receipt','raw_rows'):assert sha(ROOT/view[k])==view[k+'_sha256']
    used={e['id'] for e in ends if e['wire'].startswith(('XP02.','XP03.')) and e.get('group')!='JPWM'}
    holds=used&set(view['active_clearance_holds'])-set(changed_source_ids)
    if holds:raise ValueError('Replan whole receiving sources BEFORE any JPWM middle/pose search: '+str(sorted(holds)))
