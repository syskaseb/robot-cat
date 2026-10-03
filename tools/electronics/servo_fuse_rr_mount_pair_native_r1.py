"""Editable linked four-mount BankRight/Deck pair from the clear R2 design.

One shared foot width drives the new foot and its matching Deck pad; all
upstream native documents remain unmodified. No opaque scripted final solid.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-mount-pair-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rr-mount-pair-native-r1'


def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p)
        return json.loads(p.read_text(encoding='utf-8'))
    def load(rel):
        p=ROOT/rel;pins[rel]=sha(p);return Part.read(str(p))
    fit=read('hardware/electronics/full-cat/servo-fuse-rr-mount-pair-r2/checks.json')
    assert not fit['contacts'] and not fit['errors'] and fit['bank_mounts']==4
    assert fit['washer_bearing_missing_mm3']<1e-5 and all(v>0 for v in fit['full_fork_embeds_mm3'])
    fixed=read('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1/checks.json')
    deckpath=ROOT/fixed['exports'][0]['file']
    bankpath=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd'
    external=[deckpath,bankpath]+[ROOT/p for p in fixed['exports'][0]['external_documents']]
    external=list(dict.fromkeys(external))
    for p in external:pins[p.relative_to(ROOT).as_posix()]=sha(p)
    targetbank=load('hardware/electronics/full-cat/servo-fuse-rr-mount-pair-r2/BankRight_CANDIDATE.brep')
    targetledge=load('hardware/electronics/full-cat/servo-fuse-rr-mount-pair-r2/DeckLedge_CANDIDATE.brep')
    dd=A.openDocument(str(deckpath));bd=A.openDocument(str(bankpath))
    d=A.newDocument('BankDeckMountPair');dest=CAD/'BankDeckMountPair.FCStd'
    try:
        d.saveAs(str(dest)) # External links require an already saved owner.
        p=d.addObject('App::VarSet','SharedMountParameters')
        for name,value in [('FootWidth',12),('MountY',-108.5)]:
            p.addProperty('App::PropertyDistance',name);setattr(p,name,value)
        def link(name,target):
            q=d.addObject('App::Link',name);q.setLink(target);return q
        parent=link('OldDeckReference',dd.FixedRROutputFinished)
        bank=link('OldBankReference',bd.RearOutputPassagesFinished)
        oldfoot=link('OldFootReference',bd.RightFoot57)
        oldpost=link('OldPostReference',bd.RightPost57)
        movedpost=link('FourthPostMoved',bd.RightPost57)
        movedpost.LinkPlacement=A.Placement(A.Vector(3,-16,0),A.Rotation())
        movedpost.setExpression('LinkPlacement.Base.y','SharedMountParameters.MountY + 92.5 mm')
        def primitive(name,b):
            q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
            q.Placement.Base=A.Vector(*b[:3]);return q
        foot=primitive('FourthFoot',[-63,-113,109,-51,-105,113])
        foot.setExpression('Length','SharedMountParameters.FootWidth')
        foot.setExpression('Placement.Base.y','SharedMountParameters.MountY - 4.5 mm')
        pad=primitive('MatchingDeckPad',fit['fork_boxes_mm'][0])
        pad.setExpression('Length','SharedMountParameters.FootWidth + 1 mm')
        pad.setExpression('Placement.Base.y','SharedMountParameters.MountY - 5.5 mm')
        arms=[primitive('DeckForkArm'+str(i),b) for i,b in enumerate(fit['fork_boxes_mm'][1:])]
        for q in arms:q.setExpression('Placement.Base.y','SharedMountParameters.MountY + 2.5 mm')
        hole=d.addObject('Part::Cylinder','SharedBoltPassage');hole.Radius=1.2;hole.Height=8.2
        hole.Placement.Base=A.Vector(-60,-108.5,104.9)
        hole.setExpression('Placement.Base.y','SharedMountParameters.MountY')
        def union(name,parts):
            q=d.addObject('Part::MultiFuse',name);q.Shapes=parts;q.Refine=False;return q
        def cut(name,base,tool):
            q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=tool;q.Refine=False;return q
        oldmount=union('OriginalFourthMount',[oldfoot,oldpost])
        remainder=cut('RetainedBankWithoutOldFourthMount',bank,oldmount)
        rawshoulder=union('DeckForkStock',[pad]+arms)
        shoulder=cut('DeckShoulderFinished',rawshoulder,hole)
        footdone=cut('FourthFootFinished',foot,hole)
        d.recompute()
        base=(footdone.Shape.Volume,shoulder.Shape.Volume)
        p.FootWidth=12.2;d.recompute();probe=(footdone.Shape.Volume,shoulder.Shape.Volume)
        assert all(b>a for a,b in zip(base,probe)),(base,probe)
        p.FootWidth=12;d.recompute();restored=(footdone.Shape.Volume,shoulder.Shape.Volume)
        assert all(abs(a-b)<1e-6 for a,b in zip(base,restored))
        assert abs(movedpost.Shape.BoundBox.YMin+113)<1e-6
        delta=shoulder.Shape.cut(targetledge).Volume+targetledge.cut(shoulder.Shape).Volume
        assert delta<1e-5,('Deck local/native mismatch',delta)
        bankfinal=union('FourMountBankRightFinished',[remainder,footdone,movedpost]);d.recompute()
        bs=bankfinal.Shape.copy();assert bs.isValid() and len(bs.Solids)==1 and not bs.check(True)
        bankdelta=bs.cut(targetbank).Volume+targetbank.cut(bs).Volume
        assert bankdelta<1e-5,('Bank preflight/native mismatch',bankdelta)
        local=dict(parameter_mm=[12,12.2,12],foot_shoulder_volumes_mm3=[base,probe,restored],
            exact_bank_symmetric_difference_mm3=bankdelta,exact_shoulder_symmetric_difference_mm3=delta)
        save(OUT/'local-preflight.json',dict(local,selected=False,physical_pass=False))
        d.saveAs(str(dest));print('MOUNT_PAIR_NATIVE_LOCAL_COMPLETE',flush=True)
        deckfinal=union('FourMountDeckFinished',[parent,shoulder])
        print('MOUNT_PAIR_NATIVE_DECK_UNION',flush=True);d.recompute()
        ds=deckfinal.Shape.copy();print('MOUNT_PAIR_NATIVE_DECK_BOP',flush=True)
        assert ds.isValid() and len(ds.Solids)==1 and not ds.check(True)
        d.saveAs(str(dest));exports=[]
        for tag,obj,s in [('BankRight',bankfinal,bs),('Deck',deckfinal,ds)]:
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            if tag=='BankRight':mesh.rotate(math.pi,0,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=obj.Name,single_solid=True,
                strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=s.Volume,
                print_orientation='Top bank panel on bed/posts upwards' if tag=='BankRight' else 'Existing Deck flat base down',
                local_shared_parameter=local))
        print('MOUNT_PAIR_NATIVE_EXPORTS_COMPLETE',flush=True)
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-mount-pair-relocate-') as td:
        temp=Path(td)
        for fp in [dest]+external:
            target=temp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        r=A.openDocument(str(temp/dest.relative_to(ROOT)))
        try:
            r.recompute()
            for row in exports:
                s=r.getObject(row['final']).Shape
                assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume_mm3'])<1e-5
                row['relocated_reopen']=True
            for name in ('OldDeckReference','OldBankReference','OldFootReference','OldPostReference','FourthPostMoved'):
                q=r.getObject(name);assert q.LinkedObject is not None
                assert Path(q.LinkedObject.Document.FileName).is_relative_to(temp),q.LinkedObject.Document.FileName
            # Also ensure the retained linked Deck resolves its own source pair locally.
            q=r.OldDeckReference.LinkedObject.Document
            for name in ('CurrentDeckParent','RemovableBankReference'):
                assert Path(q.getObject(name).LinkedObject.Document.FileName).is_relative_to(temp)
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FOUR_MOUNT_PAIR_COMPLETE_SHARED_BANK_WITHDRAWAL_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,bank_mounts=4,
        changed_bolt_axis_mm=fit['changed_axis_mm'],protruding_thread_mm=fit['protruding_thread_mm'],
        worksheet='Same fourM2x12/fourM2nuts/eightOD5washers; zero added printed part or fastener.',
        changed_mount_pairs=fit['pairs'],changed_mount_contacts=0,changed_mount_continuous_withdrawal_mm=100,
        entire_module_withdrawal_qualified=False,
        external_documents=[fp.relative_to(ROOT).as_posix() for fp in external],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('MOUNT_PAIR_NATIVE_COMPLETE',json.dumps(dict(exports=2,bank_mounts=4,selected=False)),flush=True)


if __name__=='__main__':main()
