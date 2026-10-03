"""One local bottom-open clearance for the exact R15 Cover/Deck edge hit.

Keep existing mount material and bearing rings. Native subtractive change
only; same Cover print, hardware and wiring. No global coincident difference.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,tempfile,shutil,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-deck-edge-service-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-cover-deck-edge-service-r1'

def main():
    import FreeCAD as A,Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True);pins={}
    assert not (OUT/'checks.json').exists()
    def read(rel):pins[rel]=sha(ROOT/rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    failure=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r15/checks.json')
    assert not failure['errors'] and failure['completed_clear_lifts_mm']==[2] and len(failure['hits'])==1
    hit=failure['hits'][0];assert (hit['phase'],hit['part'],hit['owner'])==('sampled_lift_5','Cover','CandidateDeck')
    native=read('hardware/electronics/full-cat/servo-fuse-cover-fixed-guard-service-r1/checks.json')
    row=native['exports'][0];pins[row['file']]=sha(ROOT/row['file'])
    d=A.openDocument(str(ROOT/row['file']));external=[Path(q.FileName) for q in A.listDocuments().values() if q.FileName]
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    parent=d.getObject(row['final']);bounds=hit['bounds_mm'];bottom=parent.Shape.BoundBox.ZMin-.1
    p=d.addObject('App::VarSet','DeckEdgeClearanceParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.35
    tool=d.addObject('Part::Box','WholeLocalDeckEdgeSweep');tool.Placement.Base=A.Vector(bounds[0]-.35,bounds[1]-.35,bottom)
    tool.setExpression('Length',f'{bounds[3]-bounds[0]} mm + 2*DeckEdgeClearanceParameters.Allowance')
    tool.setExpression('Width',f'{bounds[4]-bounds[1]} mm + 2*DeckEdgeClearanceParameters.Allowance')
    tool.setExpression('Height',f'{bounds[5]-bottom} mm + DeckEdgeClearanceParameters.Allowance')
    tool.setExpression('Placement.Base.x',f'{bounds[0]} mm - DeckEdgeClearanceParameters.Allowance')
    tool.setExpression('Placement.Base.y',f'{bounds[1]} mm - DeckEdgeClearanceParameters.Allowance')
    final=d.addObject('Part::Cut','CoverDeckEdgeServiceFinished');final.Base=parent;final.Tool=tool;final.Refine=False
    dest=CAD/'CoverDeckEdgeClearance.FCStd';exports=[];mounts=[]
    try:
        print('COVER_EDGE_RECOMPUTE',os.getpid(),flush=True);d.recompute();d.saveAs(str(dest))
        assert not final.Shape.isNull()
        removed=parent.Shape.common(tool.Shape)
        for x in (-84,106):
            for side in (-1,1):
                lo,hi=sorted((side*88,side*102));zone=Part.makeBox(12,hi-lo,12,A.Vector(x-6,lo,109))
                ring=Part.makeCylinder(2.5,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)).cut(Part.makeCylinder(1.2,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)))
                loss=removed.common(zone).Volume;ringloss=removed.common(ring).Volume
                assert loss<1e-5 and ringloss<1e-5,('MOUNT_MATERIAL_CHANGED',x,side,loss,ringloss)
                mounts.append(dict(xy=[x,side*91],original_zone_removed_mm3=loss,bearing_removed_mm3=ringloss))
        v=final.Shape.Volume;assert removed.Volume>0 and abs(parent.Shape.Volume-v-removed.Volume)<1e-5
        p.Allowance=.45;d.recompute();probe=final.Shape.Volume;assert probe<v
        p.Allowance=.35;d.recompute();assert abs(final.Shape.Volume-v)<1e-5
        s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        d.save();s.exportBrep(str(CAD/'Cover_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0)
        bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Cover_UNSELECTED.stl'))
        exports.append(dict(tag='Cover',file=dest.relative_to(ROOT).as_posix(),final=final.Name,single_solid=True,strict_BOP_errors=0,closed_STL=True,
          dimensions_mm=dims,volume_mm3=v,removed_mm3=removed.Volume,added_mm3=0,parameter_mm=[.35,.45,.35],nominal_probe_volumes_mm3=[v,probe,v]))
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-cover-edge-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            to=tmp/fp.relative_to(ROOT);to.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,to)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute();s=re.getObject(exports[0]['final']).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-exports[0]['volume_mm3'])<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values());exports[0]['relocated_reopen']=True
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_COVER_DECK_EDGE_COMPLETE_SHARED_REMOVAL_OPEN',selected=False,physical_pass=False,W5_complete=False,
      exports=exports,mounts=mounts,subtractive_by_native_construction=True,parent_cover_brep='hardware/cad/studies/servo-fuse-cover-fixed-guard-service-r1/Cover_WORLD.brep',
      parent_cover_brep_sha256=sha(ROOT/'hardware/cad/studies/servo-fuse-cover-fixed-guard-service-r1/Cover_WORLD.brep'),
      added_parts=0,added_fasteners=0,added_wires=0,whole_fixed_Guard_service=True,hit=hit,
      source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('COVER_EDGE_NATIVE_COMPLETE',flush=True)
if __name__=='__main__':main()
