"""Exact BRep distances for a constant-radius route reservation.

A valid connected centreline inside a valid shell, at distance >= radius
from it and retained solids, gives a conservative round-tube clearance.
Distance below radius is a rejected reservation, NOT a measured physical
collision or volume. No bounding-box overlap alone is used as a verdict.
Primitive case budgets are tested before any curve work. Native grips,
downstream circuits and service remain OPEN regardless of this gate.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, time
import FreeCAD as A
import Part
import open_prototype_source_group as B
import open_prototype_source_approach_search as G
from open_prototype_entry_chambers import CONTEXT, MOUNTS
ROOT=G.ROOT
POINT_SCREEN=False

def run():
    tick=time.monotonic();assert not G.PROOF.exists(),'Receive owned worker; no unchanged repeat'
    plan=G.read(G.PLAN);rebuilt=G.build()
    if plan.get('recipe_compact'):
        assert G.geometry_digest(rebuilt)==plan['materialized_geometry_digest'],'Compact recipe changed geometry'
        for n,h in plan['source_sha256'].items():assert G.sha(ROOT/n)==h,n
        rebuilt['mutual_path_preflight']=plan['mutual_path_preflight']
        plan=rebuilt
    assert not any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in plan['mutual_path_preflight']['near_pairs']), 'Known mutual crossing: do not launch expensive gate'
    def equivalent(a,b):
        if isinstance(a,bool) or isinstance(b,bool):return a==b
        if isinstance(a,(int,float)) and isinstance(b,(int,float)):return abs(a-b)<=1e-7
        if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(equivalent(a[k],b[k]) for k in a)
        if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
        return a==b
    for key in ('stations','mta','tails','holders','s1_routes','ports','permutation','body_ends'):
        assert equivalent(plan[key],rebuilt[key]),key
    import open_prototype_source_group_separated as D
    import open_prototype_source_search as S
    import open_prototype_source_approach_search as H
    paths=[G.PLAN,CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd',Path(__file__),Path(G.__file__),
        Path(B.__file__),Path(D.__file__),Path(S.__file__),Path(H.__file__),G.OUT/'obstacle-map-current.json']
    if hasattr(G,'CAPACITY'):paths.extend([G.CAPACITY,H.PLAN])
    pins={p.relative_to(G.ROOT).as_posix():G.sha(p) for p in paths}
    result=dict(status='PENDING',errors=[],outside=[],case_overlaps=[],distance_conflicts=[],
        exact_path_pairs=[],tested_pairs=0,source_sha256=pins,selected=False,
        plan_rebuilt_geometry_absolute_tolerance_mm=1e-7,
        stage_completed=False,physical_pass=False,
        basis='Case planning budgets plus actual saved retained BRep. Exact centreline/material distance, conservative constant-radius tube reservation; not measured supplier geometry or physicalPASS.')
    docs=[];scene=[];retained=[];modules=[];routes=[]
    def box(c,size):return Part.makeBox(*size,A.Vector(*[v-d/2 for v,d in zip(c,size)]))
    def wire(parts):
        edges=[Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end'])) if p['kind']=='line'
            else Part.Arc(A.Vector(*p['start']),A.Vector(*p['mid']),A.Vector(*p['end'])).toShape() for p in parts]
        s=Part.Wire(edges);assert s.isValid(),'Invalid path is not clearance'
        return s
    def distance(n,s,m,t,required):
        assert s.isValid() and t.isValid(),(n,m)
        # Expanded boxes only choose potential pairs; the verdict below is
        # a real distance query against valid geometry, never a bbox test.
        sb=s.BoundBox;tb=t.BoundBox
        gap=math.sqrt(sum(max(0,a-d,c-b)**2 for a,b,c,d in
            ((sb.XMin,sb.XMax,tb.XMin,tb.XMax),(sb.YMin,sb.YMax,tb.YMin,tb.YMax),(sb.ZMin,sb.ZMax,tb.ZMin,tb.ZMax))))
        if gap>required+1e-6:return
        d,pts,info=s.distToShape(t);result['tested_pairs']+=1
        assert math.isfinite(d),('Invalid distance',n,m)
        if d<required-1e-6:
            result['distance_conflicts'].append(dict(a=n,b=m,distance_mm=round(d,6),required_mm=required,
                interpretation='Rejected clearance reservation, not measured delivered-part collision'))
    def trim(parts,first=0,last=0):
        # Source/receiver face caps only. All remaining own-case geometry
        # remains checked, including return/reentry later in a curve.
        import copy
        q=copy.deepcopy(parts)
        if first:
            assert q[0]['kind']=='line' and math.dist(q[0]['start'],q[0]['end'])>first
            q[0]['start']=B.add(q[0]['start'],B.mul(B.segment_geometry(q[0])[1],first))
        if last:
            assert q[-1]['kind']=='line' and math.dist(q[-1]['start'],q[-1]['end'])>last
            q[-1]['end']=B.sub(q[-1]['end'],B.mul(B.segment_geometry(q[-1])[2],last))
        return wire(q)
    try:
        docs=[A.openDocument(str(p)) for p in (CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd')]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1 and torso.Shells
        prior_cases=None
        if getattr(G,'REUSE_CASES_FROM',None):
            previous=G.read(G.REUSE_CASES_FROM)
            proof=G.read(G.OUT/'source-group-point-screen.json')
            assert not proof['outside'] and not proof['errors']
            for f in (CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd',G.OUT/'obstacle-map-current.json'):
                assert G.sha(f)==proof['source_sha256'][f.relative_to(ROOT).as_posix()]
            prior_cases={r['role']:(r['centre_mm'],r['size_mm']) for r in previous['stations']+previous['mta']+previous['holders']}
            result['unchanged_case_inside_checks_reused_from']='source-group-point-screen.json; pinned geometry unchanged, no reuse of open case-overlap/tube checks'
        for r in plan['stations']+plan['mta']+plan['holders']:
            s=box(r['centre_mm'],r['size_mm']);assert s.isValid() and len(s.Solids)==1
            scene.append((r['role'],s))
            if not prior_cases or prior_cases[r['role']]!=(r['centre_mm'],r['size_mm']):
                outside=s.cut(torso);assert outside.isValid()
                if outside.Volume>1e-6:result['outside'].append(dict(name=r['role'],volume_mm3=round(outside.Volume,6)))
        if result['outside']:
            result['status']='REJECTED_CASE_SPACE_BUDGET_BEFORE_EXPENSIVE_CURVES'
            return
        changed_rings={}
        for r in plan['s1_routes']:
            old=B.WEST if r['terminal'] in (2,3) else B.EAST
            if old==r['barrel_direction']:continue
            n='S1_ring_'+str(r['terminal']);s=ctx.getObject(n).Shape.copy()
            rot=A.Rotation(A.Vector(*old),A.Vector(*r['barrel_direction']))
            s.rotate(A.Vector(*r['eye_mm']),rot.Axis,rot.Angle*180/math.pi)
            assert s.isValid() and s.Solids;changed_rings[n]=s;scene.append((n,s))
        excluded=[]
        for r in G.read(G.OUT/'obstacle-map-current.json')['objects']:
            n=r['name']
            if r['kind'] in ('candidate_station','replaceable_support') or n in changed_rings:
                excluded.append(n);continue
            if r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                v=r['bounds_mm'];modules.append((n,box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])));continue
            obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
            assert obj is not None and hasattr(obj,'Shape'),n
            assert obj.Shape.isValid() and obj.Shape.Solids,n
            retained.append((n,obj.Shape))
        assert {'F_PWM_CP2','S1_body_CP2','CurrentTailSupport'}.issubset({n for n,_ in retained})
        assert sum(n.startswith('F_') and '_CP2_' in n for n,_ in retained)>=48
        result.update(retained_solid_count=len(retained),whole_module_budgets=[n for n,_ in modules],
            changed_actual_rings=list(changed_rings),invalidated_not_qualified=excluded)
        reuse_case_gate=getattr(G,'REUSE_CHANGED_CASE_GATE',None)
        if reuse_case_gate:
            prior=G.read(reuse_case_gate)
            assert not any(prior[k] for k in ('outside','case_overlaps','errors'))
            for f in (G.PLAN,CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd',G.OUT/'obstacle-map-current.json'):
                assert G.sha(f)==prior['source_sha256'][f.relative_to(ROOT).as_posix()]
            result['changed_case_common_reused_from']=reuse_case_gate.relative_to(ROOT).as_posix()
        for i,(n,s) in enumerate(scene):
            if reuse_case_gate:continue
            if POINT_SCREEN and n not in plan.get('changed_case_names',[]):continue
            for m,t in scene[:i]+modules+retained:
                if n.startswith('S1_ring_') and m in ('S1_screw_'+n[-1],'S1_seat_budget_'+n[-1]):continue
                if not s.BoundBox.intersect(t.BoundBox):continue
                common=s.common(t);assert common.isValid();result['tested_pairs']+=1
                if common.Volume>1e-6:result['case_overlaps'].append(dict(a=n,b=m,volume_mm3=round(common.Volume,6)))
        for r in plan['tails']:
            routes.append((r['wire'],r['segments'],r['OD_mm']/2,'MTA_'+r['leg'],r['target'].split('.')[0]))
        for r in plan['s1_routes']:
            routes.append((r['wire'],r['segments'],r['OD_mm']/2,'S1_ring_'+str(r['terminal']),r['target'].split('.')[0]))
        for h in plan['holders']:
            for side in ('input','output'):
                routes.append((h['role']+'/'+side,h[side+'_segments'],2,h['role'],h['input_target'].split('.')[0] if side=='input' else None))
            routes.append((h['role']+'/sleeve',[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],3,None,None))
            routes.append((h['role']+'/new_insulation',[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],1.05,None,None))
        if POINT_SCREEN:
            # A point strictly inside valid real material is a positive
            # rejection witness. An empty result NEVER proves tube clearance.
            from open_prototype_path_preflight import samples
            witnesses={};outside_points={};count=queries=0
            inventory=[(m,t,t.BoundBox) for m,t in scene+modules+retained]
            for n,parts,radius,source,receiver in routes:
                if plan.get('changed_path_names') and n not in plan['changed_path_names']:continue
                for segment,p in samples(parts):
                    count+=1;v=A.Vector(*p)
                    if n not in outside_points and not torso.isInside(v,1e-7,True):
                        outside_points[n]=dict(name=n,segment=segment,point_mm=p,
                            interpretation='Centreline point outside torso; whole tube still unqualified')
                    for m,t,bbox in inventory:
                        if (n,m) in witnesses or not bbox.isInside(v):continue
                        if m==source and math.dist(p,parts[0]['start'])<=radius+1e-5:continue
                        if m==receiver and math.dist(p,parts[-1]['end'])<=radius+1e-5:continue
                        queries+=1
                        if t.isInside(v,1e-7,False):
                            witnesses[n,m]=dict(a=n,b=m,segment=segment,point_mm=p,
                                basis='Positive point-in-valid-solid witness, NOT bbox overlap; case budgets remain assumptions')
            result.update(point_intrusions=list(witnesses.values()),outside=list(outside_points.values()),
                sample_count=count,point_in_solid_queries=queries,changed_path_names=plan.get('changed_path_names'),
                tube_clearance_not_qualified=True,case_common_gate_not_run=not bool(plan.get('changed_case_names')),
                status='REJECTED_POSITIVE_POINT_WITNESSES' if witnesses or outside_points or result['case_overlaps'] else 'NO_POINT_INTRUSION_FOUND_NOT_CLEARANCE')
            return
        curves=[];boundary=torso.Shells[0]
        for n,parts,radius,source,receiver in routes:
            s=wire(parts);curves.append((n,s,radius))
            if plan.get('changed_path_names') and n not in plan['changed_path_names']:continue
            d=s.distToShape(boundary)[0]
            inside=torso.isInside(A.Vector(*parts[0]['start']),1e-7,True)
            if not inside or d<radius-1e-6:result['outside'].append(dict(name=n,shell_distance_mm=round(d,6),required_mm=radius,first_point_inside=inside))
            for m,t in scene+modules+retained:
                candidate=s
                if m==source:candidate=trim(parts,first=radius+1e-5)
                if m==receiver:candidate=trim(parts,last=radius+1e-5)
                distance(n,candidate,m,t,radius)
        for i,(n,s,radius) in enumerate(curves):
            for m,t,other_radius in curves[:i]:
                changed=plan.get('changed_path_names')
                if changed and n not in changed and m not in changed:continue
                same_holder='/' in n and '/' in m and n.split('/')[0]==m.split('/')[0]
                if same_holder and ('sleeve' in (n.split('/')[-1],m.split('/')[-1])) and 'input' not in (n.split('/')[-1],m.split('/')[-1]):continue
                before=len(result['distance_conflicts']);distance(n,s,m,t,radius+other_radius)
                if len(result['distance_conflicts'])>before:result['exact_path_pairs'].append([n,m])
        result['status']='REJECTED_SOURCE_CLEARANCE_RESERVATIONS' if any(result[k] for k in
            ('outside','case_overlaps','distance_conflicts')) else 'CONSERVATIVE_SOURCE_CLEARANCE_ONLY_DOWNSTREAM_NATIVE_SERVICE_OPEN'
        if plan.get('changed_path_names'):
            result['checked_material_clearance_path_names']=plan['changed_path_names']
            result['complete_source_group_not_qualified']=True
            if result['status']=='CONSERVATIVE_SOURCE_CLEARANCE_ONLY_DOWNSTREAM_NATIVE_SERVICE_OPEN':
                result['status']='CONSERVATIVE_CHANGED_PATH_CLEARANCE_ONLY_COMPLETE_SOURCE_STILL_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        if not all(G.sha(ROOT/p)==h for p,h in pins.items()):
            result['errors'].append('Source changed during gate; no acceptance')
            result['status']='INVALID_SOURCE_PIN_CHANGED'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        G.PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        keys=('status','outside','case_overlaps','errors','worker_seconds','sample_count','point_in_solid_queries','point_intrusions') if POINT_SCREEN else ('status','outside','case_overlaps','distance_conflicts','errors','tested_pairs','worker_seconds')
        print(json.dumps({k:result.get(k) for k in keys}),flush=True)
    assert all(G.sha(ROOT/p)==h for p,h in pins.items())

if __name__=='__main__':
    import sys
    if '--capacity' in sys.argv or '--point-screen' in sys.argv:
        import open_prototype_source_capacity_plan as G
    if '--point-screen' in sys.argv:
        POINT_SCREEN=True
        G.PROOF=G.OUT/'source-group-point-screen.json'
    if '--frame-points' in sys.argv:
        import open_prototype_source_frame_corridor as G
        POINT_SCREEN=True
        G.REUSE_CASES_FROM=G.OUT/'source-group-capacity-plan.json'
    if '--rr-points' in sys.argv:
        import open_prototype_rr_receiving_branch as G
        POINT_SCREEN=True
    if '--rr-distance' in sys.argv:
        import open_prototype_rr_receiving_branch as G
        G.REUSE_CHANGED_CASE_GATE=G.PROOF
        G.PROOF=G.OUT/'rr-receiving-branch-distance.json'
    run()
