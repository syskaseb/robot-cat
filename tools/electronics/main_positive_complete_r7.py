"""Complete changed F_PI corridor, with transverse straps above the P0 support.

Prototype reserves are not delivered dimensions. Preserve every selected R43
part except explicitly slotted Deck; failed candidates never produce STL.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys
import main_positive_input_route_r2 as R2
R=R2.R; M=R.M; ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-positive-complete-r7'
CAD=ROOT/'hardware/cad/studies/main-positive-complete-r7'

def geometry():
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    line=lambda a,b:Part.makeLine(A.Vector(*a),A.Vector(*b))
    paths=R2.geometry()
    start=A.Vector(129,-8,81)
    finish=A.Vector(114.869,4.91,67.5748)
    u=A.Vector(finish.x-start.x,finish.y-start.y,0); length=u.Length; u.normalize()
    down=A.Vector(0,0,-1); rad=6
    def first(t):return start+down*(rad*math.sin(t))+u*(rad*(1-math.cos(t)))
    a=first(math.pi/2);b=a+u*(length-2*rad)
    def second(t):return b+u*(rad*math.sin(t))+down*(rad*(1-math.cos(t)))
    tail=second(math.pi/2)
    paths['W078']=list(rounded([A.Vector(*p) for p in [[40,-30,130],[129,-30,130],[129,-8,130],[129,-8,81]]],6).Edges)+[
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
    # R3 named WAGO obstructions require a longitudinal strap. Its lower
    # band occupies a shallow OPEN TOP channel, not the P0Support0 region.
    bands={};slots=[]
    bs=[box([-76.2,-26.25,107.8,-75,-22.75,132.2]),
        box([-20,-26.25,107.8,-18.8,-22.75,132.2]),
        box([-75,-26.25,131,-20,-22.75,132.2]),
        box([-75,-26.25,107.8,-20,-22.75,109]),
        box([-82.2,-27.5,109,-76.2,-21.5,113])]
    bands.update({f'holder_tie_0_{i}':s for i,s in enumerate(bs)})
    slots.append([-76.4,-26.5,107.6,57.8,4,1.6])
    foot=box([27,-29,108.8,53,-26,127])
    beam=box([27,-32.5,124,53,-26,132.1])
    groove=Part.makeCylinder(2.1,26.2,A.Vector(26.9,-30,130),A.Vector(1,0,0))
    seat=foot.fuse(beam).cut(groove)
    beam_slots=[]
    for j,x in enumerate((31,49)):
        bs=[box([x-1.25,-33.7,122.8,x+1.25,-32.5,133.3]),
            box([x-1.25,-26,122.8,x+1.25,-24.8,133.3]),
            box([x-1.25,-32.5,132.1,x+1.25,-26,133.3]),
            box([x-1.25,-32.5,122.8,x+1.25,-26,124]),
            box([x-3,-39.7,119.1,x+3,-33.7,123.1])]
        bands.update({f'splice_tie_{j}_{i}':s for i,s in enumerate(bs)})
        notch=[x-1.45,-32.7,122.6,x+1.45,-25.8,124]
        beam_slots.append(notch);seat=seat.cut(box(notch))
    projected=deck.copy()
    for x,y,z,w,l,h in slots:projected=projected.cut(Part.makeBox(w,l,h,A.Vector(x,y,z)))
    # Actual red vertical crossing, full-depth aperture, not a blind mark.
    portal=Part.makeCylinder(2.3,4.2,A.Vector(129,-8,104.9))
    portal_raw=box([126.2,-11.4,108.8,132,-6.3,123.8])
    portal_seat=portal_raw.cut(Part.makeCylinder(1.7,15.2,A.Vector(129,-8,108.7)))
    projected=projected.cut(portal).fuse(seat).fuse(portal_seat)
    for i,s in enumerate([
        box([125,-12.6,119.2,126.2,-5.1,121.7]),
        box([132,-12.6,119.2,133.2,-5.1,121.7]),
        box([126.2,-12.6,119.2,132,-11.4,121.7]),
        box([126.2,-6.3,119.2,132,-5.1,121.7]),
        box([125.2,-18.6,118,131.2,-12.6,122])]):bands[f'positive_portal_tie_{i}']=s
    old_main=owners.pop('MAIN_R40')
    raw_main=box([126.5,-10.5,83,134,1,89])
    main_seat=raw_main.cut(Part.makeCylinder(1.7,6.2,A.Vector(129,-8,82.9)))
    import main_input_return_r4 as W
    black_curve=W.M.geometry()[-2]
    black_groove=Part.Wire([black_curve]).makePipeShell([Part.Wire([Part.makeCircle(1.7,black_curve.valueAt(black_curve.FirstParameter),black_curve.tangentAt(black_curve.FirstParameter))])],True,False)
    main_seat=main_seat.cut(black_groove)
    main_band_notch=box([126.4,-1.5,83,134.1,-.3,85.5])
    main_seat=main_seat.cut(main_band_notch)
    main_seat=main_seat.cut(box([126.55,-2.9,82.9,129.45,-1.3,89.1]))
    changed_main=old_main.fuse(main_seat)
    # Retain black strap. Separate transverse red strap is normal to its
    # vertical wire, rather than the rejected shared YZ loop crossed by red.
    for i,s in enumerate([
        box([125.3,-11.7,83,126.5,-.3,85.5]),
        box([134,-11.7,83,135.2,-.3,85.5]),
        box([126.5,-11.7,83,134,-10.5,85.5]),
        box([126.5,-1.5,83,134,-.3,85.5]),
        box([134,-17.7,79.3,140,-11.7,83.3])]):bands[f'positive_MAIN_tie_{i}']=s
    holder=box(R.HOLDER)
    neck=paths['W078'][-1]
    sleeve=Part.Wire([neck]).makePipeShell([Part.Wire([Part.makeCircle(1.1,neck.valueAt(neck.FirstParameter),neck.tangentAt(neck.FirstParameter))])],True,False)
    splice=Part.makeCylinder(2.1,20,A.Vector(30,-30,130),A.Vector(1,0,0))
    # Two separate thin inner sleeves protect the copper. Replace the old
    # lone W060 outer reserve by one shared outer boot. Width qualification
    # against the supplier sleeve remains mandatory before selection.
    old_boot=owners.pop('Input/W060_input_outer_boot')
    tail_edge=paths['W078'][-2]
    needed=6.01-tail_edge.Length
    preceding=paths['W078'][-3]
    parameter=preceding.getParameterByLength(preceding.Length-needed)
    cut_edge=preceding.Curve.toShape(parameter,preceding.LastParameter)
    bootpath=Part.Wire([cut_edge,tail_edge,neck])
    redboot=bootpath.makePipeShell([Part.Wire([Part.makeCircle(2.1,cut_edge.valueAt(cut_edge.FirstParameter),cut_edge.tangentAt(cut_edge.FirstParameter))])],True,False)
    commonboot=old_boot.fuse(redboot)
    assert commonboot.isValid() and len(commonboot.Solids)==1
    pieces={**wires,**bands,'F_PI_holder':holder,'splice_seat':seat,'splice_sleeve':splice,'W078_neck_sleeve':sleeve}
    pieces['MAIN_input_common_boot']=commonboot
    pieces['positive_portal_seat']=portal_seat
    pieces['MAIN_positive_seat']=main_seat
    rows=[]
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in pieces.items():
        for m,t in owners.items():
            if n in ('W078_9','W078_neck_sleeve','MAIN_input_common_boot') and m=='MAIN/SupplierFamilyReference':continue
            if n=='MAIN_input_common_boot' and (m.startswith('W060/') or m=='Input/W060_neck_inner'):continue
            check(n,s,m,t)
        if n not in ('splice_seat','positive_portal_seat'):check(n,s,'ChangedDeck',projected)
        if n!='MAIN_positive_seat':check(n,s,'ChangedMAIN',changed_main)
    for n,s in wires.items():
        for m,t in bands.items():check(n,s,m,t)
        check(n,s,'splice_seat',seat)
        if n not in ('W043_2','W077_0'):check(n,s,'F_PI_holder',holder)
    for n,s in bands.items():
        check(n,s,'splice_seat',seat);check(n,s,'F_PI_holder',holder);check(n,s,'splice_sleeve',splice)
    check('W078_neck_sleeve',sleeve,'splice_seat',seat)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    soft=[h for h in hits if h['part']=='MAIN_input_common_boot' and h['owner']=='hardware/electronics/full-cat/pi-power-usb-r4/PI_GND_0_DESIGN.brep']
    blocking=[h for h in hits if h not in soft]
    end=datetime.now(timezone.utc)
    for n,s in pieces.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    projected.exportBrep(str(OUT/'Deck_candidate.brep'))
    changed_main.exportBrep(str(OUT/'MAIN_candidate.brep'))
    c=dict(status='REJECTED' if blocking else 'SCREEN_CLEAR_WITH_EXPLICIT_SOFT_FIT',hits=hits,blocking_hits=blocking,soft_contacts=soft,rows=rows,
           lengths_mm=lengths,slots_mm=slots,beam_slots_bbox_mm=beam_slots,portal_xyzr_mm=[129,-8,104.9,2.3],
           source_sha256=hashes,script_sha256=M.sha(Path(__file__)),selected=False,physical_pass=False,W5_complete=False,
           started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),
           changed_approach='R3 WAGO hits removed by open-top strap channel and above-WAGO cantilever. Separate copper inner sleeves, ONE shared input outer boot, not two intersecting boots.',
           common_boot_requires_supplier_fit_check=True,collision_free=False,
           soft_contact_condition='Shared input boot touches selected Pi GND soft reserve; fit/shrink off PETG in phase2, not physical PASS. Old R40 contact0.1773396448mm3 was already explicit.',
           project_reserves_not_manufacturer_dimensions=['holder22mm closed height','factoryOD3.4','redOD3','spliceOD4.2','neckOD2.2','R6'])
    M.save(OUT/'checks.json',c)
    print(json.dumps(dict(status=c['status'],blocking_hits=blocking,soft_contacts=soft,lengths=lengths,pairs=len(rows))),flush=True)

if __name__=='__main__':main()
