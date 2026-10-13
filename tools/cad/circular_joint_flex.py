"""Constant-length circular/straight flex in an actual joint-normal plane.

Unlike a180degree single cubic, circular pieces preserve the required radius
exactly. Their radius may change with angle at constant total cable length.
The same turning topology must work for every pose of one physical section.
"""
import math
from plan_current_moving_looms import add,sub,mul,dot,cross,norm
from plan_current_mta_interfaces import line
from rigid_tangent_channel import unit,turn

def csc(start,u,end,v,normal,radius,signs):
    n=unit(normal);u=unit(u);v=unit(v);w=unit(cross(n,u));left,right=signs
    assert abs(dot(n,u))<1e-6 and abs(dot(n,v))<1e-6
    assert abs(dot(sub(end,start),n))<1e-5
    cs=add(start,mul(w,left*radius));ce=add(end,mul(cross(n,v),right*radius))
    d=sub(ce,cs);x=dot(d,u);y=dot(d,w);distance=math.hypot(x,y)
    if distance<1e-8 or distance<abs(left-right)*radius:return None
    theta=math.atan2(y,x)+math.asin(max(-1,min(1,(left-right)*radius/distance)))
    tangent=add(mul(u,math.cos(theta)),mul(w,math.sin(theta)));sn=cross(n,tangent)
    ps=sub(cs,mul(sn,left*radius));pe=sub(ce,mul(sn,right*radius))
    span=dot(sub(pe,ps),tangent)
    if span<-1e-6:return None
    assert norm(sub(sub(pe,ps),mul(tangent,span)))<1e-5
    delta=math.atan2(dot(v,w),dot(v,u));a=(left*theta)%(2*math.pi);b=(right*(delta-theta))%(2*math.pi)
    parts=[]
    if a>1e-8:
        q,_=turn(start,u,mul(w,left),a,radius);parts+=q
        assert math.dist(parts[-1]['end'],ps)<1e-5
    if span>1e-8:parts.append(line(ps,pe))
    if b>1e-8:
        q,heading=turn(pe,tangent,mul(sn,right),b,radius);parts+=q
        assert math.dist(parts[-1]['end'],end)<1e-5 and math.dist(heading,v)<1e-6
    if not parts:return None
    return dict(parts=parts,length_mm=sum(p['length_mm'] for p in parts),radius_mm=radius,signs=list(signs))

def plane_shift(start,heading,normal,offset,radius=31.5):
    """Rigid same-heading S; new flex plane derived from real source socket."""
    if abs(offset)<1e-7:return [],start
    direction=mul(unit(normal),1 if offset>0 else -1);height=abs(offset)
    angle=math.pi/2 if height>=2*radius else math.acos(1-height/(2*radius))
    first,u=turn(start,heading,direction,angle,radius);parts=list(first);p=parts[-1]['end']
    if height>2*radius:
        q=add(p,mul(direction,height-2*radius));parts.append(line(p,q));p=q
    toward=add(mul(heading,math.sin(angle)),mul(direction,-math.cos(angle)))
    last,u=turn(p,u,toward,angle,radius);parts+=last
    assert math.dist(u,heading)<1e-6
    assert abs(dot(sub(parts[-1]['end'],start),unit(normal))-offset)<1e-6
    return parts,parts[-1]['end']

def fixed_length(start,u,end,v,normal,signs,length,min_radius=31.5):
    lo=min_radius;first=csc(start,u,end,v,normal,lo,signs)
    if first is None or first['length_mm']>length+1e-7:return None
    if abs(first['length_mm']-length)<1e-7:return first
    hi=lo
    # Radius growth is a bounded scalar equation for a declared topology,
    # not a set of translated CAD variants or relaxed minimum radius.
    for _ in range(14):
        hi*=1.2;q=csc(start,u,end,v,normal,hi,signs)
        if q is None:return None
        if q['length_mm']>=length:break
    else:return None
    for _ in range(42):
        mid=(lo+hi)/2;q=csc(start,u,end,v,normal,mid,signs)
        if q is None:return None
        if q['length_mm']<length:lo=mid
        else:hi=mid
    result=csc(start,u,end,v,normal,(lo+hi)/2,signs)
    # A turning angle can wrap0->2pi while radius changes. That branch has
    # a real length discontinuity, so the requested length is not feasible;
    # do not accept a bisection endpoint on the other side of that jump.
    if abs(result['length_mm']-length)>1e-6:return None
    assert result['radius_mm']>=min_radius
    return result

def fixed_length_straight_slack(start,u,end,v,normal,signs,length,min_radius=31.5):
    """Translate the round return outward, retain radius; add straight slack.

    Increasing radius was nonmonotone near a CSC centre crossing and forced
    almost-full circles. Same-heading straight legs vary the free return's
    depth instead; they are FREE cable, not additional grip claims.
    """
    def at(offset):
        s=add(start,mul(u,offset));e=sub(end,mul(v,offset))
        q=csc(s,u,e,v,normal,min_radius,signs)
        if q is None:return None
        parts=([line(start,s)] if offset>1e-8 else [])+q['parts']+([line(e,end)] if offset>1e-8 else [])
        return dict(parts=parts,length_mm=sum(p['length_mm'] for p in parts),radius_mm=min_radius,straight_slack_each_mm=offset,signs=list(signs))
    first=at(0)
    if first is None or first['length_mm']>length+1e-7:return None
    if abs(first['length_mm']-length)<1e-7:return first
    lo,hi=0.,100.;last=at(hi)
    if last is None or last['length_mm']<length:return None
    for _ in range(42):
        mid=(lo+hi)/2;q=at(mid)
        if q is None:return None
        if q['length_mm']<length:lo=mid
        else:hi=mid
    q=at((lo+hi)/2)
    return q if abs(q['length_mm']-length)<1e-6 else None
