"""Complete changed F_PI corridor, with transverse straps above the P0 support.

Prototype reserves are not delivered dimensions. Preserve every selected R43
part except explicitly slotted Deck; failed candidates never produce STL.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys
import main_positive_input_route_r2 as R2
R=R2.R; M=R.M; ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-positive-complete-r3'
CAD=ROOT/'hardware/cad/studies/main-positive-complete-r3'

def geometry():
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    line=lambda a,b:Part.makeLine(A.Vector(*a),A.Vector(*b))
    paths=R2.geometry()
    start=A.Vector(129,-5.9,81)
    finish=A.Vector(114.869,4.91,67.5748)
    u=A.Vector(finish.x-start.x,finish.y-start.y,0); length=u.Length; u.normalize()
    down=A.Vector(0,0,-1); rad=6
    def first(t):return start+down*(rad*math.sin(t))+u*(rad*(1-math.cos(t)))
    a=first(math.pi/2);b=a+u*(length-2*rad)
    def second(t):return b+u*(rad*math.sin(t))+down*(rad*(1-math.cos(t)))
    tail=second(math.pi/2)
    paths['W078']=list(rounded([A.Vector(*p) for p in [[40,-30,130],[129,-30,130],[129,-5.9,130],[129,-5.9,81]]],6).Edges)+[
        Part.Arc(start,first(math.pi/4),a).toShape(),line(list(a),list(b)),
        Part.Arc(b,second(math.pi/4),tail).toShape(),line(list(tail),list(finish)),line(list(finish),R.PAD)]
    return paths

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Do not overwrite completed evidence'
    begin=datetime.now(timezone.utc)
    box=lambda b:Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    owners,hashes=R.C.current_owners();deck=owners.pop('Deck_R41')
    paths=geometry();wires={};lengths={}
    for name,edges in paths.items():
        lengths[name]=sum(e.Length for e in edges)
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
        for i,e in enumerate(edges):
            bare=name=='W078' and i==len(edges)-1
            radius=math.sqrt(.823/math.pi) if bare else (1.5 if name=='W078' else 1.7)
            s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(radius,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            assert s.isValid() and len(s.Solids)==1
            wires[f'{name}_{i}']=s;e.exportBrep(str(OUT/f'{name}_{i}_CENTERLINE.brep'))
    # Two transverse straps: no longitudinal bottom band under P0Support0.
    bands={};slots=[]
    for j,x in enumerate((-45,-30)):
        bs=[box([x-1.75,-31.05,103.8,x+1.75,-29.85,133.4]),
            box([x-1.75,-12.15,103.8,x+1.75,-10.95,133.4]),
            box([x-1.75,-29.85,132.2,x+1.75,-12.15,133.4]),
            box([x-1.75,-29.85,103.8,x+1.75,-12.15,105]),
            box([x-4,-37,99.8,x+4,-31.05,103.8])]
        bands.update({f'holder_tie_{j}_{i}':s for i,s in enumerate(bs)})
        for y in (-31.35,-12.45):slots.append([x-2,y,104.9,4,1.8,4.2])
    # Integral 26x9 post supports the insulated stationary inline splice.
    foot=box([27,-34.5,108.8,53,-25.5,130])
    groove=Part.makeCylinder(3.5,26.2,A.Vector(26.9,-30,130),A.Vector(1,0,0))
    seat=foot.cut(groove)
    for j,x in enumerate((31,49)):
        bs=[box([x-1.25,-35.7,103.8,x+1.25,-34.5,134.7]),
            box([x-1.25,-25.5,103.8,x+1.25,-24.3,134.7]),
            box([x-1.25,-34.5,133.5,x+1.25,-25.5,134.7]),
            box([x-1.25,-34.5,103.8,x+1.25,-25.5,105]),
            box([x-3,-41.2,99.8,x+3,-35.7,103.8])]
        bands.update({f'splice_tie_{j}_{i}':s for i,s in enumerate(bs)})
        for y in (-36,-25.8):slots.append([x-1.55,y,104.9,3.1,1.8,4.2])
    projected=deck.copy()
    for x,y,z,w,l,h in slots:projected=projected.cut(Part.makeBox(w,l,h,A.Vector(x,y,z)))
    # Actual red vertical crossing, full-depth aperture, not a blind mark.
    portal=Part.makeCylinder(2.3,4.2,A.Vector(129,-5.9,104.9))
    projected=projected.cut(portal).fuse(seat)
    holder=box(R.HOLDER)
    neck=paths['W078'][-1]
    sleeve=Part.Wire([neck]).makePipeShell([Part.Wire([Part.makeCircle(1.1,neck.valueAt(neck.FirstParameter),neck.tangentAt(neck.FirstParameter))])],True,False)
    splice=Part.makeCylinder(3.5,20,A.Vector(30,-30,130),A.Vector(1,0,0))
    pieces={**wires,**bands,'F_PI_holder':holder,'splice_seat':seat,'splice_sleeve':splice,'W078_neck_sleeve':sleeve}
    rows=[]
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in pieces.items():
        for m,t in owners.items():
            if n in ('W078_10','W078_neck_sleeve') and m=='MAIN/SupplierFamilyReference':continue
            check(n,s,m,t)
        if n!='splice_seat':check(n,s,'ChangedDeck',projected)
    for n,s in wires.items():
        for m,t in bands.items():check(n,s,m,t)
        check(n,s,'splice_seat',seat)
        if n not in ('W043_2','W077_0'):check(n,s,'F_PI_holder',holder)
    for n,s in bands.items():
        check(n,s,'splice_seat',seat);check(n,s,'F_PI_holder',holder);check(n,s,'splice_sleeve',splice)
    check('W078_neck_sleeve',sleeve,'splice_seat',seat)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    end=datetime.now(timezone.utc)
    for n,s in pieces.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    projected.exportBrep(str(OUT/'Deck_candidate.brep'))
    c=dict(status='REJECTED' if hits else 'SCREEN_CLEAR_NEEDS_NATIVE_AND_TERMINATIONS',hits=hits,rows=rows,
           lengths_mm=lengths,slots_mm=slots,portal_xyzr_mm=[129,-5.9,104.9,2.3],
           source_sha256=hashes,script_sha256=M.sha(Path(__file__)),selected=False,physical_pass=False,W5_complete=False,
           started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),
           changed_approach='R6 arcs raised3mm; individually sleeved5mm red neck instead of intersecting4.2mm boot',
           project_reserves_not_manufacturer_dimensions=['holder22mm closed height','factoryOD3.4','redOD3','spliceOD7','neckOD2.2','R6'])
    M.save(OUT/'checks.json',c)
    print(json.dumps(dict(status=c['status'],hits=hits,lengths=lengths,pairs=len(rows))),flush=True)

if __name__=='__main__':main()
