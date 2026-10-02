"""W036 above capped fuses, with one shared five-mouth G1 restraint.

Not the rejected R1/R2 corridor: Z132, laneY70, FR_G.1 at leftmostX-46.5.
G1 mouths/roles are preserved. Replace two overlapping local G1 straps with
one T30L around an integral comb, leaving BAT and W025 mouth reserves clear.
"""
from datetime import datetime,timezone
import json,math,sys
from pathlib import Path
import body_ground_routes_r1 as M

ROOT=M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/body-ground-front-shared-r3'
SPEC=('G1.4',[73.5,11,113.5],1,'FR_G.1',[-46.5,-30.5,113.5],1,132,70)
COMB_X=[51,58.5,66,73.5,81]
COMB_RADIUS=[1.75,2.3,2.3,2.3,1.8]
SOURCE=ROOT/'hardware/cad/studies/main-input-return-finish-r3/DeckMainInput.FCStd'

def current_owners():
    import FreeCAD as A
    import Part
    import main_input_return_r4 as W
    owners,hashes=W.M.current_owners()
    owners.pop('Deck_R38');owners.pop('MAIN/Adapter')
    def load(rel):
        p=ROOT/rel;hashes[rel]=M.sha(p);s=Part.Shape();s.read(str(p));return s
    owners['Deck_R40']=load('hardware/cad/studies/main-input-return-finish-r3/Deck_WORLD.brep')
    owners['MAIN_R40']=load('hardware/cad/studies/main-input-return-finish-r2/MAINMount_WORLD.brep')
    for p in (ROOT/'hardware/electronics/full-cat/main-input-return-r4').glob('W060_*_DESIGN.brep'):
        owners['W060/'+p.stem]=load(p.relative_to(ROOT).as_posix())
    for folder in ('main-input-return-finish-r2','main-input-return-finish-r3'):
        for p in (ROOT/'hardware/cad/studies'/folder).glob('*_WORLD.brep'):
            name=p.stem.removesuffix('_WORLD')
            if name.startswith(('Deck_input_tie_','MAIN_input_tie_','W060_')):
                # New MAIN strap supersedes R2; retain only the R3 version.
                if name.startswith('MAIN_input_tie_') and folder.endswith('r2'):continue
                owners['Input/'+name]=load(p.relative_to(ROOT).as_posix())
    for n in list(owners):
        if n.startswith('W061_tie/G1_end/'):owners.pop(n)
    # R40 G1_input_tie was not included above: intentionally superseded here.
    iface=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r3/interface.json'
    hashes[iface.relative_to(ROOT).as_posix()]=M.sha(iface)
    hashes[SOURCE.relative_to(ROOT).as_posix()]=M.sha(SOURCE)
    return owners,hashes

def design_shapes():
    import FreeCAD as A
    import Part
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    comb=box([47,11.5,108.8,85,14,114.2])
    for x,r in zip(COMB_X,COMB_RADIUS):
        comb=comb.cut(Part.makeCylinder(r,2.7,A.Vector(x,11.4,113.5),A.Vector(0,1,0)))
    g1={f'G1_shared_tie_{i}':s for i,s in enumerate([
        box([44.9,11.25,103.8,46.1,14.75,116.8]),
        box([85.9,11.25,103.8,87.1,14.75,116.8]),
        box([44.9,11.25,115.6,87.1,14.75,116.8]),
        box([44.9,11.25,103.8,87.1,14.75,105]),
        box([85.5,9,98.8,94.5,17,103.8])])}
    fr=box([-50.5,-30,108.8,-42.5,-27.5,114.2])
    fr=fr.cut(Part.makeCylinder(2.3,2.7,A.Vector(-46.5,-30.1,113.5),A.Vector(0,1,0)))
    post=box([1,58,108.8,5,62,133.5]);beam=box([-1,58,127.6,7,81,133.5])
    mid=post.fuse(beam).cut(Part.makeCylinder(2.3,8.2,A.Vector(-1.1,70,132),A.Vector(1,0,0)))
    for y in (64.5,75.5):mid=mid.cut(box([1.4,y-1,127.5,4.6,y+1,133.6]))
    bands={}
    for name,x,y,z,bottom,head,turn in [('FR',-46.5,-28.75,113.5,103.8,100.1,0),('Middle',3,70,132,126.4,122.7,90)]:
        upper=z+2.2
        pieces=[box([dx-.6,-1.25,bottom,dx+.6,1.25,upper+1.2]) for dx in (-5.5,5.5)]
        pieces += [box([-6.1,-1.25,upper,6.1,1.25,upper+1.2]),box([-6.1,-1.25,bottom,6.1,1.25,bottom+1.2]),box([4.5,-2.5,head,10.5,2.5,head+4])]
        for i,s in enumerate(pieces):
            s.rotate(A.Vector(),A.Vector(0,0,1),turn);s.translate(A.Vector(x,y,0));bands[f'{name}_tie_{i}']=s
    return {'G1_shared_comb':comb,'FR_seat':fr,'Middle_seat':mid}, {**g1,**bands}

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc)
    M.save(OUT/'intent.json',dict(parent='one-batch-prototype-r40',wire='W036',spec=SPEC,
        wire_SKU='TKD2500125',OD_mm=4.2,radius_mm=21,strip_by_end_mm={'G1.4':[12,14],'FR_G.1':11},
        G1_comb_x_mm=COMB_X,G1_comb_radius_mm=COMB_RADIUS,
        G1_existing_cage_labels=['.1','.5','.3','.4','.2'],FR_G_positive_X_labels=['.1','.2','.3','.4','.5'],
        G1_replaces=['W061/G1_end small tie and seat','W060/G1 small tie and seat'],
        G1_shared_tie_SKU='111-03410 T30L',G1_shared_tie_stock='1 from existing planned20 in100pc bag',
        G1_head_reserve_mm=[9,8,5],G1_head_is_measured=False,
        G1_preserved_reserved_mouths={'BAT_LAPP0107001':[51,11,113.5],'W025':[66,11,113.5]},
        distinction='R132 clears entire fuse129.8; FR leftmost mouth avoids P_FRONT. Shared G1 restraint eliminates adjacent-mouth strap conflicts, no remap of selected electrical roles.',
        physical_pass=False,W5_complete=False,selected=False,started_utc=begin.isoformat()))
    M.STRAIGHT=2;w=M.route(SPEC);pieces={}
    for i,e in enumerate(w.Edges):
        s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(2.1,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        pieces[f'W036_{i}']=s;s.exportBrep(str(OUT/f'W036_{i}_DESIGN.brep'));e.exportBrep(str(OUT/f'W036_{i}_CENTERLINE.brep'))
    owners,hashes=current_owners();seats,bands=design_shapes();rows=[]
    for n,s in seats.items():
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        s.exportBrep(str(OUT/(n+'.brep')))
    for n,s in bands.items():s.exportBrep(str(OUT/(n+'.brep')))
    # Preserve R40 base; only remove two explicitly replaced raised seats.
    deck=owners.pop('Deck_R40')
    for b in ([54.5,11.25,109,62.5,13.75,120],[77,11.5,109,85,14.5,120]):
        deck=deck.cut(Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3])))
    for x,y,width,length in [(45.5,13,2,4.2),(86.5,13,2,4.2),(-52,-28.75,2,3.2),(-41,-28.75,2,3.2)]:
        deck=deck.cut(Part.makeBox(width,length,4.2,A.Vector(x-width/2,y-length/2,104.9)))
    owners['Deck_projected_change']=deck
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in {**pieces,**seats,**bands}.items():
        for m,t in owners.items():
            if n in seats and m=='Deck_projected_change':continue # deliberate integral attachment, checked separately
            check(n,s,m,t)
    for n,s in pieces.items():
        for m,t in {**seats,**bands}.items():check(n,s,m,t)
    for n,s in bands.items():
        for m,t in seats.items():check(n,s,m,t)
    # Reserved mouths are solid insulated exit stubs, not claimed full routes.
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

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
