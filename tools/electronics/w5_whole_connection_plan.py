"""Bind all49 received body routes to retention and continuous leg looms.

Plan physical interfaces before more native CAD. Matching endpoint positions
alone does not qualify a continuous cable: compare its two path tangents too.
No collision, moving-range or manufacturing selection is inferred here.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import math
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import save, sha

ROOT = N.ROOT
BASE = N.BASE
OUT = BASE/'w5-whole-connection-plan-r1'
GRAPH = ROOT/'hardware/electronics/power-platform/wiring-p0.json'
CORRIDORS = BASE/'w5-leg-corridors-r3/intent.json'
FANOUT = BASE/'w5-leg-fanouts-r5/intent.json'
V_RECEIPT = BASE/'w5-leg-joint-source-layout-r1/checks.json'
CENTRAL_RETENTION = BASE/'w5-central-retention-layout-r4/checks.json'
SIDE_RETENTION = BASE/'w5-side-retention-plan-r1/plan.json'
NATIVE_RECEIPTS = [BASE/'w5-central-retention-native-r1/checks.json',
                   BASE/'w5-side-retention-native-r1/checks.json']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def incoming_tangent(A, Part, path, endpoint):
    """Tangent pointing FROM this open curve INTO the endpoint interface."""
    point = A.Vector(*endpoint)
    candidates = []
    for edge in path.Edges:
        for at_start in (True, False):
            parameter = edge.FirstParameter if at_start else edge.LastParameter
            if (edge.valueAt(parameter)-point).Length > 1e-5:
                continue
            tangent = edge.tangentAt(parameter)
            if at_start:
                tangent = -tangent
            tangent.normalize()
            candidates.append(tangent)
    assert len(candidates) == 1, ('Endpoint must bind one actual open path end', endpoint, len(candidates))
    return candidates[0]


def main():
    import FreeCAD as A, Part
    start = datetime.now(timezone.utc)
    assert not (OUT/'plan.json').exists(), 'Preserve existing result'
    pins = [Path(__file__), GRAPH, CORRIDORS, FANOUT, V_RECEIPT,
            N.CENTRAL, CENTRAL_RETENTION, SIDE_RETENTION, *NATIVE_RECEIPTS]
    for receipt_path in NATIVE_RECEIPTS:
        receipt = read(receipt_path)
        assert receipt['restored'] and receipt['relocated_reopen']
        for rel, value in {**receipt['source_sha256'], **receipt['files']}.items():
            assert sha(ROOT/rel) == value, rel
            pins.append(ROOT/rel)
    central = read(N.CENTRAL)
    graph = {r['id']:r for r in read(GRAPH)['wires']}
    aux_path = BASE/'aux-power-r1/circuit.json'; pins.append(aux_path)
    aux = next(r for r in read(aux_path)['feeds'] if r['id']=='XA05')
    graph['XA05'] = dict(id='XA05', a=aux['from'].removeprefix('P0 '), b=aux['to'])
    body_rows = read(FANOUT)['routes']
    corridors = read(CORRIDORS)['routes']
    assert len(body_rows)==36 and len(corridors)==12
    moving_path_file = BASE/'w5-leg-corridors-r3/CENTERLINES_WORLD.brep'
    pins.append(moving_path_file)
    moving_paths = Part.read(str(moving_path_file)).childShapes()
    assert len(moving_paths)==12
    inherited_paths_file = BASE/'w5-leg-joint-source-layout-r1/CENTERLINES_WORLD.brep'
    inherited_paths = Part.read(str(inherited_paths_file)).childShapes()
    v_rows = read(V_RECEIPT)['routes']; assert len(v_rows)==len(inherited_paths)==36
    v_paths = {r['wire']:s for r,s in zip(v_rows,inherited_paths) if r['role']=='V'}
    pins.append(inherited_paths_file)
    frames = []
    for row, moving in zip(corridors,moving_paths):
        centre = row['fixed_breakout_provisional_mm']
        incoming = incoming_tangent(A,Part,moving,centre)
        cores = []
        for body in [r for r in body_rows if r['loom']==row['loom']]:
            wire = body['wire']; endpoint = body['waypoints_mm'][-1]
            if body['role']=='V':
                path = v_paths[wire]
                basis = inherited_paths_file.relative_to(ROOT).as_posix()
            else:
                path_file = N.centreline(wire, central)
                path = Part.read(str(path_file)); pins.append(path_file)
                basis = path_file.relative_to(ROOT).as_posix()
            approach = incoming_tangent(A,Part,path,endpoint)
            onward = -incoming
            cosine = max(-1, min(1, approach.dot(onward)))
            turn = math.degrees(math.acos(cosine))
            offset = A.Vector(*endpoint)-A.Vector(*centre)
            cores.append(dict(wire=wire,role=body['role'],logical_body_end=body['body_end'],
                logical_servo_end=body['servo_end'],body_path=basis,
                virtual_split_point_mm=endpoint,offset_from_bundle_axis_mm=list(offset),
                transverse_offset=abs(offset.dot(incoming))<1e-6,
                incoming_body_tangent=list(approach),outgoing_to_servo_tangent=list(onward),
                join_direction_change_deg=turn,
                tangent_continuous=turn<1e-5,
                virtual_split_is_not_a_connector=True,new_splice_count=0))
        assert {r['role'] for r in cores}=={'D','G','V'}
        frames.append(dict(loom=row['loom'],fixed_split_axis_mm=centre,
            moving_path=moving_path_file.relative_to(ROOT).as_posix(),
            moving_path_child_index=len(frames),moving_path_incoming=list(incoming),
            rigid_servo_carriers=row['carriers'],cores=cores,
            continuous_join_complete=all(r['tangent_continuous'] for r in cores),
            fixed_and_moving_grips_complete=False,moving_range_complete=False))
        print('WHOLE_JOIN',row['loom'],[round(r['join_direction_change_deg'],3) for r in cores],flush=True)
    central_ends = read(CENTRAL_RETENTION)['endpoint_recipes']
    side_ends = read(SIDE_RETENTION)['endpoints']
    assert len(central_ends)==10 and len(side_ends)==35
    frozen_wires = set(central['routes'])
    accepted = read(BASE/'w5-branch-joint-routes-r3/checks.json')['accepted']
    pins.append(BASE/'w5-branch-joint-routes-r3/checks.json')
    frozen_wires.update(r['wire'] for r in accepted if r['wire'] not in central['routes'])
    assert len(frozen_wires)==37
    v_wires = set(v_paths); assert len(v_wires)==12 and not frozen_wires & v_wires
    endpoint_rows = []
    for wire in sorted(frozen_wires | v_wires):
        circuit = graph[wire]
        for end in (circuit['a'], circuit['b']):
            block = end.split('.')[0]
            if block in ('G1','G2'):
                seats=[r for r in central_ends if r['wire']==wire]
                if wire=='W061':
                    seats=[r for r in seats if r['key']==('W061_A' if block=='G1' else 'W061_B')]
                assert len(seats)==1,(wire,end)
                role='qualified_central_insulation_seat'
                basis=NATIVE_RECEIPTS[0].relative_to(ROOT).as_posix()
                note='Logical circuit port and provisional rotated physical station are distinct; do not relabel from station order.'
            elif any(r['wire']==wire and r['end']==end for r in side_ends):
                role='qualified_side_insulation_seat'
                basis=NATIVE_RECEIPTS[1].relative_to(ROOT).as_posix(); note=None
            elif block in {r['loom'] for r in frames}:
                role='continuous_factory_plug_via_unqualified_split_and_moving_grips'
                basis=BASE.joinpath('w5-leg-end-preparation-r1/interface.json').relative_to(ROOT).as_posix()
                note='One plug and one cable per servo, not three purchased cables or a splice at the split.'
            elif end.startswith('F_') and end.endswith('.out') and wire in v_wires:
                role='qualified_bank_local_V_end_whole_loom_open'
                basis='hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r47/manifest.json'; note=None
            else:
                role='remote_fixed_end_requires_exact_current_restraint_binding'
                basis=None; note='Do not infer current retention from an obsolete or shifted wire name.'
            endpoint_rows.append(dict(wire=wire,logical_end=end,role=role,basis=basis,note=note))
    assert len(endpoint_rows)==98
    counts={role:sum(r['role']==role for r in endpoint_rows) for role in {r['role'] for r in endpoint_rows}}
    assert sorted(counts.values())==[5,10,12,35,36],counts
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'plan.json',dict(status='WHOLE_49_BODY_WIRE_CONNECTION_AND_RETENTION_PLAN',
        body_wire_count=49,end_count=98,endpoint_roles=counts,endpoints=endpoint_rows,
        continuous_factory_looms=12,split_interfaces=frames,
        discontinuous_core_joins=sum(not c['tangent_continuous'] for f in frames for c in f['cores']),
        whole_joint_range_or_collision_proof=False,
        retained_outside49_scope=dict(P0_wire_ids=sorted(set(graph)-frozen_wires-v_wires-{'XA05'}),
            AUX_ids=['XA01','XA02','XA03','XA04','XA06'],
            note='Preserve previously qualified bank/source/head/tail/Pi/AUX recipes; reconcile their changed owner attachments at selection, not rebuild their unchanged wiring.'),
        ordered_plan=[
            'Preserve bankR47,37received body paths and centralDeck/sideCarrier/Cover.',
            'Receive all12 continuous factory split interfaces together. Match position AND tangent; no added electrical junction.',
            'Use the measured saved path directions to allocate one common finite-radius return and fixed/moving grip scheme BEFORE native brackets or movement checks.',
            'Bind5remote fixed ends BAT.minus/BUS.D/BUS.G/MAIN.GND/G_AUX.1 to actual current insulation restraints.',
            'Support necessary long flights using fixed body owners; never attach a fixed split to a moving servo carrier.',
            'Execute whole staged mount/removal of hoods, fixedCarrier, bank+Cover and crossing leads; changed sweep interfaces only.',
            'Unify49wire lengths with31otherP0 roles, remaining AUX, selected head/tail/Pi recipes and unique tie stock; then one linked export and selection.'],
        no_bounding_box_collision_claim=True,no_new_splices=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)}))
    print('WHOLE_CONNECTION_PLAN',counts,flush=True)


if __name__=='__main__':main()
