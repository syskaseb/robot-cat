"""Bind five remote ends to current geometry before native CAD changes.

Preserve the existing BUS plug strap and MAIN tail restraint where their
actual stations still match. Replace only BAT's obsolete strap, and add one
integral AUX seat. No new connector, electrical splice or servo cable.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, re
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import sha, save
from w5_exact_separation import separated
ROOT=N.ROOT; BASE=N.BASE; OUT=BASE/'w5-remote-end-layout-r1'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))


def current(A, Part):
    """Current49-wire/native census plus unchanged installed fixed owners."""
    import w5_central_shared_routes as scope
    fixed, printed, ends, family, rows, inherited, _, _=scope.load_scope(A,Part)
    pins={}
    def pin(p):
        p=Path(p); pins[p.relative_to(ROOT).as_posix()]=sha(p); return p
    def load(p): return Part.read(str(pin(p)))
    materials={}; central=read(pin(N.CENTRAL))
    for wire,row in central['routes'].items(): materials[wire]=load(ROOT/row['geometry'])
    bp=pin(BASE/'w5-branch-joint-routes-r3/checks.json')
    for row in read(bp)['accepted']:
        wire=row['wire']
        if wire not in materials:
            materials[wire]=load(N.centreline(wire,central).parent/(wire+'_WORLD.brep'))
    assert len(materials)==37
    vp=pin(BASE/'w5-leg-joint-source-layout-r1/checks.json')
    for row,s in zip(read(vp)['routes'],load(vp.parent/'FANOUTS_WORLD.brep').childShapes()):
        if row['role']=='V': materials[row['wire']]=s
    assert len(materials)==49
    wire_ids=set(materials)
    for key in list(fixed):
        if any(re.search(r'(?<![A-Za-z0-9])'+w+r'(?![A-Za-z0-9])',key) for w in wire_ids):
            fixed.pop(key)
    # Retain the MAIN restraint after explicitly receiving its unchanged tail.
    from w5_selected_owners_r52 import cached
    cache,cache_receipt=cached()
    for key,s in cache.items():
        if key.startswith('Input/MAIN_input_tie_'): fixed[key]=s
    for key in ('Source/ReturnWireTie_DESIGN',): fixed.pop(key,None)
    for key in N.OWNER_ALIASES: fixed.pop(key,None)
    # These registered parent owners are replaced by the current native set.
    for key in ('CandidateDeck','SourceDeck','SourceCarrier','SourceCover','SourceEastHood',
                'SourceWestHood','SourceBankLeft','BankLeft','Cover',
                'hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep'):
        fixed.pop(key,None)
    rp=pin(BASE/'w5-loom-fixed-native-r1/checks.json')
    for name in read(rp)['editable_final_objects']:
        materials[name]=load(ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'/(name+'_CANDIDATE_WORLD.brep'))
    for name in ('SourceCarrier','SourceCover'):
        materials[name]=load(ROOT/'hardware/cad/studies/w5-side-retention-native-r1'/(name+'_CANDIDATE_WORLD.brep'))
    materials['SourceWestHood']=load(ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/SourceWestHood_CANDIDATE_WORLD.brep')
    materials['SourceBankLeft']=load(ROOT/'hardware/cad/studies/w5-source-bank-passage-native-r1/BankLeft_WORLD.brep')
    cp=pin(BASE/'w5-leg-corridors-r3/intent.json')
    for row,s in zip(read(cp)['routes'],load(cp.parent/'CORRIDORS_WORLD.brep').childShapes()):
        materials['Factory/'+row['loom']]=s
    for folder,prefix in (('w5-source-link-grips-r2','Link/'),('w5-source-hip-grips-r3','Hip/')):
        bp=pin(BASE/folder/'blueprint.json')
        for name,s in zip(read(bp)['roles'],load(bp.parent/'TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep').childShapes()):
            materials[prefix+name]=s
    # Cache geometry and each actual receipt are compact transitive dependencies.
    for p in (BASE/'w5-installed-r52/owners.json', BASE/'w5-installed-r52/installed.brep',
              BASE/'w5-source-hip-harness-interface-r1/checks.json',
              BASE/'w5-source-link-harness-interface-r1/checks.json'):
        pin(p)
    materials.update({'Fixed/'+k:s for k,s in fixed.items()})
    return materials,pins,central,cache


def blueprint():
    return dict(
        BAT=dict(wire='W001',logical_end='BAT.minus',station_mm=[55.5,72,70],axis=[0,1,0],
                 OD_mm=3.1,owner='Fixed/Source/Bridge',root_box_mm=[52.8,70.6,58.8,58.2,73.4,70],
                 groove_radius_mm=1.75,groove_start_mm=[55.5,70.5,70],groove_height_mm=3,
                 tie_local_mm=dict(across=2.05,bottom=55.8,top=71.55),
                 replace='Source/ReturnWireTie_DESIGN',new_ties=0),
        AUX=dict(wire='XA05',logical_end='G_AUX.1',station_mm=[107.5,-57,113.5],axis=[1,0,0],
                 OD_mm=2.5,owner='CompleteDeck',root_box_mm=[106.1,-59.45,108.8,108.9,-54.55,113.5],
                 groove_radius_mm=1.45,groove_start_mm=[106,-57,113.5],groove_height_mm=3,
                 tie_local_mm=dict(across=1.75,bottom=103.8,top=114.75),
                 replace='obsolete XA05 outrigger/ties from prior route, not selected again',new_ties=1),
        BUS=dict(wires=['W002','W003'],logical_ends=['BUS.D','BUS.G'],
                 station_z_mm=85.75,source_xy_mm=[[-44.53188896810009,30.285041680133354],[-42.53188896810009,30.285041680133354]],
                 owner='CompleteDeck',reuse='w5-bus-restraints-r3/Plug',new_ties=0,
                 source_plug_factory=True,terminal_OD_mm=2,
                 assembly='Thread existing plug strap before Deck is populated; keep V contact removed and identify D/G by continuity.'),
        MAIN=dict(wire='W060',logical_end='MAIN.GND',reuse='Input/MAIN_input_tie_0..4',
                  owner='existing MAIN native mounting adapter',new_ties=0,
                  unchanged_tail='w5-main-ground-low-return-r3 retains main_input_return_r4 cubic tail and bare pad',
                  assembly='Retain insulated tail, two inner sleeves and common outer boot. Tighten existing MAIN strap only on insulation, not solder.'))


def proposed(A,Part,bp):
    def box(b): return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    out={};cuts={}
    for name in ('BAT','AUX'):
        r=bp[name];x,y,z=r['station_mm'];axis=r['axis']
        groove=Part.makeCylinder(r['groove_radius_mm'],r['groove_height_mm'],A.Vector(*r['groove_start_mm']),A.Vector(*axis))
        out[name+'Seat']=box(r['root_box_mm']).cut(groove)
        # Local transverse-X / cable-Y coordinates, rotated for AUX's X cable.
        transform=A.Placement(A.Vector(x,y,0),A.Rotation(A.Vector(0,0,1),0 if axis==[0,1,0] else -90))
        t=r['tie_local_mm'];a=t['across'];lo=t['bottom'];hi=t['top']
        boxes=[[-a-1.2,-1.25,lo,-a,1.25,hi+1.2],[a,-1.25,lo,a+1.2,1.25,hi+1.2],
               [-a,-1.25,hi,a,1.25,hi+1.2],[-a,-1.25,lo,a,1.25,lo+1.2],
               [-2.25,-2.4,lo-3.5,2.25,2.4,lo]]
        for i,b in enumerate(boxes):
            s=box(b);s.Placement=transform.multiply(s.Placement);out[name+('Tie' if i<4 else 'Head')+str(i)]=s
        tools=[]
        for u in (-a-1.2,a):
            s=box([u-.2,-1.55,lo-.2,u+1.4,1.55,hi+1.4]);s.Placement=transform.multiply(s.Placement);tools.append(s)
        cuts[name]=Part.makeCompound(tools)
    import w5_bus_restraints_r3 as bus
    sx=sum(p[0] for p in bp['BUS']['source_xy_mm'])/2
    out.update({'BUS'+k:s for k,s in bus.restraints(A,Part,sx).items() if k.startswith('Plug/')})
    return out,cuts


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);bp=blueprint()
    save(OUT/'blueprint.json',dict(status='FIVE_REMOTE_ENDS_SAVED_BEFORE_MATERIAL_CHECK',groups=bp,
         prepared_ends=5,changed_native_owners=['Source/Bridge','CompleteDeck'],
         no_new_splices=True,no_new_connector_SKUs=True,net_new_ties=1,
         selected=False,W1_complete=False,W5_complete=False,physical_pass=False))
    materials,pins,central,cache=current(A,Part)
    proposed_shapes,cuts=proposed(A,Part,bp)
    received_tails=[]
    for name in ('BAT','AUX'):
        r=bp[name];pathfile=N.centreline(r['wire'],central);pins[pathfile.relative_to(ROOT).as_posix()]=sha(pathfile)
        path=Part.read(str(pathfile));point=A.Vector(*r['station_mm'])
        edges=[e for e in path.Edges if type(e.Curve).__name__=='Line' and e.distToShape(Part.Vertex(point))[0]<1e-6]
        assert len(edges)==1,name
        e=edges[0];u=e.Curve.parameter(point)
        margins=[abs(u-e.FirstParameter),abs(e.LastParameter-u)]
        assert min(margins)>=1.4,name
        received_tails.append(dict(group=name,station_mm=r['station_mm'],straight_edge_mm=e.Length,station_margins_mm=margins))
    for wire,xy in zip(bp['BUS']['wires'],bp['BUS']['source_xy_mm']):
        p=N.centreline(wire,central);pins[p.relative_to(ROOT).as_posix()]=sha(p)
        s=Part.read(str(p));v=A.Vector(*xy,bp['BUS']['station_z_mm'])
        assert any(type(e.Curve).__name__=='Line' and e.distToShape(Part.Vertex(v))[0]<1e-6 for e in s.Edges),wire
        received_tails.append(dict(group='BUS',wire=wire,station_mm=list(v),existing_shared_plug_strap=True))
    # Native roots must have real positive bearing overlap, never just touch a bbox.
    bearings=[]
    for name in ('BAT','AUX'):
        seat=proposed_shapes[name+'Seat'];owner=materials[bp[name]['owner']]
        v=sum(seat.common(q).Volume for q in owner.Solids if seat.BoundBox.intersect(q.BoundBox))
        bearings.append(dict(group=name,owner=bp[name]['owner'],root_overlap_mm3=v));assert v>1e-6,bearings[-1]
        materials[bp[name]['owner']]=owner.fuse(seat).cut(cuts[name])
    hits=[];errors=[];pairs=0
    test_parts={k:s for k,s in proposed_shapes.items() if not k.endswith('Seat')}
    test_parts.update({k:s for k,s in cache.items() if k.startswith('Input/MAIN_input_tie_')})
    def check(label,s,owner,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-6:hits.append(dict(part=label,owner=owner,mm3=c.Volume))
                except Exception as ex:errors.append(dict(part=label,owner=owner,error=str(ex)))
    for label,s in proposed_shapes.items():
        if label.endswith('Seat'):
            own=bp[label[:-4]]['owner']
            for owner,t in materials.items():
                if owner!=own:check(label,s,owner,t)
    for label,s in test_parts.items():
        for owner,t in materials.items():
            if owner!=label:check(label,s,owner,t)
    for wire in ('W001','W002','W003','XA05'):
        for owner in ('Fixed/Source/Bridge','CompleteDeck'):check(wire,materials[wire],owner,materials[owner])
    roles=list(proposed_shapes);geom=OUT/'REMOTE_END_MATERIAL_PROPOSED_WORLD.brep'
    Part.makeCompound(list(proposed_shapes.values())).exportBrep(str(geom))
    finish=datetime.now(timezone.utc)
    for p in (Path(__file__),OUT/'blueprint.json',ROOT/'tools/electronics/w5_bus_restraints_r3.py',
              BASE/'w5-main-ground-low-return-r3/checks.json',
              BASE/'main-input-return-finish-r3/checks.json',
              BASE/'battery-feed-mount-finish-r2/checks.json'):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    save(OUT/'checks.json',dict(status='REMOTE_END_LAYOUT_REJECTED' if hits or errors else 'FIVE_REMOTE_END_LAYOUT_STATIC_CLEAR_NATIVE_PENDING',
         endpoint_count=5,tail_station_bindings=received_tails,bearing_bindings=bearings,
         reused_MAIN_tail_restraint=True,reused_BUS_plug_restraint=True,roles=roles,
         materials_count=len(materials),pairs=pairs,hits=hits,errors=errors,
         source_sha256=pins,files={geom.relative_to(ROOT).as_posix():sha(geom)},
         started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
         selected=False,native_complete=False,shared_mount_removal_open=True,W1_complete=False,W5_complete=False,physical_pass=False))
    print('REMOTE_END_LAYOUT',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
