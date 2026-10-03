"""One coupled owner transfer: both existing FR source grips to fixed Deck.

Keep wire routes, insulation seats/grooves/ties exactly in place. Two native
risers/bridges support them from Deck. Bank gets one open-inner-edge passage
above its retained fourth foot; no moving screw or imagined parking motion.
Preflight the entire addition against all current owners before native CAD.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    print('FR_FIXED_SOURCE_PREFLIGHT_START',os.getpid(),start.isoformat(),flush=True)
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-fr-source-fixed-deck-r1')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owners_only');exec(compile(code,str(loader),'exec'),ns)
    owners,pins,_=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def load(rel):p=ROOT/rel;pins[rel]=sha(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    deck=load('hardware/cad/studies/servo-fuse-rr-mount-pair-native-r1/Deck_WORLD.brep')
    bank=load('hardware/cad/studies/servo-fuse-output-rib-exits-native-r3/BankRight_WORLD.brep')
    owners['CandidateDeck']=deck
    owners['Bank/LeftClipAccessFinished_WORLD']=load('hardware/cad/studies/servo-fuse-output-rib-exits-native-r3/BankLeft_WORLD.brep')
    passage=[-86,-106.5,113.1,-43,-85,170]
    candidate=bank.cut(box(passage));assert candidate.isValid() and len(candidate.Solids)==1
    owners['Bank/RightClipAccessFinished_WORLD']=candidate
    source=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd'
    pins[source.relative_to(ROOT).as_posix()]=sha(source);d=A.openDocument(str(source))
    stocks=[('FactoryPad',[-50.7,-106,105,-46.5,-103,109]),
            ('FactoryRiser',[-50.5,-106,108.8,-46.5,-103,144.9]),
            ('FactoryBridge',[-50.5,-106,143.9,-46,-89,147.1]),
            ('ExtensionPad',[-83.5,-102,105,-79.5,-92,109]),
            ('ExtensionRiser',[-83.5,-102,108.8,-79.5,-99,144.9]),
            ('ExtensionBridge',[-83.5,-102,143.9,-79.5,-89,147.1])]
    parts=[box(b) for n,b in stocks];datums=[]
    try:
        for role in ('Factory','Extension'):
            seat=d.getObject('FR'+role+'Seat');groove=d.getObject('FR'+role+'WireGroove');slot=d.getObject('FR'+role+'TiePass')
            assert seat and groove and slot
            shape=seat.Shape.cut(groove.Shape.fuse(slot.Shape));parts.append(shape)
            datums.append(dict(role=role,seat=seat.Name,groove=groove.Name,slot=slot.Name,
                               seat_bounds_mm=bounds(seat.Shape),unchanged_intact_insulation_grip_mm=4))
        fixture=parts[0].multiFuse(parts[1:]);assert fixture.isValid() and len(fixture.Solids)==2 and not fixture.check(True)
    finally:A.closeDocument(d.Name)
    embeds=[]
    for name,b in [('Factory',[-50.7,-106,105,-50.5,-103,109]),('Extension',[-83.5,-95,108.8,-79.5,-92,109])]:
        p=box(b);v=p.common(deck).Volume
        embeds.append(dict(name=name,box_mm=b,expected_mm3=p.Volume,actual_mm3=v,full=abs(v-p.Volume)<1e-5))
    hits=[];errors=[];pairs=0
    for key,t in owners.items():
        if key=='CandidateDeck':continue # Exactly integral base stock, actual anchorage checked above.
        if not fixture.BoundBox.intersect(t.BoundBox):continue
        pairs+=1
        try:
            c=fixture.common(t)
            if c.Volume>1e-5:
                hits.append(dict(part='CoupledFRSourceDeckFixture',owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc:errors.append(dict(owner=key,error=str(exc)))
    for name,s in [('FRSourceFixture',fixture),('BankRight',candidate)]:s.exportBrep(str(OUT/(name+'_CANDIDATE.brep')))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or errors or not all(e['full'] for e in embeds) else 'COUPLED_FIXED_FR_SOURCE_PREFLIGHT_CLEAR_NATIVE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,embeds=embeds,
        native_stocks=[dict(name=n,box_mm=b) for n,b in stocks],retained_native_seat_datums=datums,
        open_inner_bank_passage_mm=passage,bank_mounts_preserved=4,added_prints=0,added_fasteners=0,added_wires=0,added_ties=0,
        source_ties_remain_fixed_for_bank_removal=True,whole_bank_removal_qualified=False,
        recipe='Both source grooves/slots/ties and all wires unchanged in world coordinates; Deck owns two risers and bridges. Bank inner passage above113.1mm preserves fourth foot109..113 and its post outsideY-107. Guard stays with bank.',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('FR_FIXED_SOURCE_PREFLIGHT_COMPLETE',json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors),full_feet=all(e['full'] for e in embeds))),flush=True)

if __name__=='__main__':main()
