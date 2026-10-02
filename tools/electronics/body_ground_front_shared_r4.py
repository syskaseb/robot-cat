"""W036: pass below XA02 with a longer R45 lift, then above fuse caps.

Replace crowded G1 endpoint restraints by three narrow individual saddles.
Keep different wire diameters independently restrained; no common mixed-OD cap.
Preserve the rejected R3 evidence and all selected R40 source files.
"""
from datetime import datetime, timezone
import json, math, sys
from pathlib import Path
import body_ground_front_shared_r3 as P

M=P.M; ROOT=M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/body-ground-front-shared-r4'
SPEC=('G1.4',[73.5,11,113.5],1,'FR_G.1',[-46.5,-30.5,113.5],1,132,89)
G1=[('W061',58.5,2.3,2.1),('W036',73.5,2.3,2.1),('W060',81,1.8,1.5)]
SOURCE=P.SOURCE

def route():
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    M.STRAIGHT=2; M.R=45
    ea,pa=M.elevated_start(SPEC[1],1,132)
    M.R=21
    eb,pb=M.elevated_start(SPEC[4],1,132)
    middle=rounded([pa,A.Vector(pa.x,89,132),A.Vector(pb.x,89,132),pb],21)
    back=[]
    for e in reversed(eb):
        start=e.valueAt(e.LastParameter);end=e.valueAt(e.FirstParameter)
        back.append(Part.Arc(start,e.valueAt((e.FirstParameter+e.LastParameter)/2),end).toShape() if hasattr(e.Curve,'Radius') else Part.makeLine(start,end))
    w=Part.Wire(ea+middle.Edges+back);assert w.isValid()
    for a,b in zip(w.Edges,w.Edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    assert min(e.Curve.Radius for e in w.Edges if hasattr(e.Curve,'Radius'))>=21-1e-7
    return w

def design_shapes():
    import FreeCAD as A
    import Part
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    seats={};bands={}
    def tie(name,x,y,z,bottom,head,turn=0,half=5.5,od=4.2,centred_head=False):
        upper=z+od/2+.1
        pieces=[box([dx-.6,-1.25,bottom,dx+.6,1.25,upper+1.2]) for dx in (-half,half)]
        pieces += [box([-half-.6,-1.25,upper,half+.6,1.25,upper+1.2]),box([-half-.6,-1.25,bottom,half+.6,1.25,bottom+1.2])]
        pieces.append(box([-3,-2.5,head,3,2.5,head+4] if centred_head else [half-1,-2.5,head,half+5,2.5,head+4]))
        for i,s in enumerate(pieces):
            s.rotate(A.Vector(),A.Vector(0,0,1),turn);s.translate(A.Vector(x,y,0));bands[f'{name}_tie_{i}']=s
    for name,x,r,odr in G1:
        # Shallow finite trough; individual strap provides retention, no thin U lip.
        s=box([x-2.2,11.5,108.8,x+2.2,14,112])
        seats['G1_'+name+'_seat']=s.cut(Part.makeCylinder(r,2.7,A.Vector(x,11.4,113.5),A.Vector(0,1,0)))
        tie('G1_'+name,x,12.5,113.5,103.8,100.1,half=3,od=2*odr,centred_head=True)
    fr=box([-50.5,-30,108.8,-42.5,-27.5,114.2])
    seats['FR_seat']=fr.cut(Part.makeCylinder(2.3,2.7,A.Vector(-46.5,-30.1,113.5),A.Vector(0,1,0)))
    post=box([-9,84,108.8,-5,88,133.5]);beam=box([-11,77,127.6,-3,100,133.5])
    mid=post.fuse(beam).cut(Part.makeCylinder(2.3,8.2,A.Vector(-11.1,89,132),A.Vector(1,0,0)))
    for y in (83.5,94.5):mid=mid.cut(box([-8.6,y-1,127.5,-5.4,y+1,133.6]))
    seats['Middle_seat']=mid
    tie('FR',-46.5,-28.75,113.5,103.8,100.1)
    tie('Middle',-7,89,132,126.4,122.7,turn=90)
    return seats,bands

def projected_deck(deck):
    import FreeCAD as A
    import Part
    for b in ([54.5,11.25,109,62.5,13.75,120],[77,11.5,109,85,14.5,120]):
        deck=deck.cut(Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3])))
    slots=[(x+dx,12.5,1.6,3.2) for _,x,_,_ in G1 for dx in (-3,3)]
    slots += [(-52,-28.75,2,3.2),(-41,-28.75,2,3.2)]
    for x,y,width,length in slots:
        deck=deck.cut(Part.makeBox(width,length,4.2,A.Vector(x-width/2,y-length/2,104.9)))
    return deck

def main():
    import FreeCAD as A
    import Part
    sys.path.insert(0,str(ROOT/'tools/cad'))
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc)
    M.save(OUT/'intent.json',dict(parent='one-batch-prototype-r40',wire='W036',spec=SPEC,
        source_lift_radius_mm=45,destination_and_plan_radius_mm=21,wire_OD_mm=4.2,wire_SKU='TKD2500125',
        strip_by_end_mm={'G1.4':[12,14],'FR_G.1':11},
        changed_reason='R3 hit XA02 at Y48/Z132. R45 source lift passes below it before reaching Z132; laneY89 clears complete fuse caps. Independent narrow G1 saddles replace the crowded wider seats, avoiding a mixed-diameter common clamp.',
        replaces_G1_restraints=['W061/G1_end','W060/G1_input'],G1_individual_saddles=G1,
        tie_SKU='111-02370 T18I',ties_replaced=2,ties_selected=5,net_extra_ties=3,
        tie_head_reserve_mm=[6,5,4],tie_head_is_measured=False,
        G1_preserved_reserved_mouths={'BAT':[51,11,113.5],'W025':[66,11,113.5]},
        W5_complete=False,physical_pass=False,selected=False,started_utc=begin.isoformat()))
    w=route();pieces={}
    for i,e in enumerate(w.Edges):
        s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(2.1,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        pieces[f'W036_{i}']=s;s.exportBrep(str(OUT/f'W036_{i}_DESIGN.brep'));e.exportBrep(str(OUT/f'W036_{i}_CENTERLINE.brep'))
    owners,hashes=P.current_owners();seats,bands=design_shapes();rows=[]
    for n,s in {**seats,**bands}.items():
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        s.exportBrep(str(OUT/(n+'.brep')))
    deck=projected_deck(owners.pop('Deck_R40'));owners['Deck_projected_change']=deck
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in {**pieces,**seats,**bands}.items():
        for m,t in owners.items():
            if n in seats and m=='Deck_projected_change':continue
            check(n,s,m,t)
    for n,s in pieces.items():
        for m,t in {**seats,**bands}.items():check(n,s,m,t)
    for n,s in bands.items():
        for m,t in seats.items():check(n,s,m,t)
    for name,x,_,_ in G1:
        # Adjacent active wires need their own restraints; do not ignore their hits.
        for n,s in bands.items():
            if n.startswith('G1_'):
                for m,t in bands.items():
                    if n<m:check(n,s,m,t)
                break
        break
    reserves={name:Part.makeCylinder(r,2,A.Vector(x,11,113.5),A.Vector(0,1,0)) for name,x,r in [('BAT_reserved',51,1.55),('W025_reserved',66,2.1)]}
    for n,s in {**seats,**bands}.items():
        for m,t in reserves.items():check(n,s,m,t)
    roots={n:s.common(deck).Volume for n,s in seats.items()}
    hits=[r for r in rows if r['hit_mm3']>1e-5];end=datetime.now(timezone.utc)
    M.save(OUT/'checks.json',dict(status='REJECTED' if hits or not all(v>0 for v in roots.values()) else 'CLEAR_FOR_NATIVE_FINISH',
        hits=hits,rows=rows,root_overlap_mm3=roots,source_sha256=hashes,script_sha256=M.sha(Path(__file__)),
        route_length_mm=w.Length,nominal_blank_mm=math.ceil((w.Length+58)/10)*10,
        physical_pass=False,W5_complete=False,selected=False,started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    M.save(OUT/'preview-lines.json',dict(points=[list(p) for e in w.Edges for p in e.discretize(Deflection=.2)]))
    print(json.dumps(dict(status='REJECTED' if hits else 'CLEAR',hits=hits,roots=roots,pairs=len(rows))),flush=True)

if __name__=='__main__':main()
