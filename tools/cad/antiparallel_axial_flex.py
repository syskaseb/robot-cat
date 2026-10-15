"""Constant-length two-arc return with opposed axial end tangents.

The existing down-entry family need not fit every leg: this complete macro
family enters along the Hip axis, turns in its transverse displacement plane
and returns axially to the real source. Radius is NOT reduced to get a pass.
"""
import math
from plan_current_moving_looms import add,sub,mul,dot,norm,exact_turn_to
from plan_current_mta_interfaces import line


def build(start,end,entry,length,bridge_cosine=0,radius=31.5):
    assert abs(norm(entry)-1)<1e-7 and -.9<=bridge_cosine<=.9
    delta=sub(end,start);longitudinal=dot(delta,entry)
    transverse=sub(delta,mul(entry,longitudinal));reach=norm(transverse)
    if reach<2*radius-1e-7:return None
    sine=math.sqrt(1-bridge_cosine**2)
    bridge=add(mul(entry,bridge_cosine),mul(transverse,sine/reach))
    b=(reach-2*radius)/sine
    difference=longitudinal-b*bridge_cosine;total=length-math.pi*radius-b
    a,c=(total+difference)/2,(total-difference)/2
    if min(a,b,c)<-1e-7:return None
    exit=mul(entry,-1);p=list(start);parts=[]
    for axis,distance,turn in ((entry,a,bridge),(bridge,b,exit),(exit,c,None)):
        if distance>1e-8:q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
        if turn is not None:
            arc=exact_turn_to(p,axis,turn,radius);parts.append(arc);p=arc['end']
    assert norm(sub(p,end))<1e-5 and abs(sum(q['length_mm'] for q in parts)-length)<1e-5
    return parts
