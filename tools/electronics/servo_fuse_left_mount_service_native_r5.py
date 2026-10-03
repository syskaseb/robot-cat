"""Linked native left bank/Deck hole pair by drilling native substrate before retained fixture union for clear changed-foot R2.

Shared hole clearance, retained post and remaining three mount axes;
same M2x12/nut/TWOwashers per bolt. No fixed cage/roof or wire relocation.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,tempfile,shutil,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-service-native-r5'
CAD=ROOT/'hardware/cad/studies/servo-fuse-left-mount-service-native-r5'

def main():
    import FreeCAD as A
    import Part,MeshPart
    t=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();pins={}
    def read(rel):pins[rel]=sha(ROOT/rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    fit=read('hardware/electronics/full-cat/servo-fuse-left-mount-service-r2/checks.json')
    assert fit['status']=='LEFT_MOUNT_SERVICE_PREFLIGHT_CLEAR' and not fit['hits'] and not fit['errors']
    assert fit['washer_bearing_missing_mm3']<1e-5 and fit['state']['solids']==1
    for rel,h in fit['source_sha256'].items():assert sha(ROOT/rel)==h,rel;pins[rel]=h
    bankreceipt=read('hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r3/checks.json')
    deckreceipt=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json')
    sources={tag:next(q for q in receipt['exports'] if q['tag']==tag) for tag,receipt in [('BankLeft',bankreceipt),('Deck',deckreceipt)]}
    docs={tag:A.openDocument(str(ROOT/r['file'])) for tag,r in sources.items()}
    external=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    for source_doc in reversed(list(A.listDocuments().values())):
        print('LEFT_SOURCE_RECOMPUTE',source_doc.Name,sum('Touched' in obj.State for obj in source_doc.Objects),flush=True)
        source_doc.recompute()
    d=A.newDocument('LeftBankServiceMount');dest=CAD/'LeftBankServiceMount.FCStd';d.saveAs(str(dest))
    p=d.addObject('App::VarSet','LeftMountParameters');p.addProperty('App::PropertyLength','HoleDiameter');p.HoleDiameter=2.4
    def link(n,target):q=d.addObject('App::Link',n);q.setLink(target);q.LinkPlacement=target.Placement;return q
    def box(n,b):q=d.addObject('Part::Box',n);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];q.Placement.Base=A.Vector(*b[:3]);return q
    def cut(n,base,tool):q=d.addObject('Part::Cut',n);q.Base=base;q.Tool=tool;q.Refine=False;return q
    def union(n,items):q=d.addObject('Part::MultiFuse',n);q.Shapes=items;q.Refine=False;return q
    parents={tag:link(tag+'Previous',docs[tag].getObject(r['final'])) for tag,r in sources.items()}
    deckparts=docs['Deck'].getObject(sources['Deck']['final']).Shapes
    assert len(deckparts)==2
    substrate=link('DeckSubstrate',deckparts[0]);fixture=link('FixedGuardFixture',deckparts[1])
    d.recompute(None,True,True)
    hole=d.addObject('Part::Cylinder','SharedLeftM2Passage');hole.Height=8.3;hole.Placement.Base=A.Vector(*fit['new_axis_mm'],104.9)
    hole.setExpression('Radius','LeftMountParameters.HoleDiameter / 2')
    rest=cut('BankLeftWithoutOldFoot',parents['BankLeft'],box('OldFootRemoval',fit['old_foot_removal_mm']))
    foot=cut('LeftFootFinished',box('LeftFootStock',fit['new_foot_mm']),hole)
    bank=cut('BankLeftServiceMountFinished',union('BankLeftJoinedStock',[rest,foot]),hole)
    drill=d.addObject('Part::Cylinder','DeckLeftM2Passage');drill.Height=8.3;drill.Placement.Base=A.Vector(*fit['new_axis_mm'],104.9)
    drill.setExpression('Radius','LeftMountParameters.HoleDiameter / 2')
    deckbase=cut('DeckDrilledSubstrate',substrate,drill)
    deck=union('DeckLeftServiceMountFinished',[deckbase,fixture]);exports=[]
    try:
        print('LEFT_MOUNT_NATIVE_RECOMPUTE',os.getpid(),flush=True);d.recompute(None,True,True)
        for q in [substrate,fixture,drill,deckbase,deck]:
            print('LEFT_CUT_STATE',q.Name,q.State,q.Shape.isNull(),q.getStatusString() if hasattr(q,'getStatusString') else '',flush=True)
        assert not deck.Shape.isNull(), 'Native substrate cut/retained fixture union failed'
        diag=Part.read(str(ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-deck-cut-diagnosis-r1/Deck_drill_8.3.brep'))
        assert deck.Shape.cut(diag).Volume+diag.cut(deck.Shape).Volume<1e-5
        targetpath=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-service-r2/BankLeft_CANDIDATE.brep';pins[targetpath.relative_to(ROOT).as_posix()]=sha(targetpath)
        target=Part.read(str(targetpath));assert bank.Shape.cut(target).Volume+target.cut(bank.Shape).Volume<1e-5
        nominal=[bank.Shape.Volume,deck.Shape.Volume];p.HoleDiameter=2.6;d.recompute(None,True,True);probe=[bank.Shape.Volume,deck.Shape.Volume]
        assert all(b<a for a,b in zip(nominal,probe));p.HoleDiameter=2.4;d.recompute(None,True,True)
        assert all(abs(a-b)<1e-5 for a,b in zip(nominal,[bank.Shape.Volume,deck.Shape.Volume]))
        for tag,q in [('BankLeft',bank),('Deck',deck)]:
            print('LEFT_MOUNT_NATIVE_EXPORT',tag,flush=True);s=q.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            if tag=='BankLeft':mesh.rotate(math.pi,0,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];brim=6 if tag=='Deck' else 10
            assert dims[0]+brim<=256 and dims[1]+brim<=256 and dims[2]<=256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=q.Name,single_solid=True,strict_BOP_errors=0,closed_STL=True,
                dimensions_mm=dims,total_brim_allowance_mm=brim,volume_mm3=s.Volume,
                shared_parameter_mm=[2.4,2.6,2.4],bank_deck_nominal_probe_volumes_mm3=[nominal,probe,nominal]))
        for q in d.Objects:
            if hasattr(q,'Visibility'):q.Visibility=False
        bank.Visibility=True;deck.Visibility=True;d.save()
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-left-mount-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            to=tmp/fp.relative_to(ROOT);to.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,to)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            for source_doc in reversed(list(A.listDocuments().values())):
                if source_doc!=re:source_doc.recompute()
            re.recompute(None,True,True)
            for r in exports:
                s=re.getObject(r['final']).Shape;assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-r['volume_mm3'])<1e-5;r['relocated_reopen']=True
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_LEFT_MOUNT_PAIR_COMPLETE_WHOLE_MODULE_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,exports=exports,
        changed_axis_mm=fit['new_axis_mm'],unchanged_axes_mm=[[128,-92.5],[128,92.5],[-60,-108.5]],bank_mounts=4,
        washer_bearing_missing_mm3=0,protruding_thread_mm=fit['protruding_thread_mm'],four_mount_hardware=dict(M2x12=4,M2nuts=4,OD5washers=8),
        continuous_changed_foot_mm=100,whole_module_service_complete=False,unchanged_wire_routes=True,unchanged_fixed_cage_roofs=True,
        added_prints=0,added_fasteners=0,source_sha256=pins,script_sha256=sha(Path(__file__)),external_documents=[p.relative_to(ROOT).as_posix() for p in external],
        started_utc=t.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-t).total_seconds()))
    print('LEFT_MOUNT_NATIVE_COMPLETE',len(exports),flush=True)
if __name__=='__main__':main()
