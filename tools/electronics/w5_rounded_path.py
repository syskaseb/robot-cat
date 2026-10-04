"""Exact adjacent corner consumption, including unclipped path endpoints.

A first/last segment has only one corner: it need not reserve two radii.
Interior segments must reserve the sum of the two actual corner offsets.
This never reduces the chosen bend radius to force a path into a small gap.
"""
import math


def corner_offsets(points,radius):
    assert radius>0
    def sub(a,b):return [x-y for x,y in zip(a,b)]
    def length(a):return math.sqrt(sum(x*x for x in a))
    lengths=[length(sub(b,a)) for a,b in zip(points,points[1:])]
    assert all(n>1e-7 for n in lengths),'Repeated path point'
    units=[[x/n for x in sub(b,a)] for a,b,n in zip(points,points[1:],lengths)]
    cuts=[0.0]
    for u,v in zip(units,units[1:]):
        angle=math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v)))))
        assert angle<math.pi-1e-7,'Reverse tangent requires a real service loop'
        cuts.append(radius*math.tan(angle/2))
    cuts.append(0.0)
    for i,length_mm in enumerate(lengths):
        assert cuts[i]+cuts[i+1]<length_mm-1e-7,'Adjacent bend offsets overlap'
    return cuts,units


def rounded(A,Part,points,radius=10):
    clean=[]
    for p in points:
        if not clean or (p-clean[-1]).Length>1e-7:clean.append(p)
    cuts,units=corner_offsets([list(p) for p in clean],radius)
    edges=[];current=clean[0]
    for i,p in enumerate(clean[1:-1],1):
        if cuts[i]<1e-7:continue
        u=A.Vector(*units[i-1]);v=A.Vector(*units[i])
        before=p-u*cuts[i];after=p+v*cuts[i]
        normal=v-u*u.dot(v);normal.normalize()
        center=before+normal*radius
        bisector=(before-center)+(after-center);bisector.normalize()
        mid=center+bisector*radius
        if (before-current).Length>1e-7:edges.append(Part.makeLine(current,before))
        edges.append(Part.Arc(before,mid,after).toShape());current=after
    if (clean[-1]-current).Length>1e-7:edges.append(Part.makeLine(current,clean[-1]))
    wire=Part.Wire(edges)
    assert wire.isValid()
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
    return wire
