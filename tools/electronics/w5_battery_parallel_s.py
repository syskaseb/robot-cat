"""Exact two-arc S connection for the parallel opposed terminal departures."""
import math
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul


def route(start,target,radius=12.4,straight=6):
    delta=[b-a for a,b in zip(start,target)];advance=delta[1]-2*straight
    offset=math.hypot(delta[0],delta[2]);assert advance>0 and offset>0
    normal=[delta[0]/offset,0,delta[2]/offset]
    phase=math.atan2(2*radius-offset,advance)
    ratio=2*radius/math.hypot(advance,2*radius-offset)
    assert ratio<=1
    angle=math.asin(ratio)-phase;assert 0<angle<math.pi/2
    length=(advance-2*radius*math.sin(angle))/math.cos(angle);assert length>=0
    c=CentreLine(start,[0,1,0]);c.line(add(c.p,[0,straight,0]))
    c.arc(normal,angle,radius);c.line(add(c.p,mul(c.t,length)))
    bend=[(y-t*math.cos(angle))/math.sin(angle) for y,t in zip([0,1,0],c.t)]
    c.arc(bend,angle,radius);c.line(add(c.p,[0,straight,0]))
    assert math.dist(c.p,target)<1e-7 and math.dist(c.t,[0,1,0])<1e-7
    return dict(edges=c.edges,body_mm=sum(e['length_mm'] for e in c.edges),
        start=start,target=target,start_tangent=[0,1,0],end_tangent=[0,1,0],
        radius_mm=radius,straight_end_allowance_mm=straight)
