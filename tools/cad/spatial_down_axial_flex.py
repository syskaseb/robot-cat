"""Exact CSC family: down entry, axial X exit, inclined spatial bridge.

No supplier or physical qualification. Positive runs and total length are
solved together. The actual source axis is retained instead of forcing UP.
"""
import math
from plan_current_moving_looms import add,sub,mul,dot,norm,exact_turn_to
from plan_current_mta_interfaces import line
DOWN=[0,0,-1]


def build(start,end,exit,length,beta_degrees,radius=31.5):
    assert abs(abs(exit[0])-1)<1e-7 and abs(exit[1])+abs(exit[2])<1e-7
    dx,dy,dz=sub(end,start);assert abs(dy)>1e-6
    beta=math.radians(beta_degrees);cb=math.cos(beta);sb=math.sin(beta)
    angle1=math.acos(-sb);k1=radius*math.tan(angle1/2)
    # Opposite axial direction provides the turn-back space; Y follows the
    # actual endpoint. Do not bracket through bridge.Y=0.
    sign=1 if dy>0 else -1
    lo,hi=(math.pi/2+.001,math.pi-.001) if exit[0]>0 else (.001,math.pi/2-.001)
    def trial(phi):
        u=[math.cos(phi)*cb,sign*math.sin(phi)*cb,sb]
        angle2=math.acos(max(-1,min(1,dot(u,exit))))
        k2=radius*math.tan(angle2/2)
        shift=add(mul(add(DOWN,u),k1),mul(add(u,exit),k2))
        b=(dy-shift[1])/u[1];c=(dx-shift[0]-b*u[0])/exit[0]
        a=shift[2]+b*u[2]-dz
        return a+b+c+radius*(angle1+angle2)-length,(a,b,c,u)
    previous=None;options=[]
    for i in range(121):
        phi=lo+(hi-lo)*i/120;item=trial(phi)
        if previous is not None and previous[1][0]*item[0]<=0:
            left,p=previous;right=phi
            for _ in range(45):
                mid=(left+right)/2;q=trial(mid)
                if p[0]*q[0]<=0:right=mid
                else:left=mid;p=q
            err,recipe=trial((left+right)/2)
            if abs(err)<1e-6 and min(recipe[:3])>=-1e-7:options.append(recipe)
        previous=(phi,item)
    if not options:return None
    a,b,c,u=options[0];p=list(start);parts=[]
    for axis,distance,turn in ((DOWN,a,u),(u,b,exit),(exit,c,None)):
        if distance>1e-8:q=add(p,mul(axis,distance));parts.append(line(p,q));p=q
        if turn is not None:
            arc=exact_turn_to(p,axis,turn,radius);parts.append(arc);p=arc['end']
    assert norm(sub(p,end))<1e-5 and abs(sum(p['length_mm'] for p in parts)-length)<1e-5
    return parts
