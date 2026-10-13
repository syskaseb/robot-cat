"""Replace arbitrary final outboard grips with real socket-owned straight lands.

One common plan, not an accepted wire or mount. Keep eight Hip flex sections
and their rigid quarter joins; requalify the four direct Hip and eight Knee
flex sections whose endpoints/tangents change. All dimensions at the keyed
plug remain explicitly project reservations pending delivery measurement.
"""
import copy
import itertools
import json
import math
import time
from pathlib import Path

from plan_current_main_sources import ROOT, OUT, SHA
from plan_current_joint_local_looms import solve_loop
from plan_current_moving_looms import add, sub, mul, rotation
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import parts_for_loom, self_screen
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs

R = 31.5
LAND = 9.0
ANGLES = tuple(range(-15, 16))


def pose(row, angle, length):
    end = add(row['pivot_mm'], rotation(sub(row['moving_anchor_rest_world_mm'], row['pivot_mm']), row['joint_axis'], angle))
    tangent = rotation(row['moving_tangent_rest_world'], row['joint_axis'], angle)
    start = add(row['fixed_anchor_world_mm'], mul(row['fixed_tangent_world'], LAND))
    last = sub(end, mul(tangent, LAND))
    chord = math.dist(start, last)
    handles = tuple(dict.fromkeys((chord / 2, chord * .75, chord, R * 1.5, R * 2, R * 3)))
    for handle in handles:
        q = solve_loop(start, row['fixed_tangent_world'], last, tangent, length, (handle,))
        if q and q['sampled_minimum_R_mm'] >= R:
            return [line(row['fixed_anchor_world_mm'], start), q, line(last, end)]
    return None


def run():
    tick = time.monotonic()
    files = [OUT/'continuous-joint-family-plan.json', OUT/'harness-interfaces-plan.json',
             ROOT/'hardware/simulation/p0/e6-leg-compatibility.json']
    family, ends, axesdoc = [json.loads(p.read_text()) for p in files]
    family = copy.deepcopy(family)
    sources = {r['loom']: r for r in ends['looms']}
    changed = []
    for hip in family['hips']:
        row = next((r for r in family['knees'] if r['loom'] == hip['loom']), hip)
        source = sources[row['loom']]
        port = source['connector_reservation_world_mm'][source['project_connector_choice']]
        exit = source['cable_exit_world_axis']
        row['previous_moving_anchor_world_mm'] = row['moving_anchor_rest_world_mm']
        # End of final9mm straight land is at the provisional plug boundary;
        # its curve-to-land junction is port+23axis. No extra rigid return.
        row['moving_anchor_rest_world_mm'] = add(port, mul(exit, 14))
        row['moving_tangent_rest_world'] = mul(exit, -1)
        row['poses'] = []
        row['source_socket_reservation_mm'] = port
        row['moving_grip_centre_world_mm'] = add(port, mul(exit, 18.5))
        row['source_end_straight_land_mm'] = [add(port, mul(exit, 23)), add(port, mul(exit, 14))]
        row['source_owner'] = source['moving_saved_stage']
        changed.append(row)
    errors = []; trials = []
    for rows in ([r for r in changed if r['loom'].endswith(str(i))] for i in (1, 2, 3)):
        chord = max(math.dist(add(r['fixed_anchor_world_mm'], mul(r['fixed_tangent_world'], LAND)),
                             sub(add(r['pivot_mm'], rotation(sub(r['moving_anchor_rest_world_mm'], r['pivot_mm']), r['joint_axis'], a)),
                                 mul(rotation(r['moving_tangent_rest_world'], r['joint_axis'], a), LAND)))
                    for r in rows for a in (-15, 0, 15))
        lengths = [math.ceil((chord + extra * math.pi * R / 2) / 10) * 10 for extra in (1, 2, 3)]
        chosen = None
        for length in lengths:
            failed = [(r['loom'], a) for r in rows for a in (-15, 0, 15) if pose(r, a, length) is None]
            trials.append(dict(motor_role=rows[0]['loom'][-1], length_mm=length, failed_extrema=failed))
            if not failed:
                chosen = length
                break
        if chosen is None:
            errors.append(dict(motor_role=rows[0]['loom'][-1], cause='SOCKET_ENDPOINT_FAMILY_RADIUS_OR_LENGTH', tried_lengths_mm=lengths))
            continue
        for row in rows:
            row.update(flex_guide_mm=chosen, flex_length_mm=chosen, guide_mm=chosen+2*LAND)
            for angle in ANGLES:
                parts = pose(row, angle, chosen)
                if parts is None:
                    errors.append(dict(loom=row['loom'], angle=angle, cause='INTERMEDIATE_RADIUS_OR_LENGTH'))
                else:
                    row['poses'].append(dict(angle=angle, parts=parts))
            print('Socket-owned family', row['loom'], chosen, 'poses', len(row['poses']), flush=True)
    near = []; self_hits = []; budgets = []; cases = 0
    if not errors:
        for leg in ('FrontLeft', 'FrontRight', 'RearLeft', 'RearRight'):
            names = [r['loom'] for r in family['hips'] if r['physical_leg'] == leg]
            for hip, knee in itertools.product((-15, 0, 15), repeat=2):
                paths = []
                for name in names:
                    parts = parts_for_loom(family, name, hip, knee, axesdoc['axes'])
                    hit = self_screen(parts)
                    if hit:
                        self_hits.append(dict(loom=name, hip=hip, knee=knee, **hit))
                    paths.append(dict(wire=name, OD_mm=6, segments=sampling_parts(parts)))
                near.extend(dict(leg=leg, hip=hip, knee=knee, **q) for q in only_new_pairs([], paths))
                cases += 1
            for name in names:
                length = sum(p['length_mm'] for p in parts_for_loom(family, name, 0, 0, axesdoc['axes']))
                budgets.append(dict(loom=name, servo_to_body_grip_mm=length,
                    nominal_900mm_remaining_after_50mm_trim_mm=850-length,
                    body_fanout_is_not_yet_routed=True, static_extension_selected=False))
            print('Socket-owned whole leg screen', leg, flush=True)
    rejected = [r for r in near if r['status'] == 'REJECT_PLANNING_PROXIMITY']
    report = dict(status='REJECTED_SOCKET_ANCHORED_LEG_PLAN' if errors or rejected or self_hits else 'SOCKET_ANCHORED_LEG_MATH_ONLY',
        hips=family['hips'], knees=family['knees'], interstage=family['interstage'], errors=errors,
        changed_sections=[r['section'] for r in changed], unchanged_sections=8,
        trials=trials, near_pairs=near, rejected=rejected, self_contacts=self_hits, cases=cases,
        changed_math_poses=sum(len(r['poses']) for r in changed), length_budgets=budgets,
        topology='Final independent9mm land at real project socket exit replaces outboard grip plus long folding rigid approach.',
        invalidated='Old final12sections and all their old material/roots; unchanged8Hip/interstage require exact-equality receipt before reuse.',
        socket14mm_OD6_R31_5_are_project_reservations=True, manufacturer_dimensions_confirmed=False,
        selected=False, native_changed=False, W5_complete=False, physical_pass=False,
        continuous_sweep_verified=False,
        open=['actual material and all neighboring looms in sampled motions', 'all changed load paths and native grips',
              'actual body fanouts/termination/stock and assembly', 'delivered connector/cable and protection E3'],
        source_sha256={p.relative_to(ROOT).as_posix(): SHA(p) for p in files+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick, 3))
    (OUT/'socket-anchored-leg-plan.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'errors', 'changed_math_poses', 'cases', 'worker_seconds')}),
          'self', len(self_hits), 'mutual', len(rejected), flush=True)
    return report


if __name__ == '__main__':
    run()
