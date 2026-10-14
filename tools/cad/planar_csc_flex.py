"""Exact two-turn flex for a general oblique fixed-entry direction.

Three nonnegative straight lengths solve2D endpoint and length equations.
Either sign of the length coefficient is supported; no vertical-entry-only
assumption. Nominal geometry, not a mechanical sweep or physical bend proof.
"""
import math
from plan_current_moving_looms import add,sub,mul,dot,norm,exact_turn_to
from plan_current_mta_interfaces import line


def domain(start,end,entry,exit,beta_degrees,radius=31.5):
    delta=sub(end,start);assert max(abs(delta[0]),abs(entry[0]),abs(exit[0]))<1e-6
    side=1 if delta[1]>0 else -1;beta=math.radians(beta_degrees)
    bridge=[0,side*math.cos(beta),math.sin(beta)]
    angles=[math.acos(max(-1,min(1,dot(u,v)))) for u,v in ((entry,bridge),(bridge,exit))]
    if min(angles)<1e-7 or max(angles)>math.pi-1e-7:return None
    shift=add(mul(add(entry,bridge),radius*math.tan(angles[0]/2)),mul(add(bridge,exit),radius*math.tan(angles[1]/2)))
    y,z=delta[1]-shift[1],delta[2]-shift[2]
    det=entry[1]*bridge[2]-entry[2]*bridge[1]
    if abs(det)<1e-9:return None
    a0=(y*bridge[2]-z*bridge[1])/det;b0=(entry[1]*z-entry[2]*y)/det
    ac=(-exit[1]*bridge[2]+exit[2]*bridge[1])/det;bc=(-entry[1]*exit[2]+entry[2]*exit[1])/det
    lo,hi=0.,850.
    for base,slope in ((a0,ac),(b0,bc)):
        if abs(slope)<1e-12:
            if base<-1e-8:return None
        elif slope>0:lo=max(lo,-base/slope)
        else:hi=min(hi,-base/slope)
    if hi<lo-1e-8:return None
    l0=a0+b0+radius*sum(angles);lc=ac+bc+1
    limits=sorted((l0+lc*lo,l0+lc*hi))
    return dict(beta_degrees=beta_degrees,entry=entry,bridge=bridge,exit=exit,radius_mm=radius,
        a0=a0,ac=ac,b0=b0,bc=bc,l0=l0,lc=lc,c_min=lo,c_max=hi,
        minimum_mm=max(0,limits[0]),maximum_mm=min(850,limits[1]))


def build(start,end,length,r):
    if abs(r['lc'])<1e-10:
        if abs(length-r['l0'])>1e-6:return None
        c=(r['c_min']+r['c_max'])/2
    else:c=(length-r['l0'])/r['lc']
    a,b=r['a0']+r['ac']*c,r['b0']+r['bc']*c
    if min(a,b,c)<-1e-7:return None
    p=list(start);parts=[]
    def straight(axis,distance):
        nonlocal p
        if distance>1e-8:
            q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
    straight(r['entry'],a)
    arc=exact_turn_to(p,r['entry'],r['bridge'],r['radius_mm']);parts.append(arc);p=arc['end']
    straight(r['bridge'],b)
    arc=exact_turn_to(p,r['bridge'],r['exit'],r['radius_mm']);parts.append(arc);p=arc['end']
    straight(r['exit'],c)
    assert norm(sub(p,end))<1e-5,(p,end)
    assert abs(sum(p['length_mm'] for p in parts)-length)<1e-5
    return parts
