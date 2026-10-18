"""Containment-aware minimum distance of actual solid children.

OCC/FreeCAD distToShape at Compound level can return a surface distance even
when one solid is contained in another. Never use that as an air-gap proof.
No healing, tessellation, Boolean volume claim or invalid-source waiver.
"""
import math


def bbox_lower_bound(a,b):
    return math.sqrt(sum(max(0,u-v,w-x)**2 for u,v,w,x in
        ((a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax))))


def distance(a,b):
    assert a.isValid() and b.isValid(),'Invalid source, no gap proof'
    aa=a.Solids;bb=b.Solids
    assert aa and bb,'Only actual solids, not curves/shell-only budgets'
    if a.ShapeType=='Solid' and b.ShapeType=='Solid':return float(a.distToShape(b)[0])
    best=math.inf
    for x in aa:
        assert x.ShapeType=='Solid' and x.isValid()
        for y in bb:
            assert y.ShapeType=='Solid' and y.isValid()
            if bbox_lower_bound(x.BoundBox,y.BoundBox)>=best:continue
            best=min(best,float(x.distToShape(y)[0]))
            if best<1e-9:return 0.
    return best
