"""One balanced central ground rail between the two received DATA straps.

W011 strap ends at Y-11.4; W012 strap begins Y22.4. G2 half-depth after
rotation is15. Its centre therefore lies in (3.6,7.4) for zero contact.
Choose the midpoint5.5, giving1.9mm at BOTH straps, not a scalar search.
G1 moves with the rail and all ten attached central ends use the same datum.
"""
import copy
import w5_ground_joint_layout_r2 as base
ROOT = base.ROOT
BLOCKS = copy.deepcopy(base.BLOCKS)
CENTRAL_Y = (-11.4 + 15 + 22.4 - 15) / 2
assert abs(CENTRAL_Y - 5.5) < 1e-8
for block, row in BLOCKS.items():
    row['translation_mm'] = [0, CENTRAL_Y if block in ('G1', 'G2') else 0, 0]


def ports():
    result = base.ports()
    for endpoint, row in result.items():
        delta = BLOCKS[endpoint.rsplit('.', 1)[0]]['translation_mm']
        row['point_mm'] = [a + b for a, b in zip(row['point_mm'], delta)]
    return result


def attached_ends(graph):
    datums = ports()
    return [dict(row, **datums[row['end']]) for row in base.attached_ends(graph)]


def placement(A, row):
    return A.Placement(A.Vector(*row['translation_mm']), A.Rotation()) * base.placement(A, row)
