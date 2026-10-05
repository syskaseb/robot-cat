"""One joint central retention layout, keeping all received wire datums.

Native integration follows actual-material preflight. Bands are nominal
T18I envelopes; tightening/pull-out and lever fit remain physical tests.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_harness_passages_native as N
import w5_received_central_scope as received
from servo_fuse_inputs_r1 import save, sha

OUT = N.BASE / 'w5-central-retention-layout-r2'
TIE = N.ROOT / 'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'


def layout():
    # Straps cross the two bodies, not the crowded five outlet mouths.
    # One strap plane lies between G1 ports; G2 is well inside the west edge.
    return dict(body_bands=[
        dict(name='G1', x=68.25, y0=-5.5, y1=16.5, top=120, bottom=103.8),
        dict(name='G2', x=105, y0=-9.5, y1=20.5, top=118, bottom=103.8)],
        stops=[
            ('G1WestStop', [51.5,-3,108.8,53.1,3,112]),
            ('G1EastStop', [90.9,-3,108.8,92.9,3,112]),
            ('G1SouthStop', [55,-7.5,108.8,59,-5.9,112]),
            ('G2WestStop', [93.1,-3,108.8,95.1,3,112]),
            ('G2SouthStop', [97,-11.5,108.8,100,-9.9,112]),
            ('G2NorthStop', [97,20.9,108.8,100,22.5,112])],
        new_body_ties=2, new_screws=0, new_separate_prints=0,
        bearing_plane_mm=109, selected=False)


def geometry(A, Part, spec):
    def box(b):
        return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    bands = {}; slots = {}
    for b in spec['body_bands']:
        name=b['name']; x=b['x']; y0=b['y0']; y1=b['y1']; lo=b['bottom']; hi=b['top']
        bands[name+'South'] = box([x-1.25,y0-1.2,lo,x+1.25,y0,hi+1.2])
        bands[name+'North'] = box([x-1.25,y1,lo,x+1.25,y1+1.2,hi+1.2])
        bands[name+'Top'] = box([x-1.25,y0,hi,x+1.25,y1,hi+1.2])
        bands[name+'Bottom'] = box([x-1.25,y0,lo,x+1.25,y1,lo+1.2])
        cy=(y0+y1)/2
        bands[name+'Head'] = box([x-2.25,cy-2.4,lo-3.5,x+2.25,cy+2.4,lo])
        for suffix,y in [('South',y0-1.2),('North',y1)]:
            slots[name+suffix] = [x-1.55,y-.3,100,x+1.55,y+1.5,123]
    return bands, {n:box(v) for n,v in spec['stops']}, slots


def endpoint_geometry(A,Part,family):
    from w5_ground_entries_r1 import profile
    bands={}; seats={}; slots={}; recipes=[]
    # G2's6mm pitch is less than two thick-wire strap envelopes. Alternate
    # stations on each received6mm straight; do not move its outlet ports.
    offsets={'W060':2,'W025':4.5,'W061_A':2,'W036':4.5,'W001':2,
             'XA05':2,'W003':4.5,'W061_B':2,'W063':4.5,'W062':2}
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    for key,offset in offsets.items():
        wire=key.split('_')[0]
        edge=(family['whole_W001']['recipe']['edges'][0] if key=='W001'
              else family['ends'][key]['edges'][0])
        start=edge['start']; end=edge['end']; axis=[round((b-a)/6,9) for a,b in zip(start,end)]
        assert edge['kind']=='line' and abs(sum((b-a)**2 for a,b in zip(start,end))-36)<1e-6,key
        assert axis in ([0,1,0],[1,0,0]),(key,axis)
        diameter=3.4 if wire=='W001' else profile(wire)['OD_mm']
        radius=diameter/2; angle=0 if axis==[0,1,0] else -90
        transform=A.Placement(A.Vector(start[0],start[1],0),A.Rotation(A.Vector(0,0,1),angle))
        def box(b):
            s=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
            s.Placement=transform.multiply(s.Placement);return s
        z=start[2]; low=103.8; across=radius+.4
        raw=[-radius-1.2,offset-1.4,108.8,radius+1.2,offset+1.4,z]
        seat=box(raw)
        bore=Part.makeCylinder(radius+.2,2.8,A.Vector(0,offset-1.4,z),A.Vector(0,1,0))
        bore.Placement=transform.multiply(bore.Placement)
        seats[key+'InsulationSeat']=seat.cut(bore)
        local_bands=[('Left',[-across-1.2,offset-1.25,low,-across,offset+1.25,z+radius+1.2]),
                     ('Right',[across,offset-1.25,low,across+1.2,offset+1.25,z+radius+1.2]),
                     ('Top',[-across,offset-1.25,z+radius,across,offset+1.25,z+radius+1.2]),
                     ('Bottom',[-across,offset-1.25,low,across,offset+1.25,low+1.2]),
                     ('Head',[-2.4,offset-2.25,low-3.5,2.4,offset+2.25,low])]
        for suffix,b in local_bands:bands[key+suffix]=box(b)
        for suffix,x in [('Left',-across-1.2),('Right',across)]:
            b=[x-.3,offset-1.55,100,x+1.5,offset+1.55,123]
            slots[key+suffix]=bounds(box(b))
        recipes.append(dict(key=key,wire=wire,point_mm=start,angle_deg=angle,
                            straight_mm=6,station_mm=offset,band_width_mm=2.5,
                            OD_mm=diameter,raw_seat_local_mm=raw,groove_allowance_mm=.2,
                            nominal_tie_loop_mm=2*(2*across+z+radius-low)+4*1.2))
    return bands,seats,slots,recipes


def main():
    import FreeCAD as A, Part
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc); assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    spec=layout(); tie=json.loads(TIE.read_text(encoding='utf-8'))
    assert (tie['band_width_mm'],tie['band_thickness_mm']) == (2.5,1.2)
    fixed,printed,ends,family,rows,pins,reused,replaced=received.load(A,Part)
    central=json.loads(N.CENTRAL.read_text(encoding='utf-8'))
    for wire,row in central['routes'].items():
        p=N.ROOT/row['geometry']; fixed[wire]=Part.read(str(p)); pins.append(p)
    # Endpoint fragments are superseded by the nine complete bodies above.
    for owner in ('SourceDeck','SourceCarrier','SourceCover','SourceEastHood','SourceWestHood'):
        p=N.CAD/(owner+'_CANDIDATE_WORLD.brep'); printed[owner]=Part.read(str(p)); pins.append(p)
    # Portal/splice shapes are integral Deck subfeatures, not extra prints.
    for label in N.OWNER_ALIASES:
        printed.pop(label,None)
    bands,stops,slots=geometry(A,Part,spec)
    end_bands,end_seats,end_slots,end_recipes=endpoint_geometry(A,Part,family)
    bands.update(end_bands);stops.update(end_seats);slots.update(end_slots)
    assert not (set(bands)&set(stops)), 'Physical roles must not overwrite each other'
    assert (len(bands),len(stops),len(slots))==(60,16,24)
    tool=Part.makeCompound([Part.makeBox(v[3]-v[0],v[4]-v[1],v[5]-v[2],A.Vector(*v[:3])) for v in slots.values()])
    hits=[];errors=[];joins={};pairs=0
    def check(label,s,owner,t):
        nonlocal pairs
        if not s.Solids or not t.Solids:return
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                if separated(a,b):continue
                try:
                    common=a.common(b)
                    if common.Volume>1e-6:
                        bb=common.BoundBox
                        hits.append(dict(part=label,owner=owner,mm3=common.Volume,
                            bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as e:errors.append(dict(part=label,owner=owner,error=str(e)))
    for label,s in {**bands,**stops}.items():
        for owner,t in fixed.items():check(label,s,owner,t)
        for owner,t in printed.items():
            if owner=='SourceDeck':
                if label in stops:
                    joins[label]=s.common(t).Volume
                # Actual through slots, not an exemption for strap material.
                # Inspect the proposed post-slot Deck at each strap separately.
                if label in bands:
                    check(label,s.cut(tool),'DeckOutsideNativeTieSlots',t)
            else:check(label,s,owner,t)
        s.exportBrep(str(OUT/(label+'_WORLD.brep')))
        print('CENTRAL_RETENTION',label,len(hits),len(errors),flush=True)
        save(OUT/'progress.json',dict(last_part=label,hits=hits,errors=errors,joins=joins,pairs=pairs,
             started_utc=begin.isoformat(),updated_utc=datetime.now(timezone.utc).isoformat()))
    for label,s in bands.items():
        for owner,t in stops.items():check(label,s,owner,t)
    labels=list(bands)
    for i,label in enumerate(labels):
        for other in labels[:i]:
            # Pieces of a single ideal bent strap meet intentionally. Check
            # distinct ties only, including both body-retention ties.
            suffixes=('South','North','Top','Bottom','Head','Left','Right')
            group=lambda name:next(name[:-len(t)] for t in suffixes if name.endswith(t))
            if group(label)!=group(other):check(label,bands[label],other,bands[other])
    # Pure passage cuts cannot introduce contacts absent from the received
    # full37-wire map. Recheck its actual42 pairs, coalescing Deck subfeatures.
    before=len(hits)
    plan=json.loads(N.PLAN.read_text(encoding='utf-8'))
    material_pairs={(r['wire'],N.root_owner(r['owner'])) for r in plan['actual_contacts']}
    for wire,owner in sorted(material_pairs):
        check('ReceivedRoute/'+wire,fixed[wire],owner,printed[owner])
        print('RECEIVED_PASSAGE_CONTACT',wire,owner,len(hits)-before,flush=True)
    passage_hits=hits[before:]
    loops={b['name']:2*(b['y1']-b['y0']+b['top']-b['bottom'])+4*1.2 for b in spec['body_bands']}
    assert all(v+tie['head_length_mm']+20<tie['length_mm'] for v in loops.values())
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(received.__file__),TIE,N.CENTRAL,N.PLAN,N.OUT/'checks.json']
    save(OUT/'checks.json',dict(status='CENTRAL_RETENTION_LAYOUT_REJECTED' if hits or errors or any(v<=0 for v in joins.values()) else 'CENTRAL_RETENTION_LAYOUT_STATIC_CLEAR_NATIVE_PENDING',
        specification=spec,slots_mm=slots,strap_loop_allowance_mm=loops,
        endpoint_recipes=end_recipes,new_insulation_ties=10,
        minimum_pull_tail_allowance_mm=20,stop_bearing_join_mm3=joins,
        hits=hits,errors=errors,pairs=pairs,parameter_and_native_pending=True,
        received_passage_pairs=len(material_pairs),received_passage_hits=passage_hits,
        inherited_noncontact_basis='Unchanged paths/owners; passage-only Part::Cut removes material, no added supports in this receipt.',
        all_endpoint_restraints_pending=True,lever_access_requires_cut_body_ties=True,
        assembly=['Fit blocks on bearing floor109 against native stops.',
                  'Connect and operate lever cages before closing the two body ties.',
                  'Separate insulation restraints are required; body ties do not qualify strain relief.',
                  'Cut and replace body ties to remove blocks or inspect covered lever regions.'],
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(N.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(N.ROOT).as_posix():sha(p) for p in OUT.glob('*.brep')}))


if __name__=='__main__':main()
