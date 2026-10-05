"""One connected DATA layout: all four blocks, all 16 wires, no isolated exit.

Rotate four blocks within their footprints. Include BUS and all three links,
not just the twelve servo branches. This is a prototype routing candidate.
"""
import json
from w5_ground_joint_layout_r4 import ROOT
from w5_leg_fanouts_r1 import CAGE_ORDER
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul
from w5_rounded_path import corner_offsets


def ports():
    result = {}
    for leg in ('FL', 'FR', 'RL', 'RR'):
        x = 3 if leg.startswith('F') else 111
        side = 1 if leg.endswith('L') else -1
        for slot, logical in enumerate(CAGE_ORDER['D_' + leg]):
            # Exact 180-degree transform of saved nominal cage registration.
            result[f'D_{leg}.{logical}'] = dict(
                point_mm=[x + 13.5 - slot * 6.75, side * 49.5, 113.5],
                outward_axis=[0, side, 0])
    return result


def prefix(end):
    p = ports()[end]
    c = CentreLine(p['point_mm'], p['outward_axis'])
    c.line(add(c.p, mul(c.t, 6)))
    c.arc([0, 0, 1], radius=10)
    c.line(add(c.p, mul(c.t, 6)))
    return dict(edges=c.edges, tip=c.p, tangent=c.t)


def recipes():
    raw = json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))['routes']
    graph = json.loads((ROOT/'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))['wires']
    result = []
    for old in raw:
        if old['role'] != 'D': continue
        a = prefix(old['body_end']); p = a['tip']; q = old['waypoints_mm'][-1]
        level = 154 + 4 * int(old['loom'][-1])
        result.append(dict(wire=old['wire'], a=a, b=None, radius_mm=10,
            middle=[p, [p[0], p[1], level], [q[0], p[1], level], [q[0], q[1], level], q],
            retained_moving_candidate_mm=old['moving_candidate_length_mm'], strip_mm=11))
    for wire, level in [('W007', 180), ('W011', 184), ('W012', 188)]:
        link = next(w for w in graph if w['id'] == wire)
        a, b = prefix(link['a']), prefix(link['b']); p, q = a['tip'], b['tip']
        result.append(dict(wire=wire, a=a, b=b, radius_mm=10,
            middle=[p, [p[0], p[1], level], [q[0], q[1], level], q], strip_mm=22))
    bus = ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    src = json.loads(bus.read_text(encoding='utf-8'))['source_lead_datums']['W002']
    a = prefix('D_FL.1'); p = a['tip']
    result.append(dict(wire='W002', a=a, b=None, lead_in=True, radius_mm=10,
        middle=[src, [src[0], src[1], 150], [p[0], p[1], 150], p], strip_mm=11))
    required = {w['id'] for w in graph if w['a'].startswith('D_') or w['b'].startswith('D_')}
    assert {r['wire'] for r in result} == required and len(result) == 16
    for r in result: corner_offsets(r['middle'], r['radius_mm'])
    return result


if __name__ == '__main__':
    print('Complete DATA scope:', len(recipes()), 'wires;', len(ports()), 'cages; not selected')
