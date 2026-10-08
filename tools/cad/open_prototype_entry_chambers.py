"""Whole distribution entry-space constraints, before another route trial.

The cylinders are planning reservations, NOT routed conductors or actual
connector cavities. Their overlap with valid retained material tells us which
mount/source interface must change; it does not certify a delivered defect.
"""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys
import time

from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT = BASE/'wiring-checkpoint'
MOUNTS = OUT/'LocalStationsAssembly.FCStd'
CONTEXT = BASE/'OpenPrototypePlan.FCStd'


def occupancy(scope, permutation):
    result = defaultdict(list)
    for row in scope['physical_pair_groups']:
        for old in row['ends']:
            role = permutation.get(old, old)
            result[role].append(dict(logical_ends=row['ends'],
                graph_ids=row['graph_ids'], physical_role=role))
    return result


def build_plan():
    distribution = read(BASE/'mounting-checkpoint/distribution-mount-plan.json')['distribution']
    allocation = read(OUT/'source-layout-plan.json')
    scope = read(OUT/'routing-scope-plan.json')
    loads = occupancy(scope, allocation['proposed_same_bus_port_permutation'])
    rows = [dict(role=f"{r['role']}.{port}", native=r['native'],
        side=r['side'], port=port, width_mm=r['size_mm'][0],
        load_edges=loads.get(f"{r['role']}.{port}", []),
        reserved_straight_mm=9, reservation_OD_mm=4.2,
        basis='Project independent insulation-grip allowance; worst retained4mm2 OD; NOT supplier pitch or complete grip envelope')
        for r in distribution for port in range(1,6)]
    files=[MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd',
        BASE/'mounting-checkpoint/distribution-mount-plan.json',
        OUT/'source-layout-plan.json',OUT/'routing-scope-plan.json',Path(__file__)]
    return dict(status='ALL20_DISTRIBUTION_ENTRY_SPACES_PLANNED',rows=rows,
        occupied_ports=sum(bool(r['load_edges']) for r in rows),
        same_bus_permutation=allocation['proposed_same_bus_port_permutation'],
        budget_intersection_is_not_actual_wire_collision=True,
        complete_route_or_restraint_proof=False, selected=False,
        stage_completed=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        next='Keep one entry chamber for every occupied port before allocating all five FHAC bodies, both exits, four S1 wires, PWM and service space together. No scalar wire offsets.')


def recovery_plan():
    """One coupled allocation proposal; no change to20 WAGO case positions.

    Incline the two obstructing51mm bodies together. Derive both input datums
    from the existing R6 quarter-turn/3mm exit/9mm grip recipe, rather than
    moving terminals until a wire happens to fit. Actual torso/neighbor BReps
    must reject or confirm this direction BEFORE rebuilding native carriers.
    """
    source=read(OUT/'source-layout-plan.json')
    proof=read(OUT/'entry-chambers-checks.json')
    a=math.radians(50);u=[-math.cos(a),0,-math.sin(a)]
    poses=[]
    for row in source['source_plan']:
        r=dict(row)
        r['changed']=row['holder'] in ('F_PI','F_TY')
        if r['changed']:
            goal=row['target_entry_mm'];v=[0,1 if row['holder']=='F_PI' else -1,0]
            span=abs(goal[1]-row['input_exit_mm'][1])
            start=[goal[i]-9*u[i]-span*v[i] for i in range(3)]
            entry_straight=span-6
            assert entry_straight>=9
            inlet_length=3+math.pi*6/2+entry_straight
            allowance=14 if row['holder']=='F_PI' else 11
            limit=50 if row['holder']=='F_PI' else 84.5
            assert inlet_length+allowance<limit
            axis=[-x for x in u]
            end=[start[i]+51*axis[i] for i in range(3)]
            # MaxZ of the stored51x20.25x22 body allowance after inclination.
            zmax=end[2]+12*math.cos(a)
            assert zmax+1<158,'Necessary height bound only; actual rounded torso still required'
            r.update(old_input_exit_mm=row['input_exit_mm'],input_exit_mm=start,
                output_exit_mm=end,input_departure=u,output_departure=axis,
                rotation_world_y_deg=-50,
                input_recipe=dict(exit_straight_mm=3,radius_mm=6,
                    quarter_arc_direction=v,entry_straight_mm=entry_straight,
                    strip_allowance_mm=allowance,centreline_mm=inlet_length),
                nominal_input_blank_mm=math.ceil(inlet_length+allowance),
                output_recipe=dict(exit_straight_mm=3,radius_mm=6,
                    final_departure=[1,0,0],arc_angle_deg=50,
                    straight_before_cut_mm=15,
                    factory_fit_blank_mm=math.ceil(3+6*a+15),
                    covered_factory_side_mm=14,
                    new_insulated_wire_straight_mm=21.5,
                    clearance_sleeve_OD_mm=6),
                necessary_ZMax_mm=zmax,
                native_load_path_not_inherited=True,
                full_output_to_load_route_not_inherited=True)
        poses.append(r)
    return dict(status='ONE_COUPLED_SOURCE_ALLOCATION_PROPOSAL_NOT_SELECTED',
        source_plan=poses,source_angle_deg=50,
        angle_basis='Design50deg leaves >1mm below158mm necessary height bound for BOTH51mm bodies; NOT a guarantee inside rounded torso',
        retained20_WAGO_positions=True,
        historical_entry_proof_commit='6017388',
        entry_proof_sha256=sha(OUT/'entry-chambers-checks.json'),
        baseline_native_or_case_constraints=[r for r in proof['blocked_required_space']
            if 'body_budget' in r['target'] or r['target'].endswith(('SourceLeftCarrier','SourceRightCarrier'))],
        retained_own_input_wire_occupancy_not_a_blocker=True,
        source_carriers=['Replace both affected source supports as ONE set; preserve pitch anchor and original base attachment datum',
            'Reserve ALL100 entry chambers before adding inclined seats or tie slots; open wire channels, not pierced bought casings',
            'Requalify all affected input/body/output ties; old tie paths do not inherit acceptance after inclination'],
        S1_four_wire_plan=['Keep both current S1 rows/TE ends and all4 WAGO ends',
            'Allocate first9mm, R25.2 and PWM departures together; no four independent overlapping fillets',
            '920mm is historical stock, not current routed length'],
        required_next_gate=['Both changed case bodies and BOTH factory exits versus actual torso/retained neighbors/all port chambers',
            'Coupled native supports, ties, all5 branch connections, head/tail/PWM and S1 routing',
            'Current material totals and assembly only after route choice'],
        extra_purchased_parts_or_splices=0,selected=False,
        stage_completed=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (
            OUT/'source-layout-plan.json',OUT/'entry-chambers-plan.json',
            OUT/'entry-chambers-checks.json',MOUNTS,CONTEXT,
            OUT/'TailLocalCurrent.FCStd',Path(__file__))})


def save_recovery_plan():
    plan=recovery_plan()
    (OUT/'coupled-source-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=plan['status'],changed=[dict(holder=r['holder'],
        input=r['input_exit_mm'],output=r['output_exit_mm'],
        nominal_input_blank_mm=r['nominal_input_blank_mm'],
        necessary_ZMax_mm=r['necessary_ZMax_mm']) for r in plan['source_plan'] if r['changed']]),indent=2))


def check_recovery():
    """Check the changed direction without rebuilding any native support.

    Old carriers/ties are explicitly pending replacement, not magically
    removed from a clearance claim. Reservations remain provisional.
    """
    import FreeCAD as A
    import Part
    tick=time.monotonic();plan=recovery_plan()
    (OUT/'coupled-source-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd')]
    mount,context,tail=docs
    result=dict(status='PENDING',source_sha256=plan['source_sha256'],
        contacts=[],support_changes=[],tie_budget_intersections=[],
        entry_reservation_overlaps=[],outside_torso=[],errors=[],tested_pairs=0,
        native_supports_and_full_routes_open=True,selected=False,
        stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.Name.startswith(('F_PI_','F_TY_')):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in context.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','MTA_','S0_')):
                if o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        new={}
        for row in plan['source_plan']:
            if not row['changed']:continue
            name=row['holder'];p=A.Vector(*row['input_exit_mm']);u=A.Vector(*row['input_departure'])
            s=mount.getObject(name+'_body_budget_CurrentReference').Shape.copy()
            old=A.Vector(*row['old_input_exit_mm'])
            s.rotate(old,A.Vector(0,1,0),row['rotation_world_y_deg']);s.translate(p-old)
            new[name+'_Body']=s
            q=row['input_recipe'];v=A.Vector(*q['quarter_arc_direction'])
            a=p+u*3;c=a+v*6;b=c+u*6;end=b+v*q['entry_straight_mm']
            assert (end-A.Vector(*row['target_entry_mm'])).Length<1e-7
            inlet=[Part.makeLine(p,a),Part.Arc(a,c+(u-v)*(6/math.sqrt(2)),b).toShape(),Part.makeLine(b,end)]
            def tube(edges,od):
                path=Part.Wire(edges);first=path.Edges[0]
                circle=Part.Wire([Part.makeCircle(od/2,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
                shape=path.makePipeShell([circle],True,False)
                assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
                return shape,path.Length
            new[name+'_Input'],length=tube(inlet,4)
            assert abs(length-q['centreline_mm'])<1e-6
            p=A.Vector(*row['output_exit_mm']);u=A.Vector(*row['output_departure'])
            a=p+u*3;c=a+A.Vector(u.z,0,-u.x)*6;r=a-c
            rotation=A.Rotation(A.Vector(0,1,0),50)
            b=c+rotation.multVec(r);mid=c+A.Rotation(A.Vector(0,1,0),25).multVec(r)
            cut=b+A.Vector(15,0,0)
            outlet=[Part.makeLine(p,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,cut)]
            new[name+'_Output'],_=tube(outlet,4)
            new[name+'_Sleeve'],_=tube([Part.makeLine(cut-A.Vector(14,0,0),cut+A.Vector(12.5,0,0))],6)
            new[name+'_NewWireGrip'],_=tube([Part.makeLine(cut,cut+A.Vector(21.5,0,0))],2.1)
        def check(n,s,m,t,category='contacts'):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result[category].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for n,s in new.items():
            outside=s.cut(context.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:result['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume,bounds_mm=bounds(outside)))
            for m,t in targets.items():
                category='support_changes' if m.endswith(('SourceLeftCarrier','SourceRightCarrier')) else (
                    'tie_budget_intersections' if '_tie' in m else 'contacts')
                check(n,s,m,t,category)
            # Check all100 ports, not just the two fuse supply ports. Only
            # the case bodies can obstruct a chamber: the matching input wire
            # occupying its own entry is intentional, not a route collision.
            if n.endswith('_Body'):
                for r in read(OUT/'entry-chambers-checks.json')['rows']:
                    chamber=Part.makeCylinder(2.1,9,A.Vector(*r['point_mm']),A.Vector(*r['departure']))
                    check(n,s,'entry/'+r['role'],chamber,'entry_reservation_overlaps')
        # Different holders must not overlap. Same-holder sleeve/new-wire
        # material reservations intentionally overlap their physical lead.
        items=list(new.items())
        for i,(n,s) in enumerate(items):
            for m,t in items[i+1:]:
                if n.rsplit('_',1)[0].split('_')[1]!=m.rsplit('_',1)[0].split('_')[1]:check(n,s,m,t)
        result['status']='COUPLED_SOURCE_DIRECTION_REQUIRES_WHOLE_LAYOUT_CHANGE' if any(result[k] for k in ('contacts','entry_reservation_overlaps','outside_torso','errors')) else 'COUPLED_SOURCE_DIRECTION_CLEAR_SUPPORTS_AND_FULL_ROUTES_OPEN'
    finally:
        for doc in docs:A.closeDocument(doc.Name)
    assert all(sha(ROOT/p)==h for p,h in plan['source_sha256'].items())
    result.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'coupled-source-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','entry_reservation_overlaps','outside_torso','errors','tested_pairs','worker_seconds')}),flush=True)


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic();plan=build_plan()
    (OUT/'entry-chambers-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd')]
    mount,context,tail=docs
    result=dict(status='PENDING',source_sha256=plan['source_sha256'],
        rows=[],blocked_required_space=[],blocked_NC_space=[],errors=[],
        tested_pairs=0, reservation_is_not_wire=True,
        selected=False,stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in context.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (
                o.Name.startswith(('P0_','Head_','TailBridge','MTA_','S0_'))):
                if o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        for row in plan['rows']:
            body=mount.getObject(row['native']);assert body is not None
            b=bounds(body.Shape)
            pitch=(row['width_mm']-11)/4
            p=[b[0]+5.5+(row['port']-1)*pitch,
                b[1] if row['side']=='L' else b[4], (b[2]+b[5])/2]
            d=[0,-1 if row['side']=='L' else 1,0]
            s=Part.makeCylinder(row['reservation_OD_mm']/2,
                row['reserved_straight_mm'],A.Vector(*p),A.Vector(*d))
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            entry=dict(role=row['role'],point_mm=p,departure=d,
                occupied=bool(row['load_edges']),load_edges=row['load_edges'],blocked_by=[])
            for name,target in targets.items():
                if name=='mount/'+row['native'] or not s.BoundBox.intersect(target.BoundBox):continue
                result['tested_pairs']+=1
                try:
                    assert target.isValid(),'Invalid target BRep is not clearance'
                    hit=s.common(target);assert hit.isValid()
                    if hit.Volume>1e-5:
                        item=dict(port=row['role'],target=name,
                            reserved_space_overlap_mm3=hit.Volume,bounds_mm=bounds(hit))
                        result['blocked_required_space' if entry['occupied'] else 'blocked_NC_space'].append(item)
                        entry['blocked_by'].append(name)
                except Exception as e:result['errors'].append(dict(port=row['role'],target=name,error=str(e)))
            result['rows'].append(entry)
        assert len(result['rows'])==100
        result['status']='SHARED_ENTRY_CHAMBERS_REQUIRE_COUPLED_LAYOUT_CHANGE' if result['blocked_required_space'] else 'ENTRY_CHAMBERS_CLEAR_NOT_FULL_ROUTES'
        if result['errors']:result['status']='ENTRY_CHAMBER_GEOMETRY_ERRORS_OPEN'
    finally:
        for doc in docs:A.closeDocument(doc.Name)
    assert all(sha(ROOT/p)==h for p,h in plan['source_sha256'].items())
    result.update(worker_seconds=time.monotonic()-tick,
        finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'entry-chambers-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],occupied_ports=plan['occupied_ports'],
        blocked_ports=sorted({r['port'] for r in result['blocked_required_space']}),
        blocking_parts=sorted({r['target'] for r in result['blocked_required_space']}),
        errors=result['errors'],tested_pairs=result['tested_pairs'],worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':
    if '--plan-recovery' in sys.argv:save_recovery_plan()
    elif '--check-recovery' in sys.argv:check_recovery()
    else:main()
