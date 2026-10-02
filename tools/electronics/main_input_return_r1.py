"""One W060 input return on R39; source-preserving CAD construction.

Wire OD and bend target are prototype allowances, not Joy-IT ratings.
No selection until route, insulation and restraints are all finished.
"""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/main-input-return-r1'
START = [81, 11, 113.5]
PAD = [114.869, 8.41, 62.5748]
POLES = [[81, 13, 113.5], [81, 38, 113.5],
         [114.869, 8.41, 82], [114.869, 8.41, 64.5748]]

def radius_bound(poles, depth=9):
    """All-parameter bound, not sampled curvature: de Casteljau hulls.

    Cubic derivative lies in the quadratic derivative control hull; second
    derivative in a line hull. Positive projection gives a speed lower bound;
    every cross product is a convex combination of pairwise control crosses.
    Therefore curvature <= max|Di x Aj| / min(dot(Di,axis))**3 on each leaf.
    """
    def sub(a,b): return tuple(x-y for x,y in zip(a,b))
    def scale(a,k): return tuple(k*x for x in a)
    def dot(a,b): return sum(x*y for x,y in zip(a,b))
    def norm(a): return math.sqrt(dot(a,a))
    def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    def split(p):
        levels=[p]
        while len(levels[-1])>1:
            q=levels[-1];levels.append([scale(tuple(x+y for x,y in zip(a,b)),.5) for a,b in zip(q,q[1:])])
        return [q[0] for q in levels], [q[-1] for q in reversed(levels)]
    leaves=[poles]
    for _ in range(depth): leaves=[q for p in leaves for q in split(p)]
    bounds=[]
    for p in leaves:
        d=[scale(sub(b,a),3) for a,b in zip(p,p[1:])]
        dd=[scale(sub(b,a),2) for a,b in zip(d,d[1:])]
        axis=scale(tuple(sum(v[j] for v in d) for j in range(3)),1/3)
        axis=scale(axis,1/norm(axis));speed=min(dot(v,axis) for v in d)
        if speed<=0: return 0
        upper=max(norm(cross(v,a)) for v in d for a in dd)
        bounds.append(speed**3/upper if upper else math.inf)
    return min(bounds)

def main():
    import FreeCAD as A
    import Part
    sys.path.insert(0,str(ROOT/'tools/cad'))
    sys.path.insert(0,str(ROOT/'tools/electronics'))
    import body_ground_front_return_r1 as C
    import body_ground_routes_r1 as M
    from check_main_p0_placement import SavedShapes
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve trials; use new revision'
    begin=datetime.now(timezone.utc)
    bound=radius_bound(POLES)
    M.save(OUT/'intent.json',dict(parent='one-batch-prototype-r39',wire='W060',
        source='G1.2',destination='MAIN.input_GND',start_mm=START,pad_mm=PAD,
        poles_mm=POLES,diameter_allowance_mm=3,geometric_radius_lower_bound_mm=bound,
        radius_target_mm=6,radius_not_supplier_qualification=True,
        wire_SKU='Joy-IT K-1474 black18AWG0.823mm2; existing shared offcut',
        maximum_blank_mm=300,strip_G1_mm=[12,14],strip_MAIN_mm=5,
        pad_bare_neck_mm=2,source_pad_basis='R5 local GND_IN+offset105.82,8.16,52',
        physical_pass=False,selected=False,restraints_complete=False,W5_complete=False,
        started_utc=begin.isoformat()))
    assert bound>=6, bound
    c=Part.BezierCurve();c.setPoles([A.Vector(*p) for p in POLES])
    edges=[Part.makeLine(A.Vector(*START),A.Vector(*POLES[0])),c.toShape(),
           Part.makeLine(A.Vector(*POLES[-1]),A.Vector(*PAD))]
    pieces=[]
    for i,e in enumerate(edges):
        radius=math.sqrt(.823/math.pi) if i==2 else 1.5
        s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(radius,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        pieces.append(s);s.exportBrep(str(OUT/f'W060_{i}_DESIGN.brep'));e.exportBrep(str(OUT/f'W060_{i}_CENTERLINE.brep'))
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    owners,hashes=C.current_owners()
    reader=SavedShapes();native=ROOT/'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd'
    for name in ('Adapter','SupplierFamilyReference'):
        s=reader.shape(native,name);s.translate(A.Vector(105.82,8.16,52));owners['MAIN/'+name]=s
    hashes.update(reader.hashes)
    rows=[]
    for i,p in enumerate(pieces):
        for n,s in owners.items():
            for j,q in enumerate(s.Solids):
                if p.BoundBox.intersect(q.BoundBox):
                    if i==2 and n=='MAIN/SupplierFamilyReference': continue # Own through-hole copper landing only.
                    v=p.common(q).Volume
                    rows.append(dict(segment=i,owner=n,solid=j,hit_mm3=v))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    length=sum(e.Length for e in edges)
    end=datetime.now(timezone.utc)
    M.save(OUT/'checks.json',dict(status='REJECTED' if hits else 'ROUTE_CLEAR_NEEDS_INSULATION_RESTRAINTS',
        hits=hits,rows=rows,length_mm=length,nominal_blank_mm=math.ceil((length+14+3+20)/10)*10,
        geometric_radius_lower_bound_mm=bound,source_sha256=hashes,script_sha256=M.sha(Path(__file__)),
        selected=False,physical_pass=False,W5_complete=False,
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    M.save(OUT/'preview-lines.json',dict(poles=POLES,points=[list(p) for e in edges for p in e.discretize(Deflection=.2)]))
    print(json.dumps(dict(hits=hits,length_mm=length,radius_bound_mm=bound,pairs=len(rows))),flush=True)

if __name__=='__main__': main()
