"""Single unselected six-block layout, with the entire attached-end scope.

Body envelopes are received conservative reservations. Cage datums are an
editable prototype registration, NOT a measured manufacturer cavity pitch.
Keep the R53 selection untouched until routes, native seats and service close.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
BLOCKS = {
    'G1': dict(centre=[66, 0], dz=10, angle=0, pitch=7.5,
               labels=[1, 5, 3, 4, 2], mouth_y=11),
    'G2': dict(centre=[111, 0], dz=10, angle=0, pitch=6,
               labels=[2, 3, 1, 4, 5], mouth_y=9.5),
    'FL_G': dict(centre=[-33, 40], dz=4, angle=180, pitch=6,
                 labels=[1, 2, 3, 4, 5], mouth_y=30.5),
    'FR_G': dict(centre=[-33, -40], dz=4, angle=180, pitch=6,
                 labels=[2, 1, 3, 4, 5], mouth_y=-30.5),
    'RL_G': dict(centre=[75, 40], dz=4, angle=180, pitch=6,
                 labels=[1, 2, 3, 4, 5], mouth_y=30.5),
    'RR_G': dict(centre=[75, -40], dz=4, angle=180, pitch=6,
                 labels=[3, 2, 1, 4, 5], mouth_y=-30.5),
}


def ports():
    result = {}
    for block, row in BLOCKS.items():
        cx, cy = row['centre']
        for index, label in enumerate(row['labels']):
            x, y = cx + (index - 2) * row['pitch'], row['mouth_y']
            outward = 1 if y > cy else -1
            if row['angle'] == 180:
                x, y, outward = 2 * cx - x, 2 * cy - y, -outward
            result[f'{block}.{label}'] = dict(
                point_mm=[x, y, 113.5 + row['dz']],
                outward_axis=[0, outward, 0], physical_cage_before_rotation=index + 1,
                provisional=True)
    return result


def attached_ends(graph):
    datums = ports()
    rows = []
    for wire in graph['wires']:
        for side in ('a', 'b'):
            endpoint = wire[side]
            if endpoint in datums:
                rows.append(dict(wire=wire['id'], end=endpoint,
                                 other_end=wire['b' if side == 'a' else 'a'],
                                 **datums[endpoint]))
    # The auxiliary circuit uses the prefix P0G2 for the same logical block.
    auxiliary = json.loads((ROOT / 'hardware/electronics/full-cat/aux-power-r1/circuit.json').read_text(encoding='utf-8'))
    aux = next(w for w in auxiliary['feeds'] if w['id'] == 'XA05')
    assert {aux['from'], aux['to']} == {'P0 G2.5', 'G_AUX.1'}
    rows.append(dict(wire='XA05', end='G2.5', other_end='G_AUX.1', **datums['G2.5']))
    assert len(rows) == 26 and len({r['wire'] for r in rows}) == 21
    assert len({r['end'] for r in rows}) == len(rows)
    assert set(datums) - {r['end'] for r in rows} == {f'{leg}_G.5' for leg in ('FL', 'FR', 'RL', 'RR')}
    assert {'W001', 'W003', 'W060', 'W061', 'XA05'} <= {r['wire'] for r in rows}
    return rows


def placement(A, row):
    cx, cy = row['centre']
    if row['angle'] == 180:
        return A.Placement(A.Vector(2 * cx, 2 * cy, row['dz']), A.Rotation(A.Vector(0, 0, 1), 180))
    return A.Placement(A.Vector(0, 0, row['dz']), A.Rotation())
