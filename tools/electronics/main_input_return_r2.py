"""W060 east-side descent: avoid R1's output-wire and DATA tie corridor.

Top lane stays below the selected carrier. Deck penetration is intentional
only after a native replaceable Deck passage/restraint is constructed.
"""
from datetime import datetime,timezone
import json,math,sys
from pathlib import Path
import main_input_return_r1 as B

ROOT=B.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-input-return-r2'
POLES=[[133,21,95],[133,21,95-30.4252/3],
       [114.869,8.41,64.5748+30.4252/3],[114.869,8.41,64.5748]]

def main():
    import FreeCAD as A
    import Part
    import body_ground_front_return_r1 as C
    import body_ground_routes_r1 as M
    from xb11_upstream_route import rounded
    from check_main_p0_placement import SavedShapes
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc);bound=B.radius_bound(POLES)
    M.save(OUT/'intent.json',dict(parent='one-batch-prototype-r39',wire='W060',
        route='G1.2 +Y, rise to lane138, eastX133 descent; dedicated Deck passage required',
        source_mm=B.START,pad_mm=B.PAD,fan_poles_mm=POLES,diameter_allowance_mm=3,
        radius_target_mm=6,fan_radius_lower_bound_mm=bound,radius_not_supplier_qualification=True,
        physical_pass=False,selected=False,W5_complete=False,started_utc=begin.isoformat()))
    assert bound>=6,bound
    path=rounded([A.Vector(*p) for p in [B.START,[81,21,113.5],[81,21,138],[133,21,138],[133,21,95]]],6)
    c=Part.BezierCurve();c.setPoles([A.Vector(*p) for p in POLES])
    edges=list(path.Edges)+[c.toShape(),Part.makeLine(A.Vector(*POLES[-1]),A.Vector(*B.PAD))]
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    pieces=[]
    for i,e in enumerate(edges):
        r=math.sqrt(.823/math.pi) if i==len(edges)-1 else 1.5
        s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(r,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        s.exportBrep(str(OUT/f'W060_{i}_DESIGN.brep'));e.exportBrep(str(OUT/f'W060_{i}_CENTERLINE.brep'));pieces.append(s)
    owners,hashes=C.current_owners()
    reader=SavedShapes();native=ROOT/'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd'
    for n in ('Adapter','SupplierFamilyReference'):
        s=reader.shape(native,n);s.translate(A.Vector(105.82,8.16,52));owners['MAIN/'+n]=s
    hashes.update(reader.hashes);rows=[]
    for i,p in enumerate(pieces):
        for n,s in owners.items():
            for j,q in enumerate(s.Solids):
                if p.BoundBox.intersect(q.BoundBox):
                    if i==len(edges)-1 and n=='MAIN/SupplierFamilyReference':continue
                    rows.append(dict(segment=i,owner=n,solid=j,hit_mm3=p.common(q).Volume))
    hits=[r for r in rows if r['hit_mm3']>1e-5];end=datetime.now(timezone.utc)
    length=sum(e.Length for e in edges)
    M.save(OUT/'checks.json',dict(status='NEEDS_DECK_PASSAGE' if hits and {r['owner'] for r in hits}=={'Deck_R38'} else 'REJECTED' if hits else 'CLEAR_NEEDS_RESTRAINTS',
        hits=hits,rows=rows,length_mm=length,nominal_blank_mm=math.ceil((length+14+3+20)/10)*10,
        geometric_radius_lower_bound_mm=min(6,bound),source_sha256=hashes,
        script_sha256=M.sha(Path(__file__)),physical_pass=False,selected=False,W5_complete=False,
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    M.save(OUT/'preview-lines.json',dict(points=[list(p) for e in edges for p in e.discretize(Deflection=.2)]))
    print(json.dumps(dict(hits=hits,length_mm=length,blank_mm=math.ceil((length+37)/10)*10,pairs=len(rows))),flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
