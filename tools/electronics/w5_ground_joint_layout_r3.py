"""Side-exit ground layout, with central blocks clear of the W011 corridor.

The received W011 wire/strap reaches Y-11.4; unshifted quarter-turn bodies
occupy that corridor. Move BOTH central blocks +8Y as a complete interface,
retaining their Z109 underside and the four outward-facing leg blocks.
"""
import copy
import w5_ground_joint_layout_r2 as base
ROOT = base.ROOT
BLOCKS = copy.deepcopy(base.BLOCKS)
for block, row in BLOCKS.items():
    row['translation_mm'] = [0, 8 if block in ('G1', 'G2') else 0, 0]


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
