"""Four factory parent leads and one explicit provisional mounting envelope.

No wrong CHEYEN drawing: MTA0100335 Cu4mm2 is sourced, while body35x16x22,
OD5/R20, exit stations and each usable lead100mm are PROJECT assumptions.
Four shelves and wire grips are intended additions to native Deck, not
selected opaque solids. New geometric contacts remain failures.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feeds-r1'


def geometry(A, Part):
    def box(b): return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    shapes, rows, shelves, holes = {}, [], {}, []
    for leg, wire in [('FL','W026'),('FR','W037'),('RL','W045'),('RR','W053')]:
        side = 1 if leg.endswith('L') else -1
        base = -69 if leg.startswith('F') else 39
        x = base-13.5; cx = x-4
        start = A.Vector(x,side*49.5,113.5)
        end = A.Vector(cx,side*85,122)
        out = A.Vector(0,side,0); shift = A.Vector(-4,0,8.5)
        h = shift.Length; transverse = shift/h; radius = 20
        angle = math.acos(1-h/(2*radius))
        p = start+out*9
        edges = [Part.makeLine(start,p)]
        begin = A.Vector(p)
        def q(t): return begin+out*(radius*math.sin(t))+transverse*(radius*(1-math.cos(t)))
        edges.append(Part.Arc(q(0),q(angle/2),q(angle)).toShape()); p=q(angle)
        begin=A.Vector(p)
        tangent=out*math.cos(angle)+transverse*math.sin(angle)
        inward=out*math.sin(angle)-transverse*math.cos(angle)
        def q2(t): return begin+tangent*(radius*math.sin(t))+inward*(radius*(1-math.cos(t)))
        edges.append(Part.Arc(q2(0),q2(angle/2),q2(angle)).toShape()); p=q2(angle)
        assert (end-p).dot(out)>0 and abs(p.x-end.x)<1e-7 and abs(p.z-end.z)<1e-7
        edges.append(Part.makeLine(p,end)); path=Part.Wire(edges)
        tube=path.makePipeShell([Part.Wire([Part.makeCircle(2.5,start,out)])],True,False)
        assert tube.isValid() and len(tube.Solids)==1
        shapes[wire+'_WIRE']=tube; shapes[wire+'_CENTERLINE']=path
        lo,hi=sorted((side*85,side*120))
        shapes[leg+'_HOLDER']=box([cx-8,lo,111,cx+8,hi,133])
        lo,hi=sorted((side*83,side*122))
        shelf=box([cx-10,lo,109,cx+10,hi,111])
        # Two downward ribs connect the cantilever to the retained Deck edge.
        for a,b in ((cx-10,cx-8),(cx+8,cx+10)):
            shelf=shelf.fuse(box([a,lo,103,b,hi,109]))
        for index,y in enumerate((side*97,side*113.5)):
            for sign in (-1,1):
                notch=[cx+sign*9-1, y-1.45,102.9,cx+sign*9+1,y+1.45,111.1]
                shelf=shelf.cut(box(notch)); holes.append(dict(kind='holder_tie',leg=leg,bounds_mm=notch))
            # Transverse tie, factory fuse cover stays accessible after bank removal.
            for j,b in enumerate([[cx-10,y-1.25,107.8,cx-8.8,y+1.25,134.2],
                                  [cx+8.8,y-1.25,107.8,cx+10,y+1.25,134.2],
                                  [cx-8.8,y-1.25,133,cx+8.8,y+1.25,134.2],
                                  [cx-8.8,y-1.25,107.8,cx+8.8,y+1.25,109],
                                  [cx-3,y-2,134.2,cx+3,y+2,139.2]]):
                shapes[leg+'_BODY_TIE_'+str(index)+'_'+str(j)]=box(b)
        shelves[leg+'_SHELF']=shelf
        lo,hi=sorted((side*50.5,side*57.5))
        grip=box([x-4.5,lo,109,x+4.5,hi,113.5])
        grip=grip.cut(Part.makeCylinder(2.75,hi-lo+.2,A.Vector(x,lo-.1,113.5),A.Vector(0,1,0)))
        y=side*54.5
        for sign in (-1,1):
            notch=[x+sign*3.5-.8,y-1.45,108.9,x+sign*3.5+.8,y+1.45,113.6]
            grip=grip.cut(box(notch)); holes.append(dict(kind='feed_tie',leg=leg,bounds_mm=notch))
        shelves[leg+'_GRIP']=grip
        for j,b in enumerate([[x-4.1,y-1.25,108,x-2.9,y+1.25,117.2],
                              [x+2.9,y-1.25,108,x+4.1,y+1.25,117.2],
                              [x-2.9,y-1.25,116,x+2.9,y+1.25,117.2],
                              [x-2.9,y-1.25,108,x+2.9,y+1.25,109],
                              [x-9,y-2,117.2,x-3,y+2,122.2]]):
            shapes[leg+'_FEED_TIE_'+str(j)]=box(b)
        blank=math.ceil((path.Length+11+10)/10)*10
        assert blank<=100
        rows.append(dict(leg=leg,wire=wire,WAGO_mm=list(start),holder_entry_mm=list(end),
                         holder_center_mm=[cx,side*102.5,122],insulated_path_mm=path.Length,
                         nominal_factory_free_lead_required_mm=blank,assumed_available_mm=100,
                         actual_available_mm=None,actual_cut_mm=None,
                         new_stock_wire_mm=0,body_ties=2,feed_ties=1))
    return shapes,shelves,holes,rows


def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'
    shapes,shelves,holes,rows=geometry(A,Part)
    save(OUT/'intent.json',dict(started_utc=begin.isoformat(),selected=False,physical_pass=False,
         assumptions=dict(holder_mm=[35,16,22],wire_OD_mm=5,static_radius_mm=20,each_usable_factory_lead_mm=100,
                          assumed_not_supplier_dimensions=True,replaceable_delivery_datum=True),
         confirmed='MTA0100335 nominal Cu4mm2 only; catalogueL140 does not prove each lead length.',
         ends='Preserve moulded holder connection; strip other untinned end to deliveredWAGO221-415 marking, one conductor per port.',
         routes=rows,holes=holes,new_ties=12,
         native_required='Four integral Deck shelves and four grooves, no extra separate PETG prints. CandidateBREP alone is not a native export.'))
    print('LOAD_CURRENT_OWNERS',flush=True)
    owners,hashes,_=layout.current_owners()
    def load(p):
        hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    for n in list(owners):
        if any(f in n for f in ('/servo-fuse-bank-restraints-r2/','/servo-fuse-bank-restraints-fit-r2/')): del owners[n]
    owners['R49Deck']=load(ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep')
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'): owners[p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('*_DESIGN.brep'):
        if p.stem.startswith(('W0','F_')): owners['R11/'+p.stem]=load(p)
    print('CURRENT_INLINE_OWNERS '+json.dumps([n for n in owners if n.startswith(('F_FL','F_FR','F_RL','F_RR'))]),flush=True)
    deck=owners.pop('R49Deck')
    for s in shelves.values(): deck=deck.fuse(s)
    # Cut feed-tie paths through the retained Deck as well as their new grip.
    for hole in holes:
        if hole['kind']=='feed_tie':
            b=hole['bounds_mm']; b=[b[0],b[1],104.9,b[3],b[4],b[5]]
            deck=deck.cut(Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3])))
    assert deck.isValid() and len(deck.Solids)==1
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'));owners['CandidateDeck']=deck
    hits,errors=[],[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                c.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    installed={n:s for n,s in shapes.items() if not n.endswith('_CENTERLINE')}
    for n,s in {**shapes,**shelves}.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for n,s in installed.items():
        print('FIT '+n,flush=True)
        for m,t in owners.items():check(n,s,m,t)
    for n,s in shelves.items():
        for m,t in owners.items():
            if m!='CandidateDeck':check(n,s,m,t)
    for i,(n,s) in enumerate(installed.items()):
        for m,t in list(installed.items())[i+1:]:
            # The only expected terminal entry is the wire into its own
            # moulded inline holder. Tie/holder touch is surface contact.
            wire=next((r for r in rows if n==r['wire']+'_WIRE' and m==r['leg']+'_HOLDER'),None)
            if wire:continue
            check(n,s,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='PARENT_FEED_CONSTRUCTION_CONFLICTS' if hits or errors else 'PROVISIONAL_PARENT_FEEDS_CLEAR_NATIVE_PENDING',
         selected=False,physical_pass=False,W5_complete=False,routes=rows,holes=holes,hits=hits,errors=errors,pairs=pairs,
         source_sha256=hashes,script_sha256=sha(Path(__file__)),
         open=['NativeDeck/parameter/reopen/export proof before selection.','Verify provisionalMTA body/lead geometry after delivery.','UpstreamS1-to-holder feeds remain wholeW5, not these four outgoing leads.'],
         started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs,blanks=[r['nominal_factory_free_lead_required_mm'] for r in rows])),flush=True)


if __name__=='__main__':main()
