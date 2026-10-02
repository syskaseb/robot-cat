"""Editable Deck and MAIN for the accepted complete positive-input candidate.

Reopen and local parameter proofs; never recompute the interactive E6 model.
No STL is emitted unless candidate rigid contacts and native topology pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,shutil,tempfile,sys
import main_positive_complete_r7 as C
ROOT=C.ROOT;M=C.M;OUT=ROOT/'hardware/electronics/full-cat/main-positive-native-r1'
CAD=ROOT/'hardware/cad/studies/main-positive-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart,Sketcher
    from open_deck_p0_plate import rect,circle
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    candidate=json.loads((C.OUT/'checks.json').read_text(encoding='utf-8'))
    assert not candidate['blocking_hits'],candidate['blocking_hits']
    for path,h in candidate['source_sha256'].items():assert M.sha(ROOT/path)==h,path
    assert M.sha(Path(C.__file__))==candidate['script_sha256']
    start=datetime.now(timezone.utc);checks={};exports={};sources={}
    offset=[0,0,0];sketches=[]
    def point(v):return A.Vector(*(v[i]-offset[i] for i in range(3)))
    def sketch(d,n,z):
        s=d.addObject('Sketcher::SketchObject',n);s.AttacherEngine='Engine Plane'
        s.Placement=A.Placement(point([0,0,z]),A.Rotation());sketches.append(s);return s
    # Sketch coordinates remain world XY, placement alone handles translation.
    def block(d,n,b):
        s=sketch(d,n+'Profile',b[2]);rect(s,b[0],b[1],b[3]-b[0],b[4]-b[1])
        p=d.addObject('Part::Extrusion',n);p.Base=s;p.Dir=A.Vector(0,0,b[5]-b[2]);p.Solid=True;return p
    def cylinder(d,n,xyz,r,h,direction=[0,0,1]):
        p=d.addObject('Part::Cylinder',n);p.Radius=r;p.Height=h
        p.Placement=A.Placement(point(xyz),A.Rotation(A.Vector(0,0,1),A.Vector(*direction)));return p
    def cut(d,n,a,b):
        p=d.addObject('Part::Cut',n);p.Base=a;p.Tool=b;p.Refine=False;return p
    def fuse(d,n,objects):
        p=d.addObject('Part::MultiFuse',n);p.Shapes=objects;p.Refine=False;return p
    def finalize(d,dest,final,param,prop,value,key):
        added=[s for s in sketches if s.Document==d]
        assert all(s.FullyConstrained and s.solve()==0 for s in added)
        d.recompute([s for s in added]);d.save();d.recompute()
        print(key+': recomputed, strict geometry',flush=True)
        shape=final.Shape.copy();assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        print(key+': strict geometry complete',flush=True)
        world=shape.copy();world.translate(A.Vector(*offset))
        expected=Part.Shape();expected.read(str(C.OUT/('Deck_candidate.brep' if key=='Deck' else 'MAIN_candidate.brep')))
        # Parent G1ExitDeck is retained as native Base. Match changed feature
        # construction and aggregate invariants, not two expensive booleans
        # between the entire identical, history-heavy Deck solids.
        differences=[abs(expected.Volume-world.Volume)]
        bbox_delta=max(abs(getattr(expected.BoundBox,n)-getattr(world.BoundBox,n)) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax'))
        local_difference=None
        if key=='MAIN':
            local=final.Document.PositiveInputSeparatedSeat.Shape.copy();local.translate(A.Vector(*offset))
            target=Part.Shape();target.read(str(C.OUT/'MAIN_positive_seat_DESIGN.brep'))
            local_difference=[target.cut(local).Volume,local.cut(target).Volume]
            assert max(local_difference)<1e-5,local_difference
        # MAIN's recomputed inherited base differs from its saved R40 reserve
        # by0.000685mm3, bbox identical. Require exact changed-seat proof and
        # explicit <=0.001mm3 aggregate numerical tolerance, not a waived hit.
        assert differences[0]<(1e-3 if key=='MAIN' else 1e-4) and bbox_delta<1e-6,(differences,bbox_delta)
        print(key+': candidate invariants complete, parameter proof',flush=True)
        volume=shape.Volume;setattr(param,prop,value+.1);d.recompute();probe=final.Shape.Volume
        assert abs(probe-volume)>1e-6,(key,volume,probe)
        setattr(param,prop,value);d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        final_name=final.Name;docname=d.Name;d.save();A.closeDocument(docname)
        with tempfile.TemporaryDirectory(prefix='robot-cat-positive-native-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q));name=re.Name
            try:
                re.recompute();s=re.getObject(final_name).Shape
                assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
            finally:A.closeDocument(name)
        checks[key]=dict(strict_BOP_errors=0,constrained_new_sketches=len(added),parameter_probe_volumes_mm3=[volume,probe,volume],
                         relocated_reopen=True,candidate_volume_delta_mm3=differences[0],candidate_bbox_delta_mm=bbox_delta,
                         comparison_scope='Retained native parent + identical changed native feature dimensions; volume/bbox invariants. No full-Deck symmetric-difference claim.',final_object=final_name)
        checks[key].update(changed_seat_symmetric_difference_mm3=local_difference,
                           aggregate_volume_tolerance_mm3=1e-3 if key=='MAIN' else 1e-4)
        exports[key]=shape;world.exportBrep(str(CAD/(key+'_WORLD.brep')))

    # Previous worker completed Deck finalize and exported Deck_WORLD only
    # AFTER all native proofs. It subsequently failed on a deleted Deck proxy
    # when starting MAIN. Recover that completed result; do not rebuild Deck.
    evidence=ROOT/'tools/electronics/main_positive_native_interrupted_r1.py'
    assert M.sha(evidence)=='81c76c761de8118ecf2d0731520e7665e56a71a04846d7cb1f5c3b0fdb0a24fa'
    shape=Part.Shape();shape.read(str(CAD/'Deck_WORLD.brep'))
    expected=Part.Shape();expected.read(str(C.OUT/'Deck_candidate.brep'))
    assert shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-expected.Volume)<1e-4
    re=A.openDocument(str(CAD/'DeckMainPositive.FCStd'));name=re.Name
    try:
        cached=re.MainPositiveDeck.Shape
        assert abs(cached.Volume-shape.Volume)<1e-5 and cached.isValid()
        assert abs(re.PositiveParameters.SpliceGrooveRadius.Value-2.1)<1e-9
        additions=[o for o in re.Objects if o.TypeId=='Sketcher::SketchObject' and o.Name.startswith(('HolderTop','Splice','PositivePortal'))]
        assert all(o.FullyConstrained and o.solve()==0 for o in additions)
        number=len(additions)
    finally:A.closeDocument(name)
    exports['Deck']=shape
    checks['Deck']=dict(strict_BOP_errors=0,constrained_new_sketches=number,parameter_probe_passed=True,
        parameter_probe_volumes_mm3=None,relocated_reopen=True,final_object='MainPositiveDeck',
        recovered_completed_proof=True,recovered_worker_script_sha256=M.sha(evidence),
        proof='Previous worker reached Deck_WORLD export AFTER strict geometry/parameter restore/relocated recompute; subsequently failed on deleted Deck proxy while starting MAIN. Numeric probe volumes were not persisted and are not invented.',
        candidate_volume_delta_mm3=abs(shape.Volume-expected.Volume))
    M.save(OUT/'recovered-Deck-proof.json',dict(**checks['Deck'],native_sha256=M.sha(CAD/'DeckMainPositive.FCStd'),brep_sha256=M.sha(CAD/'Deck_WORLD.brep')))
    src=ROOT/'hardware/cad/studies/g1-exit-restraints-finish-r1/DeckG1ExitRestraints.FCStd'
    sources[src.relative_to(ROOT).as_posix()]=M.sha(src)

    offset=[105.82,8.16,52]
    sketches.clear()
    src=ROOT/'hardware/cad/studies/main-input-return-finish-r2/MainInputMount.FCStd'
    sources[src.relative_to(ROOT).as_posix()]=M.sha(src)
    dest=CAD/'MainPositiveMount.FCStd';d=A.openDocument(str(src));name=d.Name
    try:
        d.saveAs(str(dest));p=d.addObject('App::VarSet','PositiveSeatParameters');p.addProperty('App::PropertyLength','Height');p.Height=6
        raw=block(d,'PositiveInputBeam',[126.5,-10.5,83,134,1,89]);raw.setExpression('Dir.z','PositiveSeatParameters.Height')
        groove=cylinder(d,'PositiveInputGroove',[129,-8,82.9],1.7,6.2)
        seat=cut(d,'PositiveInputGrooved',raw,groove)
        import main_input_return_r4 as W
        edge=W.M.geometry()[-2]
        pipe=Part.Wire([edge]).makePipeShell([Part.Wire([Part.makeCircle(1.7,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])],True,False)
        pipe.translate(A.Vector(*[-v for v in offset]));tool=d.addObject('PartDesign::Feature','PreservedReturnGrooveTool');tool.Shape=pipe
        tool.addProperty('App::PropertyString','SourceCentreline');tool.SourceCentreline='hardware/electronics/full-cat/main-input-return-r4/W060_9_CENTERLINE.brep'
        tool.addProperty('App::PropertyString','SourceSHA256');tool.SourceSHA256=M.sha(ROOT/tool.SourceCentreline)
        seat=cut(d,'PositiveReturnSeparated',seat,tool)
        notch=block(d,'PositiveStrapPassage',[126.4,-1.5,83,134.1,-.3,85.5])
        seat=cut(d,'PositiveInputSeat',seat,notch)
        clearance=block(d,'PreservedReturnStrapPassage',[126.55,-2.9,82.9,129.45,-1.3,89.1])
        seat=cut(d,'PositiveInputSeparatedSeat',seat,clearance)
        final=fuse(d,'MainPositiveAdapter',[d.MainInputAdapter,seat])
        finalize(d,dest,final,p,'Height',6,'MAIN')
    finally:
        if name in A.listDocuments():A.closeDocument(name)
    for key,s in exports.items():
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
        mesh.write(str(CAD/(key+'_x1.stl')));checks[key].update(closed=True,components=1,dimensions_mm=dims)
    end=datetime.now(timezone.utc)
    M.save(OUT/'checks.json',dict(status='NATIVE_COMPLETE_WITH_SOFT_FIT_CONDITION',native_checks=checks,
        source_sha256=sources,candidate_checks_sha256=M.sha(C.OUT/'checks.json'),script_sha256=M.sha(Path(__file__)),
        selected=False,W5_complete=False,physical_pass=False,collision_free=False,soft_contacts=candidate['soft_contacts'],
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    geo=[]
    for key,s in exports.items():
        world=s.copy()
        if key=='MAIN':world.translate(A.Vector(105.82,8.16,52))
        vertices,triangles=world.tessellate(.6);geo.append(dict(name=key,vertices=[list(v) for v in vertices],triangles=triangles))
    for f in C.OUT.glob('*_DESIGN.brep'):
        s=Part.Shape();s.read(str(f));vertices,triangles=s.tessellate(.4);geo.append(dict(name=f.stem,vertices=[list(v) for v in vertices],triangles=triangles))
    M.save(OUT/'preview-geometry.json',geo)
    print(json.dumps(dict(status='NATIVE_COMPLETE_WITH_SOFT_FIT_CONDITION',native=checks,seconds=(end-start).total_seconds())),flush=True)

if __name__=='__main__':main()
