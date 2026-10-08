"""Rebind Stage3 endpoints to retained mounts without rebuilding either CAD.

Preserve net identity. Stored world datums are transformed by the delta between
old and current object placements, never by the current placement twice.
Supplier envelopes and cable exits remain explicit provisional reservations.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import math
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT = BASE / 'wiring-checkpoint/endpoint-plan.json'
CURRENT = BASE / 'mounting-checkpoint/RetentionMountsAssembly.FCStd'
EXPECTED = '5e8bf36ada7b150297aa527d59eeea1d975cfefdee9fc3d526ddd4391b62cc71'
LEG_MAP = ROOT / 'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    b = shape.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]


def short_source_screen(rows, boundary):
    """Necessary bounds only: reject obsolete short blanks before CAD."""
    result = []
    seen = set()
    for row in rows + boundary:
        ends = row.get('ends', [])
        datums = row.get('resolved_datums', {})
        if ends and isinstance(ends[0], dict):
            datums = {e['role']: e for e in ends}
        for holder in ('F_PI', 'F_AUX', 'F_HY', 'F_HP', 'F_TY'):
            role = holder + '.in'
            if role not in datums or holder in seen:
                continue
            peers = [e for name,e in datums.items() if name != role and 'point_mm' in e]
            if not peers or 'point_mm' not in datums[role]:
                continue
            seen.add(holder)
            a, b = datums[role], peers[0]
            direct = math.dist(a['point_mm'], b['point_mm'])
            strip = b.get('insertion_strip_min_mm', 0)
            prefuse = holder in ('F_PI', 'F_AUX')
            result.append(dict(holder=holder, target=b['role'],
                straight_plus_min_strip_mm=direct+strip,
                retained_nominal_blank_mm=row.get('nominal_CP2_blank_mm'),
                factory_minimum_mm=84.5, prefuse_project_limit_mm=50 if prefuse else None,
                prefuse_impossible_at_current_datums=prefuse and direct+strip > 50,
                factory_minimum_too_short=direct+strip > 84.5,
                bound_not_route_or_safety_acceptance=True))
    return result


def main():
    import FreeCAD as A
    started = datetime.now(timezone.utc)
    tick = time.monotonic()
    plan = read(BASE / 'layout.json')
    # layout.json inherited most endpoints from the earlier harness graph,
    # NOT from its displayed OpenPrototype.FCStd. Use that actual datum donor.
    donor_graph_path = BASE.parent / 'whole-harness-board-plan.json'
    donor_graph = read(donor_graph_path)
    old_path = BASE.parent / 'BranchSourceCandidate.FCStd'
    context_path = BASE / 'OpenPrototypePlan.FCStd'
    distribution_path = BASE / 'mounting-checkpoint/distribution-mount-plan.json'
    assert sha(CURRENT) == EXPECTED, 'Current mount source changed'
    assert sha(old_path) == donor_graph['source_sha256'][old_path.relative_to(ROOT).as_posix()]
    sources = [CURRENT, old_path, context_path, distribution_path,
        donor_graph_path, BASE / 'layout.json', LEG_MAP, Path(__file__)]
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}
    old = A.openDocument(str(old_path))
    current = A.openDocument(str(CURRENT))
    context = A.openDocument(str(context_path))
    distribution = {r['native']: r for r in read(distribution_path)['distribution']}
    rows = copy.deepcopy(plan['body_conductors'])
    boundary = copy.deepcopy(plan['distribution_boundary'])
    changed = []
    unresolved = []
    try:
        inventory = {}
        for obj in context.Objects + current.Objects:
            if 'Shape' in obj.PropertiesList and not obj.Shape.isNull():
                if obj.Name.endswith('_CP2') or obj.Name.startswith('P0_'):
                    inventory[obj.Name] = dict(bounds_mm=bounds(obj.Shape),
                        placement_origin_mm=list(obj.Placement.Base),
                        placement_rotation_xyzw=list(obj.Placement.Rotation.Q))

        def bind(end):
            name = end.get('native')
            if not name or 'point_mm' not in end:
                return
            before = old.getObject(name)
            after = current.getObject(name) or context.getObject(name)
            if name in distribution:
                spec = distribution[name]
                port = int(end['role'].rsplit('.', 1)[1])
                assert 1 <= port <= 5
                # Declared envelope-derived entry allowance, not a supplier
                # pitch. The old 415 pitch placed port5 outside its casing.
                # Keep5.5mm edge margins until the delivered layout is known.
                b = bounds(after.Shape)
                width = spec['size_mm'][0]
                pitch = (width - 11) / 4
                x = b[0] + 5.5 + (port-1)*pitch
                y = b[1] if spec['side'] == 'L' else b[4]
                z = b[2] + spec['size_mm'][2]/2
                original = end['point_mm']
                end.update(point_mm=[x,y,z], departure=[0,-1 if spec['side']=='L' else 1,0],
                    current_frame_bound=True, frame_source=CURRENT.relative_to(ROOT).as_posix(),
                    basis='Current flat lever-up casing; inward entry; project5.5mm edge/equal-pitch allowance, NOT manufacturer datum',
                    datum_is_not_manufacturer_pin=True, provisional_pitch_mm=pitch)
                changed.append(dict(role=end['role'], native=name, old_mm=original,
                    current_mm=end['point_mm'], reason='Re-derived from actual current rail casing frame'))
                return
            if before is None or after is None:
                unresolved.append(dict(role=end['role'], native=name,
                    reason='Native not present in both source documents'))
                end['current_frame_bound'] = False
                return
            point = A.Vector(*end['point_mm'])
            delta = after.Placement.multiply(before.Placement.inverse())
            result = delta.multVec(point)
            restored = delta.inverse().multVec(result)
            assert (restored-point).Length < 1e-7
            original = list(point)
            end['point_mm'] = list(result)
            if 'departure' in end:
                end['departure'] = list(delta.Rotation.multVec(A.Vector(*end['departure'])))
            end['current_frame_bound'] = True
            end['frame_source'] = CURRENT.relative_to(ROOT).as_posix()
            end['datum_is_not_manufacturer_pin'] = 'provisional' in end.get('basis', '').lower()
            if (result-point).Length > 1e-7:
                changed.append(dict(role=end['role'], native=name, old_mm=original,
                    current_mm=list(result), delta_mm=list(result-point)))

        for row in rows:
            for end in row['ends']:
                bind(end)
            row['route_status'] = 'CURRENT_ENDPOINT_PLAN_ONLY; NO_ROUTE_ACCEPTANCE'
            row['actual_cut_mm'] = None
            row.pop('straight_distance_only_mm', None)
            if 'nominal_CP2_blank_mm' in row:
                row['obsolete_nominal_CP2_blank_mm'] = row.pop('nominal_CP2_blank_mm')
                row['obsolete_route_proof'] = row.pop('proof', None)
        for row in boundary:
            for role, datum in row['resolved_datums'].items():
                datum.setdefault('role', role)
                bind(datum)
            row['route_status'] = 'CURRENT_ENDPOINT_PLAN_ONLY; NO_ROUTE_ACCEPTANCE'

        legs = []
        for loom in read(LEG_MAP)['looms']:
            name = 'P0_' + loom['pcb']
            obj = context.getObject(name)
            verified = obj is not None and max(abs(x-y) for x, y in zip(
                bounds(obj.Shape), loom['pcb_bounds_world_mm'])) < 1e-5
            record = copy.deepcopy(loom)
            record['current_pcb_native'] = name
            record['source_world_frame_retained'] = verified
            legs.append(record)
            for signal, connection in loom['electrical'].items():
                wire = next(r for r in rows if r['id'] == connection['wire'])
                assert {wire['a'], wire['b']} == {connection['servo_end'], connection['body_end']}
                end = next(e for e in wire['ends'] if e['role'] == connection['servo_end'])
                end.update(physical_loom=loom['loom'], current_pcb_native=name,
                    pin_cavity_order_known=False, source_world_frame_retained=verified,
                    factory_plugs_installed=1, second_socket='NC',
                    connector_reservations_mm=loom['connector_reservation_world_mm'] if verified else None,
                    cable_exit_axis=loom['cable_exit_world_axis'] if verified else None,
                    basis='Inherited provisional cable exit reservation, NOT individual D/V/G pin position',
                    status='CABLE_EXIT_RESERVATION' if verified else 'OPEN_CURRENT_LEG_FRAME')

        assert len(rows) == len({r['id'] for r in rows}) == 80
        assert {(r['id'], r['a'], r['b'], r['net']) for r in rows} == {
            (r['id'], r['a'], r['b'], r['net']) for r in plan['body_conductors']}
        assert len(legs) == 12
        for row in rows:
            if all('point_mm' in e for e in row['ends']):
                row['straight_distance_only_mm'] = math.dist(*[e['point_mm'] for e in row['ends']])
        unbound = [e['role'] for r in rows for e in r['ends'] if 'point_mm' not in e]
        result = dict(status='CURRENT_DATUM_REBIND_AND_LEG_EXIT_PLAN', selected=False,
            stage_completed=False, W5_complete=False, physical_pass=False,
            source_sha256=pins, current_native=CURRENT.relative_to(ROOT).as_posix(),
            body_conductors=rows, distribution_boundary=boundary, components=inventory,
            short_source_length_screen=short_source_screen(rows, boundary),
            changed_endpoints=changed, unresolved_native_roles=unresolved,
            leg_looms=legs, point_bound_ends=160-len(unbound), remaining_nonpoint_roles=unbound,
            distinction='Cable reservations are not individual supplier pins or completed routes',
            next='Bind BUS actual connector reference; joint route/restraint/assembly allocation; preserve unknown U1 padmap',
            started_utc=started.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=time.monotonic()-tick)
        assert all(sha(ROOT / p) == digest for p, digest in pins.items())
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(dict(output=OUT.relative_to(ROOT).as_posix(),
            changed_endpoints=len(changed), unresolved_native_role_count=len(unresolved),
            leg_frames_retained=sum(r['source_world_frame_retained'] for r in legs),
            point_bound_ends=result['point_bound_ends'], worker_wall_seconds=result['worker_wall_seconds'])), flush=True)
    finally:
        A.closeDocument(current.Name)
        A.closeDocument(old.Name)
        A.closeDocument(context.Name)


if __name__ == '__main__':
    main()
