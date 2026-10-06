"""Bind the full body ledger and distribution boundary to current CP2 datums.

Read-only native inventory and necessary length bounds, not routing or release.
Unresolved connector pads stay unresolved; no body centre substitutes for a pin.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
NATIVE = BASE / 'MTAHorizontalCandidate.FCStd'
OUT = BASE / 'whole-harness-shared-plan.json'
BRANCH_SOURCES='--branch-sources' in sys.argv
if BRANCH_SOURCES:
    NATIVE=BASE/'BranchSourceCandidate.FCStd'
    OUT=BASE/'whole-harness-current-plan.json'
BODY = ROOT / 'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(ends):
    return tuple(sorted(ends))


def distance(a, b):
    return math.dist(a, b)


def runout_lower_bound(start, departure, goal, goal_departure, strip):
    """Necessary length under declared3mm exit/9mm entry straight design."""
    a = [p + 3 * u for p, u in zip(start, departure)]
    b = [p + 9 * u for p, u in zip(goal, goal_departure)]
    return 3 + distance(a, b) + 9 + strip


def main():
    import FreeCAD as A
    started = datetime.now(timezone.utc)
    tick = time.monotonic()
    assert started < datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    assert not OUT.exists(), 'Receive the prior bound graph; no unchanged run'
    sys.path.insert(0, str(ROOT / 'tools/cad'))
    from whole_cat_interior import splice_inventory
    identity = splice_inventory()
    inputs = [NATIVE, BASE / 'interfaces.json', BASE / 'ato-stack-checks.json',
              BASE / 'mta-horizontal-corrected-plan.json', BODY, Path(__file__),
              ROOT / 'tools/cad/whole_cat_interior.py',
              ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json']
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
    short_inputs={}
    branch_proof=None
    if BRANCH_SOURCES:
        branch_path=BASE/'branch-source-static-checks.json'
        branch_proof=json.loads(branch_path.read_text(encoding='utf-8'))
        assert sha(NATIVE)==branch_proof['candidate_native_sha256']
        assert branch_proof['static_body_pipe_and_strip_contacts']==[]
        pins[branch_path.relative_to(ROOT).as_posix()]=sha(branch_path)
        short_inputs={row['id']:row for row in branch_proof['recipe']['routes']}
    interface = json.loads(inputs[1].read_text(encoding='utf-8'))
    ato = json.loads(inputs[2].read_text(encoding='utf-8'))
    layout = json.loads(inputs[3].read_text(encoding='utf-8'))
    body = json.loads(BODY.read_text(encoding='utf-8'))['conductors']
    assert len(body) == len({w['id'] for w in body}) == 80
    assert not layout['shared_package_contradictions']
    doc = A.openDocument(str(NATIVE))
    try:
        # No recompute/save: measurements belong to the pinned saved candidate.
        datums = {}
        owners = interface['service_boundary']['distribution_owners']
        for role in owners:
            ob = doc.getObject(role + '_CP2')
            assert ob and ob.Shape.isValid() and len(ob.Shape.Solids) == 1
            power615 = role in ['P_SYS', 'P_FRONT', 'P_REAR', 'G1']
            pitch, face, height = (7.5, 22, 5.5) if power615 else (6.75, 19, 4.5)
            for port in range(1, 6):
                pt = ob.Placement.multVec(A.Vector(5.5 + (port - 1) * pitch, face, height))
                out = ob.Placement.Rotation.multVec(A.Vector(0, 1, 0))
                datums[f'{role}.{port}'] = dict(native=ob.Name, point_mm=list(pt),
                    departure=list(out), insertion_strip_max_mm=14 if power615 else 11,
                    insertion_strip_min_mm=12 if power615 else 11,
                    basis='SKU envelope and provisional port pitch; not supplier pin datum',
                    route_restraint_and_lever_qualified=False)
        for row in ato['terminal_datums']:
            ob = doc.getObject(row['native'])
            assert ob and ob.Shape.isValid()
            # Read current expressions/placement, not stale pre-relocation JSON.
            pt = ob.Shape.BoundBox.Center
            pt.z = ob.Shape.BoundBox.ZMin
            datums[row['holder'] + '.' + row['role'].lower()] = dict(
                native=ob.Name, point_mm=list(pt), departure=row['wire_departure'],
                straight_grip_design_mm=9, basis='Nominal TE mouth; seating/axes provisional',
                route_restraint_and_lever_qualified=False)
        branch_rows = []
        for row in interface['FHAC']['branches']:
            role = row['role']
            ob = doc.getObject(role + '_CP2')
            for end in ['input', 'output']:
                direction = row[end + '_exit_direction']
                x = 51 if direction[0] > 0 else 0
                # Original exit is 10mm above the origin, not bbox centre11.
                pt = ob.Placement.multVec(A.Vector(x, 10.125, 10))
                dep = ob.Placement.Rotation.multVec(A.Vector(*direction))
                logical = role + ('.in' if end == 'input' else '.out')
                datums[logical] = dict(native=ob.Name, point_mm=list(pt), departure=list(dep),
                    supplied_shortest_including_strip_mm=84.5,
                    basis='FHAC0001ZXJ lead84.5..94.5; exit/OD/R6 provisional',
                    route_restraint_and_lever_qualified=False)
                branch_rows.append(dict(role=logical, **datums[logical]))
        for row in layout['factory_segments']:
            logical = 'F_' + row['holder'] + ('.in' if row['role'] == 'SOURCE' else '.out')
            sign = -1 if row['role'] == 'SOURCE' else 1
            datums[logical] = dict(native='MTA_' + row['holder'] + '_CP2',
                point_mm=row['wire_exit_mm'], departure=[sign, 0, 0],
                extension_port_mm=row['joint_extension_port_mm'],
                inline_connector='Joint_' + row['holder'] + '_' + row['role'],
                factory_cut_required_mm=20, available_factory_length_confirmed=False,
                basis='MTA35x22x16/opposite exits provisional; L140 not length/side',
                route_restraint_and_lever_qualified=False)
        for ep in layout['open_routes']:
            if ep['holder'] == 'S1':
                terminal = next(e for e in [ep['electrical_a'], ep['electrical_b']] if e.startswith('S1.'))
                datums[terminal] = dict(native=ep['joint'], point_mm=ep['start'],
                    departure=ep['tangent'], basis='Nominal TE barrel end; bearing conditional',
                    route_restraint_and_lever_qualified=False)
            elif ep['holder'] == 'S0':
                datums['S0.out'] = dict(native=ep['joint'], point_mm=ep['start'],
                    departure=ep['tangent'], basis='Nominal TE barrel end; bearing conditional',
                    route_restraint_and_lever_qualified=False)
        # Retained nominal source datums: bind BOTH ends without rebuilding
        # unchanged battery/F0/S0 pipes. Actual mating dimensions provisional.
        for role, native, point in [
                ('BAT.plus', 'XT60_CP2', [-73,-58.8,50]),
                ('BAT.minus', 'XT60_CP2', [-73,-58.8,57]),
                ('F0.in', 'F0_CP2', [-48,-58.8,50]),
                ('F0.out', 'F0_CP2', [3,-58.8,50])]:
            assert doc.getObject(native)
            datums[role] = dict(native=native, point_mm=point,
                basis='Retained source builder nominal cups/exits; polarity from markings',
                route_restraint_and_lever_qualified=False)
        sp = interface['S0_joint_plan']
        s0_in = [p + 26.9 * u for p, u in zip(sp['stud_centres_mm'][0], sp['ring_barrel_directions'][0])]
        datums['S0.in'] = dict(native='S0_ring_IN', point_mm=s0_in,
            departure=sp['ring_barrel_directions'][0],
            basis='Retained nominal S0 barrel, bearing conditional',
            route_restraint_and_lever_qualified=False)
        recipes = {w['id']: w for w in body}
        bound_rows = []
        for w in body:
            ends = [dict(role=e, **datums[e]) if e in datums else dict(
                role=e, status='OPEN_DATUM', basis='No current pin/mating datum; never use bbox centre')
                for e in [w['a'], w['b']]]
            row = dict(id=w['id'], a=w['a'], b=w['b'], net=w['net'], ends=ends,
                bound_end_count=sum('point_mm' in e for e in ends), route_status='OPEN_CP2_FULL_ROUTE',
                selected_R53_blank_mm=w.get('nominal_selected_blank_mm'),
                selected_R53_recipe=w.get('selected_recipe'),
                selected_R53_is_not_CP2_route_acceptance=True,
                material=w['material'], actual_cut_mm=None)
            if all('point_mm' in e for e in ends):
                row['straight_distance_only_mm'] = distance(ends[0]['point_mm'], ends[1]['point_mm'])
                row['distance_not_routed_length'] = True
            if w['id'] in short_inputs:
                row['route_status']='STATIC_NOMINAL_INPUT; grip and service OPEN'
                row['nominal_CP2_blank_mm']=short_inputs[w['id']]['nominal_blank_mm']
                row['proof']='branch-source-static-checks.json; not whole-harness acceptance'
            bound_rows.append(row)
        # Distribution boundary covers AUX/head/tail as well as body. Preserve
        # aliases for the same pair; an alias is never another bought wire.
        body_by_pair = {key([w['a'], w['b']]): w['id'] for w in body}
        assert len(body_by_pair) == 80
        boundary = []
        sb = interface['service_boundary']
        for source_scope in ['lower_boundary_wires', 'internal_tray_wires']:
            for row in sb[source_scope]:
                ends = row['ends']
                alias = body_by_pair.get(key(ends))
                boundary.append(dict(ends=ends, graph_aliases=row['graph_edge_aliases'],
                    body_id=alias, scope=source_scope,
                    ends_bound=sum(e in datums for e in ends),
                    route_status='OPEN_CP2_FULL_ROUTE',
                    resolved_datums={e: datums[e] for e in ends if e in datums}))
        assert len(boundary) == len({key(r['ends']) for r in boundary})
        # Necessary lower bounds reject too-short choices cheaply. Unknown
        # output board pads explicitly preclude a pass, even with spare lead.
        branch_limits = []
        for br in interface['FHAC']['branches']:
            logical = br['role'] + '.in'
            target = interface['FHAC']['supply_roles'][br['role']]
            direct = distance(datums[logical]['point_mm'], datums[target]['point_mm'])
            strip = datums[target]['insertion_strip_max_mm']
            min_strip = datums[target]['insertion_strip_min_mm']
            old_id = body_by_pair.get(key([logical, target]))
            old_blank = recipes[old_id].get('nominal_selected_blank_mm') if old_id else None
            minimum = direct + strip
            design_bound = runout_lower_bound(datums[logical]['point_mm'],
                datums[logical]['departure'], datums[target]['point_mm'],
                datums[target]['departure'], min_strip)
            route_id='W043' if br['role']=='F_PI' else 'XA01' if br['role']=='F_AUX' else None
            current=short_inputs.get(route_id)
            if current:
                assert distance(current['start_mm'],datums[logical]['point_mm'])<1e-7
                assert distance(current['end_mm'],datums[target]['point_mm'])<1e-7
            branch_limits.append(dict(holder=br['role'], wire_id=old_id,
                supply=target, factory_exit_mm=datums[logical]['point_mm'],
                target_mm=datums[target]['point_mm'], straight_distance_only_mm=direct,
                strip_max_mm=strip, straight_blank_at_max_strip_mm=minimum,
                absolute_straight_bound_at_min_strip_mm=direct + min_strip,
                design_runout_bound_at_min_strip_mm=design_bound,
                design_straights_mm=dict(factory_exit=3, WAGO_entry=9),
                supplied_shortest_mm=84.5, old_selected_blank_mm=old_blank,
                old_selected_blank_impossible=old_blank is not None and minimum > old_blank,
                actual_current_nominal_input_blank_mm=current['nominal_blank_mm'] if current else None,
                old_blank_superseded_in_candidate_only=bool(current),
                guaranteed_shortest_lead_too_short_under_design=design_bound > 84.5,
                upstream_branch_limit_mm=50 if br['role'] in ['F_PI','F_AUX'] else None,
                upstream_branch_limit_not_waived=True,
                decision='STATIC_INPUT_BELOW50; restraint and service OPEN; not R53 selection' if current else
                    'SHARED_RELOCATION_REQUIRED_OR_EXPLICIT_E3_LEAD_REDESIGN' if br['role'] in ['F_PI','F_AUX'] and design_bound > 50 else
                    'EXISTING_XB11_SPLICE_AND_HELU23502_EXTENSION_REUSE_REQUIRED' if br['role']=='F_HY' else
                    'REAL_EXTENSION_JOIN_STOCK_AND_RESTRAINT_REQUIRED' if design_bound > 84.5 else
                    'RADIUS_AND_OBSTACLES_STILL_REQUIRE_ROUTE; bound alone is not acceptance',
                output_status='OPEN: bind board/servo connector or existing insulated splice datum',
                physical_pass=False))
        known_pieces = {e['native']: e for e in datums.values()}
        reopen = []
        for name in sorted(known_pieces):
            ob = doc.getObject(name)
            assert ob and ob.Shape.isValid() and len(ob.Shape.Solids) == 1
            reopen.append(dict(native=name, valid=True, solids=1, volume_mm3=ob.Shape.Volume))
        missing = sorted({e['role'] for row in bound_rows for e in row['ends'] if 'point_mm' not in e} |
                         {e for row in boundary for e in row['ends'] if e not in datums})
        result = dict(status='FULL_GRAPH_BOUND_PARTIALLY_NOT_ROUTE_RELEASE', selected=False,
            physical_pass=False, W1_complete=False, W5_complete=False,
            source_sha256=pins, saved_native_reopen=reopen,
            body_conductors=bound_rows, distribution_boundary=boundary,
            FHAC_both_exits=branch_rows, branch_input_length_gate=branch_limits,
            missing_endpoint_roles=missing,
            scope=dict(body_conductors=80, body_ends=160,
                bound_body_ends=sum(r['bound_end_count'] for r in bound_rows),
                fully_bound_body_pairs=sum(r['bound_end_count'] == 2 for r in bound_rows),
                distribution_unique_pairs=len(boundary),
                non_body_boundary_pairs=sum(r['body_id'] is None for r in boundary),
                both_FHAC_ends=10, all_routes_qualified=False,
                fixed_module_internal_wires_not_exploded_into_extra_cables=True),
            stock=dict(main_MTA_inline2212411_candidate=8, source_additions=4, output_replacements=4,
                branch_extensions_not_chosen=True, stock_closed=False,
                retained_XB11_221412_role='P_AUX.2 to F_HY.in, NOT Pi solder joint',
                Pi_W077_W078_preserve_one_insulated_solder_joint=True,
                lead_gate_changes_require_real_join_material_and_restraint=True),
            splice_identity_correction=dict(current_binding=identity,
                original_CP2_interface_metadata_stale=True,
                mistake='Splice_L1 XB11 was wrongly mapped to W077/W078; native box is NOT proof of connection',
                corrected_new_layout_does_not_modify_pinned_original_CP2=True),
            assembly_sequence=[
                'Dorsal/side cosmetic covers removed; electrical assembly stays mounted.',
                '12 ATO straight extraction bays kept; no routine WAGO74-wire unclamping.',
                'Fit structure/mounts and unloaded connectors before crimped harness installation.',
                'Install retained battery/F0/S0 first; revised S1 and horizontal receivers then both MTA ends.',
                'Resolve ALL5 FHAC input/output leads before finalising supports; never park their bodies alone.',
                'Place24TE ends plus12 factory leg cable triplets; establish strain grips clear of service paths.',
                'Complete AUX/head/tail/PWM/balance and then one shared lever/tool/removal qualification.',
                'Only then freeze nominal fit lengths and whole shared stock/export selection.'],
            next_gate='Resolve missing physical endpoints and5branch lead graph, then ONE corridor plan for all wires before native mounts.',
            started_utc=started.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick, 3))
        # All retained MTA factory exit points stay; moved receiver GOALS do
        # not. A route worker may only consume this current endpoint bundle.
        router_endpoints=[]
        for ep in layout['open_routes']:
            owner=ep['target'].removesuffix('_CP2')
            role=next(e for e in [ep['electrical_a'],ep['electrical_b']] if e.startswith(owner+'.'))
            datum=datums[role]
            updated={k:v for k,v in ep.items() if k!='info'}
            updated['goal']=datum['point_mm']
            updated['goal_u']=[-x for x in datum['departure']]
            updated['goal_rebound_from_current_native']=True
            router_endpoints.append(updated)
        result['current_MTA_S0_S1_route_endpoints']=router_endpoints
        result['branch_source_static_proof']=branch_proof
        if BRANCH_SOURCES:
            result['next_gate']='Resolve F_PI lid/TE_OUT assembly sequence without another scalar offset, remaining3FHAC inputs/5outputs and missing exact/provisional board/leg interfaces; use THIS current receiver bundle, never stale P_FRONT/P_REAR goals.'
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        assert all(sha(ROOT / rel) == value for rel, value in pins.items())
        print('FULL_GRAPH', result['scope'], flush=True)
        print('BRANCH_LENGTH_GATE', branch_limits, flush=True)
        print('MISSING_ENDPOINTS', missing, flush=True)
    finally:
        A.closeDocument(doc.Name)


if __name__ == '__main__':
    main()
