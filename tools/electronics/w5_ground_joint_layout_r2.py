"""Ground rail exits: central blocks face +X; four leg blocks face outward.

The raised R1 bodies hit existing thick positive feeds. This layout keeps
their original underside Z109 and changes the central footprints/directions
together, rather than moving already-accepted source wires independently.
"""
import copy
from w5_ground_joint_layout_r1 import ROOT, BLOCKS as RECEIVED, attached_ends as received_ends

BLOCKS = copy.deepcopy(RECEIVED)
for block, row in BLOCKS.items():
    row['dz'] = 0
    if block in ('G1', 'G2'): row['angle'] = -90


def rotate_xy(x, y, angle):
    return {0: (x, y), 90: (-y, x), -90: (y, -x), 180: (-x, -y)}[angle]


def ports():
    result = {}
    for block, row in BLOCKS.items():
        cx, cy = row['centre']
        original_side = 1 if row['mouth_y'] > cy else -1
        for index, label in enumerate(row['labels']):
            dx, dy = rotate_xy((index - 2) * row['pitch'], row['mouth_y'] - cy, row['angle'])
            ax, ay = rotate_xy(0, original_side, row['angle'])
            result[f'{block}.{label}'] = dict(point_mm=[cx + dx, cy + dy, 113.5],
                outward_axis=[ax, ay, 0], physical_cage_before_rotation=index + 1,
                provisional=True)
    return result


def attached_ends(graph):
    datums = ports()
    return [dict(row, **datums[row['end']]) for row in received_ends(graph)]


def placement(A, row):
    cx, cy = row['centre']
    dx, dy = rotate_xy(cx, cy, row['angle'])
    return A.Placement(A.Vector(cx - dx, cy - dy, 0), A.Rotation(A.Vector(0, 0, 1), row['angle']))
