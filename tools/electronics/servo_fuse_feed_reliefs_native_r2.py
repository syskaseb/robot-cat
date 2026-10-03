"""Editable open-bottom cover slots for actual retained feed intersections.

Bank relief is confined to the RR WAGO body, not the24 terminal restraints.
Neither part is selected: cradles and fixed-wire conflicts remain OPEN.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, tempfile, shutil

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r2'
CAD = ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r2'


def main():
    import FreeCAD as A
    import Part, MeshPart
    started = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'
    pins = {}; result = []
    def pin(p): pins[p.relative_to(ROOT).as_posix()] = sha(p)
    def load(p): pin(p); return Part.read(str(p))
    def bounds(s): return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    folder = ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'
    q = folder/'checks.json'; pin(q); feeds = json.loads(q.read_text(encoding='utf-8'))
    assert not feeds['errors'] and not feeds['factory_failures']
    for tag, source, finalname, contacts in [
        ('Cover', 'hardware/cad/studies/servo-fuse-main-reliefs-native-r1/CoverRRMainRelief.FCStd',
         'RRMainReliefFinished', [r for r in feeds['hits'] if r['owner']=='RetainedCover']),
        ('BankRight', 'hardware/cad/studies/servo-fuse-bank-clip-access-r1/ServoFuseBank.FCStd',
         'RightClipAccessFinished', [r for r in feeds['hits'] if r['part']=='W053_221412' and r['owner']=='Bank/RightClipAccessFinished_WORLD'])]:
        path=ROOT/source;pin(path);d=A.openDocument(str(path));dest=CAD/(tag+'FeedReliefs.FCStd')
        try:
            parent=d.getObject(finalname);base=parent.Shape.copy();before=base.Volume
            p=d.addObject('App::VarSet','FeedReliefParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=1
            tools=[]; changed={}; openings=[]
            for i,row in enumerate(contacts):
                name=row['part'];tube=load(folder/(name+'_DESIGN.brep'));changed[name]=tube
                hit=base.common(tube);assert hit.Volume>1e-5
                # Conservative bound is a deliberate clearance-tool size, not
                # proof that an intersection witness is invalid.
                b=bounds(hit);zbottom=base.BoundBox.ZMin-1
                tool=d.addObject('Part::Box','OpenBottomFeedTool'+str(i))
                tool.setExpression('Length',f'{b[3]-b[0]} mm + 2*FeedReliefParameters.Allowance')
                tool.setExpression('Width',f'{b[4]-b[1]} mm + 2*FeedReliefParameters.Allowance')
                tool.setExpression('Height',f'{b[5]-zbottom} mm + FeedReliefParameters.Allowance')
                tool.setExpression('Placement.Base.x',f'{b[0]} mm - FeedReliefParameters.Allowance')
                tool.setExpression('Placement.Base.y',f'{b[1]} mm - FeedReliefParameters.Allowance')
                tool.Placement.Base.z=zbottom;tools.append(tool)
                openings.append(dict(feed=name,contact_volume_mm3=hit.Volume,contact_bounds_mm=b,open_bottom_z_mm=zbottom))
            assert tools
            union=d.addObject('Part::MultiFuse','FeedReliefTools');union.Shapes=tools;union.Refine=False
            final=d.addObject('Part::Cut','FeedReliefsFinished');final.Base=parent;final.Tool=union;final.Refine=False
            print('FEED_RELIEF_RECOMPUTE',tag,len(tools),flush=True);d.recompute()
            shape=final.Shape.copy();strict=shape.check(True)
            if len(shape.Solids)!=1 or not shape.isValid() or strict:
                shape.exportBrep(str(OUT/(tag+'_REJECTED.brep')))
                save(OUT/'fault.json',dict(tag=tag,selected=False,physical_pass=False,
                    solids=[dict(volume_mm3=s.Volume,bounds_mm=bounds(s)) for s in shape.Solids],
                    strict=str(strict),openings=openings,reason='Open-bottom slots disconnect material; preserve proof, not a native export.'))
            assert shape.isValid() and len(shape.Solids)==1 and not strict,(tag,str(strict),len(shape.Solids))
            volume=shape.Volume;assert volume<before
            for name,tube in changed.items(): assert shape.common(tube).Volume<1e-5,name
            p.Allowance=1.2;d.recompute();probe=final.Shape.Volume;assert probe<volume
            p.Allowance=1;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
            if tag=='BankRight':
                # Only the central RR WAGO clearance is changed. Protect the
                # raised fuse panel, everyclip and both12end restraint rows.
                guard=Part.makeBox(500,500,200,A.Vector(-250,-250,144.4))
                assert base.cut(final.Shape).common(guard).Volume<1e-5
                for name in ('LeftClipAccessFinished','RightClipAccessFinished'):
                    assert d.getObject(name) is not None
            shape=final.Shape.copy();parent.Visibility=False;union.Visibility=False
            for tool in tools:tool.Visibility=False
            d.saveAs(str(dest));shape.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert max(dims[0]+10,dims[1]+10)<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-feed-reliefs-') as td:
            moved=Path(td)/dest.name;shutil.copy2(dest,moved);re=A.openDocument(str(moved))
            try:re.recompute();assert abs(re.FeedReliefsFinished.Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        result.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final='FeedReliefsFinished',
            single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,
            parameter_mm=[1,1.2,1],volumes_mm3=[volume,probe,volume],removed_mm3=before-volume,
            dimensions_mm=dims,openings=openings,changed_feed_contacts=0))
        save(OUT/'progress.json',dict(parts=result,selected=False,physical_pass=False))
        print('FEED_RELIEF_SAVED',tag,flush=True)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FEED_OPENINGS_FIT_MOUNTS_SERVICE_OPEN',parts=result,
        selected=False,physical_pass=False,W5_complete=False,source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=started.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-started).total_seconds(),
        open=['Fixed-wire conflicts, native mounts/straps and full module removal remain OPEN.',
              'No new stock or one-batch selection. Cable slots are open-bottom to avoid lift trapping; unpowered assembly/physical finish phase2.']))


if __name__=='__main__':main()
