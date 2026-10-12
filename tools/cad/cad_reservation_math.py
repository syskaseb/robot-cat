"""Triangle/box SAT for a cheap MESH planning screen, never a BRep receipt."""
def triangle_box(triangle,center,half):
    v=[tuple(a-b for a,b in zip(p,center)) for p in triangle]
    edges=[tuple(b-a for a,b in zip(v[i],v[(i+1)%3])) for i in range(3)]
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    axes=[(1,0,0),(0,1,0),(0,0,1),cross(edges[0],edges[1])]
    axes += [cross(e,a) for e in edges for a in axes[:3]]
    for axis in axes:
        if sum(a*a for a in axis)<1e-20:continue
        projected=[sum(a*b for a,b in zip(p,axis)) for p in v]
        radius=sum(h*abs(a) for h,a in zip(half,axis))
        if min(projected)>radius+1e-10 or max(projected)<-radius-1e-10:return False
    return True
