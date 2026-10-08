"""Bind retained local harness boundaries; never turn a missing seat into a pin.

The body feeds terminate at existing insulated module tails, not JR cavity
centres. Old fixed cover paths and old body fuse/WAGO coordinates are excluded.
"""
import json
import math
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT = BASE / 'wiring-checkpoint'
CONTEXT = BASE / 'OpenPrototypePlan.FCStd'
SOURCES = {
    'layout': ROOT / 'hardware/cad/studies/whole-cat-packaging/layout.json',
    'inventory': ROOT / 'hardware/cad/studies/whole-cat-packaging/inventory.json',
    'yaw': ROOT / 'hardware/cad/studies/head-fixed-yaw-feed-r3/plan.json',
    'pitch': ROOT / 'hardware/electronics/full-cat/head-fixed-pitch-conductors-r1/checks.json',
    'tail': ROOT / 'tools/electronics/tail_central_routes_r1.py',
    'tail_finish': ROOT / 'hardware/electronics/full-cat/tail-local-finish-r2/README.md',
    'holders': OUT / 'fhac-mount-plan.json',
    'endpoints': OUT / 'endpoint-plan.json',
    'body_layout': BASE / 'layout.json',
    'scope': OUT / 'routing-scope-plan.json',
    'context': CONTEXT,
    'script': __file__,
}


def translated(point, shift):
    return [a+b for a,b in zip(point, shift)]


def build():
    layout = {r['name']: r for r in read(SOURCES['layout'])['parts']}
    inventory = {r['name']: r for r in read(SOURCES['inventory'])['parts']}
    holders = {r['holder']: r for r in read(SOURCES['holders'])['source_plan']}
    endpoint = read(SOURCES['endpoints'])
    ports = {e['role']: e for r in endpoint['body_conductors'] for e in r['ends']}
    for r in endpoint['distribution_boundary']:
        ports.update(r['resolved_datums'])
    rows = []

    def record(wire, role, point, owner, kind, departure, retained):
        shift = layout[owner]['shift_mm']
        root = translated(point, shift)
        start = holders[role.split('.')[0]]['output_exit_mm'] if role.startswith('F_') else ports.get(role, {}).get('point_mm')
        rows.append(dict(wire=wire, body_role=role, local_boundary_original_mm=point,
            local_boundary_current_candidate_mm=root, shift_mm=shift, native_owner=owner,
            boundary_kind=kind, outward_from_module=departure,
            original_native_source=inventory[owner]['source'],
            body_source_mm=start, necessary_straight_length_mm=math.dist(start,root) if start else None,
            material={'XB':'HELU23302 red', 'XS':'HELU23308 yellow'}.get(wire[:2], 'unallocated'),
            conductor_area_mm2=.5, insulation_OD_mm=2.1, minimum_fixed_radius_mm=12.6,
            terminal_pin_invented=False, known_current_attachment=retained,
            actual_cut_mm=None, route_qualified=False))

    # One existing yaw insulation seat serves three wires; this point is NOT
    # an electrical terminal or a newly invented three-conductor pinout.
    for wire,role in [('XB12','F_HY.out'),('XB13','G_AUX.3'),('XS13','R1.2')]:
        record(wire, role, [-70,-56.8,60.2], 'Head_YawCarrier',
               'Existing stationary yaw insulated-tail boundary; individual packing to be retained from local harness',
               [1,0,0], True)
    # The OLD fixed cover is not in CP2's retained native module inventory.
    # Its translated boundary is a candidate only, not inherited support proof.
    for r in read(SOURCES['pitch'])['routes']:
        role = {'XB22':'F_HP.out','XB23':'G_AUX.4','XS23':'R2.2'}[r['wire']]
        record(r['wire'], role, r['end_mm'], 'Head_PitchCarrier',
               'Historical fixed-cover transition; current fixed support and moving-loop adaptation OPEN',
               [0,-1,0], False)
    n=1.05/math.sqrt(3)
    for wire,role,point in [('XB32','F_TY.out',[68,-45,77-2*n]),
                           ('XB33','G_TAIL.2',[68,-43.95,77+n]),
                           ('XS33','R3.2',[68,-46.05,77+n])]:
        record(wire, role, point, 'P0_MG92BMount29',
               'TailLocalCompleteSupportR2 insulation boundary; current native uses older P0 support, replacement integration OPEN',
               [-1,0,0], False)
    for r in rows:
        if r['wire'] in ('XB13','XB23','XB33'):
            r['material']='HELU23301 black'
    pins = {str(p.relative_to(ROOT)).replace('\\','/'): sha(p)
            for p in map(Path, SOURCES.values())}
    body_layout=read(SOURCES['body_layout'])
    corridors={wire:label for label,wires in body_layout['corridor_assignments'].items() for wire in wires}
    body_rows=[]
    for wire in endpoint['body_conductors']:
        body_rows.append(dict(id=wire['id'],a=wire['a'],b=wire['b'],net=wire['net'],
            corridor=corridors.get(wire['id']),
            ends=[dict(role=e['role'],point_mm=e.get('point_mm'),
                       exit_reservation=e.get('connector_reservations_mm'),
                       manufacturer_pin_known=False,
                       physical_loom=e.get('physical_loom'),
                       current_frame_bound=e.get('current_frame_bound',False)) for e in wire['ends']],
            existing_route_only=wire['id'] in ('W077','W078'),actual_cut_mm=None))
    scope=read(SOURCES['scope'])
    legacy=[dict(graph_ids=r['graph_ids'],ends=r['ends'],current_datums=r['current_datums'],
                 old_920mm_not_current_stock_acceptance=True)
            for r in scope['physical_pair_groups'] if r['scope'].startswith('LEGACY_SOURCE_920MM')]
    return dict(status='ONE_SHARED_LOCAL_BOUNDARY_PLAN_NOT_ROUTE_ACCEPTANCE', source_sha256=pins,
        rows=rows, selected=False, stage_completed=False, physical_pass=False,
        body_rows=body_rows, shared_corridor_reservations_mm=body_layout['shared_corridors_mm'],
        legacy_source=legacy, full_logical_scope_reference=SOURCES['scope'].relative_to(ROOT).as_posix(),
        corridor_reservations_not_wire_paths_or_contacts=True,
        factory_MG92B_leads_unchanged_mm=250, connectors_added=0,
        old_body_routes_not_reused=True, old_fixed_cover_not_present_in_current_inventory=True,
        remaining_output_AUX=dict(role='F_AUX.out -> AUX.VIN',
            body_source_mm=holders['F_AUX']['output_exit_mm'],
            delivered_padmap_required=True, target_pin_mm=None),
        assembly_plan=[
            'Keep finished source carriers, bankR47 and existing input grips unchanged.',
            'Lay shared fixed body bundles before installing populated boards. Preserve dedicated motor returns.',
            'Bind stationary yaw at its retained insulation seat. Do not treat its shared boundary as three coincident conductor paths.',
            'Integrate the existing tail local support, rather than adding another JR or cutting factory leads.',
            'Re-anchor the pitch flexible loop to the open-prototype structure; the former fixed-cover support is not retained.',
            'Give body tails independent insulation restraint at existing rails, keeping ATO lid and WAGO levers accessible.',
            'After one common route check, reconcile lengths/ties/material stock and qualify the common service sequence.'],
        physical_gates=['Delivered U1 and AUX pads/polarity', 'JR view/pin cavity and actual factory lead exits',
                        'Nominal routes are for dry fit; print, bend, pull and thermal tests remain phase2'],
        next='One shared body layout including9local tails/80body rows/legacy920mm source; no rechecking unchanged fixtures')


def verify_context(plan):
    import FreeCAD as A
    import Part
    doc=A.openDocument(str(CONTEXT))
    rows=[]
    try:
        for name in ('Head_YawCarrier','Head_PitchCarrier'):
            record=next(r for r in plan['rows'] if r['native_owner']==name)
            source=Part.Shape()
            source.read(str(ROOT/record['original_native_source']['file']))
            source.translate(A.Vector(*record['shift_mm']))
            current=doc.getObject(name)
            assert current is not None, name
            assert source.isValid() and current.Shape.isValid(), name
            common=source.common(current.Shape)
            difference=source.Volume+current.Shape.Volume-2*common.Volume
            assert abs(difference)<1e-4, (name,difference)
            rows.append(dict(native=name, current_bounds_mm=bounds(current.Shape),
                transformed_source_difference_mm3=difference, source_shape_retained=True,
                bbox_not_used_as_collision_test=True))
        tail=doc.getObject('P0_MG92BMount29')
        assert tail is not None
        rows.append(dict(native=tail.Name,current_bounds_mm=bounds(tail.Shape),
            native_present=True, local_finish_support_integration_qualified=False,
            reason='Retained inventory references P0 support, not TailLocalCompleteSupportR2'))
    finally:
        A.closeDocument(doc.Name)
    return rows


if __name__=='__main__':
    tick=time.monotonic()
    plan=build()
    if '--verify-context' in sys.argv:
        plan['context_checks']=verify_context(plan)
    elif '--retain-context-checks' in sys.argv:
        previous=read(OUT/'local-boundary-plan.json')
        key=CONTEXT.relative_to(ROOT).as_posix()
        assert previous['source_sha256'][key]==plan['source_sha256'][key]
        identity=lambda p:[(r['wire'],r['native_owner'],r['shift_mm'],r['local_boundary_current_candidate_mm']) for r in p['rows']]
        assert identity(previous)==identity(plan)
        plan['context_checks']=previous['context_checks']
        plan['unchanged_context_checks_retained']=True
    plan['created_utc']=datetime.now(timezone.utc).isoformat()
    plan['worker_wall_seconds']=time.monotonic()-tick
    (OUT/'local-boundary-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=plan['status'],boundaries=len(plan['rows']),
        context_checks=plan.get('context_checks'),wall_seconds=plan['worker_wall_seconds'])),flush=True)
