"""Memoize exact OCC bounds of immutable scene instances, not clearance.

Keep each input alive to prevent id reuse. Callers must create a new shape
instance for every changed placement, as the shared-motion checker does.
The broad phase is the original Euclidean distance between exact BoundBoxes.
An intersecting box still requires the unchanged exact BRep pair checker.
"""
import time
import FreeCAD as A


class ImmutableBounds:
    def __init__(self):
        self.shapes={};self.bounds={};self.calls=0;self.seconds=0.

    def bound(self,s):
        key=id(s)
        if key not in self.bounds:
            tick=time.monotonic();b=s.BoundBox
            self.bounds[key]=(b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)
            self.shapes[key]=s;self.seconds+=time.monotonic()-tick
        return A.BoundBox(*self.bounds[key])

    def near(self,s,t,r=0):
        self.calls+=1;a,b=self.bound(s),self.bound(t)
        return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ')<=(r+1e-6)**2

    def profile(self):
        return dict(calls=self.calls,immutable_instances=len(self.shapes),bounds_seconds=round(self.seconds,3))
