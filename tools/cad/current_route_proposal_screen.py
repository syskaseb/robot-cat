"""Route proposals use the actual 1.25mm design core budget, not 1.55.

The legacy mesh screen reserves extra space for a different planning task.
No proxy result qualifies a route: lazy exact and whole-curve gates follow.
"""
import itertools
import numpy as np


def clear(scene, points, row):
    data = scene.data
    root = np.asarray(row['bundle_root_world_mm'])
    end = np.asarray(row['receiver_point_mm'])
    for p in points:
        if np.any(p < data['low']) or np.any(p > data['high']):
            return False
        if np.linalg.norm(p - end) >= 1.1 and scene.material_hit(p) is not None:
            return False
        key = tuple(np.floor(p / scene.cell).astype(int))
        indexes = [scene.wires[k] for delta in itertools.product((-1, 0, 1), repeat=3)
                   if (k := tuple(a + b for a, b in zip(key, delta))) in scene.wires]
        if not indexes:
            continue
        ix = np.concatenate(indexes)
        close = np.linalg.norm(data['wire_points'][ix] - p, axis=1) < data['wire_radii'][ix] + 1.25 - 1e-6
        for i in ix[close]:
            name = str(data['wire_names'][data['wire_ids'][i]])
            if name in ('new/' + row['wire'] + '/source', 'new/' + row['wire'] + '/receiver'):
                continue
            if name.startswith('leg/' + row['loom'] + '/') and np.linalg.norm(p - root) < 6:
                continue
            return False
    return True
