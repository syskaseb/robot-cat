"""Editable three-part source-grip owner transfer from accepted R3 preflight.

Deck owns two linked existing source saddles, native risers and bridges.
Bank and Cover get matched native open-edge/open-bottom passages. Shared
clearance roundtrip is exercised on the small fixture and mating cuts before
the expensive complete Deck union. No opaque final Part::Feature solids.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,shutil,tempfile,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    print('FR_FIXED_NATIVE_START',os.getpid(),start.isoformat(),flush=True)
    pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    fit=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r3/checks.json')
    assert not fit['hits'] and not fit['errors'] and all(r['full'] for r in fit['embeds'])
    prior=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    cr=next(r for r in prior['exports'] if r['tag']=='Cover')
    sources=dict(Deck=('hardware/cad/studies/servo-fuse-rr-mount-pair-native-r1/BankDeckMountPair.FCStd','FourMountDeckFinished'),
                 BankRight=('hardware/cad/studies/servo-fuse-output-rib-exits-native-r3/OutputRibDownwardExits.FCStd','BankRightOutputExitsFinished'),
                 Cover=(cr['file'],cr['final']))
    docs={tag:A.openDocument(str(ROOT/fp)) for tag,(fp,name) in sources.items()}
    datumfile=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd'
    datum=A.openDocument(str(datumfile))
    external=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    d=A.newDocument('FRSourceFixedDeck');dest=CAD/'FRSourceFixedDeck.FCStd';d.saveAs(str(dest))
    p=d.addObject('App::VarSet','FRServiceParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.25
    def link(name,target):q=d.addObject('App::Link',name);q.setLink(target);return q
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];q.Placement.Base=A.Vector(*b[:3]);return q
    def union(name,items):q=d.addObject('Part::MultiFuse',name);q.Shapes=items;q.Refine=False;return q
    def cut(name,base,tool):q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=tool;q.Refine=False;return q
    parents={tag:link(tag+'CurrentParent',docs[tag].getObject(name)) for tag,(fp,name) in sources.items()}
    stock=[box(r['name'],r['box_mm']) for r in fit['native_stocks']];tools=[]
    for role in ('Factory','Extension'):
        stock.append(link('Retained'+role+'Seat',datum.getObject('FR'+role+'Seat')))
        old=datum.getObject('FR'+role+'WireGroove')
        groove=d.addObject('Part::Cylinder',role+'UnchangedGroove');groove.Height=old.Height;groove.Placement=old.Placement
        groove.setExpression('Radius','2.75 mm + FRServiceParameters.Allowance');tools.append(groove)
        tools.append(link('Retained'+role+'TiePass',datum.getObject('FR'+role+'TiePass')))
    tools.append(box('ExtensionExistingEdgePassage',fit['pad_edge_relief_mm']))
    fixture=cut('FixedSourceFixtureFinished',union('FixedSourceStock',stock),union('FixedSourceTools',tools))
    bp=box('BankInnerSourcePassage',fit['open_inner_bank_passage_mm'])
    for prop,val in [('Length',float(bp.Length)),('Width',float(bp.Width))]:bp.setExpression(prop,f'{val-.5} mm + 2*FRServiceParameters.Allowance')
    for axis,val in [('x',bp.Placement.Base.x),('y',bp.Placement.Base.y)]:bp.setExpression('Placement.Base.'+axis,f'{val+.25} mm - FRServiceParameters.Allowance')
    bank=cut('BankRightFixedSourceFinished',parents['BankRight'],bp)
    covertools=[]
    for i,row in enumerate(fit['cover_reliefs']):
        b=row['tool_mm'];q=box('CoverOpenBottomSourcePassage'+str(i),b)
        for prop,val in [('Length',float(q.Length)),('Width',float(q.Width))]:q.setExpression(prop,f'{val-.5} mm + 2*FRServiceParameters.Allowance')
        q.setExpression('Height',f'{float(q.Height)-.25} mm + FRServiceParameters.Allowance')
        for axis,val in [('x',b[0]),('y',b[1])]:q.setExpression('Placement.Base.'+axis,f'{val+.25} mm - FRServiceParameters.Allowance')
        covertools.append(q)
    cover=cut('CoverFixedSourceFinished',parents['Cover'],union('CoverFixedSourceTools',covertools))
    exports=[];parameter=[]
    try:
        print('FR_FIXED_NATIVE_SMALL_AND_MATES',flush=True);d.recompute()
        small=[fixture,bank,cover];nominal=[q.Shape.Volume for q in small]
        counts={q.Name:dict(valid=q.Shape.isValid(),solids=len(q.Shape.Solids),volume_mm3=q.Shape.Volume,state=[str(v) for v in q.State]) for q in small}
        print('FR_FIXED_NATIVE_INITIAL_COUNTS',json.dumps(counts),flush=True)
        if len(fixture.Shape.Solids)!=2 or len(bank.Shape.Solids)!=1 or len(cover.Shape.Solids)!=1:
            d.save()
            for q in small:q.Shape.exportBrep(str(OUT/(q.Name+'_REJECTED.brep')))
            save(OUT/'initial-native-fault.json',dict(counts=counts,selected=False,physical_pass=False,
                reason='Native initial result differs from clear preflight; preserve exact objects before further repair.'))
        assert len(fixture.Shape.Solids)==2 and len(bank.Shape.Solids)==1 and len(cover.Shape.Solids)==1
        for tag,q in [('FRSourceFixture',fixture),('BankRight',bank),('Cover',cover)]:
            fp=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r3'/(tag+'_CANDIDATE.brep');pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
            s=Part.read(str(fp));delta=q.Shape.cut(s).Volume+s.cut(q.Shape).Volume
            assert delta<1e-5,(tag,delta)
        p.Allowance=.35;d.recompute();probe=[q.Shape.Volume for q in small]
        assert all(b<a for a,b in zip(nominal,probe)),(nominal,probe)
        p.Allowance=.25;d.recompute();restored=[q.Shape.Volume for q in small]
        assert all(abs(a-b)<1e-5 for a,b in zip(nominal,restored))
        parameter=dict(allowance_mm=[.25,.35,.25],small_fixture_and_mate_volumes_mm3=[nominal,probe,restored],nominal_preflight_delta_mm3=0)
        for tag,q in [('BankRight',bank),('Cover',cover)]:
            s=q.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        d.save();save(OUT/'local-preflight.json',dict(parameter=parameter,selected=False,physical_pass=False))
        print('FR_FIXED_NATIVE_DECK_UNION',flush=True)
        deck=union('DeckFixedSourceFinished',[parents['Deck'],fixture]);d.recompute()
        for tag,q in [('Deck',deck),('BankRight',bank),('Cover',cover)]:
            print('FR_FIXED_NATIVE_BOP_EXPORT',tag,flush=True)
            s=q.Shape.copy();strict=s.check(True) or []
            if not s.isValid() or len(s.Solids)!=1 or strict:
                s.exportBrep(str(OUT/(tag+'_REJECTED.brep')));save(OUT/'fault.json',dict(tag=tag,valid=s.isValid(),solids=len(s.Solids),BOP=[str(v) for v in strict]))
            assert s.isValid() and len(s.Solids)==1 and not strict
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            if tag!='Deck':mesh.rotate(math.pi,0,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=q.Name,single_solid=True,
                strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=s.Volume,shared_parameter=parameter))
            d.save();save(OUT/'progress.json',dict(exports=exports,selected=False,physical_pass=False))
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        for q in (deck,bank,cover):q.Visibility=True
        d.save()
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-fr-source-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            target=tmp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        r=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            r.recompute()
            for row in exports:
                s=r.getObject(row['final']).Shape;assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume_mm3'])<1e-5
                row['relocated_reopen']=True
            for doc in A.listDocuments().values():assert Path(doc.FileName).is_relative_to(tmp),doc.FileName
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FIXED_FR_SOURCE_THREE_PARTS_COMPLETE_WHOLE_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,bank_mounts_preserved=4,
        unchanged_source_grips_and_wires=True,source_ties_owner='FIXED_DECK',added_prints=0,added_fasteners=0,added_wires=0,added_ties=0,
        changed_pairs=fit['pairs'],contacts=0,embeds=fit['embeds'],whole_bank_removal_qualified=False,
        external_documents=[p.relative_to(ROOT).as_posix() for p in external],source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('FR_FIXED_NATIVE_COMPLETE',len(exports),flush=True)

if __name__=='__main__':main()
