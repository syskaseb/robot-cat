"""Matched editable rear output passages in four retained PETG owners.

R8 routes are clear of actual wires/terminals/purchased parts; every remaining
contact is explicitly matched here. Sweep tools use the saved full centreline
and a native radius expression, not broad curved-surface bounding boxes.
Cut-only parts preserve prior obstacles by subset. No grips/removal/selection
or physical qualification is inferred from channel clearance.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-reliefs-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists() and not (OUT/'progress.json').exists(),'Preserve previous result'
    pins={};parts=[]
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8'
    q=folder/'checks.json';pin(q);routes=json.loads(q.read_text(encoding='utf-8'))
    assert not routes['errors'] and not routes['factory_failures']
    shelfkey='hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.brep'
    accepted={'CandidateDeck','ModifiableCover','Bank/RightClipAccessFinished_WORLD',shelfkey}
    assert len(routes['hits'])==9 and all(h['owner'] in accepted for h in routes['hits'])
    definitions=[
        ('Deck','hardware/cad/studies/servo-fuse-rl-source-station-native-r5/DeckRLSourceStation.FCStd',
         'RLSourceStationFinished','CandidateDeck','Deck_WORLD.brep'),
        ('Cover','hardware/cad/studies/servo-fuse-rr-source-station-native-r4/CoverRRSourceStation.FCStd',
         'RRSourceCoverFinished','ModifiableCover','Cover_WORLD.brep'),
        ('BankRight','hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/BankRightFRGuard.FCStd',
         'FRGuardBankFinished','Bank/RightClipAccessFinished_WORLD','BankRight_WORLD.brep'),
        ('Shelf','hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.FCStd',
         'FinishedMount',shelfkey,'ShelfPWMGroundTerminal.brep')]
    geometries={n:load(folder/(n+'_DESIGN.brep')) for n in {h['part'] for h in routes['hits']}}
    for tag,source,name,owner,basefile in definitions:
        p=ROOT/source;pin(p);d=A.openDocument(str(p));dest=CAD/(tag+'RearOutputPassages.FCStd')
        try:
            parent=d.getObject(name);assert parent is not None,(tag,name)
            base=parent.Shape.copy();basepath=p.parent/basefile;original=load(basepath)
            assert base.isValid() and len(base.Solids)==1 and abs(base.Volume-original.Volume)<1e-5
            par=d.addObject('App::VarSet','RearOutputPassageParameters')
            par.addProperty('App::PropertyLength','Clearance');par.Clearance=.35
            tools=[];names=sorted({h['part'] for h in routes['hits'] if h['owner']==owner})
            for ident in names:
                if ident.endswith('_extension'):
                    path=load(folder/(ident+'_CENTERLINE.brep'))
                    spine=d.addObject('Part::Feature',ident+'PinnedRoute');spine.Shape=path
                    spine.addProperty('App::PropertyString','SourcePath');spine.SourcePath=str((folder/(ident+'_CENTERLINE.brep')).relative_to(ROOT))
                    edge=path.Edges[0];point=edge.valueAt(edge.FirstParameter);tangent=edge.tangentAt(edge.FirstParameter)
                    circle=d.addObject('Part::Circle',ident+'PassageProfile')
                    circle.setExpression('Radius','2.1 mm + RearOutputPassageParameters.Clearance')
                    circle.Placement=A.Placement(point,A.Rotation(A.Vector(0,0,1),tangent))
                    sweep=d.addObject('Part::Sweep',ident+'ClearanceSweep');sweep.Sections=[circle]
                    sweep.Spine=(spine,[]);sweep.Solid=True;sweep.Frenet=False;tools.append(sweep)
                else:
                    assert ident.endswith('_221412')
                    b=geometries[ident].BoundBox
                    tool=d.addObject('Part::Box',ident+'HousingPassage')
                    for prop,val in [('Length',b.XLength),('Width',b.YLength),('Height',b.ZLength)]:
                        tool.setExpression(prop,f'{val} mm + 2*RearOutputPassageParameters.Clearance')
                    for axis,val in [('x',b.XMin),('y',b.YMin),('z',b.ZMin)]:
                        tool.setExpression('Placement.Base.'+axis,f'{val} mm - RearOutputPassageParameters.Clearance')
                    tools.append(tool)
            assert tools
            compound=d.addObject('Part::Compound','RearOutputPassageTools');compound.Links=tools
            final=d.addObject('Part::Cut','RearOutputPassagesFinished');final.Base=parent;final.Tool=compound;final.Refine=False
            d.saveAs(str(dest));print('REAR_OUTPUT_NATIVE_RECOMPUTE',tag,flush=True);d.recompute()
            shape=final.Shape.copy();strict=shape.check(True) or []
            if not shape.isValid() or len(shape.Solids)!=1 or strict:
                shape.exportBrep(str(OUT/(tag+'_REJECTED.brep')))
                save(OUT/'fault.json',dict(tag=tag,valid=shape.isValid(),solids=len(shape.Solids),strict=[str(x) for x in strict],source_sha256=pins))
            assert shape.isValid() and len(shape.Solids)==1 and not strict,(tag,str(strict),len(shape.Solids))
            volume=shape.Volume;assert volume<base.Volume
            contacts={n:shape.common(geometries[n]).Volume for n in names}
            assert all(v<1e-5 for v in contacts.values()),(tag,contacts)
            # A Cut-only native feature cannot add a new collision. Check
            # channels here; preserve all unchanged-pair proofs from R8/R17.
            par.Clearance=.45;d.recompute();probe=final.Shape.Volume;assert probe<volume
            par.Clearance=.35;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
            shape=final.Shape.copy()
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            final.Visibility=True;d.save();shape.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1,(tag,'non-manifold mesh')
            b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
            assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
            mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            row=dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=final.Name,source=source,
                source_final=name,single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,
                channel_clearance_mm=[.35,.45,.35],parameter_volumes_mm3=[volume,probe,volume],
                removed_mm3=base.Volume-volume,channel_contacts_mm3=contacts,
                native_cut_only_preserves_unchanged_collision_pairs=True,
                route_skeleton='Pinned explicit R8 BRep centreline; native Sweep radius editable. Full route changes require regenerate skeleton.',
                physical_pass=False,selected=False)
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-rear-output-') as td:
            moved=Path(td)/dest.name;shutil.copy2(dest,moved);re=A.openDocument(str(moved))
            try:
                re.recompute();s=re.getObject(row['final']).Shape
                assert s.isValid() and abs(s.Volume-volume)<1e-5
                row['relocated_reopen']=True
            finally:A.closeDocument(re.Name)
        parts.append(row);save(OUT/'progress.json',dict(parts=parts,source_sha256=pins,selected=False,physical_pass=False))
        print('REAR_OUTPUT_NATIVE_SAVED',tag,flush=True)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REAR_OUTPUT_NATIVE_PASSAGES_COMPLETE_GRIPS_SERVICE_OPEN',parts=parts,
        selected=False,physical_pass=False,W5_complete=False,source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds(),
        open=['Native WAGO housing and independent insulation grips are still required.',
            'New channels are not proof of retained load paths, PETG stiffness, lever actuation or whole-bank release.',
            'Match supports/assembly/stock/E3 before selecting whole bank; R51 remains selected15/20=75%.']))
    print(json.dumps(dict(parts=len(parts),selected=False,physical_pass=False)),flush=True)
if __name__=='__main__':main()
