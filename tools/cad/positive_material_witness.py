"""A sampled centre INSIDE a valid solid proves rejection, never clearance.

No point found means unknown and must fall through to exact radius distance.
"""
import numpy as np
from immutable_bounds import A


def witness(s,t,bounds,points):
    if not t.Solids:return None
    key=id(s)
    if key not in points:points[key]=np.asarray([list(v) for e in s.Edges for v in e.discretize(Distance=1)])
    pp=points[key];bb=bounds.bound(t)
    lo=np.asarray([bb.XMin,bb.YMin,bb.ZMin]);hi=np.asarray([bb.XMax,bb.YMax,bb.ZMax])
    near=pp[np.all(pp>=lo,axis=1)&np.all(pp<=hi,axis=1)]
    for p in near:
        try:
            if t.isInside(A.Vector(*p),1e-7,True):return p.tolist()
        except (RuntimeError,TypeError,ValueError):return None
    return None
