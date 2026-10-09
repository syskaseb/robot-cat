"""Pure 3-D tangent biarcs. No material or clearance verdict is inferred here.

Equal/unequal tangent lengths provide a small explicit corridor family. Every
result is checked for C1 continuity and the requested minimum bend radius.
"""
import math
from open_prototype_source_group import add, sub, mul, dot, unit, line, check_path


def tangent_arc(start, tangent, end):
    tangent = unit(tangent)
    chord = sub(end, start)
    along = dot(chord, tangent)
    transverse = sub(chord, mul(tangent, along))
    h = math.sqrt(dot(transverse, transverse))
    if h < 1e-8:
        if along <= 1e-8:
            raise ValueError('Reversed/zero collinear arc')
        return line(start, end)
    radius = dot(chord, chord) / (2*h)
    theta = 2*math.atan2(h, along)
    if theta > math.pi + 1e-8:
        raise ValueError('Reflex arc is not a useful corridor')
    normal = mul(transverse, 1/h)
    mid = add(start, add(mul(tangent, radius*math.sin(theta/2)),
                         mul(normal, radius*(1-math.cos(theta/2)))))
    return dict(kind='arc', start=start, mid=mid, end=end)


def biarc(start, t0, end, t1, ratio=1, minimum_radius=25.2):
    t0, t1 = unit(t0), unit(t1)
    v = sub(end, start)
    aa = 2*ratio*(1-dot(t0, t1))
    bb = 2*dot(v, add(t0, mul(t1, ratio)))
    cc = -dot(v, v)
    if abs(aa) < 1e-10:
        if bb <= 1e-10:
            raise ValueError('Parallel tangents face away from the corridor')
        d = -cc/bb
    else:
        d = (-bb+math.sqrt(bb*bb-4*aa*cc))/(2*aa)
    join = mul(add(add(mul(start, ratio), end), mul(sub(t0, t1), ratio*d)),
               1/(1+ratio))
    a = tangent_arc(start, t0, join)
    reverse = tangent_arc(end, mul(t1, -1), join)
    b = dict(reverse, start=reverse['end'], end=reverse['start'])
    parts = [a, b]
    check_path(parts, start, end, minimum_radius)
    return parts


def terminated(start, departure, end, arrival, ratio=1, waypoint=None,
               minimum_radius=25.2, land=9):
    first = add(start, mul(departure, land))
    last = sub(end, mul(arrival, land))
    if waypoint:
        point, tangent = waypoint
        middle = biarc(first, departure, point, tangent, ratio, minimum_radius)
        middle += biarc(point, tangent, last, arrival, ratio, minimum_radius)
    else:
        middle = biarc(first, departure, last, arrival, ratio, minimum_radius)
    parts = [line(start, first)] + middle + [line(last, end)]
    check_path(parts, start, end, minimum_radius)
    return parts
