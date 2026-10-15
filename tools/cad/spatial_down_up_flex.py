"""Exact spatial two-arc flex, down entry and X-axis-tilted up exit.

Nominal geometric construction only. Positive straight runs, actual material,
retention, cable specifications and motion qualification remain separate gates.
Unlike planar helpers, fixed and moving lands need not share an X coordinate.
"""
import math
from plan_current_moving_looms import add, sub, mul, dot, norm, exact_turn_to
from plan_current_mta_interfaces import line

DOWN = [0, 0, -1]


def solution(start, end, exit, length, radius=31.5, beta_degrees=0):
    assert abs(norm(exit)-1) < 1e-7 and abs(exit[0]) < 1e-8 and exit[2] > 0
    dx, dy, dz = sub(end, start)
    assert abs(dx) > 1e-6, 'Use planar construction for equal X'
    beta=math.radians(beta_degrees);cb=math.cos(beta);sb=math.sin(beta)
    assert cb>.1, 'Bridge inclination too close to a vertical singularity'
    first_angle=math.acos(-sb);first_scale=radius*math.tan(first_angle/2)
    bearing = math.atan2(dy, dx)
    if abs(exit[1]) < 1e-9:
        reach = math.hypot(dx, dy)
        bridge = [dx/reach*cb, dy/reach*cb, sb]
        b = (reach - 2*radius)/cb
        c = (length-math.pi*radius-b*(1+sb)+dz)/2
        a = b*sb+c-dz
        return dict(a=a, b=b, c=c, bridge=bridge, exit=exit, radius=radius) if min(a,b,c) >= -1e-7 else None

    def trial(phi):
        u = [math.cos(phi)*cb, math.sin(phi)*cb, sb]
        if abs(u[0]) < 1e-8: return None
        angle = math.acos(max(-1., min(1., dot(u, exit))))
        shift = add(mul(add(DOWN,u),first_scale), mul(add(u,exit),radius*math.tan(angle/2)))
        b = (dx-shift[0])/u[0]
        c = (dy-shift[1]-b*u[1])/exit[1]
        a = shift[2]+b*u[2]+c*exit[2]-dz
        total = a+b+c+radius*(first_angle+angle)
        return total-length, dict(a=a,b=b,c=c,bridge=u,exit=exit,radius=radius)

    # Do not bracket across the singularity at bridge.X=0.
    span = min(math.radians(40), abs(math.atan2(abs(dx),abs(dy)))*.9)
    previous = None; found = []
    for i in range(161):
        phi = bearing-span+2*span*i/160
        item = trial(phi)
        if item is None: previous=None; continue
        if previous is not None and previous[1][0]*item[0] <= 0:
            lo, left = previous; hi=phi
            for _ in range(48):
                mid=(lo+hi)/2; probe=trial(mid)
                if left[0]*probe[0] <= 0: hi=mid
                else: lo=mid; left=probe
            error, result = trial((lo+hi)/2)
            if abs(error)<1e-6 and min(result[k] for k in ('a','b','c')) >= -1e-7:
                found.append((abs((lo+hi)/2-bearing),result))
        previous=(phi,item)
    return min(found,key=lambda r:r[0])[1] if found else None


def build(start, end, exit, length, radius=31.5, beta_degrees=0):
    recipe=solution(start,end,exit,length,radius,beta_degrees)
    if recipe is None: return None
    p=list(start); parts=[]
    for axis, distance, turn in ((DOWN,recipe['a'],recipe['bridge']),
                                 (recipe['bridge'],recipe['b'],exit),
                                 (exit,recipe['c'],None)):
        if distance>1e-8:
            q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
        if turn is not None:
            arc=exact_turn_to(p,axis,turn,radius);parts.append(arc);p=arc['end']
    assert norm(sub(p,end))<1e-5,(p,end)
    assert abs(sum(p['length_mm'] for p in parts)-length)<1e-5
    return parts
