"""One complete 21-wire body-ground layout, not isolated end patches.

R4 body positions are retained except a six-mm G2 stand-off. All five G2
ends move together. G1 electrical and physical cage labels stay unchanged.
Correct W001 to the selected LAPP, not the TKD used for the four returns.
Dimensions of delivered cages and moving servo cables remain provisional.
"""
import copy
import json
import math
from w5_ground_joint_layout_r4 import ROOT, BLOCKS as ORIGINAL, ports as original_ports
from w5_ground_joint_layout_r1 import attached_ends as original_ends
from w5_ground_entries_r1 import profile as original_profile
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul, X, Y, Z
from w5_rounded_path import corner_offsets

BLOCKS = copy.deepcopy(ORIGINAL)
BLOCKS['G2']['translation_mm'][2] = 6
RETURNS = {'W025': 180, 'W036': 186, 'W062': 192, 'W063': 198}


def profile(wire):
    if wire == 'W001':
        return dict(OD_mm=3.1, radius_mm=12.4, wire_sku='LAPP0107001',
                    basis='selected BATTERY-INLET-P0 LAPP fixed installation', supplier_radius=True)
    info = original_profile(wire)
    info['wire_sku'] = ('TKD2500125' if wire in {*RETURNS, 'W061'} else
                        'HELU23501' if wire == 'XA05' else 'received prototype cable')
    return info


def ports():
    result = original_ports()
    for label, row in result.items():
        if label.startswith('G2.'):
            row['point_mm'][2] += 6
    return result


def attached_ends():
    graph = json.loads((ROOT / 'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))
    return [dict(row, **ports()[row['end']]) for row in original_ends(graph)]


def prefix(row):
    wire = row['wire']; radius = profile(wire)['radius_mm']
    c = CentreLine(row['point_mm'], row['outward_axis'])
    leg = '_G.' in row['end']
    straight = 31 if leg else 7 if wire == 'W003' else 3.5 if wire == 'W001' else 4 if wire == 'XA05' else 1
    c.line(add(c.p, mul(c.t, straight)))
    if wire in ('W025', 'W036') and row['end'].startswith('G1.'):
        # Both R21 arcs keep tangency while fanning away from the received
        # RR feed crossing. This is one paired front-return departure.
        side = 1 if wire == 'W025' else -1
        c.arc([0, side / math.sqrt(2), 1 / math.sqrt(2)], radius=radius)
        c.arc([0, -side / math.sqrt(2), 1 / math.sqrt(2)], math.pi / 4, radius=radius)
    else:
        c.arc(mul(Z, -1 if wire in ('W001', 'W003') else 1), radius=radius)
    c.line(add(c.p, mul(c.t, 5 if wire == 'W001' else 7)))
    return dict(row, profile=profile(wire), edges=c.edges, tip=c.p, tangent=c.t,
                straight_preparation_mm=straight, native_insulation_seat_complete=False)


def recipes():
    entries = [prefix(row) for row in attached_ends()]
    ends = {row['wire'] + '@' + row['end']: row for row in entries}
    old = json.loads((ROOT / 'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))
    result = []
    for wire, level in RETURNS.items():
        pair = [row for row in entries if row['wire'] == wire]
        assert len(pair) == 2
        a, b = pair
        pa, pb = a['tip'], b['tip']
        middle = [pa, [pa[0], pa[1], level], [pb[0], pb[1], level], pb]
        corner_offsets(middle, 21)
        result.append(dict(wire=wire, a=a, b=b, middle=middle, radius_mm=21,
                           body_route_complete=True, moving_route=False))
    a, b = ends['W061@G1.5'], ends['W061@G2.1']
    pa, pb = a['tip'], b['tip']
    middle = [pa, [pa[0], pa[1], 172], [pb[0], pb[1], 172], pb]
    corner_offsets(middle, 21)
    result.append(dict(wire='W061', a=a, b=b, middle=middle, radius_mm=21,
                       body_route_complete=True, moving_route=False))
    for row in old['routes']:
        if row['role'] != 'G':
            continue
        wire = row['wire']; a = ends[wire + '@' + row['body_end']]
        pa, pb = a['tip'], row['waypoints_mm'][-1]
        rank = int(row['loom'][-1]) - 1
        level = 175 + rank * 4
        middle = [pa, [pa[0], pa[1], level], [pb[0], pa[1], level],
                  [pb[0], pb[1], level], pb]
        corner_offsets(middle, 10)
        result.append(dict(wire=wire, a=a, b=None, middle=middle, radius_mm=10,
                           body_route_complete=True, moving_route=True,
                           loom=row['loom'], retained_moving_candidate_mm=row['moving_candidate_length_mm'],
                           retained_breakout_mm=pb, moving_envelope_not_requalified=True))
    a = ends['W001@G1.1']; tip = a['tip']
    middle = [[55.5, 75, 70], [55.5, 46, 70], [tip[0], 46, 70],
              [tip[0], tip[1], 70], tip]
    corner_offsets(middle, 12.4)
    result.append(dict(wire='W001', a=a, b=None, middle=middle, radius_mm=12.4,
                       lead_in=True, fixed_remote_end='received XT60 robot negative solder datum',
                       body_route_complete=True, moving_route=False, previous_max_blank_mm=150))
    a = ends['W003@G2.4']; tip = a['tip']
    bus = json.loads((ROOT / 'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json').read_text(encoding='utf-8'))
    src = bus['source_lead_datums']['W003']; level = 87
    middle = [src, [src[0], src[1], level], [src[0], 65, level],
              [tip[0], 65, level], [tip[0], tip[1], level], tip]
    corner_offsets(middle, 10)
    result.append(dict(wire='W003', a=a, b=None, middle=middle, radius_mm=10, lead_in=True,
                       fixed_remote_end='received BUS H3 G lead datum; SAME factory plug as W002',
                       body_route_complete=True, moving_route=False, factory_cable_nominal_mm=300))
    a = ends['W060@G1.2']; tip = a['tip']
    middle = [tip, [tip[0], tip[1], 170], [132.5, 0, 170], [132.5, 0, 95]]
    corner_offsets(middle, 10)
    result.append(dict(wire='W060', a=a, b=None, middle=middle, radius_mm=10,
                       retained_MAIN_tail=True, body_route_complete=True, moving_route=False,
                       retained_tail_radius_bound_mm=6, supplier_radius_unknown=True))
    a = ends['XA05@G2.5']
    b = prefix(dict(wire='XA05', end='G_AUX.1', point_mm=[110.5, -57, 113.5],
                    outward_axis=[-1, 0, 0], provisional=True))
    pa, pb = a['tip'], b['tip']; level = 165
    middle = [pa, [pa[0], pa[1], level], [pb[0], pb[1], level], pb]
    corner_offsets(middle, 15)
    result.append(dict(wire='XA05', a=a, b=b, middle=middle, radius_mm=15,
                       body_route_complete=True, moving_route=False, W1_access_reopened=True))
    assert len(result) == 21 and len({r['wire'] for r in result}) == 21
    return entries, result
