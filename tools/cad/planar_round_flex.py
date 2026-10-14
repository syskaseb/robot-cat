"""Exact planar CSC flex with a tilted bridge and a proved length interval.

Unlike a horizontal bridge alone, its straight runs can accommodate tilted
moving lands without a negative bridge. This is nominal pose geometry, not
physical dynamic bend qualification or a continuous-motion sweep proof.
"""
import math
from plan_current_moving_looms import add,sub,mul,dot,norm,exact_turn_to
from plan_current_mta_interfaces import line


def domain(start,end,exit,beta_degrees,radius=31.5):
    delta=sub(end,start)
    assert abs(delta[0])<1e-6 and abs(exit[0])<1e-6 and exit[2]>.8
    side=1 if delta[1]>0 else -1;beta=math.radians(beta_degrees)
    u=[0,side*math.cos(beta),math.sin(beta)];down=[0,0,-1]
    angles=[math.acos(max(-1,min(1,dot(a,b)))) for a,b in ((down,u),(u,exit))]
    shift=add(mul(add(down,u),radius*math.tan(angles[0]/2)),mul(add(u,exit),radius*math.tan(angles[1]/2)))
    b0=(delta[1]-shift[1])/u[1];bc=-exit[1]/u[1]
    a0=shift[2]+u[2]*b0-delta[2];ac=u[2]*bc+exit[2]
    lo=0.;hi=850.
    for base,slope in ((a0,ac),(b0,bc)):
        if abs(slope)<1e-12:
            if base<-1e-8:return None
        elif slope>0:lo=max(lo,-base/slope)
        else:hi=min(hi,-base/slope)
    if hi<lo-1e-8:return None
    l0=a0+b0+radius*sum(angles);lc=ac+bc+1
    assert lc>0
    return dict(beta_degrees=beta_degrees,direction=u,angles=angles,a0=a0,ac=ac,b0=b0,bc=bc,
        l0=l0,lc=lc,minimum_mm=l0+lc*lo,maximum_mm=min(850,l0+lc*hi),radius_mm=radius)


def merge(intervals):
    result=[]
    for lo,hi in sorted(intervals):
        if hi<lo-1e-8:continue
        if result and lo<=result[-1][1]+1e-8:result[-1][1]=max(result[-1][1],hi)
        else:result.append([lo,hi])
    return result


def intersect(a,b):
    return merge([(max(x,z),min(y,w)) for x,y in a for z,w in b if max(x,z)<=min(y,w)+1e-8])


def build(start,end,exit,length,recipe):
    r=recipe;c=(length-r['l0'])/r['lc'];a=r['a0']+r['ac']*c;b=r['b0']+r['bc']*c
    if min(a,b,c)<-1e-6:return None
    parts=[];p=list(start);down=[0,0,-1]
    def straight(axis,distance):
        nonlocal p
        if distance>1e-8:
            q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
    straight(down,a)
    arc=exact_turn_to(p,down,r['direction'],r['radius_mm']);parts.append(arc);p=arc['end']
    straight(r['direction'],b)
    arc=exact_turn_to(p,r['direction'],exit,r['radius_mm']);parts.append(arc);p=arc['end']
    straight(exit,c)
    assert norm(sub(p,end))<1e-6,(p,end)
    assert abs(sum(p['length_mm'] for p in parts)-length)<1e-6
    return parts
