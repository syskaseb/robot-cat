"""Conservative exact surface pruning, matching the earlier R13 principle.

Disjoint face bounds alone do NOT prove disjoint solids: test every connected
component for containment as well. Any uncertainty falls back to common().
No meshes, no exemptions for PETG, no replacement of collision evidence.
"""
CACHE={}
STATS={'surface_pruned':0,'uncertain_or_overlap':0}


def cached(shape):
    b=shape.BoundBox
    key=(shape.hashCode(),*(getattr(b,q) for q in ('XMin','YMin','ZMin','XMax','YMax','ZMax')))
    if key not in CACHE:
        CACHE[key]=(shape.isValid(),[f.BoundBox for f in shape.Faces])
    return CACHE[key]


def separated(a,b):
    try:
        av,af=cached(a); bv,bf=cached(b)
        if not av or not bv or not a.Solids or not b.Solids: return False
        if any(x.intersect(y) for x in af for y in bf):
            STATS['uncertain_or_overlap']+=1; return False
        for one,other in ((a,b),(b,a)):
            for solid in one.Solids:
                if not solid.Vertexes or other.isInside(solid.Vertexes[0].Point,1e-7,True):
                    STATS['uncertain_or_overlap']+=1; return False
        STATS['surface_pruned']+=1; return True
    except Exception:
        STATS['uncertain_or_overlap']+=1; return False


def validate(A,Part):
    outer=Part.makeBox(10,10,10)
    rows=[]
    for x,y,z,dx,dy,dz,want in ((2,2,2,1,1,1,False),
                               (9,2,2,2,1,1,False),
                               (10,2,2,1,1,1,False),
                               (11,2,2,1,1,1,True)):
        q=Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
        result=separated(q,outer); volume=q.common(outer).Volume
        assert result==want,(result,want,volume)
        rows.append(dict(separated=result,exact_common_mm3=volume))
    CACHE.clear(); STATS.update(surface_pruned=0,uncertain_or_overlap=0)
    return rows
