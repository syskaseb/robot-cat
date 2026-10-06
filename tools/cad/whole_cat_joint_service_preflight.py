"""Reconcile the rejected allocation with its electrical endpoints, without CAD.

This diagnoses an existing failed recipe; it neither selects nor repairs it.
Old optional MTA joints are deliberately invalidated, not silently translated.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'


def rotate(point, axis, degrees):
    result = list(point)
    i, j = ((1, 2) if axis == 'x' else (0, 1))
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    result[i], result[j] = c*point[i]-s*point[j], s*point[i]+c*point[j]
    return result


def transform_endpoint(end, plan, inventory):
    """Use the same world-frame rigid recipe as CAD, once, including departure."""
    name = end.get('native')
    point = end.get('point_mm')
    if name is None or point is None:
        return None
    axis, angle, origin, target = 'z', 0, [0, 0, 0], [0, 0, 0]
    if name.startswith(('F_L', 'F_R')):
        side = 1 if name.startswith('F_L') else -1
        axis, angle = 'x', side*plan['bank_tilt_deg']
        origin = [0, side*62, 126]
        target = [plan['bank_shift_x_mm'], side*plan['bank_lane_y_mm'],
                  plan['bank_flange_z_mm']]
    elif name.startswith('MTA_'):
        leg = name.split('_')[1]
        bounds = inventory[name]['bounds_mm']
        origin = [(bounds[i]+bounds[i+3])/2 for i in range(3)]
        target = plan['MTA_centres_mm'][leg]
    elif name in plan['AUX_cell_members']:
        target = plan['AUX_cell_translation_mm']
    elif name == 'P_FRONT_CP2':
        target = plan['P_FRONT_translation_mm']
    elif name in plan['head_tail_centres_mm'] or name == 'F_PWM_CP2':
        bounds = inventory[name]['bounds_mm']
        origin = [(bounds[i]+bounds[i+3])/2 for i in range(3)]
        target = (plan['F_PWM_centre_mm'] if name == 'F_PWM_CP2'
                  else plan['head_tail_centres_mm'][name])
        angle = plan['F_TY_rotate_z_deg'] if name == 'F_TY_CP2' else 0
    elif name in {leg+'_'+suffix+'_CP2' for leg in ('FL', 'FR', 'RL', 'RR')
                  for suffix in ('P', 'G')} | {'D_FL_CP2', 'D_FR_CP2'}:
        target = [0, 0, -plan['side_WAGO_lower_z_mm']]
    else:
        return None
    moved = rotate([point[i]-origin[i] for i in range(3)], axis, angle)
    return dict(role=end['role'], native=name, old_point_mm=point,
                proposed_point_mm=[moved[i]+target[i] for i in range(3)],
                proposed_departure=rotate(end.get('departure', [0, 0, 0]), axis, angle),
                route_mount_restraint_status='INVALIDATED_NEEDS_SHARED_LAYOUT')


def classify_contact(pair, stale):
    if set(pair) == {'P_REAR_CP2', 'XA01_SHORT_STRIP_CP2'}:
        return 'DESIGNED_INSERTION_NOT_OBSTRUCTION'
    if set(pair) & set(stale):
        return 'STALE_JOINT_GEOMETRY_NOT_NEW_LAYOUT_OBSTRUCTION'
    return 'UNRESOLVED_RESERVATION_CONFLICT_NOT_SUPPLIER_COLLISION'


def reconcile(gate, graph, inventory):
    plan = gate['recipe']
    stale = sorted({e['inline_connector'] for row in graph['body_conductors']
                    for e in row['ends'] if e.get('native', '').startswith('MTA_')})
    rows = []
    for wire in graph['body_conductors']:
        changes = [r for end in wire['ends']
                   if (r := transform_endpoint(end, plan, inventory)) is not None]
        if changes:
            rows.append(dict(id=wire['id'], a=wire['a'], b=wire['b'], ends=changes,
                full_route_length_stock_accepted=False))
    fhac = [r for end in graph['FHAC_both_exits']
            if (r := transform_endpoint(end, plan, inventory)) is not None]
    contacts = [dict(**c, classification=classify_contact(c['pair'], stale))
                for c in gate['contacts']]
    input_roles = [dict(id=w['id'], a=w['a'], b=w['b'],
        decision='DIRECT_FACTORY_TO_DISTRIBUTION_IF_LENGTH_ALLOWS; '
                 'extra source joint needs actual extension justification')
        for w in graph['body_conductors']
        if any(e.get('inline_connector', '').endswith('_SOURCE') for e in w['ends'])]
    return dict(status='REJECTED_RECIPE_DEPENDENCIES_RECONCILED_NOT_READY',
        selected=False, physical_pass=False, W1_complete=False, W5_complete=False,
        invalidated_native_joints=stale, MTA_input_topology=input_roles,
        affected_conductors=rows, moved_FHAC_datums=fhac, classified_contacts=contacts,
        outside=gate['outside'],
        preserved_short_inputs=[dict(holder=r['holder'],
            blank_mm=r['actual_current_nominal_input_blank_mm'],
            branch_limit_mm=r['upstream_branch_limit_mm'])
            for r in graph['branch_input_length_gate'] if r['holder'] in ('F_PI', 'F_AUX')],
        blockers=['Rejected shared spatial allocation remains rejected',
            'All8 old MTA joints excluded until actual mates and full leads are replanned',
            'Unknown MTA factory lead length cannot justify extra4 source joints',
            'Affected full routes, mounts, restraints and assembly need a coherent replacement',
            'Remaining unbound endpoints in the source graph are not repaired by this transform'],
        next='Choose one jointly feasible allocation of source/logic and complete fuse cells; '
             'bind all dependent endpoints before detailed CAD; do not retry this recipe')


def main():
    started = datetime.now(timezone.utc); tick = time.monotonic()
    paths = [BASE / name for name in ('joint-service-layout.json',
             'whole-harness-board-plan.json', 'service-zone-inventory.json')]
    paths.append(Path(__file__))
    pins = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}
    gate, graph, inventory = [json.loads(p.read_text(encoding='utf-8')) for p in paths[:3]]
    result = reconcile(gate, graph, {r['name']: r for r in inventory['components']})
    result.update(source_sha256=pins, started_utc=started.isoformat(),
                  finished_utc=datetime.now(timezone.utc).isoformat(),
                  worker_wall_seconds=round(time.monotonic()-tick, 3))
    output = BASE / 'joint-service-preflight.json'
    assert not output.exists(), 'Receive existing result; no unchanged retry'
    output.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n',
                      encoding='utf-8')
    counts = {c: sum(r['classification'] == c for r in result['classified_contacts'])
              for c in {r['classification'] for r in result['classified_contacts']}}
    print(result['status'], len(result['affected_conductors']), 'affected conductors',
          len(result['invalidated_native_joints']), 'stale joints', counts)


if __name__ == '__main__':
    main()
