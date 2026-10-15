"""Owner-relative surface/wire planning, followed by the caller's exact gate.

Actual current BReps supply the tessellation; no old masks or bbox collision
claims. Same-leg Hip poses are coupled, other legs/head poses independent.
Surface tangency is not positive volume. No mesh result accepts a support.
"""
import itertools,math,time
import numpy as np
import FreeCAD as A
import check_near_axis_hip_sources as C
from fast_carrier_reservations import TriangleBucket,WireBucket


class Reservations:
    def __init__(self,targets,wires,owners,wire_owners,additions,axes,row,low,high,mesh_cache,wire_cache,allowed_union=()):
        self.surface={};self.cloud={};self.memo={};self.blockers={};cell=self.cell=10
        self.half=row['arm_half_widths_world_mm'];low=np.asarray(low);high=np.asarray(high)
        self.cloud_steps=max(1,math.ceil((max((r for _,r in wires.values()),default=0)+max(self.half)+.75)/cell))
        code=row['code'];moving=row['moving'];tick=time.monotonic()
        objects=[(n,s,owners.get(n)) for n,s in targets.items() if not n.startswith(row['name']+'/') and n not in allowed_union]
        objects += [(n,s,o) for n,(s,o) in additions.items() if not n.startswith(row['name']+'/body/')]
        for h in C.ANGLES if moving else (0,):
            inv=C.transform(axes,code,h,0,'Hip').inverse() if moving else A.Placement()
            matrix=np.asarray(inv.toMatrix().A).reshape(4,4);rot,shift=matrix[:3,:3],matrix[:3,3]
            for name,s,owner in objects:
                if moving and not C.same_leg_pose(owner,code,h):continue
                bb=s.BoundBox
                corners=np.asarray(list(itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))))@rot.T+shift
                if np.any(corners.max(axis=0)<low-3) or np.any(corners.min(axis=0)>high+3):continue
                if id(s) not in mesh_cache:
                    vv,tt=s.tessellate(.2);mesh_cache[id(s)]=(s,np.asarray([list(p) for p in vv]).reshape(-1,3),np.asarray(tt,dtype=int).reshape(-1,3))
                _,vv,tt=mesh_cache[id(s)]
                if not len(tt):continue
                triangles=(vv@rot.T+shift)[tt]
                lower=np.maximum(low,triangles.min(axis=1)-self.half);upper=np.minimum(high,triangles.max(axis=1)+self.half)
                keep=np.all(lower<=upper,axis=1)
                for triangle,a,b in zip(triangles[keep],lower[keep],upper[keep]):
                    for key in itertools.product(*(range(math.floor(x/cell),math.floor(y/cell)+1) for x,y in zip(a,b))):
                        self.surface.setdefault(key,[]).append((triangle,name))
            for name,(s,radius) in wires.items():
                if moving and not C.same_leg_pose(wire_owners.get(name),code,h):continue
                if id(s) not in wire_cache:
                    points=[list(p) for edge in s.Edges for p in edge.discretize(Distance=1)]
                    wire_cache[id(s)]=(s,np.asarray(points))
                _,points=wire_cache[id(s)];points=points@rot.T+shift
                keep=np.all(points>=low-radius-3,axis=1)&np.all(points<=high+radius+3,axis=1)
                for point in points[keep]:
                    key=tuple(np.floor(point/cell).astype(int))
                    self.cloud.setdefault(key,[]).append((point,radius+.25,name))
        self.surface={k:TriangleBucket(v) for k,v in self.surface.items()}
        self.cloud={k:WireBucket(v) for k,v in self.cloud.items()}
        print('source surface space ready',row['name'],round(time.monotonic()-tick,3),'cells',len(self.surface),flush=True)

    def clear(self,point):
        key=tuple(round(v,7) for v in point)
        if key in self.memo:return self.memo[key]
        bucket=tuple(math.floor(v/self.cell) for v in point);hit=None
        for delta in itertools.product(range(-self.cloud_steps,self.cloud_steps+1),repeat=3):
            q=self.cloud.get(tuple(a+b for a,b in zip(bucket,delta)))
            if q and (hit:=q.hit(point,self.half,0)) is not None:break
        if hit is None:
            q=self.surface.get(bucket)
            # A shared tangent face has zero material overlap. A final whole
            # BRep check still rejects every positive-volume intersection.
            hit=q.hit(point,[v-1e-4 for v in self.half]) if q else None
        self.memo[key]=hit is None
        if hit is not None:self.blockers[key]=hit
        return hit is None
