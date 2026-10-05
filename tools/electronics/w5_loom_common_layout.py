"""One four-frame proposal with explicit integral Deck bearing additions.

Do not search more holes in the rejected narrow front strips. Introduce four
flat integral landings, preserve all routes, and receive actual joins and ALL
changed material contacts before native construction. This is not a selection.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_received_central_scope as S
import w5_harness_passages_native as N
from w5_loom_attachment_plan import DECK,CORRIDORS
from servo_fuse_inputs_r1 import save,sha

ROOT=N.ROOT;BASE=N.BASE;OUT=BASE/'w5-loom-common-layout-r1'
SIDE=BASE/'w5-side-retention-native-r1/checks.json'
BEARING=BASE/'w5-loom-bearing-regions-r1/plan.json'


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    assert not read(BEARING)['whole_front_bearing_supported']
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,printed,_,_,_,pins,_,_=S.load(A,Part)
    central=read(N.CENTRAL)
    for wire,row in central['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    # Replace only superseded printed owners by their received native parts.
    for owner in ('SourceWestHood','SourceEastHood','SourceBankLeft'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep')
        if p.exists():printed[owner]=Part.read(str(p));pins.append(p)
    for owner in ('SourceCarrier','SourceCover'):
        p=ROOT/'hardware/cad/studies/w5-side-retention-native-r1'/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner]=Part.read(str(p));pins.append(p)
    deck=Part.read(str(DECK));printed['SourceDeck']=deck;pins.append(DECK)
    for alias in N.OWNER_ALIASES:printed.pop(alias,None)
    for receipt_name in ('w5-central-retention-layout-r4','w5-side-retention-received-r2'):
        p=BASE/receipt_name/'checks.json';r=read(p);pins.append(p)
        for label,rel in r.get('world_geometries',{}).items():
            q=ROOT/rel;fixed['Retained/'+label]=Part.read(str(q));pins.append(q)
    rows=read(CORRIDORS)['routes'];pins.extend([Path(__file__),CORRIDORS,BEARING,SIDE,N.CENTRAL])
    proposals={};blueprints={};joins={};holes=[];grips=[]
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    for leg in ('FL','FR','RL','RR'):
        side=1 if leg.endswith('L') else -1
        rx=-85 if leg.startswith('F') else 123;ry=side*85
        landing=[rx-13,ry-9,105,rx+13,ry+9,113]
        pad=box(landing);proposals[leg+'DeckLanding']=pad
        joins[leg]=pad.common(deck).Volume
        assert joins[leg]>1,('No actual material union',leg,joins[leg])
        raw={'Foot':[rx-13,ry-9,113,rx+13,ry+9,119]}
        post_x=rx-9 if leg.startswith('F') else rx+9
        raw['Post']=[post_x-4,ry-4,77,post_x+4,ry+4,119]
        selected=[r for r in rows if r['loom'].startswith(leg)]
        xext=min(r['fixed_breakout_provisional_mm'][0] for r in selected) if leg.startswith('F') else max(r['fixed_breakout_provisional_mm'][0] for r in selected)
        # One root-to-outer-X trunk and one outer-Y rail. Short individual
        # branches reach each received split without moving a single cable.
        outer_y=side*max(abs(r['fixed_breakout_provisional_mm'][1]) for r in selected)
        raw['XTrunk']=[min(post_x,xext)-4,ry-4,77,max(post_x,xext)+4,ry+4,83]
        raw['YRail']=[xext-4,min(ry,outer_y)-4,77,xext+4,max(ry,outer_y)+4,83]
        solids=[box(v) for v in raw.values()];cutters=[];grooves=[]
        for r in selected:
            x,y,z=r['fixed_breakout_provisional_mm'];key=r['loom']
            b=[min(xext,x)-4,y-4,77,max(xext,x)+4,y+4,83]
            raw[key+'Branch']=b;solids.append(box(b))
            seat=Part.makeCylinder(5.5,16,A.Vector(x,y,77))
            groove=Part.makeCylinder(3.05,18,A.Vector(x,y,76))
            # Open saddle: lay the cable in from the inner-X side, then wrap
            # a nominal tie. No threading a factory plug through a closed eye.
            opening=[x-6,y-3.05,83,x,y+3.05,94] if leg.startswith('F') else [x,y-3.05,83,x+6,y+3.05,94]
            cutters.extend([groove,box(opening)]);solids.append(seat)
            grooves.append(dict(name=key,origin_mm=[x,y,77],outer_radius_mm=5.5,inner_radius_mm=3.05,height_mm=16,opening_box_mm=opening))
            grips.append(dict(loom=key,owner=leg+'FixedFrame',axis_mm=[x,y,z],nominal_bundle_OD_mm=5.5,insulation_only=True,
                              tie_required=True,tie_slot_and_pullout_qualification_pending=True))
        for dx in (-5,5):
            x=rx+dx
            cutters.append(Part.makeCylinder(1.7,16,A.Vector(x,ry,104)))
            holes.append(dict(leg=leg,axis_mm=[x,ry],deck_landing_z_mm=[105,113],foot_z_mm=[113,119],
                M3_clearance_mm=3.4,fastener_length_and_nut_access_pending=True))
        fused=solids[0].multiFuse(solids[1:]);frame=fused.cut(Part.makeCompound(cutters))
        assert frame.isValid() and len(frame.Solids)==1,(leg,len(frame.Solids))
        proposals[leg+'FixedFrame']=frame
        size=[frame.BoundBox.XLength,frame.BoundBox.YLength,frame.BoundBox.ZLength]
        assert all(v+6<=256 for v in size)
        blueprints[leg]=dict(root_xy_mm=[rx,ry],landing_box_mm=landing,raw_boxes=raw,grooves=grooves,
                            candidate_dimensions_mm=size,solid_count=len(frame.Solids),fits256_with6mm_allowance=True)
    names=list(proposals);p=OUT/'FOUR_FRAMES_AND_LANDINGS_PROPOSED_WORLD.brep'
    Part.makeCompound([proposals[n] for n in names]).exportBrep(str(p))
    save(OUT/'plan.json',dict(blueprints=blueprints,holes=holes,grips=grips,proposal_roles=names,
        joins_mm3=joins,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        assembly=['Integrate four bearing pads and eight clearance holes into the linked native Deck only after contact receipt.',
                  'Mount four fixed frames from above with accessible captive nuts below; exact hardware and tool envelopes remain to receive.',
                  'Lay twelve continuous looms sideways into the open saddles; no plug threading and no new electrical joints.',
                  'Receive split saddles/tie retention together with twelve moving-carrier grips and actual joint travel before selecting W1/W5.']))
    hits=[];errors=[];pairs=0
    for name,shape in proposals.items():
        for owner,other in {**fixed,**printed}.items():
            if name.endswith('DeckLanding') and owner=='SourceDeck':continue
            if not shape.BoundBox.intersect(other.BoundBox):continue
            for a in shape.Solids:
                for b in other.Solids:
                    if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                    pairs+=1
                    try:
                        common=a.common(b)
                        if common.Volume>1e-6:hits.append(dict(proposal=name,owner=owner,mm3=common.Volume,
                            bounds_mm=[getattr(common.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                    except Exception as e:errors.append(dict(proposal=name,owner=owner,error=str(e)))
        save(OUT/'progress.json',dict(last_part=name,pairs=pairs,hits=hits,errors=errors,updated_utc=datetime.now(timezone.utc).isoformat()))
        print('COMMON_LOOM_PREFLIGHT',name,'pairs',pairs,'hits',len(hits),'errors',len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FOUR_FRAME_INTEGRAL_LANDING_CONTACT_RECEIPT',hits=hits,errors=errors,pairs=pairs,
        proposal_roles=names,actual_Deck_join_mm3=joins,whole_assembly_and_motion_complete=False,
        native_complete=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in set(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in [p,OUT/'plan.json']}))


if __name__=='__main__':main()
