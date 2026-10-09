"""Two tangent circular arcs in3D, no spline curvature assumption."""
import math
import open_prototype_source_group as B

def arc(start,tangent,end):
    chord=B.sub(end,start)
    perpendicular=B.sub(chord,B.mul(tangent,B.dot(chord,tangent)))
    norm=B.dot(perpendicular,perpendicular)
    if norm<1e-10:
        assert B.dot(chord,tangent)>0
        return B.line(start,end)
    centre=B.add(start,B.mul(perpendicular,B.dot(chord,chord)/(2*norm)))
    radial=B.sub(start,centre);other=B.sub(end,centre)
    normal=B.unit(B.cross(radial,tangent))
    angle=math.atan2(B.dot(normal,B.cross(radial,other)),B.dot(radial,other))
    if angle<=0:angle+=2*math.pi
    mid=B.add(centre,B.add(B.mul(radial,math.cos(angle/2)),B.mul(B.cross(normal,radial),math.sin(angle/2))))
    return dict(kind='arc',start=start,mid=mid,end=end)

def connect(start,departure,end,arrival,d1,straight=9):
    """d1/d2 are mathematical tangent construction lengths, not wire cuts."""
    a=B.add(start,B.mul(departure,straight));b=B.sub(end,B.mul(arrival,straight))
    delta=B.sub(b,a)
    denominator=2*(B.dot(delta,arrival)+d1*(1-B.dot(departure,arrival)))
    if denominator<=1e-8:raise ValueError('No positive tangent construction')
    d2=(B.dot(delta,delta)-2*d1*B.dot(delta,departure))/denominator
    if d2<=1e-8:raise ValueError('Negative second tangent construction')
    joint=B.mul(B.add(B.mul(B.add(a,B.mul(departure,d1)),d2),B.mul(B.sub(b,B.mul(arrival,d2)),d1)),1/(d1+d2))
    first=arc(a,departure,joint)
    reverse=arc(b,B.mul(arrival,-1),joint)
    second={**reverse,'start':reverse['end'],'end':reverse['start']}
    parts=[B.line(start,a),first,second,B.line(b,end)]
    B.check_path(parts,start,end)
    return parts
