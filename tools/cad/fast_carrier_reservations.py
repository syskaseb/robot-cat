"""Vectorized equivalent of triangle_box; planning only, no BRep claim."""
import numpy as np


class TriangleBucket:
    def __init__(self,items):
        self.tri=np.asarray([v[0] for v in items],dtype=float)
        self.names=[v[1] for v in items]
        self.low=self.tri.min(axis=1);self.high=self.tri.max(axis=1)

    def hit(self,point,half):
        p=np.asarray(point);h=np.asarray(half)
        indexes=np.flatnonzero(np.all(self.low<=p+h+1e-10,axis=1)&np.all(self.high>=p-h-1e-10,axis=1))
        if not len(indexes):return None
        v=self.tri[indexes]-p;edges=np.roll(v,-1,axis=1)-v
        keep=np.ones(len(indexes),dtype=bool)
        axes=[np.cross(edges[:,0],edges[:,1])]
        axes.extend(np.cross(edges[:,i],a) for i in range(3) for a in np.eye(3))
        for axis in axes:
            projected=np.einsum('nij,nj->ni',v,axis)
            radius=np.sum(np.abs(axis)*h,axis=1)
            separated=(projected.min(axis=1)>radius+1e-10)|(projected.max(axis=1)<-radius-1e-10)
            keep &= ~separated
            if not keep.any():return None
        return self.names[indexes[np.flatnonzero(keep)[0]]]


class WireBucket:
    def __init__(self,items):
        self.points=np.asarray([v[0] for v in items],dtype=float)
        self.radius=np.asarray([v[1] for v in items]);self.names=[v[2] for v in items]

    def hit(self,point,half,margin):
        d=np.maximum(0,np.abs(self.points-np.asarray(point))-np.asarray(half))
        # Roundoff at an exactly tangent project reservation is not contact.
        found=np.flatnonzero(np.sum(d*d,axis=1)<(self.radius+margin+.5-1e-8)**2)
        return self.names[found[0]] if len(found) else None
