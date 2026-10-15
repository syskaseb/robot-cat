"""Certified separation lower bounds for these box-minus-bore fixtures.

Bounding boxes NEVER establish contact. They enclose actual curve pieces and
provide distance lower bounds; removed cylindrical bores add analytic radial
constraints. Unknown at subdivision limit returns False, never a clear claim.
Additional negative cuts can only remove material, so ignoring them is safe.
"""
import math
from build_front_fixed_port_clearance import placement


def bbox(s):
    b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def interval_gap(a,A,b,B):return max(0,a-B,b-A)


def lower_bound(curve_box,positive_box,cylinders):
    q=curve_box;p=positive_box
    delta=[interval_gap(q[i],q[i+3],p[i],p[i+3]) for i in range(3)]
    bound=math.sqrt(sum(x*x for x in delta))
    for c in cylinders:
        x,y,z=c['base_mm'];radius=c['radius_mm']
        if z>p[2]+1e-8 or z+c['height_mm']<p[5]-1e-8:continue
        radial_max=math.hypot(max(abs(q[0]-x),abs(q[3]-x)),max(abs(q[1]-y),abs(q[4]-y)))
        radial=max(0,radius-radial_max)
        bound=max(bound,math.hypot(radial,delta[2]))
    return bound


def prove(recipe,kind,curve,required,max_depth=20,max_nodes=4096):
    if kind not in ('body','cap'):return False
    positives=([recipe['base_bounds_mm'],recipe['entry_bounds_mm']] if kind=='body' else [recipe['cap_bounds_mm']])
    q=curve.copy();q.Placement=placement(recipe['local_to_world']).inverse()*q.Placement
    stack=[(e,0) for e in q.Edges];nodes=0
    while stack:
        e,depth=stack.pop();nodes+=1
        if nodes>max_nodes:return False
        bounds=bbox(e)
        if all(lower_bound(bounds,p,recipe['cylinders'])>=required-1e-7 for p in positives):continue
        if depth>=max_depth:return False
        a,b=e.FirstParameter,e.LastParameter;mid=(a+b)/2
        if b-a<1e-12:return False
        try:
            for start,end in ((a,mid),(mid,b)):
                part=e.Curve.toShape(start,end)
                expected=(e.valueAt(start),e.valueAt(end))
                def matches(s):return (s.Vertexes[0].Point-expected[0]).Length<1e-7 and (s.Vertexes[-1].Point-expected[1]).Length<1e-7
                if not matches(part):part.Placement=e.Placement*part.Placement
                if not matches(part):return False # Never guess topological placements.
                stack.append((part,depth+1))
        except (RuntimeError,ValueError,AttributeError):return False
    return True
