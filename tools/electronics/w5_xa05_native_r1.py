"""Editable XA05 Deck/outrigger from received R5, with one witness-led slot.

R5's only contact is its own bracket at the S-rise. Preserve the route,
blocks/P0 and all other clear pairs; remove only a 3.2mm slot from the 6.6mm
rail, leaving two continuous 1.7mm cheeks. No selected/physical readiness.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-xa05-native-r1'
FIT=ROOT/'hardware/electronics/full-cat/w5-xa05-outer-support-r5/checks.json'
SOURCE=ROOT/'hardware/cad/studies/w5-bus-native-grips-r4/BusStrapSlots.FCStd'
RISE_SLOT=[151.4,-6,112,154.6,7,125.3]


def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc)
    received=json.loads(FIT.read_text(encoding='utf-8'))
    assert not received['errors'] and len(received['hits'])==1
    assert received['hits'][0]['part']=='XA05' and received['hits'][0]['owner']=='OuterBracket'
    assert all(sha(ROOT/k)==v for k,v in {**received['source_sha256'],**received['files']}.items())
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    parent=A.openDocument(str(SOURCE));d=A.newDocument('XA05JointSupports')
    target=CAD/'XA05JointSupports.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','XA05Parameters')
    p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=1.5
    p.addProperty('App::PropertyLength','RiseSlotWidth');p.RiseSlotWidth=3.2
    link=d.addObject('App::Link','R53Deck');link.setLink(parent.BusStrapSlotsFinished)
    link.LinkPlacement=parent.BusStrapSlotsFinished.Placement
    primitives=[]
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]);primitives.append(q);return q
    def cyl(name,point,r,h,axis=(0,0,1),groove=False):
        q=d.addObject('Part::Cylinder',name);q.Radius=r;q.Height=h
        q.Placement=A.Placement(A.Vector(*point),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)))
        if groove:q.setExpression('Radius','XA05Parameters.GrooveRadius')
        primitives.append(q);return q
    def compound(name,parts):
        q=d.addObject('Part::Compound',name);q.Links=parts;return q
    def fuse(name,parts):
        q=d.addObject('Part::MultiFuse',name);q.Shapes=parts;q.Refine=False;return q
    def cut(name,base,tools):
        q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=tools;q.Refine=False;return q
    rawseat=box('InnerRawSeat',[132,-36.3,108.8,136,-29.7,121.7])
    groove=cyl('InnerInsulationGroove',[131.9,-33,121],1.5,4.2,(1,0,0),True)
    slots=[box('InnerTieSlot'+str(i),[132.4,y-.8,108.8,135.6,y+.8,123.6]) for i,y in enumerate((-37.1,-28.9))]
    slots.append(box('InnerTieTunnel',[132.4,-38.1,109.4,135.6,-27.9,110.8]))
    slottools=compound('InnerStrapTools',slots)
    seat=cut('InnerFinishedSeat',cut('InnerSeatGroove',rawseat,groove),slottools)
    joined=fuse('DeckAndInnerSeat',[link,seat])
    deckslots=cut('DeckStrapThroughSlots',joined,slottools)
    deckholes=[cyl('DeckBoltHole'+str(i),[131,y,104.9],1.7,4.2) for i,y in enumerate((44,36))]
    final=cut('XA05DeckFinished',deckslots,compound('DeckBoltTools',deckholes))
    rawbracket=fuse('OutriggerRaw',[
        box('OutriggerFoot',[126.5,32,109,135.5,48,112]),
        box('OutriggerStem',[132.5,35.6,111.8,135.5,42.6,119]),
        box('OutriggerBridge',[133,35.6,116,156.3,42.6,119.8]),
        box('OutriggerRail',[149.7,-17.5,116,156.3,42.6,119.5]),
        box('OutriggerSeat',[149.7,-17.3,119.3,156.3,-10.7,121.7])])
    outertools=[cyl('FootBoltHole'+str(i),[131,y,108.9],1.7,3.2) for i,y in enumerate((44,36))]
    outertools += [cyl('OuterInsulationGroove',[153,-17.4,121],1.5,6.8,(0,1,0),True),
        box('OuterUnderTieTunnel',[147.9,-15.6,115.9,158.1,-12.4,117.7])]
    outertools += [box('OuterTieSlot'+str(i),[x-.8,-15.6,115.9,x+.8,-12.4,123.6]) for i,x in enumerate((148.9,157.1))]
    oldbracket=cut('OutriggerBeforeRiseSlot',rawbracket,compound('OutriggerStrapBoltTools',outertools))
    rise=box('S_RiseWirePassage',RISE_SLOT)
    rise.setExpression('Length','XA05Parameters.RiseSlotWidth')
    bracket=cut('OutriggerFinished',oldbracket,rise)
    d.save();print('XA05_NATIVE_EDITABLE_SAVED',flush=True);d.recompute();d.save()
    shapes=[final.Shape.copy(),bracket.Shape.copy()]
    assert all(s.isValid() and len(s.Solids)==1 for s in shapes)
    assert all(q.Shape.isValid() and not q.Shape.check(True) for q in primitives)
    def plain_box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    olddeck=Part.read(str(FIT.parent/'DECK_CANDIDATE_WORLD.brep'))
    oldouter=Part.read(str(FIT.parent/'OUTRIGGER_WORLD.brep'))
    expected_outer=oldouter.cut(plain_box(RISE_SLOT))
    equivalence={}
    for name,s,reference in [('Deck',shapes[0],olddeck),('Outrigger',shapes[1],expected_outer)]:
        extra=s.cut(reference).Volume
        delta=abs(s.Volume-reference.Volume)
        assert extra<1e-5 and delta<max(1e-5,reference.Volume*1e-8)
        equivalence[name]=dict(extra_volume_mm3=extra,absolute_volume_difference_mm3=delta)
    print('XA05_NATIVE_RECEIVED_GEOMETRY_EQUIVALENT',flush=True)
    nominal=[s.Volume for s in shapes]
    p.GrooveRadius=1.6;d.recompute();probe=[final.Shape.Volume,bracket.Shape.Volume]
    assert all(a<b for a,b in zip(probe,nominal))
    p.GrooveRadius=1.5;d.recompute()
    assert all(q.Shape.isValid() and len(q.Shape.Solids)==1 for q in (final,bracket))
    assert all(abs(q.Shape.Volume-v)<max(1e-5,v*1e-8) for q,v in zip((final,bracket),nominal))
    d.save();shapes=[final.Shape.copy(),bracket.Shape.copy()]
    for name,s in zip(('Deck','Outrigger'),shapes):s.exportBrep(str(CAD/(name+'_WORLD.brep')))
    # R5 covered unchanged external owners. A subset cannot introduce an
    # intersection. Check final interfaces explicitly, not whole E6 again.
    subset=shapes[1].cut(oldouter).Volume;assert subset<1e-5
    children=Part.read(str(FIT.parent/'ADDITIONS_WORLD.brep')).childShapes()
    assert len(children)==10
    changed={'XA05':Part.read(str(FIT.parent/'XA05_WORLD.brep'))}
    for name,s in zip(('InnerTie','OuterTie','Bolt0','Washers0','Nut0','Bolt1','Washers1','Nut1'),children[2:]):
        changed[name]=s
    hits=[];errors=[];pairs=0
    for name,s in changed.items():
        for owner,t in zip(('NativeDeck','NativeOutrigger'),shapes):
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                common=s.common(t)
                if common.Volume>1e-5:
                    b=common.BoundBox
                    hits.append(dict(part=name,owner=owner,mm3=common.Volume,
                        bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as exc:errors.append(dict(part=name,owner=owner,error=str(exc)))
    v=shapes[0].common(shapes[1]).Volume
    if v>1e-5:hits.append(dict(part='NativeOutrigger',owner='NativeDeck',mm3=v))
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(q.is_relative_to(ROOT) for q in dependencies)
    pins=[Path(__file__),FIT,*dependencies,ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json']
    base=dict(status='XA05_NATIVE_REJECTED' if hits or errors else 'XA05_NATIVE_EXPORT_PENDING',
        hits=hits,errors=errors,changed_pairs=pairs,geometry_equivalence=equivalence,
        outer_subset_extra_mm3=subset,reused_receipt=FIT.relative_to(ROOT).as_posix(),
        reused_scope='Unchanged R5 wire/straps/hardware/Deck versus existing owners; new outrigger is a proved subset, only R5 own-wire contact superseded.',
        slot_bounds_mm=RISE_SLOT,minimum_continuous_rail_cheek_mm=1.7,
        strict_local_primitive_BOP_errors=0,full_final_strict_BOP_verified=False,
        parameter_radius_mm=[1.5,1.6,1.5],parameter_volumes=[nominal,probe,[q.Shape.Volume for q in (final,bracket)]],
        native_supports_constructed=True,single_solids=[1,1],new_ties=2,tie_SKU='111-02370 T18I-PA66-BK',
        new_M3x12=2,new_M3_nuts=2,new_M3_washers=4,new_separate_prints=1,one_replacement_Deck=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        assembly=['Battery andUSB disconnected. Mount outrigger on bare Deck with2M3x12/2nuts/4washers before Carrier.',
            'Thread both newT18I through their tunnels before seating the continuous XA05 power ground.',
            'Fit310mm trial blank at P0G2.5 andG_AUX.1; final length after dry fit, no extra splice.',
            'Release2new straps and preserved end restraints/levers before wire removal; exact end/lever sequence remains open.'],
        remaining=['Both existing endpoint restraints and WAGO lever/driver access.',
            'Single selected-package/stock reconciliation before restoring W1.',
            'Printed rail stiffness and nominal screw/tie fit require phase2 trials, not physical PASS.'],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},
        started_utc=start.isoformat())
    def receipt():
        finish=datetime.now(timezone.utc)
        base.update(files={q.relative_to(ROOT).as_posix():sha(q) for q in [*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl')]},
            finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds())
        save(OUT/'checks.json',base)
    if hits or errors:receipt();print('XA05_NATIVE_REJECTED',hits,errors,flush=True);return
    dims={}
    for name,s in zip(('Deck','Outrigger'),shapes):
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;dims[name]=[b.XLength,b.YLength,b.ZLength]
        assert b.XLength+6<=256 and b.YLength+6<=256 and b.ZLength<=256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
    for n in list(A.listDocuments()):A.closeDocument(n)
    with tempfile.TemporaryDirectory(prefix='robot-cat-xa05-native-') as td:
        tmp=Path(td)
        for q in [target,*dependencies]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)));restored.recompute()
        for name,v in zip(('XA05DeckFinished','OutriggerFinished'),nominal):
            q=restored.getObject(name)
            assert q.Shape.isValid() and len(q.Shape.Solids)==1
            assert abs(q.Shape.Volume-v)<max(1e-5,v*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    base.update(status='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED',closed_STLs=True,relocated_reopen=True,dimensions_mm=dims)
    receipt();print('XA05_NATIVE_EXPORTED',dims,flush=True)


if __name__=='__main__':main()
