"""One new R48 switch/complete lead corridor, using current P_SYS.1 atX-76.5.

Preserve rejected front-facing S0. The linked family rear cylinder includes
stud space, not an exact casing solid. Own ring/stud overlaps remain conditional;
all unrelated hardware and other wires are checked without that exclusion.
No candidate is selected here. Source-only construction, no E6 reload.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import rounded,save,sha
OUT=ROOT/'hardware/electronics/full-cat/source-switch-layout-r6'


def main():
    import FreeCAD as A
    import Part
    import main_positive_input_r1 as C
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    owners,hashes=C.current_owners();owners.pop('Deck_R41');owners.pop('MAIN_R40')
    def load(p):
        p=Path(p);hashes[p.relative_to(ROOT).as_posix()]=sha(p);s=Part.Shape();s.read(str(p));return s
    deck=load(ROOT/'hardware/cad/studies/battery-feed-pair-r2/Deck_WORLD.brep')
    owners['MAIN_R44']=load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder,pattern in [('hardware/electronics/full-cat/main-positive-complete-r8','*_DESIGN.brep'),('hardware/cad/studies/main-positive-native-r2','*_WORLD.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem not in ('Deck_WORLD','MAIN_WORLD') and not p.stem.startswith('W043_'):owners['R44/'+p.stem]=load(p)
    for p,h in json.loads((ROOT/'hardware/electronics/full-cat/battery-feed-access-finish-r1/checks.json').read_text(encoding='utf-8'))['source_sha256'].items():
        if '/battery-feed-' in p and p.endswith('_DESIGN.brep'):
            # Use corrected source ties and W001, not their superseded copies.
            if '/battery-feed-bridge-r1/' in p and Path(p).stem.startswith(('W001_','W076_FREE_STUB','M2','Bridge','F0BodyTie','FreeSwitchLeadWireTie','PlusWireTie','ReturnWireTie','XT60BodyTie')):continue
            if 'ToolReserve' not in p:owners['Source/'+Path(p).stem]=load(ROOT/p)
    owners['Source/Bridge']=load(ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_WORLD.brep')
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')):owners.pop(n)
    box=lambda b:Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    cyl=lambda p,r,h,axis=(0,0,1):Part.makeCylinder(r,h,A.Vector(*p),A.Vector(*axis))
    parts={'S0_rear_family_including_studs':cyl([-61.5,55,43],28.5,40,(0,1,0)),
        'S0_neck_family':cyl([-61.5,95,43],11,3,(0,1,0)),
        'S0_key_family_tool_reserve':cyl([-61.5,98,43],15,63.5,(0,1,0))}
    panel=box([-91.5,95,6,-33,98,71])
    panel=panel.cut(cyl([-61.5,94.9,43],12,3.2,(0,1,0)))
    # Rotate the same switch45deg around its Y axis: separate the IN approach
    # from the other terminal, without changing stud pitch/lead radius.
    angle=math.pi/4
    stud_axis=A.Vector(-math.sin(angle),0,math.cos(angle))
    bolt_axis=A.Vector(math.cos(angle),0,math.sin(angle))
    bolt_centres=[A.Vector(-61.5,95,43)+bolt_axis*d for d in (-19,19)]
    for c in bolt_centres:panel=panel.cut(cyl([c.x,94.9,c.z],3.25,3.2,(0,1,0)))
    for x in (-87.5,-37):
        panel=panel.fuse(box([x-4,92,71,x+4,94.9,101])).fuse(box([x-4,92,69,x+4,98,73])).fuse(box([x-6,89.5,101,x+6,94.9,105]))
        panel=panel.cut(cyl([x,92,100.9],1.2,4.2))
    parts['S0_mount_candidate']=panel.removeSplitter()
    def line(a,b):return Part.makeLine(a,b)
    def s_shift(begin,axis,shift,r):
        h=shift.Length;u=shift/h;angle=math.acos(1-h/(2*r));run=2*r*math.sin(angle)
        def p(t):
            if t<=angle:return begin+axis*(r*math.sin(t))+u*(r*(1-math.cos(t)))
            q=t-angle
            return begin+axis*(r*math.sin(angle)+r*(math.sin(angle)-math.sin(angle-q)))+u*(r*(1-math.cos(angle))+r*(math.cos(angle-q)-math.cos(angle)))
        return [Part.Arc(p(0),p(angle/2),p(angle)).toShape(),Part.Arc(p(angle),p(1.5*angle),p(2*angle)).toShape()],p(2*angle)
    # F0 intact orange lead: oneR10 lateral shift followed by tangent arc
    # directly into the rotated IN terminal. All datums explicit prototypes.
    # Family panel->stud TIP is40, NOT the lug seating plane. Leave15mm
    # between Y55 tip and Y70 lug plane for1.05+2+8 nut stack and threads.
    inp=A.Vector(-61.5,70,43)-stud_axis*12
    edges,q=s_shift(A.Vector(-33,65,69),A.Vector(-1,0,0),A.Vector(0,5,5),10)
    edges.insert(0,line(A.Vector(-17,65,69),A.Vector(-33,65,69)))
    dx=q.x-inp.x;dz=q.z-inp.z;r=10
    theta=math.atan2(dz-r,dx)+math.asin(r/math.hypot(dx,dz-r))
    def approach(t):return q+A.Vector(-r*math.sin(t),0,r*(math.cos(t)-1))
    end=approach(theta);incoming=A.Vector(-math.cos(theta),0,-math.sin(theta))
    tip=inp-incoming*26.9
    assert (tip-end).dot(incoming)>0
    edges += [Part.Arc(q,approach(theta/2),end).toShape(),line(end,tip)]
    routes={'W076':edges};directions={'IN':-incoming}
    out=A.Vector(-61.5,70,43)+stud_axis*12;R=25.2
    alpha=math.acos((out.x+90.5)/(26.9+R));u=A.Vector(-math.cos(alpha),0,math.sin(alpha));tip=out+u*26.9
    def turn(t):return tip+u*(R*math.sin(t))+A.Vector(0,-1,0)*(R*(1-math.cos(t)))
    q=turn(math.pi/2)
    outedges=[Part.Arc(tip,turn(math.pi/4),q).toShape()]
    e,q=s_shift(q,A.Vector(0,-1,0),A.Vector(0,0,71-q.z),R);outedges+=e
    entry=A.Vector(-90.5,-65,71);outedges.append(line(q,entry))
    def front(t):return entry+A.Vector(0,-R*math.sin(t),R*(1-math.cos(t)))
    q=front(math.pi);outedges += [Part.Arc(entry,front(math.pi/2),q).toShape()]
    begin=A.Vector(-90.5,-47,121.4);outedges.append(line(q,begin))
    e,q=s_shift(begin,A.Vector(0,1,0),A.Vector(6.5,0,-7.9),R);outedges+=e
    assert q.y < -11
    outedges.append(line(q,A.Vector(-84,-11,113.5)))
    routes['W066']=outedges;directions['OUT']=u
    # Same common P_SYS potential: use westmost cage for the larger source
    # wire and move F_PI.2 to the adjacent cage. Logical graph is unchanged.
    e,q=s_shift(A.Vector(-76.5,-11,113.5),A.Vector(0,-1,0),A.Vector(3.5,0,1.5),6)
    routes['W043']=e+[line(q,A.Vector(-73,-21,115))]
    # Conservative ring widths/length from TE130207. Rear cylinder includes
    # its own terminal/stud space: not an unrelated obstruction.
    for name,centre in [('IN',inp),('OUT',out)]:
        v=directions[name];cross=A.Vector(-v.z,0,v.x)
        corners=[centre+v*a+cross*b+A.Vector(0,y,0) for a,b,y in [(-6.9,-6.75,-1.05),(26.9,-6.75,-1.05),(26.9,6.75,-1.05),(-6.9,6.75,-1.05)]]
        face=Part.Face(Part.makePolygon(corners+[corners[0]]));tongue=face.extrude(A.Vector(0,1.05,0))
        tongue=tongue.cut(cyl(list(centre+A.Vector(0,-1.15,0)),5.02,1.25,(0,1,0)))
        barrel=cyl(list(centre+v*11.9),3.2,15,v)
        parts['TE130207_'+name]=Part.makeCompound([tongue,barrel])
    wires={};lengths={};portals=[]
    for name,edges in routes.items():
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6,(name,'end')
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6,(name,'tangent')
        od={'W076':4.5,'W066':4.2,'W043':3.4}[name]
        path=sum(e.Length for e in edges);extra={'W076':18.73,'W066':32.73,'W043':22}[name]
        lengths[name]=dict(path_mm=path,nominal_candidate_blank_mm=math.ceil((path+extra)/10)*10,
            supplied_nominal_limit_mm=89.5096 if name=='W076' else None,actual_cut_mm=None)
        for i,e in enumerate(edges):
            s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(od/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            assert s.isValid();wires[f'{name}_{i}']=s
            e.exportBrep(str(OUT/f'{name}_{i}_CENTERLINE.brep'))
            if s.BoundBox.intersect(deck.BoundBox):
                portal=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(od/2+.5,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
                if portal.common(deck).Volume>1e-5:portals.append(portal);deck=deck.cut(portal)
    for x in (-87.5,-37):
        deck=deck.cut(cyl([x,92,104.9],1.2,4.2))
        parts[f'M2bolt_{x}']=cyl([x,92,97.3],1,12).fuse(cyl([x,92,109.3],1.9,2))
        parts[f'M2washers_{x}']=cyl([x,92,100.7],2.5,.3).fuse(cyl([x,92,109],2.5,.3))
        parts[f'M2nut_{x}']=cyl([x,92,99.1],2.31,1.6).cut(cyl([x,92,99],1,1.8))
    owners['Deck_candidate']=deck
    # These are prospective purchased items only, NOT a quantity selection.
    for i,c in enumerate(bolt_centres):
        parts[f'M6mount_reserve_{i}']=cyl([c.x,89,c.z],3,16,(0,1,0))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=v))
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**parts,**wires}.items():
        s.exportBrep(str(OUT/f'{n}_DESIGN.brep'))
        for m,t in owners.items():
            if n.startswith('W043_') and m=='R44/F_PI_holder_DESIGN':continue
            check(n,s,m,t)
        check(n,s,'cassette_drop40',box([-87,-27,-44,129,27,28.7]))
    for n,s in wires.items():
        for m,t in wires.items():
            if n.split('_')[0]!=m.split('_')[0] and n<m:check(n,s,m,t)
        check(n,s,'S0_mount',parts['S0_mount_candidate'])
        for m in ('TE130207_IN','TE130207_OUT'):
            if m.endswith('IN') != n.startswith('W076'):check(n,s,m,parts[m])
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'))
    for i,s in enumerate(portals):s.exportBrep(str(OUT/f'Portal_{i}_UNSELECTED.brep'))
    end=datetime.now(timezone.utc)
    decision=dict(status='REJECTED_NEW_SWITCH_CORRIDOR' if hits or errors else 'LOCAL_LAYOUT_NEEDS_NATIVE_RESTRAINTS_SHELL_PORT_AND_HARDWARE',
        parent='one-batch-prototype-r48',hits=hits,errors=errors,pairs=pairs,lengths=lengths,
        S0_axis=dict(centre=[-61.5,95,43],direction=[0,-1,0]),P_SYS_1=[-84,-11,113.5],P_SYS_2=[-76.5,-11,113.5],
        S0_rotation_deg=45,stud_centres_provisional=[list(inp),list(out)],mount_hole_centres=[list(c) for c in bolt_centres],
        P_SYS_labels_plus_X=['.1','.2','.3','.4','.5'],replaced_source_parts=['W076_FREE_STUB placeholder only','W043 route and first two physical labels'],
        factory_W076_within_nominal_limit=lengths['W076']['nominal_candidate_blank_mm']<=89.5096,
        source_sha256=hashes,script_sha256=sha(Path(__file__)),selected=False,W5_complete=False,physical_pass=False,
        prototype_not_supplier=['Rear57x40 and key66.5 family reserves; rear includes studs, NOT exact casing.',
            'Stud tipY55 from family reserve; lug seating planeY70 leaves15mm for sourced nominal M10 hardware. Pitch24 and casing start/clocking remain prototype assumptions, not exact supplier datums.',
            'F0 OD4.5/R10 accepted provisional geometry; actual minimum lead length/OD must be checked before trimming.',
            'S0 requires an aperture at the existing lower side; existing shell not silently cut or declared clear.'],
        intended_own_contacts='Own S0 rear-family stud/ring region only; no unrelated component, wire or mount exception.',
        remaining=['Complete strain relief, exactM6/M10 hardware and access, native mount/Deck, lower E6 aperture.','WholeW5 remains OPEN.'],
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',decision)
    print(json.dumps({k:decision[k] for k in ('status','hits','errors','pairs','lengths','factory_W076_within_nominal_limit','worker_wall_seconds')}),flush=True)


if __name__=='__main__':main()
