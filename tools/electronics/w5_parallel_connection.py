"""Two exact circular arcs and a line between parallel terminal tangents."""
import math
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul, dot, norm


def connect(start, target, tangent, radius, straight=6):
    assert abs(norm(tangent)-1)<1e-7
    delta=[b-a for a,b in zip(start,target)]
    advance=dot(delta,tangent)-2*straight
    perpendicular=[d-t*dot(delta,tangent) for d,t in zip(delta,tangent)]
    offset=norm(perpendicular)
    assert advance>0 and offset>0
    normal=mul(perpendicular,1/offset)
    angle=math.asin(2*radius/math.hypot(advance,2*radius-offset))-math.atan2(2*radius-offset,advance)
    assert 0<angle<math.pi/2
    distance=(advance-2*radius*math.sin(angle))/math.cos(angle)
    assert distance>0
    c=CentreLine(start,tangent); c.line(add(c.p,mul(tangent,straight)))
    c.arc(normal,angle,radius); c.line(add(c.p,mul(c.t,distance)))
    bend=[(t-u*math.cos(angle))/math.sin(angle) for t,u in zip(tangent,c.t)]
    c.arc(bend,angle,radius); c.line(add(c.p,mul(tangent,straight)))
    assert math.dist(c.p,target)<1e-7 and math.dist(c.t,tangent)<1e-7
    return c.edges
