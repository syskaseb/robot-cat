"""One whole power-pair corridor hypothesis, not a clearance/stock approval.

Retains MAIN departure and the axial Pi grip. The former extra W080 tail
was for a retired grip and is not a fixed electrical termination.
"""
import feline_tangent_routes as t


def middle(wire):
    radius, y = {'W079': (15.9, -76.8875),
                 'W080': (12.4, -80.3875)}[wire]
    z = 75.8791703544916
    rear = 71.51810963471377 + radius
    points = [(-21.5, y, z), (-21.5-radius, y, z-radius),
              (-80., y, z-radius), (-80-radius, y+radius, z-radius),
              (-80-radius, rear-radius, z-radius), (-80., rear, z-radius),
              (96.5, rear, z-radius), (96.5+radius, rear, z),
              (96.5+radius, rear, 101.6-radius),
              (96.5+radius, rear-radius, 101.6)]
    tangents = {0: (0, 0, -1), 2: (-1, 0, 0), 4: (0, 1, 0),
                6: (1, 0, 0), 8: (0, 0, 1)}
    result = [t.arc(a, tangents[i], b) if i in tangents else t.line(a, b)
              for i, (a, b) in enumerate(zip(points, points[1:]))]
    assert t.min_radius(result) >= radius - 1e-7
    for a, b in zip(result, result[1:]):
        ta = a.get('end_tangent') or t.unit(t.sub(a['end'], a['start']))
        tb = b.get('tangent') or t.unit(t.sub(b['end'], b['start']))
        assert t.norm(t.sub(ta, tb)) < 1e-7
    return result
