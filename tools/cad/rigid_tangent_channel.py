"""Exact bounded-radius 3D rigid-member channel between orthogonal tangents.

One transverse S offsets into the end plane; four circle/straight/circle
tangent constructions give geometric candidates. No obstacle or continuous
motion clearance is implied. Radius is a project requirement, not cable data.
"""
import math
from plan_current_moving_looms import add, sub, mul, dot, cross, norm
from plan_current_mta_interfaces import line


def unit(v):
    n=norm(v);assert n>1e-10;return mul(v,1/n)


def turn(start, direction, toward, angle, radius):
    assert abs(dot(direction,toward))<1e-7
    assert 0<angle<2*math.pi
    count=math.ceil(angle/(math.pi/2));parts=[];u=direction;v=toward;p=start
    for _ in range(count):
        a=angle/count
        end=add(add(p,mul(u,radius*math.sin(a))),mul(v,radius*(1-math.cos(a))))
        mid=add(add(p,mul(u,radius*math.sin(a/2))),mul(v,radius*(1-math.cos(a/2))))
        parts.append(dict(kind='arc',start=p,mid=mid,end=end,radius_mm=radius,length_mm=radius*a))
        u,v=add(mul(u,math.cos(a)),mul(v,math.sin(a))),add(mul(u,-math.sin(a)),mul(v,math.cos(a)))
        p=end
    return parts,u


def candidates(start, entry, end, exit, radius=31.5):
    u=unit(entry);v=unit(exit)
    assert abs(dot(u,v))<1e-7,'This channel requires orthogonal endpoint tangents'
    w=unit(cross(u,v));height=dot(sub(end,start),w);prefix=[];point=start
    if abs(height)>1e-7:
        r=max(radius,abs(height)/2);a=math.acos(1-abs(height)/(2*r));toward=mul(w,1 if height>0 else -1)
        first,heading=turn(point,u,toward,a,r)
        second,_=turn(first[-1]['end'],heading,add(mul(u,math.sin(a)),mul(toward,-math.cos(a))),a,r)
        prefix=first+second;point=second[-1]['end']
    assert abs(dot(sub(end,point),w))<1e-6
    output=[]
    for left,right in ((1,1),(-1,-1),(1,-1),(-1,1)):
        cs=add(point,mul(v,left*radius));ce=sub(end,mul(u,right*radius))
        d=sub(ce,cs);x=dot(d,u);y=dot(d,v);distance=math.hypot(x,y)
        if distance<1e-8 or distance<abs(left-right)*radius:continue
        theta=math.atan2(y,x)+math.asin((left-right)*radius/distance)
        t=add(mul(u,math.cos(theta)),mul(v,math.sin(theta)))
        normal=add(mul(u,-math.sin(theta)),mul(v,math.cos(theta)))
        ps=sub(cs,mul(normal,left*radius));pe=sub(ce,mul(normal,right*radius))
        span=dot(sub(pe,ps),t)
        if span<-1e-6 or norm(sub(sub(pe,ps),mul(t,span)))>1e-6:continue
        a=(left*theta)%(2*math.pi);b=(right*(math.pi/2-theta))%(2*math.pi)
        parts=list(prefix)
        if a>1e-8:
            q,_=turn(point,u,mul(v,left),a,radius);parts+=q
            assert math.dist(q[-1]['end'],ps)<1e-6
        if span>1e-8:parts.append(line(ps,pe))
        if b>1e-8:
            q,last=turn(pe,t,mul(normal,right),b,radius);parts+=q
            assert math.dist(q[-1]['end'],end)<1e-6
            assert math.dist(last,v)<1e-6
        for one,two in zip(parts,parts[1:]):assert math.dist(one['end'],two['start'])<1e-6
        if not parts:continue
        output.append(dict(parts=parts,guide_mm=sum(p['length_mm'] for p in parts),
                           topology=['L' if left>0 else 'R','S','L' if right>0 else 'R'],
                           transverse_offset_mm=height,project_minimum_R_mm=radius))
    # Close endpoint poses also admit three-circle paths. Construct middle
    # circles from the two radius2R intersections instead of stretching a
    # near-full CSC return. These are geometric topologies, not offset trials.
    for sign in (1,-1):
        cs=add(point,mul(v,sign*radius));ce=sub(end,mul(u,sign*radius))
        d=sub(ce,cs);distance=norm(d)
        if not 1e-8<distance<=4*radius:continue
        normal=unit(cross(w,d));mid=mul(add(cs,ce),.5)
        height=math.sqrt(max(0,(2*radius)**2-(distance/2)**2))
        for side in (1,-1):
            cm=add(mid,mul(normal,side*height));p1=mul(add(cs,cm),.5);p2=mul(add(cm,ce),.5)
            parts=list(prefix);heading=u;last=point
            for centre,target,s in ((cs,p1,sign),(cm,p2,-sign),(ce,end,sign)):
                before=sub(last,centre);after=sub(target,centre)
                aa=math.atan2(dot(before,v),dot(before,u));bb=math.atan2(dot(after,v),dot(after,u))
                angle=(s*(bb-aa))%(2*math.pi)
                if angle>1e-8:
                    arc,heading=turn(last,heading,unit(sub(centre,last)),angle,radius)
                    parts+=arc
                    assert math.dist(arc[-1]['end'],target)<1e-6
                last=target
            assert math.dist(heading,v)<1e-6
            output.append(dict(parts=parts,guide_mm=sum(p['length_mm'] for p in parts),
                topology=['L','R','L'] if sign>0 else ['R','L','R'],
                transverse_offset_mm=dot(sub(end,start),w),project_minimum_R_mm=radius))
    return sorted(output,key=lambda q:q['guide_mm'])
