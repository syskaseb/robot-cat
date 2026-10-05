"""Plan all eight side blocks and 35 used ends BEFORE native CAD changes.

Preserve all received paths. Four integral Carrier towers support both levels;
body ties use unused ground cages or the midpoint between DATA exits. Every
strap head, underpassage and support is part of the same proposed geometry.
This is a construction proposal, never a selected or physical fit result.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_coupled_corridors_r3 as contract
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import save, sha

ROOT = N.ROOT
OUT = N.BASE/'w5-side-retention-plan-r1'
QUALIFIED = N.BASE/'w5-harness-passages-qualified-r1/checks.json'
CENTRAL = N.BASE/'w5-central-retention-layout-r4/checks.json'
TIE = ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'


def specification():
    bodies, rows, _, pins = contract.contract()
    ends = []
    for row in rows:
        for side in ('a', 'b'):
            if side+'_datum' not in row:
                continue
            endpoint = row[side+'_end']
            block = endpoint.split('.')[0]
            if block not in bodies:
                continue
            datum = row[side+'_datum']
            ends.append(dict(wire=row['wire'], end=endpoint, block=block,
                point_mm=datum['point_mm'], axis=datum['outward_axis'],
                OD_mm=N.scope.spec(row['wire'])['OD_mm'],
                station_mm=3, straight_mm=6, groove_allowance_mm=.2,
                head_on_top=True))
    assert len(ends)==35 and len({e['end'] for e in ends})==35
    blocks=[]
    for name, bounds in bodies.items():
        attached=[e for e in ends if e['block']==name]
        cy=(bounds[1]+bounds[4])/2
        # Four ground cage5 and D_RL.5 are NC. Other DATA blocks need a gap.
        pitch=6.75 if name.startswith('D_') else 6
        possible=[cy+(i-2)*pitch for i in range(5)]
        unused=[y for y in possible if all(abs(y-e['point_mm'][1])>.01 for e in attached)]
        if not unused:
            ys=sorted(e['point_mm'][1] for e in attached)
            gaps=[(a+b)/2 for a,b in zip(ys,ys[1:])]
            station=min(gaps,key=lambda y:abs(y-cy))
        else:
            station=unused[0]
        blocks.append(dict(name=name,bounds_mm=bounds,body_tie_y_mm=station,
            floor_mm=bounds[2],body_tie_head_below=True,
            electrical_port_count=len(attached),unused_tie_lane=bool(unused)))
    towers=[]
    for leg in ('FL','FR','RL','RR'):
        front=leg.startswith('F');left=leg.endswith('L')
        # Between G and DATA footprints: exactly Y53..57 or -57..-53.
        # Carrier owns the fixed source layer; do not attach electronics to
        # a removable hood or to the bank which lifts independently.
        x=-57.5 if front else 107.5;y=55 if left else -55
        towers.append(dict(name=leg+'CarrierTower',owner='SourceCarrier',
            bounds_mm=[x-2,y-2,140,x+2,y+2,175],
            blocks=['D_'+leg,leg+'_G'],root_join_requires_actual_material=True))
    return bodies, ends, blocks, towers, pins


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'plan.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    bodies,ends,blocks,towers,pins=specification()
    pins += [Path(__file__),QUALIFIED,CENTRAL,N.CENTRAL,TIE]
    for p in (QUALIFIED,CENTRAL,N.CENTRAL):
        receipt=json.loads(p.read_text(encoding='utf-8'))
        for rel,digest in {**receipt.get('source_sha256',{}),**receipt.get('files',{})}.items():
            assert sha(ROOT/rel)==digest,rel
            pins.append(ROOT/rel)
    central=json.loads(N.CENTRAL.read_text(encoding='utf-8'))
    # Match every proposed seat to the actual received straight, not a stale
    # pre-routing datum. Wire direction in the BRep may be reversed.
    checked=[]
    for row in ends:
        p=N.centreline(row['wire'],central);pins.append(p)
        path=Part.read(str(p));origin=A.Vector(*row['point_mm'])
        axis=A.Vector(*row['axis']);end=origin+axis*6
        found=any(isinstance(e.Curve,Part.Line) and
            ((e.valueAt(e.FirstParameter)-origin).Length<1e-6 and (e.valueAt(e.LastParameter)-end).Length<1e-6 or
             (e.valueAt(e.LastParameter)-origin).Length<1e-6 and (e.valueAt(e.FirstParameter)-end).Length<1e-6)
            for e in path.Edges)
        row['received_6mm_straight_matches']=found
        checked.append(found)
    qualified=json.loads(QUALIFIED.read_text(encoding='utf-8'))
    world={}
    for owner in ('SourceCarrier','SourceDeck','SourceCover','SourceEastHood','SourceWestHood'):
        p=next(ROOT/rel for rel in qualified['files'] if rel.endswith('/'+owner+'_CANDIDATE_WORLD.brep'))
        world[owner]=Part.read(str(p));pins.append(p)
    def box(bounds):
        return Part.makeBox(*(bounds[i+3]-bounds[i] for i in range(3)),A.Vector(*bounds[:3]))
    joins={}
    for row in towers:
        # Actual Carrier material, not its bounding box. This is only root
        # feasibility; foreign owners and the whole frame remain unqualified.
        root=box([*row['bounds_mm'][:3],row['bounds_mm'][3],row['bounds_mm'][4],143])
        joins[row['name']]=root.common(world['SourceCarrier']).Volume
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='SIDE_RETENTION_CONSTRUCTION_PLAN_NOT_NATIVE',
        blocks=blocks,endpoints=ends,towers=towers,
        root_join_mm3=joins,received_straights_matched=sum(checked),
        expected_received_straights=35,all_straights_match=all(checked),
        four_root_material_joins_positive=all(v>0 for v in joins.values()),
        proposed_body_ties=8,proposed_insulation_ties=35,
        new_separate_prints=0,new_screws=0,
        no_changes_to_received_37_routes=True,no_new_splices=True,
        integral_owner='SourceCarrier',
        chosen_construction=[
            'Receive central Deck worker first; do not rebuild its accepted layout.',
            'Use four fixed Carrier towers supporting eight bodies at Z165/175.',
            'Use ground NC cage lanes / DATA inter-port lanes for body straps, never the wire mouths.',
            'Add35open insulation seats along the actual received6mm straights; include top heads, side slots and bottom tunnels BEFORE contact review.',
            'Check the ENTIRE proposed frame/bands against all37routes,12V routes,central retention and fixed owners once, with actual material witnesses.',
            'Resolve necessary Carrier/Cover/hood interfaces together; do not move frozen routes or exempt solid collisions.',
            'Integrate one editable Carrier variant only after complete preflight; verify roots/parameter/restoration/closed exports/reopen.',
            'Keep remaining central remote ends, supported flights and original moving loom ties in the same final census; no duplicate obsolete roles.',
            'Qualify assembly/teardown of fixed Carrier versus removable bank and hoods; then update one selected print and stock set.'],
        assembly=[
            'Physical battery disconnected; fit empty fixed Carrier and side blocks with hoods absent.',
            'Operate cages and fit insulation ends before closing body bands; body straps alone are not strain relief.',
            'Dress cables and close individual insulation straps, then fit source crossing leads and hoods last.',
            'For removal, remove hoods first, cut only identified replacement straps, release crossing leads and lift bank/Cover together; Carrier side blocks remain fixed.',
            'Whole access, parking and motion still require actual integrated qualification; this sequence alone is not a clearance proof.'],
        gates=['All35receivedstraightbindings','ActualCarrierrootjoins','Allforeignmaterialcontacts',
            'Allstrapheadsandslots','Nativeconnectedroots','Nohoodtrapping','Leverassemblyaccess',
            'Remainingremoteendsandflights','Existingmovingloominterfaces','Uniqueglobaltieandwirestock'],
        minimum_nominal_clearance_mm=.3,
        assumptions=['T18I supplier nominal envelope; physical tightening, creep and pullout phase2',
            'Block envelope and port datums provisional, not measured cage pitches',
            'Tower 4mm section is a prototype proposal, not a qualified strength measurement',
            'No foreign contact or service PASS is inferred from a positive root or straight match'],
        all_foreign_contacts_pending=True,native_pending=True,selected=False,
        W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)}))
    print('SIDE_RETENTION_PLAN',sum(checked),'OF35',joins,flush=True)


if __name__=='__main__':
    main()
