"""Constant-length down-to-tilted-up flex from exact arcs and straight runs.

No cubic handle/curvature approximation. Radius is an explicit project input,
not supplier dynamic qualification. Space, self-clearance and supports remain
separate gates. The outgoing axis must remain in the upward hemisphere.
"""
import math
from plan_current_moving_looms import add,sub,mul,norm,dot,exact_quarter,exact_turn_to
from plan_current_mta_interfaces import line


def state(start,end,exit,radius,last_length):
    assert exit[2]>.8 and abs(norm(exit)-1)<1e-7
    delta=sub(end,start);u=[delta[0],delta[1],0.]
    if norm(u)<1e-8:raise ValueError('No transverse U space')
    u=mul(u,1/norm(u))
    for _ in range(80):
        angle=math.acos(max(-1,min(1,dot(u,exit))))
        tangent=math.tan(angle/2)
        h=[delta[j]-exit[j]*(last_length+radius*tangent) for j in (0,1)]+[0.]
        if norm(h)<1e-8:raise ValueError('Degenerate transverse U space')
        next_u=mul(h,1/norm(h))
        if norm(sub(next_u,u))<1e-12:u=next_u;break
        u=next_u
    else:raise ValueError('Transverse direction did not converge')
    angle=math.acos(max(-1,min(1,dot(u,exit))));tangent=math.tan(angle/2)
    horizontal=[delta[j]-exit[j]*(last_length+radius*tangent) for j in (0,1)]+[0.]
    bridge=norm(horizontal)-radius*(1+tangent)
    first=start[2]-end[2]-radius+exit[2]*(last_length+radius*tangent)
    length=first+bridge+last_length+radius*(math.pi/2+angle)
    return dict(first_mm=first,bridge_mm=bridge,last_mm=last_length,
        direction=u,length_mm=length,second_angle_rad=angle)


def minimum(start,end,exit,radius=31.5):
    at=lambda c:state(start,end,exit,radius,c)
    low=0.;high=256.
    if at(low)['first_mm']<0:
        if at(high)['first_mm']<0:raise ValueError('Insufficient vertical U space')
        for _ in range(60):
            mid=(low+high)/2
            if at(mid)['first_mm']<0:low=mid
            else:high=mid
        low=high
    result=at(low)
    if result['bridge_mm']<-1e-7:raise ValueError('Transverse spacing below two radius turns')
    return result


def build(start,end,exit,length,radius=31.5):
    first=minimum(start,end,exit,radius)
    if length<first['length_mm']-1e-6:return None
    low=first['last_mm'];high=low+length
    if state(start,end,exit,radius,high)['length_mm']<length:return None
    for _ in range(64):
        mid=(low+high)/2
        if state(start,end,exit,radius,mid)['length_mm']<length:low=mid
        else:high=mid
    result=state(start,end,exit,radius,(low+high)/2)
    if min(result[k] for k in ('first_mm','bridge_mm','last_mm'))<-1e-7:return None
    parts=[];p=list(start);down=[0,0,-1]
    def straight(axis,distance):
        nonlocal p
        if distance>1e-8:
            q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
    straight(down,result['first_mm'])
    arc=exact_quarter(p,down,result['direction'],radius);parts.append(arc);p=arc['end']
    straight(result['direction'],result['bridge_mm'])
    arc=exact_turn_to(p,result['direction'],exit,radius);parts.append(arc);p=arc['end']
    straight(exit,result['last_mm'])
    assert norm(sub(p,end))<1e-6,(p,end)
    assert abs(sum(p['length_mm'] for p in parts)-length)<1e-6
    return parts
