"""Whole distribution entry-space constraints, before another route trial.

The cylinders are planning reservations, NOT routed conductors or actual
connector cavities. Their overlap with valid retained material tells us which
mount/source interface must change; it does not certify a delivered defect.
"""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
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


if __name__=='__main__':main()
