"""Complete the same R4 side bank using its measured collision locations.

Not a rerun of R1/2/3: twelve holders move outboard and upwards together.
Four P WAGOs turn in place, without the rejected inward translation. There
are no new flag-terminal/tool purchases. No shape or stock is selected here.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics'), str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r7'

def input_path(A, Part, start, end, side, lift=0, delay=0, R=12.4):
    """Tangent circular bends, not a spline with an uncontrolled turnaround.

    S-shift+X while traveling outwardsY; then Y->-Z->Y->+Z, ending
    straight into the existing TE terminal. All bends have exact radiusR.
    """
    p=A.Vector(*start); u=A.Vector(0,side,0); x=A.Vector(1,0,0)
    dz=A.Vector(0,0,-1); up=-dz; edges=[]
    def arc(first, last, angle):
        nonlocal p
        begin=A.Vector(p)
        def point(t):return begin+first*(R*math.sin(t))+last*(R*(1-math.cos(t)))
        edges.append(Part.Arc(point(0),point(angle/2),point(angle)).toShape())
        p=point(angle)
    def line(q):
        nonlocal p
        if (q-p).Length>1e-7:edges.append(Part.makeLine(p,q));p=q
    arc(u,dz,math.pi/2)
    assert p.z>end[2]
    line(A.Vector(p.x,p.y,end[2]));arc(dz,u,math.pi/2)
    shift_vector=A.Vector(end[0]-start[0],0,lift)
    shift=shift_vector.Length;assert shift_vector.x>0
    x=shift_vector/shift
    if shift>=2*R:
        arc(u,x,math.pi/2);line(p+x*(shift-2*R));arc(x,u,math.pi/2)
    else:
        angle=math.acos(1-shift/(2*R))
        arc(u,x,angle)
        # Same tangent orientation at join; curvature reverses for the S.
        tangent=u*math.cos(angle)+x*math.sin(angle)
        inward=u*math.sin(angle)-x*math.cos(angle)
        arc(tangent,inward,angle)
    assert abs(p.x-end[0])<1e-6
    stop=side*end[1]-R;assert side*p.y<stop
    line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2)
    assert (p-A.Vector(*end)).Length<1e-6
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
    wire=Part.Wire(edges)
    assert all(abs(e.Curve.Radius-R)<1e-6 for e in edges if hasattr(e.Curve,'Radius'))
    return wire

def current_owners():
    import Part
    import main_positive_input_r1 as C
    owners, hashes = C.current_owners()
    owners.pop('Deck_R41'); owners.pop('MAIN_R40')
    def load(p):
        p = Path(p); hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        s = Part.Shape(); s.read(str(p)); return s
    owners['R49Deck'] = load(ROOT/'hardware/cad/studies/source-switch-deck-native-r3/Deck_WORLD.brep')
    owners['R49S0Mount'] = load(ROOT/'hardware/cad/studies/source-switch-mount-finish-r4/Mount_WORLD.brep')
    owners['MAIN_R44'] = load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder, pattern in [('main-positive-complete-r8','*_DESIGN.brep'),
                            ('source-switch-layout-r6','*_DESIGN.brep'),
                            ('source-switch-restraints-r2','*_DESIGN.brep'),
                            ('source-switch-mount-finish-r4','M*_DESIGN.brep'),
                            ('source-switch-assembly-finish-r3','M2*_DESIGN.brep')]:
        for p in (ROOT/'hardware/electronics/full-cat'/folder).glob(pattern):
            if 'tool' in p.stem.lower(): continue # temporary bench access, not an installed obstacle
            if p.stem.startswith(('W043_', 'S0_mount_', 'M2bolt_', 'M2washers_', 'M2nut_')):
                # OldM2 axes in layoutR6 are replaced by actual assemblyR3.
                if folder != 'source-switch-assembly-finish-r3': continue
            owners[folder+'/'+p.stem] = load(p)
    for p in (ROOT/'hardware/electronics/full-cat/source-switch-layout-r6').glob('W043_*_DESIGN.brep'):
        owners['R49/'+p.stem] = load(p)
    for p in (ROOT/'hardware/cad/studies/main-positive-native-r2').glob('*_WORLD.brep'):
        if p.stem not in ('Deck_WORLD','MAIN_WORLD'): owners['R44/'+p.stem] = load(p)
    source = json.loads((ROOT/'hardware/electronics/full-cat/battery-feed-access-finish-r1/checks.json').read_text(encoding='utf-8'))
    for rel in source['source_sha256']:
        if '/battery-feed-' not in rel or not rel.endswith('_DESIGN.brep'): continue
        if 'ToolReserve' in rel: continue
        if '/battery-feed-bridge-r1/' in rel and Path(rel).stem.startswith(('W001_','W076_FREE_STUB','M2','Bridge','F0BodyTie','FreeSwitchLeadWireTie','PlusWireTie','ReturnWireTie','XT60BodyTie')): continue
        owners['Source/'+Path(rel).stem] = load(ROOT/rel)
    owners['Source/Bridge'] = load(ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_WORLD.brep')
    removed = []
    for name in list(owners):
        if re.fullmatch(r'F_(FL|FR|RL|RR)[123]_(MTA_conservative_housing|287_entire_height)', name):
            removed.append(name); del owners[name]
    assert len(removed) == 24, removed
    # Tail shape occurs twice in inherited checks; one geometry only, not a
    # deleted obstacle. Keep the selected named owner and document the alias.
    alias = 'hardware/cad/studies/tail-local-finish-r2/TailLocalCompleteSupportR2.brep'
    if alias in owners and 'Selected_tail_support' in owners:
        # OCChashCode identifies a loaded topology, not geometry across two
        # independent BREP reads. Compare their actual symmetric difference.
        a, b = owners[alias], owners['Selected_tail_support']
        assert abs(a.Volume-b.Volume)<1e-5
        assert a.cut(b).Volume+b.cut(a).Volume<1e-5
        del owners[alias]
    return owners, hashes, removed

def main():
    import FreeCAD as A
    import Part
    begin = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed construction'
    ledger = ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    rows = [r for r in json.loads(ledger.read_text(encoding='utf-8'))['conductors'] if r['group']=='SERVO_FUSE_INPUTS']
    assert len(rows) == 12
    save(OUT/'intent.json', dict(parent='one-batch-prototype-r51', selected=False, physical_pass=False,
        W5_complete=False, started_utc=begin.isoformat(),
        change='R6 removed all four wire-wire hits but ten fixed-owner contacts remain. Lower all S-fans below Deck toZ83.47 before spreadingX, with fullR12.4 tangent bends. Keep bank, terminals and S0-clear feet. Portal cuts and cover adaptation remain explicit gates.',
        predecessor='servo-fuse-side-bank-r6/checks.json:10 fixed-owner hits; wire-wire clear. Never rerun that unchanged geometry.',
        prototype=dict(MTA_seating_e_mm=0, terminal_axis_offset_y_mm=7, mouth_z_mm=120,
                       holder_y_mm=110, fixed_wire_OD_mm=3.1, fixed_radius_min_mm=12.4),
        next_gate='Routes,24ends, holders, prospective panels and current source interfaces together. If clear, complete native mounts, output routes/reliefs and E6 adaptation before selection.',
        source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger)}))
    owners, hashes, removed = current_owners()
    def box(b): return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    holders, terminals, mounts, wires, paths, lengths, placement = {}, {}, {}, {}, {}, [], {}
    deck=owners.pop('R49Deck')
    original_deck_volume=deck.Volume
    for side in (-1,1):
        # Panel top146.5 +2mm holder flange -> body/cap top148.5.
        lo, hi = sorted([side*90, side*130])
        panel = box([-97,lo,144.5,107,hi,146.5])
        # Feet sit on the unaltered Deck, above all lower source hardware.
        for x in (-95,105):
            a,b = sorted([side*91,side*97])
            post = box([x-2,a,109,x+2,b,144.7])
            foot = box([x-5,a,109,x+5,b,113])
            mounts[f'Post_{side}_{x}'] = post.fuse(foot)
        for base in (-69,39):
            for i in range(3):
                cx=base+26*i; cy=side*110
                panel=panel.cut(box([cx-5.65,cy-11.1,144.4,cx+5.65,cy+11.1,146.6]))
        mounts[f'Panel_{side}'] = panel
    for row in rows:
        fuse = next(p for p in (row['a'],row['b']) if p.startswith('F_'))
        wago = next(p for p in (row['a'],row['b']) if not p.startswith('F_'))
        name=fuse.split('.')[0]; leg=name[2:4]; index=int(name[4]); side=1 if leg.endswith('L') else -1
        base=-69 if leg.startswith('F') else 39
        sx=base+(int(wago.split('.')[1])-3)*6.75
        cx=base+26*(index-1);cy=side*110
        holders[name] = box([cx-7.75,cy-14.25,120,cx+7.75,cy+14.25,148.5])
        holders[name+'_ATO'] = box([cx-2.55,cy-9.55,148.5,cx+2.55,cy+9.55,167.3])
        for role,dy,L,H in [('IN',7,23.749,9.8552),('OUT',-7,21.717,5.080)]:
            ty=cy+side*dy; bottom=120-L-.381
            terminals[name+'_'+role] = box([cx-5.1943,ty-(H+.381)/2,bottom,cx+5.1943,ty+(H+.381)/2,120])
            if role=='IN': end=[cx,ty,bottom]
        start=[sx,side*49.5,113.5]
        e=input_path(A,Part,start,end,side,lift=0, delay=0)
        s=e.makePipeShell([Part.Wire([Part.makeCircle(1.55,A.Vector(*start),A.Vector(0,side,0))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        wires[row['id']]=s; paths[row['id']]=e
        clearance=e.makePipeShell([Part.Wire([Part.makeCircle(1.95,A.Vector(*start),A.Vector(0,side,0))])],True,False)
        if clearance.BoundBox.intersect(deck.BoundBox):deck=deck.cut(clearance)
        lengths.append(dict(id=row['id'],a=row['a'],b=row['b'],path_mm=e.Length,
            nominal_unselected_blank_mm=math.ceil((e.Length+14+8.30+10)/10)*10,
            actual_cut_mm=None, radius_lower_bound_mm=12.4))
        placement[row['id']]=dict(start=start,end=end,route='Y/-Z/Y before lower planar S-XY fan atZ83.47, then Y/+Z into TE',holder=[cx,cy,120],
            WAGO_face='Outer face after180deg in-place rotation; all five cages must be relabelled in later complete interface, not silently remapped now.')
    assert deck.isValid() and len(deck.Solids)==1
    owners['Deck_WITH_UNSELECTED_FULL_PORTALS']=deck
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'))
    for group in (holders,terminals,mounts,wires):
        for n,s in group.items(): s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for n,e in paths.items(): e.exportBrep(str(OUT/(n+'_CENTERLINE.brep')))
    hits, errors, intended, cover_hits = [], [], [], [];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for q in s.Solids:
            for v in t.Solids:
                if not q.BoundBox.intersect(v.BoundBox):continue
                pairs+=1
                try:
                    common=q.common(v)
                    vol=common.Volume
                    if vol>1e-5:
                        row=dict(part=n,owner=m,hit_mm3=vol,bounds_mm=[getattr(common.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
                        if m.endswith('/CoverYawEndSeat.brep'):cover_hits.append(row)
                        else:hits.append(row)
                except Exception as ex: errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**holders,**terminals,**mounts,**wires}.items():
        for m,t in owners.items():check(n,s,m,t)
    for n,s in wires.items():
        for m,t in {**holders,**terminals,**mounts}.items():check(n,s,m,t)
    for i,n in enumerate(wires):
        for m in list(wires)[i+1:]:check(n,wires[n],m,wires[m])
    for i,n in enumerate(terminals):
        for m in list(terminals)[i+1:]:check(n,terminals[n],m,terminals[m])
        for m,t in mounts.items():check(n,terminals[n],m,t)
    # Full boxed housing includes flange: nominal latch cutouts are separate
    # manufacturer datums, not a fabricated exact snap/clearance model.
    for n,s in holders.items():
        for m,t in mounts.items():
            if m.startswith('Panel_') and not n.endswith('_ATO'):
                if s.BoundBox.intersect(t.BoundBox):intended.append(dict(holder=n,panel=m,condition='Own MTA flange/latch fit;2mm panel and22.2x11.3nominal cutout, delivery coupon required.'))
            else:check(n,s,m,t)
    endtime=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='INTERNAL_CONFLICTS' if hits or errors else 'INTERNAL_INPUTS_CLEAR_COVER_NATIVE_OUTPUTS_RESTRAINTS_OPEN',
        hits=hits,errors=errors,cover_hits_not_waived=cover_hits,pairs=pairs,placements=placement,lengths=lengths,
        input_routes=12,terminal_reserves=24,removed_old_fuse_owners=removed,
        inherited_tail_alias_deduplicated=True,own_panel_contacts=intended,
        existing_TE_parts_preserved=True,new_purchased_terminal_or_tool_SKU=0,
        prospective_added_panels=2,prospective_print_panels_mm=[204,40,2],
        Deck_removed_mm3=original_deck_volume-deck.Volume,Deck_valid_single_solid=True,
        cover_adaptation_not_completed=True,output_routes_open=True,restraints_open=True,
        planned_required_blank_mm=sum(r['nominal_unselected_blank_mm'] for r in lengths),
        selected=False,W5_complete=False,physical_pass=False,source_sha256=hashes,
        script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=endtime.isoformat(),
        worker_wall_seconds=(endtime-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),cover_hits=len(cover_hits),errors=len(errors),pairs=pairs,
        blanks=sum(r['nominal_unselected_blank_mm'] for r in lengths))),flush=True)

if __name__=='__main__':main()




