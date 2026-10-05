"""Build one editable Cover from received bays, hood links and upper saddle.

No opaque whole-cover import, Deck cut, new fastener or source-wire move.
Only new connection material gets the two source windows. Parameter probe
and relocated reopen apply to this one replacement print, not the whole cat.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,tempfile
from servo_fuse_inputs_r1 import sha,save
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-cover-upper-front-native-r1';CAD=ROOT/'hardware/cad/studies/w5-cover-upper-front-native-r1'
RECEIPT=BASE/'w5-cover-upper-front-passages-r1/checks.json'

def main():
    import FreeCAD as A,Part,MeshPart
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    proof=json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert proof['status']=='UPPER_FRONT_PASSAGES_STATIC_ROOTS_CLEAR_NATIVE_PENDING'
    assert not proof['hits'] and not proof['errors'] and proof['patch_solids']==1
    for rel,h in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/rel)==h,rel
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    state=dict(status='UPPER_FRONT_COVER_NATIVE_PENDING',started_utc=start.isoformat(),
               selected=False,W1_complete=False,W5_complete=False,physical_pass=False)
    def progress(stage,**kw):
        state.update(stage=stage,updated_utc=datetime.now(timezone.utc).isoformat(),**kw)
        save(OUT/'progress.json',state);print('UPPER_FRONT_NATIVE',stage,flush=True)
    master=ROOT/proof['received_native_master'];parent=A.openDocument(str(master))
    d=A.newDocument('UpperFrontCoverRetention');target=CAD/'UpperFrontCoverRetention.FCStd';d.saveAs(str(target))
    params=d.addObject('App::VarSet','SourceWindowParameters')
    params.addProperty('App::PropertyLength','WindowAllowance');params.WindowAllowance=.4
    params.addProperty('App::PropertyString','Readiness')
    params.Readiness='Nominal prototype; delivered wire/threading/strength/creep phase2'
    def linked(name,source):
        q=d.addObject('App::Link',name);q.setLink(source);q.LinkPlacement=source.Placement;return q
    received=linked('ReceivedCoverFourBays',parent.getObject('CoverFourBays'))
    hood=[linked('Received'+k,parent.getObject(k)) for k in proof['keep_original_bridges']]
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length,q.Width,q.Height=[b[i+3]-b[i] for i in range(3)]
        q.Placement.Base=A.Vector(*b[:3]);return q
    raw=[box(k,b) for k,b in proof['added_boxes_mm'].items()]
    blanks=d.addObject('Part::MultiFuse','UpperFrontBridgeBlank');blanks.Shapes=raw;blanks.Refine=False
    holes=[]
    for name,b in proof['opening_boxes_mm'].items():
        q=box(name,b)
        for axis,size,i in (('x','Length',0),('y','Width',1),('z','Height',2)):
            q.setExpression('Placement.Base.'+axis,str(b[i]+.4)+' mm - SourceWindowParameters.WindowAllowance')
            q.setExpression(size,str(b[i+3]-b[i]-.8)+' mm + 2 * SourceWindowParameters.WindowAllowance')
        holes.append(q)
    tools=d.addObject('Part::Compound','TwoSourceThreadingWindows');tools.Links=holes
    bridge=d.addObject('Part::Cut','UpperFrontBridgeSlotted');bridge.Base=blanks;bridge.Tool=tools;bridge.Refine=False
    final=d.addObject('Part::MultiFuse','SourceCoverFinished');final.Shapes=[received,*hood,bridge];final.Refine=False
    d.save();progress('editable_linked_tree_saved',objects=len(d.Objects));d.recompute()
    s=final.Shape;assert s.isValid() and len(s.Solids)==1;assert not (s.check(True) or [])
    nominal=s.Volume;progress('nominal_valid',nominal_mm3=nominal)
    params.WindowAllowance=.5;d.recompute();s=final.Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume<nominal
    probe=s.Volume;progress('parameter_probe_valid',probe_mm3=probe)
    params.WindowAllowance=.4;d.recompute();s=final.Shape
    assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-nominal)<max(1e-5,nominal*1e-8)
    assert not (s.check(True) or [])
    for q in d.Objects:
        if q.ViewObject:q.ViewObject.Visibility=q==final
    d.save();s.exportBrep(str(CAD/'SourceCover_CANDIDATE_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert max(dims)+6<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'SourceCover_UNSELECTED_x1.stl'))
    progress('closed_export_saved',dimensions_mm=dims)
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(p.is_relative_to(ROOT) for p in deps)
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-upper-front-') as td:
        tmp=Path(td)
        for p in [target,*deps]:
            dest=tmp/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        moved=A.openDocument(str(tmp/target.relative_to(ROOT)));moved.recompute()
        s=moved.getObject('SourceCoverFinished').Shape
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()):A.closeDocument(name)
    finish=datetime.now(timezone.utc)
    state.update(status='UPPER_FRONT_COVER_NATIVE_PARAMETER_EXPORT_REOPEN_COMPLETE',
        nominal_mm3=nominal,probe_mm3=probe,parameter_probe_mm=[.4,.5,.4],BOP_errors=0,solids=1,
        closed_STLs=True,relocated_reopen=True,dimensions_mm=dims,editable_final_object='SourceCoverFinished',
        editable_new_bridge_object='UpperFrontBridgeSlotted',no_Deck_cut=True,new_screws=0,new_print_jobs=0,wire_paths_changed=False,
        remove_original_bridges=proof['remove_original_bridges'],keep_original_bridges=proof['keep_original_bridges'],
        minimum_nominal_inner_ligament_mm=proof['minimum_inner_ligament_mm'],assembly=proof['assembly'],
        shared_module_service_pending=True,
        manufacturing=dict(material='PETG',orientation='Received Cover lower rim toward bed; upper-window bridge remains inside inherited height',
            support='Phase2 slicer: support new high saddle/rectangular source windows, remove all support before threading wires',
            printer_profile=None,physical_fit_strength_creep_verified=False),
        finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),RECEIPT,*deps]},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in CAD.iterdir() if p.suffix.lower() in ('.fcstd','.brep','.stl')})
    save(OUT/'checks.json',state);progress('complete')

if __name__=='__main__':main()
