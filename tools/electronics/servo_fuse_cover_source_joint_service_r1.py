"""Bottom-open native passages for all three actual insulated source joints.

Use the full sleeve envelope, not the previous bare-wire contact witness.
Keep four existing mount zones and bearing rings; no new parts or hardware.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, math, tempfile, shutil, os
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r1'
CAD = ROOT/'hardware/cad/studies/servo-fuse-cover-source-joint-service-r1'

def main():
    import FreeCAD as A
    import Part, MeshPart
    start = datetime.now(timezone.utc); pins = {}
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed result'
    def read(rel):
        pins[rel] = sha(ROOT/rel)
        return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    prior = read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r17/checks.json')
    assert prior['completed_clear_lifts_mm'] == [2,5,10] and not prior['errors']
    assert prior['hits'][0]['owner'] == 'RetainedFeed/W042_BareExtension_DESIGN'
    receipt = read('hardware/electronics/full-cat/servo-fuse-cover-deck-edge-service-r2/checks.json')
    row = receipt['exports'][0]
    d = A.openDocument(str(ROOT/row['file']))
    external = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for fp in external: pins[fp.relative_to(ROOT).as_posix()] = sha(fp)
    parent = d.getObject(row['final']); bottom = parent.Shape.BoundBox.ZMin-.1
    p = d.addObject('App::VarSet', 'SourceJointServiceParameters')
    p.addProperty('App::PropertyLength','Allowance'); p.Allowance=.35
    tools=[]; envelopes=[]
    for ident in ('W042','W044','W052'):
        rels=[r for r in prior['source_sha256'] if r.endswith('/'+ident+'_Sleeve_DESIGN.brep')]
        assert len(rels)==1, (ident,rels)
        rel=rels[0]; pins[rel]=sha(ROOT/rel); assert pins[rel]==prior['source_sha256'][rel]
        s=Part.read(str(ROOT/rel)); b=s.BoundBox
        tool=d.addObject('Part::Box', ident+'WholeInsulatedJointPassage')
        for prop,val in [('Length',b.XLength),('Width',b.YLength)]:
            tool.setExpression(prop,f'{val} mm + 2*SourceJointServiceParameters.Allowance')
        tool.setExpression('Height',f'{b.ZMax-bottom} mm + SourceJointServiceParameters.Allowance')
        tool.setExpression('Placement.Base.x',f'{b.XMin} mm - SourceJointServiceParameters.Allowance')
        tool.setExpression('Placement.Base.y',f'{b.YMin} mm - SourceJointServiceParameters.Allowance')
        tool.Placement.Base.z=bottom
        tools.append(tool); envelopes.append(dict(id=ident,source=rel,bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
    compound=d.addObject('Part::Compound','WholeSourceJointPassages'); compound.Links=tools
    final=d.addObject('Part::Cut','CoverSourceJointServiceFinished')
    final.Base=parent; final.Tool=compound; final.Refine=False
    dest=CAD/'CoverSourceJointService.FCStd'; exports=[]; mounts=[]
    try:
        print('SOURCE_JOINT_COVER_RECOMPUTE',os.getpid(),flush=True)
        d.recompute(); d.saveAs(str(dest)); s=final.Shape.copy()
        strict=s.check(True) or []
        save(OUT/'progress.json',dict(stage='NATIVE_CUT',valid=s.isValid(),solids=len(s.Solids),strict_BOP_errors=[str(e) for e in strict]))
        assert s.isValid() and len(s.Solids)==1 and not strict
        removed=parent.Shape.common(compound.Shape)
        for x in (-84,106):
            for side in (-1,1):
                lo,hi=sorted((side*88,side*102))
                zone=Part.makeBox(12,hi-lo,12,A.Vector(x-6,lo,109))
                ring=Part.makeCylinder(2.5,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)).cut(Part.makeCylinder(1.2,3.5,A.Vector(x,side*96.5,116),A.Vector(0,side,0)))
                loss=removed.common(zone).Volume; ringloss=removed.common(ring).Volume
                assert loss<1e-5 and ringloss<1e-5,(x,side,loss,ringloss)
                mounts.append(dict(xy=[x,side*91],original_zone_removed_mm3=loss,bearing_removed_mm3=ringloss))
        v=s.Volume; assert removed.Volume>0 and v<parent.Shape.Volume
        p.Allowance=.45; d.recompute(); probe=final.Shape.Volume; assert probe<v
        p.Allowance=.35; d.recompute(); assert abs(final.Shape.Volume-v)<1e-5
        s=final.Shape.copy(); assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        d.save(); s.exportBrep(str(CAD/'Cover_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(math.pi,0,0); bb=mesh.BoundBox; dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin); mesh.write(str(CAD/'Cover_UNSELECTED.stl'))
        exports.append(dict(tag='Cover',file=dest.relative_to(ROOT).as_posix(),final=final.Name,single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=v,parameter_mm=[.35,.45,.35],nominal_probe_volumes_mm3=[v,probe,v]))
    finally:
        for name in list(A.listDocuments()): A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-joint-cover-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            to=tmp/fp.relative_to(ROOT); to.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(fp,to)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute(); s=re.getObject(exports[0]['final']).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-v)<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
            exports[0]['relocated_reopen']=True
        finally:
            for name in list(A.listDocuments()): A.closeDocument(name)
    end=datetime.now(timezone.utc)
    parentpath='hardware/cad/studies/servo-fuse-cover-deck-edge-service-r2/Cover_WORLD.brep'
    save(OUT/'checks.json',dict(status='NATIVE_COVER_INSULATED_SOURCE_JOINT_PASSAGES_COMPLETE_SHARED_REMOVAL_OPEN',selected=False,physical_pass=False,W5_complete=False,exports=exports,mounts=mounts,source_joint_envelopes=envelopes,subtractive_by_native_construction=True,parent_cover_brep=parentpath,parent_cover_brep_sha256=sha(ROOT/parentpath),added_parts=0,added_fasteners=0,added_wires=0,removed_mm3=removed.Volume,source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('SOURCE_JOINT_COVER_NATIVE_COMPLETE',flush=True)

if __name__=='__main__': main()
