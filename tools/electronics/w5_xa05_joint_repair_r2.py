"""Complete raised corridor and two narrow integral support/tie stations.

R1 contacts were all at or below132.2mm. Use135mm below the Carrier floor,
retaining bought blocks/endpoints, and keep supports in the two measured gaps
between the terminal blocks and centre fuse cases. No arbitrary owner omission.
"""
from pathlib import Path
BASE=Path(__file__).with_name('w5_xa05_joint_repair_r1.py')
source=BASE.read_text(encoding='utf-8')


def replace(a,b):
    global source
    assert source.count(a)==1,a
    source=source.replace(a,b)


replace("w5-xa05-joint-repair-r1'","w5-xa05-joint-repair-r2'")
replace('c.shift([0,0,17.5]);c.arc(mul(X,-1))','c.shift([0,0,21.5]);c.arc(mul(X,-1))')
replace('c.line([79,c.p[1],131]);c.arc(mul(Y,-1))','c.line([79,c.p[1],135]);c.arc(mul(Y,-1))')
replace('c.line([64,-42,131]);c.arc(X);c.shift([0,0,-17.5])','c.line([64,-42,135]);c.arc(X);c.shift([0,0,-21.5])')
replace('    edges=[];pieces=[];hits=[];errors=[];pairs=0', '''    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    seats={};ties={};tools=[];specs=[]
    for name,y in [('North',27.05),('South',-24.5)]:
        raw=[60.7,y-3.3,108.8,67.3,y+3.3,135.7]
        groove=Part.makeCylinder(1.5,6.8,A.Vector(64,y-3.4,135),A.Vector(0,1,0))
        seat=box(raw).cut(groove)
        left,right=59.9,68.1;bottom=109.5;top=137.2
        for x in (left,right):tools.append(box([x-.8,y-1.6,108.8,x+.8,y+1.6,138.5]))
        tunnel=box([left-1,y-1.6,109.4,right+1,y+1.6,110.8]);tools.append(tunnel)
        seat=seat.cut(tunnel);seats[name]=seat
        ties[name]=Part.makeCompound([
            box([x-.6,y-1.25,bottom,x+.6,y+1.25,top+1.2]) for x in (left,right)
        ]+[box([left-.6,y-1.25,top,right+.6,y+1.25,top+1.2]),
           box([left-.6,y-1.25,bottom,right+.6,y+1.25,bottom+1.2]),
           box([right-1.4,y-2.5,bottom-.1,right+3.6,y+2.5,bottom+3.9])])
        specs.append(dict(name=name,y_mm=y,seat_bounds_mm=raw,groove_centre=[64,y,135],groove_R_mm=1.5,
            tie_SKU='111-03110 T18I',tie_axis='Y',tie_head_nominal_mm=[5,5,4],actual_head_measured=False))
    # Local candidate only; native feature tree and whole updated Deck export
    # follow only if this shared wire/support/tie arrangement is clear.
    deck=owners.pop('CandidateDeck') if 'CandidateDeck' in owners else owners.pop('Deck_R53_BUS')
    deck=deck.fuse(Part.makeCompound(list(seats.values()))).cut(Part.makeCompound(tools))
    deck.exportBrep(str(OUT/'DECK_CANDIDATE_WORLD.brep'))
    print('XA05_JOINT_DECK_SAVED',deck.isValid(),len(deck.Solids),flush=True)
    assert deck.isValid() and len(deck.Solids)==1
    owners['NewDeckXA05']=deck
    edges=[];pieces=[];hits=[];errors=[];pairs=0''')
replace('    files=[]','''    for name,s in {**{n+'_seat':v for n,v in seats.items()},**{n+'_tie':v for n,v in ties.items()}}.items():
        for key,other in {**owners,**{n+'_seat':v for n,v in seats.items()}}.items():
            if key==name or (name.endswith('_seat') and key=='NewDeckXA05'):continue
            if not s.BoundBox.intersect(other.BoundBox):continue
            pairs+=1
            try:
                v=s.common(other).Volume
                if v>1e-5:hits.append(dict(part=name,owner=key,mm3=v))
            except Exception as ex:errors.append(dict(part=name,owner=key,error=str(ex)))
    files=[]
    for name,s in [('DECK_CANDIDATE_WORLD.brep',deck),('SUPPORTS_WORLD.brep',Part.makeCompound(list(seats.values()))),
                   ('TIES_WORLD.brep',Part.makeCompound(list(ties.values()))),('SLOT_TOOLS_WORLD.brep',Part.makeCompound(tools))]:
        p=OUT/name;s.exportBrep(str(p));files.append(p)''')
replace("pins += [Path(__file__),ROOT/", "pins += [BASE,Path(__file__),ROOT/")
replace("native_restraints_ready=False,selected=False,W1_complete=False", "support_specs=specs,new_ties=2,new_fasteners=0,native_restraints_ready=False,selected=False,W1_complete=False")
exec(compile(source,str(Path(__file__).resolve()),'exec'))
